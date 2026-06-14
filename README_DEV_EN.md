````md
# Minecraft Mod Translator Gemini (MMTG)

A tool that searches for `lang/*.json` files inside Minecraft mod JARs, translates them using Gemini, and repackages them back into a JAR file.

## Features

- Select JAR files or folders
- Choose input / output languages
- Scan language files
- Translation progress display
- Per-mod status tracking
- Separate log window
- Automatic `config.json` generation
- UI language switching: `ko`, `en`

## Requirements

- Python 3.12+
- `customtkinter`
- `google-genai`

## Install

```bash
pip install -r requirements.txt
````

## Run

```bash
python main.py
```

## Configuration

The program uses `config.json` at runtime.

Example:

```json
{
  "gemini_api_key": "YOUR_API_KEY",
  "window_width": 400,
  "window_height": 600,
  "ui_language": "ko"
}
```

* `gemini_api_key`: Gemini API key
* `window_width`, `window_height`: saved window size
* `ui_language`: `ko` or `en`

If `config.json` does not exist, a default file is generated automatically.

## UI Flow

1. Select input JAR file or folder
2. Select output folder
3. Scan language files
4. Select input / output languages
5. Start translation
6. Check results and logs

## UI Layout

Left panel:

* Input file selection
* Output folder selection
* Scan
* Language selection
* Start / stop translation
* Progress display
* Log viewer

Right panel:

* Mod list

## Language Handling

* UI supports `ko` / `en`
* Changing UI language reloads the entire interface
* Progress labels such as `Waiting...`, `Total Progress`, `Current JAR Progress` also update according to UI language

## Build

### Windows

```bat
release/build/build_windows.bat
```

Output:

```text
release/build/dist/MMTG/
```

### macOS

```sh
chmod +x release/build/build_macos.sh
cd release/build
./build_macos.sh
```

Output:

```text
release/build/dist/MMTG.app
```

Build scripts remove the `build/` folder after completion.

## Linux Packages

GitHub Actions releases generate platform-specific packages per Linux distribution:

* Ubuntu: `.deb`
* Debian: `.deb`
* Fedora: `.rpm`
* Arch: `.pkg.tar.zst`

Each package includes the executable and launcher scripts.

Packaging scripts are located in:

* `release/build/package_fedora.sh`
* `release/build/package_arch.sh`

## Project Structure

```text
main.py
modules/
  config.py
  find_json.py
  gemini_translator.py
  i18n.py
  unzip_jar.py
  zip_jar.py
release/
  build/
    build_windows.bat
    build_macos.sh
    package_fedora.sh
    package_arch.sh
    Minecraft Mod Translator Gemini.spec
```

## Notes

* Translation logic is handled by `main.py` and `modules/`
* GUI is responsible only for input selection, progress display, and result presentation
* Logs are shown in the GUI and can be saved manually

```
```
