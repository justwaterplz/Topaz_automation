"""File handling utilities"""
import time
from pathlib import Path
from loguru import logger


class FileHandler:
    """파일 처리 유틸리티"""
    
    @staticmethod
    def wait_for_file(file_path: Path, timeout: int = 30) -> bool:
        """
        파일이 생성될 때까지 대기
        
        Args:
            file_path: 파일 경로
            timeout: 최대 대기 시간 (초)
        
        Returns:
            파일이 존재하면 True
        """
        logger.info(f"Waiting for file: {file_path}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if file_path.exists():
                logger.info(f"File found after {time.time() - start_time:.1f}s")
                return True
            time.sleep(1)
        
        logger.warning(f"File not found after {timeout}s: {file_path}")
        return False
    
    @staticmethod
    def is_file_ready(file_path: Path, stable_time: float = 2.0) -> bool:
        """
        파일이 완전히 쓰여졌는지 확인 (크기가 안정화되었는지)
        
        Args:
            file_path: 파일 경로
            stable_time: 크기 안정화 대기 시간 (초)
        
        Returns:
            파일이 준비되었으면 True
        """
        if not file_path.exists():
            return False
        
        try:
            size1 = file_path.stat().st_size
            time.sleep(stable_time)
            size2 = file_path.stat().st_size
            
            is_ready = size1 == size2 and size1 > 0
            if is_ready:
                logger.debug(f"File is ready: {file_path} ({size2} bytes)")
            return is_ready
        except Exception as e:
            logger.error(f"Error checking file readiness: {e}")
            return False
    
    @staticmethod
    def get_unique_filename(output_dir: Path, base_name: str, extension: str) -> Path:
        """
        중복되지 않는 파일명 생성
        
        Args:
            output_dir: 출력 디렉토리
            base_name: 기본 파일명 (확장자 제외)
            extension: 확장자 (.png 등)
        
        Returns:
            고유한 파일 경로
        """
        output_path = output_dir / f"{base_name}{extension}"
        
        if not output_path.exists():
            return output_path
        
        # 파일이 존재하면 번호 추가
        counter = 1
        while True:
            output_path = output_dir / f"{base_name}_{counter}{extension}"
            if not output_path.exists():
                return output_path
            counter += 1

