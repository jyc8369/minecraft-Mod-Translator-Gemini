# Release Plan

## Windows

Build:

```bat
release/build/build_windows.bat
```

Output:

```text
release/build/dist/MMTG/
```

Package:

```text
zip the dist folder
```

## macOS

Build:

```sh
chmod +x release/build/build_macos.sh
cd release/build
./build_macos.sh
```

Output:

```text
release/build/dist/MMTG.app
```

Package:

```text
macOS arm64 and x86_64 are built in separate jobs and zipped separately.
```

Notes:

- Build arm64 and x86_64 separately on macOS runners.
- Open the `.app` once before packaging if Gatekeeper/quarantine attributes appear during local testing.
- Build scripts live under `release/build/`.

## Linux Packages

- Ubuntu: `.deb`
- Debian: `.deb`
- Fedora: `.rpm`
- Arch: `.pkg.tar.zst`

Linux jobs are split per distribution in the release workflow.
Fedora and Arch packaging scripts live under `release/build/`.

## Notes

- Build each OS on that OS.
- `google-genai` and `customtkinter` must be available in the build environment.
- macOS notarization and code signing are not included yet.
