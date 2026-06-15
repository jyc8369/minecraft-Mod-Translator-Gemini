# Minecraft Mod Translator Gemini (MMTG) - User Guide (No Build Required)

## 1. Download

Download the appropriate file for your operating system from GitHub Releases.

- Windows: `~windows.zip`
- macOS:
  - `~macos-arm64.zip`
  - `~macos-x86_64.zip`
- Linux:
  - Ubuntu: `~ubuntu.deb`
  - Debian: `~debian.deb`
  - Fedora: `~fedora.rpm`
  - Arch: `arch.pkg.tar.zst`

## 2. Installation and Execution

### Windows
1. Extract the downloaded file.
2. Run `MMTG.exe`.

If a security warning appears, select "More info → Run anyway".

### macOS
Recommended macOS 15+
1. Extract the downloaded file.
2. Move the `.app` file to the Applications folder.
3. Run the application.
4. If execution is blocked:
   - System Settings → Privacy & Security → Open Anyway.

### Linux (Ubuntu / Debian / Fedora / Arch)

#### Debian / Ubuntu
```bash
sudo dpkg -i mmtg.deb
sudo apt-get install -f
```

#### Fedora
```bash
sudo dnf install mmtg.rpm
```

#### Arch
```bash
sudo pacman -U mmtg.pkg.tar.zst
```

Run after installation:
```bash
mmtg
```

## 3. API Configuration (Required)

A `config.json` file is automatically generated upon the first run.

File Locations:
* Windows: `%APPDATA%\MMTG\config.json`
* macOS: `~/Library/Application Support/MMTG/config.json`
* Linux: `~/.config/MMTG/config.json`

Example:
```json
{
  "gemini_api_key": "YOUR_API_KEY",
  "window_width": 400,
  "window_height": 600,
  "ui_language": "en"
}
```

### How to Configure

1. Get a Google Gemini API Key.
2. Open `config.json`.
3. Enter your key in the `gemini_api_key` field.
4. Save the file and restart the program.

## 4. How to Use

1. Run the program.
2. Select a Minecraft mod JAR or folder in "Input File".
3. Select an "Output Folder".
4. Click "Scan".
5. Choose the input and output languages.
6. Click "Start Translation".
7. Monitor progress.
8. A translated JAR will be generated upon completion.

---

## 5. Key Features

* Automatic JAR Analysis: Scans for `lang/*.json`.
* Selective Language Translation: Convert to your desired language.
* Progress Bar: Check overall and individual mod status.
* Log Window: Detailed view of the translation process.
* Multilingual UI: Supports Korean and English.

## 6. Troubleshooting

### Program fails to run
* Check for missing Java or runtime environment.
* Try running as an administrator.

### Translation fails
* Verify your API Key.
* Check your internet connection.

### Result is not generated
* Check output folder permissions.
* Ensure the JAR file is not corrupted.

## 7. Notes

* The original JAR file is not modified; a copy is created.
* Translation quality depends on the Gemini API response.
* Large mods may take a significant amount of time.
