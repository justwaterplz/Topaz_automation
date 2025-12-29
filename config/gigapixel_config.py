"""Topaz Gigapixel AI specific configuration"""
import os
from pathlib import Path
from .base_config import BaseConfig


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
    PROCESSED_SUFFIXES = ['_upscaled', '-gigapixel', '_2x', '_4x', '_6x', '-enhanced']
    
    # Zoom to fit 단축키 (전체 이미지 범위 맞춤)
    SHORTCUT_ZOOM_TO_FIT = 'ctrl+0'
    
    # 저장 처리 대기 시간 (초)
    # 이미지 크기와 복잡도에 따라 조정 가능
    SAVE_PROCESSING_WAIT_TIME = 18  # 기본 18초 (여유있게)
    
    # OCR 영역 설정 (Queue 영역 - Processing 상태 감지용)
    # Queue 영역은 Export Settings 다이얼로그 왼쪽 상단에 위치
    OCR_REGION_QUEUE = {
        'x': 140,      # 좌측 상단 Queue 영역
        'y': 130,
        'width': 720,  # Queue 전체 영역
        'height': 150
    }
    
    # 저장 처리 대기 설정
    SAVE_PROCESSING_TEXT = "Processing"  # 저장 중 표시 텍스트
    SAVE_DONE_TEXT = "Done"  # 저장 완료 표시 텍스트
    
    @classmethod
    def ensure_directories(cls):
        """필요한 디렉토리 생성"""
        super().ensure_directories()
        cls.INPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

