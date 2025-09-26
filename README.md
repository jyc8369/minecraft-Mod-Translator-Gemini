# Minecraft Mod Translator with Google Gemini AI

Minecraft Forge 모드의 언어 파일을 Google Gemini AI로 번역.

## GitHub에서 클론
```bash
git clone https://github.com/jyc8369/minecraft-Mod-Translator-Gemini.git
cd minecraft-Mod-Translator-Gemini
```

## Requirements
- Python 3.8+
- `pip install -r requirements.txt`

## Usage
1. `mod` 폴더에 JAR 파일 넣기 (또는 GUI에서 입력 폴더 선택).
2. GUI 실행: `python main.py`
3. API 키 입력 및 저장.
4. 입력 폴더와 출력 폴더 선택.
5. 번역 시작.
6. 번역된 JAR 파일이 출력 폴더에 생성됨.

## 기능
- API 키 저장 (config.json)
- 입력/출력 폴더 선택 가능
- 실시간 진행 바 및 로그 표시
- exe 컴파일 지원 (PyInstaller 사용)

## exe 컴파일
PyInstaller로 exe 파일 생성:
```
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```
생성된 exe 파일은 `dist` 폴더에 있음.

## exe 사용법
- `dist/main.exe`를 실행하여 프로그램 시작
- Python 환경이 필요 없음
- 모든 의존성이 exe에 포함됨
