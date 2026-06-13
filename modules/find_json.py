from __future__ import annotations

from pathlib import Path


LANGUAGE_PRIORITY = [
    "en_us.json",
    "ru_ru.json",
    "zh_cn.json",
    "ja_jp.json",
]


def _is_lang_json(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() == ".json" and path.parent.name.lower() == "lang"


def _sort_key(path: Path) -> tuple[int, str]:
    name = path.name.lower()
    try:
        priority = LANGUAGE_PRIORITY.index(name)
    except ValueError:
        priority = len(LANGUAGE_PRIORITY)
    return priority, str(path).lower()


def find_json(unzip_folder_path: str | Path) -> list[str]:
    root = Path(unzip_folder_path)

    if not root.exists():
        raise FileNotFoundError(f"폴더가 존재하지 않습니다: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"폴더가 아닙니다: {root}")

    lang_paths = sorted(
        {
            path.resolve()
            for path in root.rglob("*.json")
            if _is_lang_json(path)
        },
        key=_sort_key,
    )
    lang_files = [str(path) for path in lang_paths]
    if lang_files:
        return lang_files

    matches: list[str] = []
    for language_file in LANGUAGE_PRIORITY:
        matches = [str(path.resolve()) for path in root.rglob(language_file)]
        if matches:
            return matches

    raise FileNotFoundError(
        "언어 파일을 찾을 수 없습니다.\n"
        f"탐색 폴더: {root}\n"
        f"탐색 대상: lang/*.json, {LANGUAGE_PRIORITY}"
    )
