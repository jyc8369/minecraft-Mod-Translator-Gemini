# Release Plan

## Windows

Build:

```bat
build_windows.bat
```

Output:

```text
dist/Minecraft-Mod-Translator-Gemini/
```

Package:

```text
zip the dist folder
```

## macOS

Build:

```sh
chmod +x build_macos.sh
./build_macos.sh
```

Output:

```text
dist/Minecraft Mod Translator Gemini.app
```

Package:

```text
zip the .app bundle
```

Notes:

- Build on macOS only.
- Open the `.app` once before packaging if Gatekeeper/quarantine attributes appear during local testing.

## Notes

- Build each OS on that OS.
- `google-genai` and `customtkinter` must be available in the build environment.
- macOS notarization and code signing are not included yet.
