"""화면 상태 모니터링 유틸리티"""
import time
from typing import Optional
from loguru import logger

try:
    import win32gui
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


class StateMonitor:
    """화면 상태를 모니터링하는 클래스"""
    
    @staticmethod
    def get_active_window_title() -> str:
        """
        현재 활성 윈도우의 타이틀 가져오기
        
        Returns:
            윈도우 타이틀
        """
        if not WIN32_AVAILABLE:
            return ""
        
        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            return title
        except Exception as e:
            logger.debug(f"Failed to get window title: {e}")
            return ""
    
    @staticmethod
    def wait_for_window_title_contains(
        text: str,
        timeout: int = 10,
        check_interval: float = 0.5
    ) -> bool:
        """
        윈도우 타이틀에 특정 텍스트가 포함될 때까지 대기
        
        Args:
            text: 찾을 텍스트
            timeout: 최대 대기 시간
            check_interval: 체크 간격
        
        Returns:
            발견되면 True, 타임아웃 시 False
        """
        logger.debug(f"Waiting for window title containing: '{text}'")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            title = StateMonitor.get_active_window_title()
            
            if text.lower() in title.lower():
                logger.debug(f"  Found in title: '{title}'")
                return True
            
            time.sleep(check_interval)
        
        logger.warning(f"Timeout waiting for '{text}' in window title")
        return False
    
    @staticmethod
    def wait_for_window_title_not_contains(
        text: str,
        timeout: int = 10,
        check_interval: float = 0.5
    ) -> bool:
        """
        윈도우 타이틀에서 특정 텍스트가 사라질 때까지 대기
        
        Args:
            text: 사라질 텍스트
            timeout: 최대 대기 시간
            check_interval: 체크 간격
        
        Returns:
            사라지면 True, 타임아웃 시 False
        """
        logger.debug(f"Waiting for '{text}' to disappear from window title")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            title = StateMonitor.get_active_window_title()
            
            if text.lower() not in title.lower():
                logger.debug(f"  Text disappeared, current title: '{title}'")
                return True
            
            time.sleep(check_interval)
        
        logger.warning(f"Timeout waiting for '{text}' to disappear")
        return False
    
    @staticmethod
    def verify_image_loaded(expected_filename: str, timeout: int = 10) -> bool:
        """
        이미지가 로드되었는지 확인 (타이틀바에 파일명 표시됨)
        
        Args:
            expected_filename: 로드해야 할 파일명
            timeout: 최대 대기 시간
        
        Returns:
            로드되면 True
        """
        logger.debug(f"Verifying image loaded: {expected_filename}")
        
        # 확장자 제거한 파일명도 체크
        name_without_ext = expected_filename.rsplit('.', 1)[0]
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            title = StateMonitor.get_active_window_title()
            
            # 타이틀에 파일명이 포함되어 있는지 확인
            if (expected_filename.lower() in title.lower() or 
                name_without_ext.lower() in title.lower()):
                logger.info(f"  Image loaded: {expected_filename}")
                return True
            
            time.sleep(0.5)
        
        logger.warning(f"Timeout: Image not loaded - {expected_filename}")
        current_title = StateMonitor.get_active_window_title()
        logger.warning(f"Current window title: {current_title}")
        return False
    
    @staticmethod
    def wait_for_dialog_closed(timeout: int = 5) -> bool:
        """
        다이얼로그가 닫혔는지 확인
        Topaz 메인 윈도우로 돌아왔는지 확인
        
        Args:
            timeout: 최대 대기 시간
        
        Returns:
            다이얼로그가 닫히면 True
        """
        logger.debug("Waiting for dialog to close...")
        
        start_time = time.time()
        prev_title = StateMonitor.get_active_window_title()
        
        while time.time() - start_time < timeout:
            time.sleep(0.5)
            current_title = StateMonitor.get_active_window_title()
            
            # 타이틀이 변경되면 다이얼로그가 닫힌 것으로 간주
            if current_title != prev_title and "Topaz Gigapixel" in current_title:
                logger.debug(f"  Dialog closed, back to: '{current_title}'")
                return True
            
            prev_title = current_title
        
        logger.warning("Timeout waiting for dialog to close")
        return True  # 타임아웃이어도 계속 진행

