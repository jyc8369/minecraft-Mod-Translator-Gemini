from __future__ import annotations

import json
import re
import logging
import time
from collections.abc import Mapping
from pathlib import Path

MAX_CHUNK_CHARS = 12000
MAX_CHUNK_ITEMS = 120
MAX_RETRIES = 4
RETRY_BASE_DELAY = 2.0


class TranslationError(RuntimeError):
    def __init__(self, message: str, user_message: str | None = None) -> None:
        super().__init__(message)
        self.user_message = user_message or message


def _extract_json_text(response) -> str:
    text = getattr(response, "text", None)
    if text and text.strip():
        return text.strip()

    candidates = getattr(response, "candidates", None) or []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", None) or []
        chunks: list[str] = []
        for part in parts:
            part_text = getattr(part, "text", None)
            if part_text:
                chunks.append(part_text)
        combined = "".join(chunks).strip()
        if combined:
            return combined

    raise ValueError("Gemini 응답에서 텍스트를 찾지 못했습니다.")


def _parse_json_payload(raw_text: str):
    text = raw_text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start_candidates = [text.find("{"), text.find("[")]
        start_candidates = [idx for idx in start_candidates if idx != -1]
        if not start_candidates:
            raise
        start = min(start_candidates)
        end = max(text.rfind("}"), text.rfind("]"))
        if end <= start:
            raise
        return json.loads(text[start : end + 1])


def _build_prompt(
    source_json: str,
    input_lang: str,
    output_lang: str,
    chunk_index: int,
    chunk_total: int,
    retry: bool = False,
) -> str:
    chunk_note = f"Chunk {chunk_index}/{chunk_total}." if chunk_total > 1 else "Single chunk."
    retry_note = "\nThis is a retry. Do not omit any keys." if retry else ""
    return f"""
Translate this Minecraft language JSON from {input_lang} to {output_lang}.

{chunk_note}
{retry_note}

Rules:
- Keep every key exactly unchanged.
- Translate values only.
- Preserve placeholders such as %s, %1$s, %d, and similar tokens.
- Return valid JSON only.

Source JSON:
{source_json}
"""


def _chunk_mapping(data: Mapping[str, object]) -> list[dict[str, object]]:
    items = list(data.items())
    chunks: list[dict[str, object]] = []
    current: dict[str, object] = {}
    current_size = 0

    for key, value in items:
        entry = {key: value}
        entry_size = len(json.dumps(entry, ensure_ascii=False))
        if current and (
            len(current) >= MAX_CHUNK_ITEMS or current_size + entry_size > MAX_CHUNK_CHARS
        ):
            chunks.append(current)
            current = {}
            current_size = 0

        current[key] = value
        current_size += entry_size

    if current:
        chunks.append(current)

    return chunks


def _translate_payload(client, payload: object, input_lang: str, output_lang: str, chunk_index: int, chunk_total: int):
    source_json = json.dumps(payload, ensure_ascii=False)
    prompt = _build_prompt(source_json, input_lang, output_lang, chunk_index, chunk_total)

    last_exc: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model="gemini-flash-lite-latest",
                contents=prompt,
            )
            raw_text = _extract_json_text(response)
            return _parse_json_payload(raw_text)
        except Exception as exc:
            last_exc = exc
            if not _is_retryable_error(exc) or attempt == MAX_RETRIES:
                raise TranslationError(
                    f"Gemini chunk 번역 실패: {exc}",
                    "AI 번역 단계에서 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
                ) from exc
            time.sleep(RETRY_BASE_DELAY * attempt)

    if last_exc is not None:
        raise last_exc


def _is_retryable_error(exc: Exception) -> bool:
    text = str(exc).lower()
    retry_markers = [
        "503",
        "unavailable",
        "resource exhausted",
        "too many requests",
        "temporarily unavailable",
        "high demand",
    ]
    return any(marker in text for marker in retry_markers)


