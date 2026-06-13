from __future__ import annotations

import json
import logging
from pathlib import Path


DEFAULT_CONFIG = {
    "gemini_api_key": "",
    "window_width": 400,
    "window_height": 600,
    "ui_language": "ko",
}


def write_config(project_root: str | Path, config_data: dict) -> None:
    config_path = Path(project_root) / "config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)


def read_config(project_root: str | Path) -> dict:
    config_path = Path(project_root) / "config.json"

    if not config_path.exists():
        write_config(project_root, DEFAULT_CONFIG)
        logging.getLogger(__name__).info("config.json이 없어 기본 파일을 생성했습니다: %s", config_path)
        return DEFAULT_CONFIG.copy()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        write_config(project_root, DEFAULT_CONFIG)
        logging.getLogger(__name__).warning("config.json을 읽을 수 없어 기본 파일로 재생성했습니다: %s", config_path)
        return DEFAULT_CONFIG.copy()
