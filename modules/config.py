from __future__ import annotations

import json
import logging
import os
import platform
from pathlib import Path


DEFAULT_CONFIG = {
    "gemini_api_key": "",
    "window_width": 400,
    "window_height": 600,
    "ui_language": "ko",
}

CONFIG_DIR_NAME = "MMTG"
CONFIG_FILE_NAME = "config.json"


def get_config_path(base_dir: str | Path | None = None) -> Path:
    if base_dir is None:
        system = platform.system().lower()
        home = Path.home()
        if system == "darwin":
            base_dir = home / "Library" / "Application Support"
        elif system == "windows":
            base_dir = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
        else:
            base_dir = home / ".config"
    return Path(base_dir) / CONFIG_DIR_NAME / CONFIG_FILE_NAME


def write_config(config_path: str | Path, config_data: dict) -> None:
    config_path = Path(config_path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)


def read_config(config_path: str | Path) -> dict:
    config_path = Path(config_path)

    if not config_path.exists():
        write_config(config_path, DEFAULT_CONFIG)
        logging.getLogger(__name__).info("config.json이 없어 기본 파일을 생성했습니다: %s", config_path)
        return DEFAULT_CONFIG.copy()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        write_config(config_path, DEFAULT_CONFIG)
        logging.getLogger(__name__).warning("config.json을 읽을 수 없어 기본 파일로 재생성했습니다: %s", config_path)
        return DEFAULT_CONFIG.copy()
