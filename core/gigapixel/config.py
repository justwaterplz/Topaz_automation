"""Topaz Gigapixel AI specific configuration"""
import os
from pathlib import Path
from core.common.base_config import BaseConfig, _get_base_path


class GigapixelConfig(BaseConfig):
    """Topaz Gigapixel AI 설정"""
    
    # Gigapixel AI 실행 파일 경로
    APP_PATH = os.getenv(
        'GIGAPIXEL_PATH',
        r'C:\Program Files\Topaz Labs\Topaz Gigapixel AI\Topaz Gigapixel AI.exe'
    )
    
    # 입출력 폴더
    INPUT_DIR = Path(os.getenv('INPUT_UPSCALING', './input/upscaling'))
    OUTPUT_DIR = Path(os.getenv('OUTPUT_UPSCALING', './output/upscaling'))
    
    # 창 제목 (프로세스 찾기용)
    WINDOW_TITLE_PATTERN = 'Topaz Gigapixel'
    PROCESS_NAME = 'Topaz Gigapixel AI.exe'
    
    # UI 요소 대기 시간
    UI_WAIT_TIME = 2  # UI 요소가 나타날 때까지 대기 시간
    
    # 처리 완료 감지 키워드
    PROCESSING_STATUS_TEXT = 'Enhancing'  # 처리 중 표시 텍스트
    
    # 처리 완료 감지 설정
    PREVIEW_UPDATED_TEXT = 'Preview Updated'  # 처리 완료 표시 텍스트
    
    # 처리된 파일 구분용 suffix (Topaz 앱에서 자동으로 추가하는 패턴)
    PROCESSED_SUFFIXES = [
        '-gigapixel',      # Gigapixel AI 기본 suffix
        '-standard',       # Standard 모델
        '-highfidelity',   # High Fidelity 모델  
        '-artcg',          # Art & CG 모델
        '-lines',          # Lines 모델
        '-lowresolution',  # Low Resolution 모델
        '-verycompressed', # Very Compressed 모델
        '_upscaled',       # 일부 버전에서 사용
        '-enhanced',       # Enhanced 출력
        '_2x', '_4x', '_6x', '-2x', '-4x', '-6x'  # 배율 suffix
    ]
    
    # Zoom to fit 단축키 (전체 이미지 범위 맞춤)
    SHORTCUT_ZOOM_TO_FIT = 'ctrl+0'
    
    # 저장 처리 대기 시간 (초)
    # 이미지 크기와 복잡도에 따라 조정 가능
    SAVE_PROCESSING_WAIT_TIME = 18  # 기본 18초 (여유있게)
    
    # OCR 영역 설정 (Queue 영역 - Processing/Done 감지용)
    # 방식 1: 창 기준 상대 좌표 (해상도/위치 무관) - 권장
    OCR_USE_WINDOW_RELATIVE = True
    OCR_REGION_RATIOS = {
        'x': 0.05,      # 창 왼쪽에서 5%
        'y': 0.12,      # 창 위에서 12%
        'width': 0.9,   # 창 너비의 90%
        'height': 0.25  # 창 높이의 25%
    }
    # 방식 2: 화면 절대 좌표 (OCR_USE_WINDOW_RELATIVE=False일 때만 사용)
    OCR_REGION_QUEUE = {
        'x': 140,
        'y': 130,
        'width': 720,
        'height': 150
    }
    
    # 저장 처리 대기 설정
    SAVE_PROCESSING_TEXT = "Processing"
    SAVE_DONE_TEXT = "Done"
    
    # 템플릿 경로 (PrintScreen+클립보드 기반 감지용, PyInstaller 빌드 시 _MEIPASS 사용)
    TEMPLATES_DIR = _get_base_path() / "assets" / "templates"
    
    # 업스케일링 완료: Ctrl+0 후 오른쪽 위에 나타나는 "Preview Updated" UI
    PREVIEW_UPDATED_TEMPLATE_PATH = TEMPLATES_DIR / "preview_updated.png"
    
    # 저장 완료: Export 다이얼로그 Queue 영역의 "Done" 텍스트
    DONE_TEMPLATE_PATH = TEMPLATES_DIR / "done_text.png"
    
    # Done 감지 사용 여부 (False면 고정 시간 대기만 사용, 클립보드 덮어쓰기 없음)
    USE_DONE_DETECTION = True
    
    # Preview Updated 감지 (미사용 - 업스케일링은 저장 과정에서 적용됨)
    USE_PREVIEW_UPDATED_DETECTION = False
    
    @classmethod
    def ensure_directories(cls):
        """필요한 디렉토리 생성"""
        super().ensure_directories()
        cls.INPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
