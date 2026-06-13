# Minecraft Mod Translator Gemini ( MMTG )

Minecraft 모드 JAR 안의 `lang/*.json` 파일을 찾아 Gemini로 번역하고, 다시 JAR로 패키징하는 도구입니다.

## Features

- JAR 파일 또는 폴더 선택
- 입력 언어 / 출력 언어 선택
- 언어 파일 스캔
- 번역 진행률 표시
- 모드별 상태 표시
- 로그 창 분리 표시
- `config.json` 자동 생성
- UI 언어 전환: `ko`, `en`

## Requirements

- Python 3.12+
- `customtkinter`
- `google-genai`

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Configuration

프로그램은 실행 시 `config.json`을 사용합니다.

예시:

```json
{
  "gemini_api_key": "YOUR_API_KEY",
  "window_width": 400,
  "window_height": 600,
  "ui_language": "ko"
}
```

- `gemini_api_key`: Gemini API 키
- `window_width`, `window_height`: 창 크기 저장값
- `ui_language`: `ko` 또는 `en`

`config.json`이 없으면 기본 파일이 자동 생성됩니다.

## UI Flow

1. 입력 JAR 파일 또는 폴더 선택
2. 출력 폴더 선택
3. 언어 파일 스캔
4. 입력 언어 / 출력 언어 선택
5. 번역 시작
6. 결과 및 로그 확인

## UI Layout

왼쪽 패널:

- 입력 파일 선택
- 출력 폴더 선택
- 스캔
- 언어 선택
- 번역 시작 / 정지
- 진행률
- 로그 보기

오른쪽 패널:

- 모드 목록

## Language Handling

- UI 언어는 `ko` / `en`을 지원합니다.
- UI 언어를 바꾸면 창을 다시 열어 전체 UI를 갱신합니다.
- 진행률 영역의 `대기 중...`, `전체 진행률`, `현재 JAR 진행률`도 UI 언어에 맞춰 바뀝니다.

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

빌드 스크립트는 마지막에 `build/` 폴더를 삭제합니다.

## Linux Packages

GitHub Actions 릴리즈는 Linux 배포판별로 전용 패키지를 만듭니다.

- Ubuntu: `.deb`
- Debian: `.deb`
- Fedora: `.rpm`
- Arch: `.pkg.tar.zst`

각 패키지는 실행 파일과 런처 스크립트를 포함합니다.
패키징 스크립트는 `release/build/package_fedora.sh`와 `release/build/package_arch.sh`에 있습니다.

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

- 번역 로직은 `main.py`와 `modules/`가 담당합니다.
- GUI는 입력 선택, 진행률, 결과 표시만 담당합니다.
- 로그는 GUI 창에 표시되며, 수동 저장이 가능합니다.
