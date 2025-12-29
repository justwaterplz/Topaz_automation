# Topaz Automation 🚀

Topaz Gigapixel AI 및 Topaz Photo AI를 자동화하는 Python 프로젝트입니다.

## 📋 기능

### ✅ 구현된 기능
- **Topaz Gigapixel AI 자동화** (이미지 업스케일링)
  - 단일 이미지 처리
  - 배치(폴더) 처리
  - 자동 파일명 생성
  - 처리 진행 상황 로깅

### 🚧 개발 예정
- **Topaz Photo AI 자동화** (이미지 벡터화)

## 📁 프로젝트 구조

```
Topaz_automation/
├── config/                      # 설정 파일들
│   ├── base_config.py          # 공통 설정
│   └── gigapixel_config.py     # Gigapixel AI 설정
├── controllers/                 # 앱 제어 모듈
│   ├── base_controller.py      # 공통 제어 로직
│   └── gigapixel_controller.py # Gigapixel AI 제어
├── utils/                       # 유틸리티 함수
│   ├── logger.py               # 로깅
│   ├── window_manager.py       # 윈도우 관리
│   └── file_handler.py         # 파일 처리
├── input/                       # 입력 이미지 폴더
│   ├── upscaling/              # 업스케일링용
│   └── vectorizing/            # 벡터화용 (예정)
├── output/                      # 출력 이미지 폴더
│   ├── upscaling/
│   └── vectorizing/
├── logs/                        # 로그 파일
├── main.py                      # 메인 실행 파일
├── requirements.txt             # 필요한 패키지
└── .env.example                 # 환경 변수 예시
```

## 🔧 설치 방법

### 1. 저장소 클론
```bash
git clone <repository-url>
cd Topaz_automation
```

### 2. 가상환경 생성 및 활성화
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 설정
`.env.example`을 `.env`로 복사하고 설정을 수정하세요:

```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

`.env` 파일 내용:
```env
# Topaz Gigapixel AI 실행 파일 경로
GIGAPIXEL_PATH=C:\Program Files\Topaz Labs\Topaz Gigapixel AI\Topaz Gigapixel AI.exe

# 입출력 폴더 (선택사항, 기본값 사용 가능)
INPUT_UPSCALING=./input/upscaling
OUTPUT_UPSCALING=./output/upscaling

# 처리 대기 시간 (초)
PROCESSING_WAIT_TIME=5
MAX_WAIT_TIME=300

# 로그 레벨
LOG_LEVEL=INFO
```

## 🚀 사용 방법

### 기본 워크플로우

1. **Topaz Gigapixel AI 실행**
   - 앱을 실행하고 원하는 설정을 적용합니다
   - 업스케일 모델, 배율, 노이즈 제거 등 옵션 설정
   - 저장 위치 설정 (File → Preferences → Output)

2. **첫 실행 시: OCR 초기화**
   - 첫 실행 시 EasyOCR 모델을 다운로드합니다 (자동, 1-2분 소요)
   - 이후에는 바로 실행됩니다

3. **스크립트 실행**

   **단일 파일 처리:**
   ```bash
   python main.py --single "D:\Images\photo.jpg"
   ```

   **배치 처리 (폴더 내 모든 이미지):**
   ```bash
   python main.py --input-dir "D:\Images\input"
   ```

   **기본 폴더 사용 (input/upscaling/):**
   ```bash
   python main.py
   ```

4. **자동 처리**
   - 스크립트가 이미지를 순차적으로 열고 → 저장 → **OCR로 저장 완료 감지** → 다음 이미지
   - **저장 모니터링**: Queue 영역의 "Processing" → "Done" 상태 변화를 OCR로 실시간 감지
   - **이미 처리된 파일은 자동으로 제외됩니다** (무한 반복 방지)

### 저장 위치 설정

**중요:** Topaz 앱에서 저장 위치를 미리 설정하세요!
```
File → Preferences → Output → Save Location
```

스크립트는 `Ctrl+S` + `Enter`로 저장하며, Topaz 설정의 output 폴더에 저장됩니다.

### 대기 시간 조정

이미지가 크거나 처리가 느린 경우:

```bash
python main.py --input-dir "D:\Images" --wait-time 10
```

## ⚙️ 명령줄 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--mode` | 처리 모드 (`upscale` 또는 `vectorize`) | `upscale` |
| `--single PATH` | 단일 파일 처리 | - |
| `--input-dir DIR` | 입력 디렉토리 (배치 처리) | `./input/upscaling` |
| `--wait-time SECONDS` | 처리 대기 시간(초) | 5 |
| `--debug-ocr` | OCR 디버그 모드 (Queue 영역 캡처 이미지 저장) | 비활성 |

