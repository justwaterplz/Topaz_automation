# Changelog

## [v1.0.0] - 2025-12-29

### ✨ Features
- **OCR 기반 처리 완료 감지**
  - EasyOCR로 "Enhancing..." 텍스트 실시간 모니터링
  - 처리 완료를 정확하게 감지하여 불완전한 이미지 저장 방지
  - OCR 실패 시 자동으로 시간 기반 대기로 폴백

- **클립보드 기반 파일 경로 입력**
  - 모든 유니코드 문자 지원 (한글, 한글 자모, 특수문자 등)
  - 파일명 제한 없음

- **Suffix 필터링**
  - 이미 처리된 파일 자동 제외
  - 무한 반복 방지 (`_upscaled`, `_2x` 등)

- **첫 이미지 전체 범위 자동 선택**
  - 마우스 휠 스크롤로 자동 설정

- **Quick Save 지원**
  - Input 폴더에 직접 저장
  - 파일 탐색 위치 문제 해결

### 🔧 Configuration
- `--wait-time`: 최대 대기 시간 설정
- `--use-save`: 일반 Save 사용
- `--no-ocr`: OCR 비활성화 (시간 기반만)

### 📦 Dependencies
- EasyOCR 1.7.1
- PyTorch 2.0.1
- pyperclip 1.8.2
- 기타 자동화 라이브러리

### 🐛 Bug Fixes
- 파일명에 특수문자가 있을 때 입력 실패 문제 해결
- 처리 완료 전에 저장되는 문제 해결
- 파일 탐색 위치 초기화 문제 해결

### 📝 Documentation
- README.md 상세 사용법 추가
- QUICKSTART.md 빠른 시작 가이드
- 문제 해결 섹션 추가

