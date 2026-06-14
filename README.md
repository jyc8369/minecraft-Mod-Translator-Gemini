# Minecraft Mod Translator Gemini (MMTG) - User Guide (No Build Required)

## 1. 다운로드

GitHub Releases에서 운영체제에 맞는 파일을 다운로드합니다.

- Windows: `~windows.zip`
- macOS:
  - `~macos-arm64.zip`
  - `~macos-x86_64.zip`
- Linux:
  - Ubuntu `~ubuntu.deb`
  - Debian: `~debian.deb`
  - Fedora: `~fedora.rpm`
  - Arch: `arch.pkg.tar.zst`

## 2. 설치 및 실행

### Windows
1. 다운로드한 파일 압축 해제
2. `MMTG.exe` 실행

보안 경고가 뜨면 "추가 정보 → 실행" 선택

### macOS
권장 MacOS 15+
1. 다운로드한 파일 압축 해제
2. `.app` 파일을 Applications 폴더로 이동
3. 실행
4. 실행이 차단될 경우:
   - 시스템 설정 → 보안 및 개인정보 보호 → 허용

### Linux (Ubuntu / Debian / Fedora / Arch)

#### Debian / Ubuntu
```bash
sudo dpkg -i mmtg.deb
sudo apt-get install -f
````

#### Fedora

```bash
sudo dnf install mmtg.rpm
```

#### Arch

```bash
sudo pacman -U mmtg.pkg.tar.zst
```

설치 후 실행:

```bash
mmtg
```

## 3. API 설정 (필수)

처음 실행하면 `config.json` 파일이 자동 생성됩니다.

파일 위치:

* Windows: `%APPDATA%\\MMTG\\config.json`
* macOS: `~/Library/Application Support/MMTG/config.json`
* Linux: `~/.config/MMTG/config.json`

예시:

```json
{
  "gemini_api_key": "YOUR_API_KEY",
  "window_width": 400,
  "window_height": 600,
  "ui_language": "ko"
}
```

### 설정 방법

1. Google Gemini API Key 발급
2. `config.json` 열기
3. `gemini_api_key` 값 입력
4. 저장 후 프로그램 재실행

## 4. 사용 방법

1. 프로그램 실행
2. “Input File”에서 Minecraft 모드 JAR 또는 폴더 선택
3. “Output Folder” 선택
4. “Scan” 클릭
5. 입력 언어 / 출력 언어 선택
6. “Start Translation” 클릭
7. 진행률 확인
8. 완료 후 결과 JAR 생성

---

## 5. 주요 기능 설명

* JAR 자동 분석: `lang/*.json` 탐색
* 언어 선택 번역: 원하는 언어로 변환
* 진행률 표시: 전체 / 개별 모드 상태 확인 가능
* 로그 창: 번역 과정 상세 확인
* UI 언어 변경: 한국어 / 영어 지원

## 6. 문제 해결

### 프로그램이 실행되지 않는 경우

* Java 또는 런타임 환경 부족 여부 확인
* 관리자 권한으로 실행

### 번역이 실패하는 경우

* API Key 확인
* 인터넷 연결 상태 확인

### 결과가 생성되지 않는 경우

* 출력 폴더 권한 확인
* JAR 파일 손상 여부 확인

## 7. 참고 사항

* 원본 JAR 파일은 수정되지 않으며 복사본이 생성됩니다.
* 번역 품질은 Gemini API 응답에 의존합니다.
* 대용량 모드는 시간이 오래 걸릴 수 있습니다.
