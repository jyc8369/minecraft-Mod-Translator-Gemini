# Minecraft Mod Translator Gemini (MMTG) - 개발자 문서

Minecraft 모드 JAR 파일 내부의 언어 파일(`lang/*.json`)을 탐색하고, Google Gemini API로 번역한 뒤 다시 JAR로 패키징하는 도구입니다.

## 1. 기술 스택

### 런타임 및 언어
- **Python 3.12+**
- 타입 힌트 기반의 모듈 분리 구조
- 표준 라이브러리 중심의 파일 I/O, 압축, 멀티스레딩 처리

### GUI
- **customtkinter**
- `tkinter` 기반이지만 현대적인 테마와 위젯 스타일을 제공하는 데스크톱 UI
- 입력 선택, 진행 상태 표시, 로그 출력, 결과 확인을 담당

### AI 번역
- **google-genai**
- Gemini API를 사용해 `lang/*.json`의 key-value 번역을 수행
- 키는 유지하고 값만 번역하는 방식으로 동작

### 빌드 및 배포
- **PyInstaller**
- Windows/macOS용 단일 실행 파일 또는 앱 번들 생성
- 릴리즈용 패키징 스크립트는 `release/build/`에 위치

### 보조 시스템
- **logging**
- **threading**
- **json / zipfile / pathlib / shutil**
- 설정 파일 관리, JAR 압축 해제/재압축, 백그라운드 작업 처리에 사용

## 2. 프로젝트 구조

```text
.
├── main.py                  # GUI 진입점, 작업 흐름 제어, 번역 실행 오케스트레이션
├── modules/                 # 핵심 비즈니스 로직
│   ├── config.py            # OS별 config.json 경로 관리 및 읽기/쓰기
│   ├── find_json.py         # JAR 내 언어 파일 검색 및 우선순위 선택
│   ├── gemini_translator.py # Gemini API 호출, 청킹, 재시도, JSON 응답 처리
│   ├── i18n.py              # UI 다국어 문자열 관리
│   ├── unzip_jar.py         # JAR 압축 해제
│   └── zip_jar.py           # 번역 결과를 포함한 JAR 재패키징
├── release/
│   └── build/               # 빌드 및 패키징 스크립트
└── requirements.txt         # Python 의존성 목록
```

## 3. 핵심 동작 흐름

프로그램은 다음 순서로 동작합니다.

`JAR 또는 폴더 선택` -> `임시 디렉터리 압축 해제` -> `언어 파일 탐색` -> `번역 대상 선정` -> `Gemini 번역` -> `파일 교체` -> `JAR 재압축` -> `결과 저장`

### 처리 방식
- 입력이 JAR이면 먼저 임시 폴더로 풀어서 내부 리소스를 분석합니다.
- `lang/*.json` 또는 우선순위가 정의된 언어 파일을 찾습니다.
- 번역은 JSON key를 유지하고 value만 변환합니다.
- 번역 완료 후 원본 구조를 보존한 상태로 다시 압축합니다.

## 4. Gemini 번역 구현 상세

### 4.1 청킹 전략
- 큰 JSON 파일은 한 번에 보내지 않고 여러 청크로 분할합니다.
- API 제한과 응답 누락을 줄이기 위해 다음 기준을 사용합니다.
  - `MAX_CHUNK_CHARS`
  - `MAX_CHUNK_ITEMS`
- 청크 단위 처리는 대용량 모드에서도 안정성을 높입니다.

### 4.2 재시도 및 안정화
- 네트워크 오류나 일시적 API 실패에 대비해 재시도 로직을 둡니다.
- `MAX_RETRIES` 범위 내에서 다시 요청합니다.
- `RETRY_BASE_DELAY`를 기반으로 지수 백오프를 적용합니다.

### 4.3 프롬프트 설계
- JSON 키는 절대 변경하지 않도록 명시합니다.
- `%s`, `%1$s`, `%d` 같은 마인크래프트 플레이스홀더 보존 규칙을 포함합니다.
- 응답 형식을 JSON으로 제한해 파싱 안정성을 높입니다.

## 5. 설정 및 환경 관리

### 설정 파일 위치
앱은 운영체제별 표준 설정 경로에 `MMTG/config.json`을 저장합니다.

- **Windows**: `%APPDATA%/MMTG/config.json`
- **macOS**: `~/Library/Application Support/MMTG/config.json`
- **Linux**: `~/.config/MMTG/config.json`

### 설정 항목 예시
```json
{
  "gemini_api_key": "YOUR_API_KEY",
  "window_width": 400,
  "window_height": 600,
  "ui_language": "ko"
}
```

### 관련 모듈
- `modules/config.py`가 경로 결정, 읽기, 저장을 담당합니다.
- 초기 실행 시 설정 파일이 없으면 자동 생성되는 흐름을 전제로 합니다.

## 6. UI/UX 구현

### 비동기 처리
- 번역 작업은 `threading`으로 백그라운드에서 실행합니다.
- UI 스레드는 입력, 진행률, 로그 표시만 담당해 프리징을 방지합니다.

### 로그 시스템
- 커스텀 `logging.Handler`로 로그를 GUI 창에 실시간 출력합니다.
- 로그 레벨별 색상 구분으로 가독성을 높입니다.

### 다국어 지원
- UI 언어는 `modules/i18n.py`에서 관리합니다.
- 기본적으로 한국어와 영어를 지원합니다.

## 7. 번역 대상 언어 선정

- `modules/find_json.py`의 `LANGUAGE_PRIORITY`를 기준으로 번역 파일을 고릅니다.
- 예를 들어 `en_us.json`부터 `ru_ru.json`까지 우선순위를 둘 수 있습니다.
- 새 언어를 우선 번역 대상으로 추가하려면 이 리스트만 조정하면 됩니다.

## 8. 빌드 및 배포

### Windows
```bat
release/build/build_windows.bat
```
- 결과물: `release/build/dist/MMTG/`

### macOS
```sh
chmod +x release/build/build_macos.sh
cd release/build
./build_macos.sh
```
- 결과물: `release/build/dist/MMTG.app`

### 빌드 후 정리
- 빌드 스크립트는 완료 후 `build/` 폴더를 삭제합니다.

## 9. Linux 패키지

GitHub Actions 릴리즈는 Linux 배포판별 전용 패키지를 생성합니다.

- Ubuntu: `.deb`
- Debian: `.deb`
- Fedora: `.rpm`
- Arch: `.pkg.tar.zst`

패키지에는 실행 파일과 런처 스크립트가 포함됩니다.

패키징 스크립트 위치:
- `release/build/package_fedora.sh`
- `release/build/package_arch.sh`

## 10. 개발 가이드

### 새로운 UI 언어 추가
1. `modules/i18n.py`의 `TRANSLATIONS`에 새 언어 코드를 추가합니다.
2. `SUPPORTED_UI_LANGS`에 동일한 언어 코드를 추가합니다.

### 번역 대상 언어 확장
1. `modules/find_json.py`의 `LANGUAGE_PRIORITY`에 새 `.json` 파일명을 추가합니다.
2. 우선순위 순서에 따라 스캔 대상이 결정됩니다.

## 11. 요구 사항

- Python 3.12+
- `pip install -r requirements.txt`

## 12. 참고 사항

- 번역 로직은 `main.py`와 `modules/`가 담당합니다.
- GUI는 입력 선택, 진행률 표시, 결과 표시에 집중합니다.
- 로그는 GUI 창에 표시되며 수동 저장이 가능합니다.
