from __future__ import annotations

from pathlib import Path
import zipfile


def unzip_jar(jar_file: str | Path, output_root: str | Path) -> Path:
    jar_path = Path(jar_file)
    output_root = Path(output_root)

    unzip_root = output_root / "unzip"
    unzip_root.mkdir(parents=True, exist_ok=True)

    extract_dir = unzip_root / jar_path.stem
    extract_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(jar_path, "r") as jar:
        jar.extractall(extract_dir)

    return extract_dir

