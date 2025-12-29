"""Base configuration for Topaz automation"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class BaseConfig:
    """공통 설정을 관리하는 베이스 클래스"""
    
    # 프로젝트 루트 경로
    PROJECT_ROOT = Path(__file__).parent.parent
    
    # 로그 설정
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = PROJECT_ROOT / 'logs'
    
    # 처리 대기 시간 설정
    PROCESSING_WAIT_TIME = int(os.getenv('PROCESSING_WAIT_TIME', '5'))
    MAX_WAIT_TIME = int(os.getenv('MAX_WAIT_TIME', '300'))
    
    # 키보드 단축키
    SHORTCUT_OPEN = 'ctrl+o'
    SHORTCUT_SAVE = 'ctrl+s'
    
    # 이미지 확장자
    SUPPORTED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.webp']
    
    @classmethod
    def ensure_directories(cls):
        """필요한 디렉토리들이 존재하는지 확인하고 없으면 생성"""
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_image_files(cls, directory: Path, exclude_suffixes: list = None) -> list:
        """
        지정된 디렉토리에서 지원하는 이미지 파일 목록 반환
        
        Args:
            directory: 검색할 디렉토리
            exclude_suffixes: 제외할 suffix 리스트 (예: ['_upscaled', '_2x'])
        
        Returns:
            이미지 파일 경로 리스트 (중복 제거됨)
        """
        if not directory.exists():
            return []
        
        # 중복 방지를 위해 set 사용
        image_files_set = set()
        
        for ext in cls.SUPPORTED_IMAGE_EXTENSIONS:
            # 소문자 확장자로 검색 (Windows는 대소문자 구분 안 함)
            image_files_set.update(directory.glob(f'*{ext}'))
            image_files_set.update(directory.glob(f'*{ext.upper()}'))
        
        # set을 list로 변환
        image_files = list(image_files_set)
        
        # Suffix 필터링 (이미 처리된 파일 제외)
        if exclude_suffixes:
            filtered_files = []
            for img_file in image_files:
                # 파일명(확장자 제외)에 suffix가 포함되어 있는지 확인
                stem = img_file.stem.lower()
                is_processed = any(suffix.lower() in stem for suffix in exclude_suffixes)
                
                if not is_processed:
                    filtered_files.append(img_file)
            
            return sorted(filtered_files)
        
        return sorted(image_files)

