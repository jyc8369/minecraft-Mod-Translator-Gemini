from __future__ import annotations

from pathlib import Path
import zipfile


def zip_jar(source_dir: str | Path, output_jar: str | Path) -> None:
    source = Path(source_dir)
    output_jar = Path(output_jar)
    output_jar.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_jar, "w", zipfile.ZIP_DEFLATED) as jar:
        for file in source.rglob("*"):
            if file.is_file():
                jar.write(file, file.relative_to(source))

