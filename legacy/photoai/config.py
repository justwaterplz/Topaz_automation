"""
LEGACY: Topaz Photo AI specific configuration

이 파일은 더 이상 사용되지 않습니다.
레거시 참조용으로 보관됩니다.
"""
import os
from pathlib import Path


class PhotoAIConfig:
    """
    LEGACY: Topaz Photo AI 설정
    
    이 클래스는 더 이상 사용되지 않습니다.
    """
    
    # Photo AI 실행 파일 경로
    APP_PATH = os.getenv(
        'PHOTOAI_PATH',
        r'C:\Program Files\Topaz Labs\Topaz Photo AI\Topaz Photo AI.exe'
    )
    
    # 입출력 폴더
    INPUT_DIR = Path(os.getenv('INPUT_PHOTOAI', './input/photoai'))
    OUTPUT_DIR = Path(os.getenv('OUTPUT_PHOTOAI', './output/photoai'))
    
    # 창 제목 (프로세스 찾기용)
    WINDOW_TITLE_PATTERN = 'Photo AI'
    PROCESS_NAME = 'Topaz Photo AI.exe'
    
    # UI 요소 대기 시간
    UI_WAIT_TIME = 2
    
    # 단축키
    SHORTCUT_OPEN = 'ctrl+o'
    SHORTCUT_SELECT_ALL = 'ctrl+a'
    SHORTCUT_EXPORT = 'ctrl+e'
    
    # 이미지별 필터 적용 대기 시간 (초)
    FILTER_APPLY_WAIT_TIME = 25
    
    # Export 처리 대기 시간 (초)
    EXPORT_PER_IMAGE_WAIT_TIME = 10
    
    # UI 버튼 절대 좌표
    APPLY_AUTOPILOT_BUTTON_X = None
    APPLY_AUTOPILOT_BUTTON_Y = None
    EXPORT_BUTTON_X = None
    EXPORT_BUTTON_Y = None
    
    # 처리된 파일 구분용 suffix
    PROCESSED_SUFFIXES = [
        '_photoai',
        '-photoai', 
        '_enhanced',
        '-enhanced',
        '_ai'
    ]
