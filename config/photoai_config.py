"""Topaz Photo AI specific configuration"""
import os
from pathlib import Path
from .base_config import BaseConfig


class PhotoAIConfig(BaseConfig):
    """Topaz Photo AI 설정"""
    
    # Photo AI 실행 파일 경로
    APP_PATH = os.getenv(
        'PHOTOAI_PATH',
        r'C:\Program Files\Topaz Labs\Topaz Photo AI\Topaz Photo AI.exe'
    )
    
    # 입출력 폴더
    INPUT_DIR = Path(os.getenv('INPUT_PHOTOAI', './input/photoai'))
    OUTPUT_DIR = Path(os.getenv('OUTPUT_PHOTOAI', './output/photoai'))
    
    # 창 제목 (프로세스 찾기용)
    # 실제 타이틀: "Topaz Photo AI" (빈 상태) 또는 "Photo AI 3  10028.jpg" (이미지 로드 후)
    # 둘 다 매칭되도록 'Photo AI' 사용
    WINDOW_TITLE_PATTERN = 'Photo AI'
    PROCESS_NAME = 'Topaz Photo AI.exe'
    
    # UI 요소 대기 시간
    UI_WAIT_TIME = 2  # UI 요소가 나타날 때까지 대기 시간
    
    # 단축키
    SHORTCUT_OPEN = 'ctrl+o'           # 파일 열기
    SHORTCUT_SELECT_ALL = 'ctrl+a'    # 모두 선택
    SHORTCUT_EXPORT = 'ctrl+e'        # Export (있다면)
    
    # 이미지별 필터 적용 대기 시간 (초)
    # Scanning + Filter Application 완료까지 대기
    FILTER_APPLY_WAIT_TIME = 25  # 기본 25초 (scanning + 업스케일링 포함)
    
    # Export 처리 대기 시간 (초)
    # 이미지당 export 처리 시간
    EXPORT_PER_IMAGE_WAIT_TIME = 10  # 기본 10초
    
    # UI 버튼 절대 좌표 (해상도에 따라 조정 필요!)
    # Apply Autopilot 버튼 좌표 (화면 절대 좌표)
    APPLY_AUTOPILOT_BUTTON_X = None  # 설정 안하면 수동 클릭 필요
    APPLY_AUTOPILOT_BUTTON_Y = None
    
    # Export 버튼 좌표 (화면 절대 좌표)
    EXPORT_BUTTON_X = None  # 설정 안하면 수동 클릭 필요
    EXPORT_BUTTON_Y = None
    
    # 처리된 파일 구분용 suffix
    PROCESSED_SUFFIXES = [
        '_photoai',
        '-photoai', 
        '_enhanced',
        '-enhanced',
        '_ai'
    ]
    
    @classmethod
    def ensure_directories(cls):
        """필요한 디렉토리 생성"""
        super().ensure_directories()
        cls.INPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

