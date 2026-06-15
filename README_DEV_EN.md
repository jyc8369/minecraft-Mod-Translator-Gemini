# Minecraft Mod Translator Gemini (MMTG) - Developer Documentation

This tool scans language files (`lang/*.json`) inside Minecraft mod JAR files, translates them with the Google Gemini API, and repackages the result back into a JAR.

## 1. Tech Stack

### Runtime and Language
- **Python 3.12+**
- Modular architecture with type hints
- Standard-library-first handling for file I/O, compression, and multithreading

### GUI
- **customtkinter**
- Desktop UI built on `tkinter` with a modern theme and widget styling
- Responsible for input selection, progress display, log output, and result review

### AI Translation
- **google-genai**
- Uses the Gemini API to translate `lang/*.json` key-value pairs
- Preserves keys and translates values only

### Build and Distribution
- **PyInstaller**
- Builds single executables or app bundles for Windows and macOS
- Release packaging scripts live under `release/build/`

### Supporting Systems
- **logging**
- **threading**
- **json / zipfile / pathlib / shutil**
- Used for config management, JAR extraction/repackaging, and background task execution

## 2. Project Structure

```text
.
├── main.py                  # GUI entry point, workflow control, translation orchestration
├── modules/                 # Core business logic
│   ├── config.py            # OS-specific config.json path management and read/write
│   ├── find_json.py         # JAR language file discovery and priority selection
│   ├── gemini_translator.py # Gemini API calls, chunking, retries, JSON response handling
│   ├── i18n.py              # UI multilingual strings
│   ├── unzip_jar.py         # JAR extraction
│   └── zip_jar.py           # Repackaging JARs with translated output
├── release/
│   └── build/               # Build and packaging scripts
└── requirements.txt         # Python dependency list
```

## 3. Core Workflow

The program runs in the following order:

`Select JAR or Folder` -> `Extract to Temporary Directory` -> `Scan Language Files` -> `Select Translation Target` -> `Gemini Translation` -> `Replace Files` -> `Repackage JAR` -> `Save Result`

### Processing Model
- If the input is a JAR, it is first extracted to a temporary directory for inspection.
- The app searches for `lang/*.json` or priority-based language files.
- Translation keeps JSON keys unchanged and translates values only.
- After translation, the original structure is preserved and compressed again.

## 4. Gemini Translation Details

### 4.1 Chunking Strategy
- Large JSON files are split into smaller chunks instead of being sent at once.
- The following limits are used to reduce API restrictions and missing responses:
  - `MAX_CHUNK_CHARS`
  - `MAX_CHUNK_ITEMS`
- Chunk-level processing improves stability for large mods.

### 4.2 Retry and Stability
- Retry logic handles network issues and temporary API failures.
- Requests are retried within the `MAX_RETRIES` limit.
- `RETRY_BASE_DELAY` is used to apply exponential backoff.

### 4.3 Prompt Design
- JSON keys are explicitly marked as immutable.
- Rules preserve Minecraft placeholders such as `%s`, `%1$s`, and `%d`.
- The response format is constrained to JSON to improve parsing reliability.

## 5. Configuration and Environment

### Config File Location
The app stores `MMTG/config.json` in the standard config path for each OS.

- **Windows**: `%APPDATA%/MMTG/config.json`
- **macOS**: `~/Library/Application Support/MMTG/config.json`
- **Linux**: `~/.config/MMTG/config.json`

### Example Config
```json
{
  "gemini_api_key": "YOUR_API_KEY",
  "window_width": 400,
  "window_height": 600,
  "ui_language": "ko"
}
```

### Related Module
- `modules/config.py` handles path resolution, reading, and writing.
- The config file is created automatically on first launch if it does not exist.

## 6. UI and UX

### Asynchronous Execution
- Translation runs in the background via `threading`.
- The UI thread stays focused on input, progress, and logs to avoid freezing.

### Logging System
- A custom `logging.Handler` streams logs to the GUI in real time.
- Log levels are color-coded for readability.

### Multilingual UI
- UI strings are managed in `modules/i18n.py`.
- Korean and English are supported by default.

## 7. Translation Target Selection

- Translation targets are chosen through the `LANGUAGE_PRIORITY` list in `modules/find_json.py`.
- For example, you can prioritize files from `en_us.json` to `ru_ru.json`.
- Add new entries to this list to expand translation coverage.

## 8. Build and Deployment

### Windows
```bat
release/build/build_windows.bat
```
- Output: `release/build/dist/MMTG/`

### macOS
```sh
chmod +x release/build/build_macos.sh
cd release/build
./build_macos.sh
```
- Output: `release/build/dist/MMTG.app`

### Post-build Cleanup
- Build scripts delete the `build/` folder when finished.

## 9. Linux Packages

GitHub Actions releases generate distribution-specific Linux packages.

- Ubuntu: `.deb`
- Debian: `.deb`
- Fedora: `.rpm`
- Arch: `.pkg.tar.zst`

Packages include the executable and launcher scripts.

Packaging scripts:
- `release/build/package_fedora.sh`
- `release/build/package_arch.sh`

## 10. Development Guide

### Add a New UI Language
1. Add a new language code and its translations to `TRANSLATIONS` in `modules/i18n.py`.
2. Add the same language code to `SUPPORTED_UI_LANGS`.

### Expand Translation Targets
1. Add a new `.json` filename to `LANGUAGE_PRIORITY` in `modules/find_json.py`.
2. The scan order follows the list order.

## 11. Requirements

- Python 3.12+
- `pip install -r requirements.txt`

## 12. Notes

- Translation logic is handled by `main.py` and `modules/`.
- The GUI is responsible only for input selection, progress display, and result presentation.
- Logs are shown in the GUI and can be saved manually.
