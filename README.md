# Topaz Automation

Topaz AI 앱 (Gigapixel AI 등)을 자동화하는 GUI 도구입니다.

## 프로젝트 구조

```
Topaz_automation/
├── apps/                      # GUI 앱
│   ├── gigapixel_app/        # Gigapixel AI 자동화 GUI
│   │   ├── main.py           # 앱 진입점
│   │   ├── main_window.py    # 메인 윈도우
│   │   └── styles.qss        # QSS 스타일시트
│   └── service2_app/         # 새 서비스 (예정)
│
├── core/                      # 비즈니스 로직
│   ├── gigapixel/            # Gigapixel 자동화 핵심 로직
│   │   ├── controller.py
│   │   └── config.py
│   └── common/               # 공통 유틸리티
│       ├── base_controller.py
│       ├── window_manager.py
│       ├── state_monitor.py
│       └── ...
│
│
├── main.py                    # 앱 Entrypoint
└── requirements.txt
```

## 설치

### 1. 가상환경 생성

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

## 실행

### GUI 모드 (권장)

```bash
python main.py
```

또는

```bash
python -m apps.gigapixel_app.main
```

### CLI 모드 (레거시)

```bash
python main.py --cli --input-dir "D:\Images"
```

CLI 옵션:
- `--input-dir PATH` : 입력 이미지 폴더
- `--single FILE` : 단일 파일 처리
- `--wait-time SEC` : 초기 대기 시간 (기본: 5초)
- `--save-wait-time SEC` : 저장 대기 시간 (기본: 18초)

## 사용 전 준비

1. **Topaz Gigapixel AI를 먼저 실행**하세요.
2. 앱에서 원하는 설정(모델, 배율 등)을 미리 적용하세요.
3. 자동화 도구를 실행하고 입력 폴더를 선택하세요.

## 빌드 (exe)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "GigapixelAutomation" apps/gigapixel_app/main.py
```

## 기술 스택

- **GUI**: PySide6 (Qt for Python)
- **자동화**: PyAutoGUI, keyboard, pywinauto
- **Windows API**: pywin32
- **로깅**: loguru

## 라이선스

MIT License