def _to_user_message(exc: Exception) -> str:
    if isinstance(exc, TranslationError):
        return exc.user_message

    text = str(exc).lower()
    if "not found" in text or "찾을 수 없습니다" in text:
        return "선택한 언어 파일을 찾지 못했습니다."
    if "json" in text and "decode" in text:
        return "언어 파일 형식이 올바르지 않습니다."
    if "api key" in text or "api_key" in text:
        return "Gemini API 키가 올바르지 않거나 비어 있습니다."
    if "503" in text or "unavailable" in text:
        return "AI 서버가 일시적으로 혼잡합니다. 잠시 후 다시 시도해 주세요."
    return "예기치 않은 오류가 발생했습니다."


def _is_suspicious_translation(source: Mapping[str, object], translated: Mapping[str, object]) -> bool:
    missing_keys = [key for key in source.keys() if key not in translated]
    if missing_keys:
        return True

    same_value_count = 0
    for key, source_value in source.items():
        translated_value = translated.get(key)
        if translated_value == source_value:
            same_value_count += 1

    if source and same_value_count / len(source) >= 0.8:
        return True

    return False


def translate_json(
    api_key: str,
    json_path: str | Path,
    input_lang: str,
    output_lang: str,
    logger: logging.Logger | None = None,
) -> None:
    try:
        from google import genai
    except ModuleNotFoundError as exc:
        raise TranslationError(
            "google-genai 패키지가 설치되어 있지 않습니다.",
            "필수 번역 라이브러리가 설치되지 않았습니다.",
        ) from exc

    client = genai.Client(api_key=api_key)
    json_path = Path(json_path)
    if logger:
        logger.info(
            "Gemini 번역 시작: %s (input=%s, output=%s)",
            json_path,
            input_lang,
            output_lang,
        )

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, Mapping):
        chunks = _chunk_mapping(data)
        if logger:
            logger.info("chunk 분할: %s -> %s chunks", json_path.name, len(chunks))
        translated: dict[str, object] = {}
        for idx, chunk in enumerate(chunks, start=1):
            if logger:
                logger.info(
                    "chunk 요청: %s chunk %s/%s (%s keys)",
                    json_path.name,
                    idx,
                    len(chunks),
                    len(chunk),
                )
            chunk_result = _translate_payload(client, chunk, input_lang, output_lang, idx, len(chunks))
            if not isinstance(chunk_result, dict):
                raise TranslationError(
                    "Gemini 응답이 JSON object 형식이 아닙니다.",
                    "AI 번역 결과 형식이 올바르지 않습니다.",
                )

            if _is_suspicious_translation(chunk, chunk_result):
                if logger:
                    missing = [key for key in chunk.keys() if key not in chunk_result]
                    logger.warning(
                        "번역 재시도: %s chunk %s/%s, 누락 key %s개, 동일값 비율 높음",
                        json_path.name,
                        idx,
                        len(chunks),
                        len(missing),
                    )
                retry_result = _translate_payload(client, chunk, input_lang, output_lang, idx, len(chunks))
                if isinstance(retry_result, dict) and not _is_suspicious_translation(chunk, retry_result):
                    chunk_result = retry_result

            missing_keys = [key for key in chunk.keys() if key not in chunk_result]
            if missing_keys and logger:
                logger.warning(
                    "누락 key 보정: %s chunk %s/%s -> %s",
                    json_path.name,
                    idx,
                    len(chunks),
                    ", ".join(missing_keys),
                )
            if logger:
                logger.info(
                    "chunk 결과: %s chunk %s/%s -> input %s keys / output %s keys",
                    json_path.name,
                    idx,
                    len(chunks),
                    len(chunk),
                    len(chunk_result),
                )

            for key, original_value in chunk.items():
                translated[key] = chunk_result.get(key, original_value)
        if logger:
            logger.info("번역 chunk 완료: %s (%s chunks)", json_path.name, len(chunks))
    else:
        if logger:
            logger.info("단일 payload 번역: %s", json_path.name)
        translated = _translate_payload(client, data, input_lang, output_lang, 1, 1)

    output_path = json_path.parent / f"{output_lang}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(translated, f, ensure_ascii=False, indent=2)
    if logger:
        logger.info("번역 결과 저장: %s", output_path)


def user_friendly_error_message(exc: Exception) -> str:
    return _to_user_message(exc)