### OCR 디버그 모드

Queue 영역의 OCR 감지가 제대로 작동하지 않을 때 사용:

```bash
python main.py --input-dir "D:\Images" --debug-ocr
```

캡처된 이미지는 `logs/ocr_debug_queue/` 폴더에 저장됩니다.

## 📝 작동 원리

이 프로젝트는 다음 방식으로 Topaz 앱을 제어합니다:

1. **키보드 단축키 기반** (가장 안정적)
   - `Ctrl+O` → 파일 선택 → `Enter`: 파일 열기
   - `Ctrl+0`: Zoom to fit (전체 이미지 화면에 맞춤)
   - `Ctrl+S` → `Enter`: 저장 (설정된 output 폴더)

2. **윈도우 관리**
   - `pywin32`: Windows API로 앱 윈도우 찾기 및 활성화
   - `psutil`: 프로세스 상태 확인

3. **자동화 흐름**
   ```
   [처리 전 파일 목록 수집 & 필터링] →
   
   각 이미지마다:
   ┌─────────────────────────────────────────────┐
   │ 1. Ctrl+O → 파일 선택 → Enter (이미지 열기) │
   │ 2. 타이틀바에서 파일명 확인 (이미지 로드 완료)│
   │ 3. Ctrl+0 (Zoom to fit - 전체 화면에 맞춤)  │
   │ 4. 5초 대기 (초기 처리)                     │
   │ 5. Ctrl+S → Enter (저장 시작)               │
   │ 6. OCR로 Queue 영역 모니터링:               │
   │    "Processing" → "Done" 감지              │
   │ 7. ESC (Export Settings 창 닫기)           │
   └─────────────────────────────────────────────┘
   ```

4. **저장 방식 & 완료 감지**
   - **저장 시작**: `Ctrl+S` + `Enter` → Export Settings 다이얼로그 표시
   - **저장 위치**: File → Preferences → Output → Save Location (미리 설정 필요)
   - **처리 모니터링 (OCR)**:
     - Export Settings 다이얼로그의 **Queue 영역**을 OCR로 실시간 감지
     - "Processing" 텍스트가 나타남 → 저장 처리 중
     - "Done" 텍스트가 나타남 → 저장 완료
     - 완료 후 ESC로 다이얼로그 닫고 다음 이미지로 진행
   - **파일명 패턴**: Topaz 설정에 따름

5. **이미지 로드 확인**
   - 윈도우 타이틀바에서 파일명 표시 여부 확인
   - 타임아웃(15초) 시에도 계속 진행

6. **무한 반복 방지**
   - 파일 처리 전에 suffix 패턴을 체크
   - 이미 처리된 파일(`_upscaled`, `_2x` 등)은 자동 제외
   - 설정: `config/gigapixel_config.py`의 `PROCESSED_SUFFIXES`

## 🔍 검증 메커니즘

스크립트는 각 단계에서 UI 상태를 확인하여 안정적으로 동작합니다:

1. **이미지 로드 확인**: 윈도우 타이틀바에 파일명이 표시되는지 확인
2. **저장 처리 완료 확인**: Queue 영역의 "Processing" → "Done" 상태 변화를 OCR로 감지
3. **다이얼로그 닫힘 확인**: 윈도우 타이틀이 Topaz Gigapixel로 돌아왔는지 확인

