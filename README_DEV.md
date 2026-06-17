# Minecraft Mod Translator Gemini - Developer Guide

[English](README_DEV.md) | [한국어](README_DEV_KO.md)

이 문서는 Minecraft Mod Translator Gemini의 구조와 동작을 개발자 기준으로 정리합니다.

## 프로젝트 목표

- Minecraft 모드 JAR 또는 폴더에서 언어 리소스를 찾는다.
- Google Gemini API로 `lang/*.json`의 문자열을 번역한다.
- 원본 구조를 보존한 채 결과 JAR을 다시 만든다.

## 현재 범위

- JAR/폴더 입력
- 언어 JSON 탐색
- Gemini 번역
- 번역 결과 병합
- JAR 재패키징
- 설정 파일 관리
- GUI 진행 상태 표시

## 핵심 파일

- `main.py`: GUI 진입점과 작업 흐름 제어
- `modules/config.py`: 설정 파일 경로와 읽기/쓰기
- `modules/find_json.py`: 언어 JSON 탐색
- `modules/gemini_translator.py`: Gemini API 호출 및 응답 처리
- `modules/unzip_jar.py`: JAR 압축 해제
- `modules/zip_jar.py`: JAR 재압축
- `modules/i18n.py`: UI 문자열 관리

## 데이터 흐름

1. 사용자가 JAR 또는 폴더를 선택한다.
2. JAR이면 임시 폴더로 압축을 푼다.
3. `lang/*.json` 또는 우선순위 대상 파일을 찾는다.
4. JSON key는 유지하고 value만 번역한다.
5. 번역 결과를 원본 구조에 반영한다.
6. 수정된 내용을 다시 JAR로 압축한다.

## 구현 상세

### 청킹

- 큰 JSON은 `MAX_CHUNK_CHARS`, `MAX_CHUNK_ITEMS` 기준으로 나눈다.
- API 제한과 응답 누락을 줄이기 위한 구조다.

### 재시도

- `MAX_RETRIES` 범위 내에서 재시도한다.
- `RETRY_BASE_DELAY`를 기준으로 지수 백오프를 사용한다.

### 설정 파일

- OS별 표준 경로에 `MMTG/config.json`을 저장한다.
- 시작 시 설정이 없으면 자동 생성할 수 있다.

## UI/UX

- 번역 작업은 백그라운드 스레드에서 실행한다.
- GUI는 입력, 진행률, 로그 표시를 담당한다.
- 한국어와 영어 UI를 지원한다.

## 주의사항

- 플레이스홀더 문자열은 번역 중 보존해야 한다.
- 대용량 모드에서는 작업 시간이 길어질 수 있다.
- 로그와 번역 결과를 분리해 확인해야 한다.

