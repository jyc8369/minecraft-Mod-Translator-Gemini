from __future__ import annotations

from typing import Any


SUPPORTED_UI_LANGS = ("ko", "en")
DEFAULT_UI_LANG = "ko"


TRANSLATIONS: dict[str, dict[str, str]] = {
    "ko": {
        "app_title": "Minecraft Mod Translator",
        "log_window_title": "번역 로그",
        "log_save_button": "로그 저장 (.log)",
        "log_clear_button": "지우기",
        "input_files": "입력 폴더 또는 파일",
        "select_files": "파일 선택",
        "select_folder": "폴더 선택",
        "output_folder": "출력 폴더",
        "selected_none_files": "선택된 파일 없음",
        "selected_none_folder": "선택된 폴더 없음",
        "scan_title": "언어파일 스캔 시작",
        "scan_button": "스캔 시작",
        "input_langs": "입력 언어 목록",
        "output_langs": "출력 언어 목록",
        "start": "번역 시작",
        "stop": "정지",
        "log_view": "로그 보기",
        "mod_list": "모드 목록",
        "waiting": "대기 중...",
        "total_progress": "전체 진행률",
        "current_progress": "현재 JAR 진행률",
        "result_title": "작업 결과",
        "result_done": "작업 완료",
        "result_success": "성공",
        "result_failed": "실패",
        "result_ok": "확인",
        "ui_language": "UI 언어",
        "language_ko": "한국어",
        "language_en": "English",
        "input_lang_label": "입력 언어 목록",
        "output_lang_label": "출력 언어 목록",
        "no_input_files": "입력 파일이 없습니다.",
        "no_output_folder": "출력 폴더가 선택되지 않았습니다.",
        "no_jar_in_folder": "선택한 폴더에서 JAR 파일을 찾지 못했습니다.",
        "scan_start": "스캔 시작",
        "scan_complete": "언어 파일 스캔 완료",
        "translation_start_request": "번역 시작 요청",
        "translation_start": "번역 시작",
        "translation_complete": "번역 완료",
        "translation_failed": "번역 실패",
        "translation_stopped": "작업이 중단되었습니다.",
        "selected_language_file": "선택된 입력 언어 파일",
        "repack_start": "재압축 시작",
        "repack_done": "재압축 완료",
        "extract_delete": "압축 해제 폴더 삭제",
        "work_delete": "임시 폴더 삭제",
        "config_missing": "config.json이 없어 기본 파일을 생성했습니다",
        "config_rebuilt": "config.json을 읽을 수 없어 기본 파일로 재생성했습니다",
        "config_api_missing": "config.json의 gemini_api_key가 비어 있습니다.",
    },
    "en": {
        "app_title": "Minecraft Mod Translator",
        "log_window_title": "Translation Log",
        "log_save_button": "Save Log (.log)",
        "log_clear_button": "Clear",
        "input_files": "Input Folder or Files",
        "select_files": "Choose Files",
        "select_folder": "Choose Folder",
        "output_folder": "Output Folder",
        "selected_none_files": "No file selected",
        "selected_none_folder": "No folder selected",
        "scan_title": "Scan Language Files",
        "scan_button": "Scan",
        "input_langs": "Input Languages",
        "output_langs": "Output Languages",
        "start": "Start Translation",
        "stop": "Stop",
        "log_view": "View Log",
        "mod_list": "Mod List",
        "waiting": "Waiting...",
        "total_progress": "Total Progress",
        "current_progress": "Current JAR Progress",
        "result_title": "Result",
        "result_done": "Task Completed",
        "result_success": "Success",
        "result_failed": "Failed",
        "result_ok": "OK",
        "ui_language": "UI Language",
        "language_ko": "한국어",
        "language_en": "English",
        "input_lang_label": "Input Languages",
        "output_lang_label": "Output Languages",
        "no_input_files": "No input file selected.",
        "no_output_folder": "No output folder selected.",
        "no_jar_in_folder": "No JAR files were found in the selected folder.",
        "scan_start": "Scan started",
        "scan_complete": "Language file scan complete",
        "translation_start_request": "Translation requested",
        "translation_start": "Translation started",
        "translation_complete": "Translation complete",
        "translation_failed": "Translation failed",
        "translation_stopped": "The job was stopped.",
        "selected_language_file": "Selected source language file",
        "repack_start": "Repacking started",
        "repack_done": "Repacking complete",
        "extract_delete": "Extracted folder removed",
        "work_delete": "Temporary folder removed",
        "config_missing": "config.json was missing, so a default file was created",
        "config_rebuilt": "config.json could not be read, so a default file was recreated",
        "config_api_missing": "gemini_api_key in config.json is empty.",
    },
}


def normalize_ui_lang(value: str | None) -> str:
    if not value:
        return DEFAULT_UI_LANG
    value = value.strip().lower()
    if value in SUPPORTED_UI_LANGS:
        return value
    if value.startswith("en"):
        return "en"
    return "ko"


def tr(key: str, lang: str | None = None, **kwargs: Any) -> str:
    normalized = normalize_ui_lang(lang)
    text = TRANSLATIONS.get(normalized, {}).get(key)
    if text is None:
        text = TRANSLATIONS[DEFAULT_UI_LANG].get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