이를 통해 **스크립트의 상태와 실제 UI 상태가 일치**하도록 보장합니다.

## 🎯 지원하는 이미지 포맷

- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- TIFF (`.tiff`, `.tif`)
- BMP (`.bmp`)
- WebP (`.webp`)

## 📊 로그

처리 진행 상황은 다음 위치에 기록됩니다:
- **콘솔**: 실시간 진행 상황
- **파일**: `logs/gigapixel_YYYYMMDD.log`

로그 파일은 자동으로 관리됩니다:
- 10MB마다 새 파일 생성
- 30일 이상 된 로그는 자동 삭제
- 오래된 로그는 자동 압축

## ⚠️ 주의사항

1. **사전 준비 (중요!)**
   - Topaz Gigapixel AI를 먼저 실행하고 설정을 완료하세요
   - 업스케일 모델, 배율, 노이즈 제거 등 옵션 설정
   - **저장 위치 설정 필수**: File → Preferences → Output
     - Save Location: 저장 폴더 지정
     - File Naming: 파일명 패턴 (예: `{filename}_upscaled`)

2. **처리 중에는**
   - ⚠️ 마우스/키보드를 사용하지 마세요 (자동화 방해)
   - 긴급 중단: 마우스를 화면 왼쪽 위 모서리로 이동 (FailSafe)
   - 처리 중인 이미지가 화면에 표시됩니다

3. **대기 시간 조정 (중요!)**
   - 기본 대기 시간: 5초
   - **"Enhancing..." 완료까지 대기하므로 충분한 시간 설정 필요**
   - 대용량 이미지: `--wait-time 15` 이상 권장
   - 고해상도 6x 업스케일: `--wait-time 30` 권장
   - 처리 시간은 이미지 크기, 배율, PC 사양에 따라 다릅니다
   - 너무 짧으면 불완전한 이미지가 저장될 수 있습니다!

4. **파일 경로**
   - 한글 경로도 지원하지만, 영문 경로 권장
   - 공백이 포함된 경로는 따옴표로 감싸세요: `"D:\My Images"`

## 🛠️ 문제 해결

### "Topaz 앱을 찾을 수 없습니다" 에러
- Topaz Gigapixel AI가 실행 중인지 확인하세요
- 앱이 최소화되어 있으면 복원됩니다

### 이미지가 열리지 않아요
- 지원하는 이미지 포맷인지 확인하세요 (jpg, png, tiff 등)
- 파일 경로가 올바른지 확인하세요
- 경로에 공백이 있으면 따옴표로 감싸세요

### 저장이 제대로 안 돼요
- Topaz 앱에서 저장 위치를 확인하세요 (File → Preferences → Output)
- 저장 권한이 있는 폴더인지 확인하세요

### 처리가 완료되기 전에 저장돼요
- **대기 시간이 너무 짧습니다!** `--wait-time`을 늘리세요
- 우측 상단 프리뷰에서 "Enhancing..." 텍스트가 사라질 때까지 기다려야 합니다
- 권장 설정:
  - 작은 이미지 (1-2MP): `--wait-time 5`
  - 중간 이미지 (2-8MP): `--wait-time 10`
  - 큰 이미지 (8MP+): `--wait-time 20`
  - 6x 업스케일: `--wait-time 30`
- `.env` 파일의 `PROCESSING_WAIT_TIME`으로 기본값 변경 가능

## 🤝 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요!

## 📄 라이선스

MIT License

## 🔮 향후 계획

- [ ] Topaz Photo AI 벡터화 기능 추가
- [ ] OCR을 이용한 "Preview Updated" 텍스트 감지
- [ ] GUI 인터페이스 추가
- [ ] 처리 설정을 스크립트에서 변경 가능하도록
- [ ] 멀티스레딩으로 성능 개선
