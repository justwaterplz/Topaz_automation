"""Window management utilities"""
import time
import pyautogui
from loguru import logger

try:
    import win32gui
    import win32con
    import win32process
    import psutil
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    logger.warning("pywin32 not available - some features may be limited")


class WindowManager:
    """윈도우 관리 유틸리티"""
    
    @staticmethod
    def find_window_by_title(title_pattern: str) -> int:
        """
        제목으로 윈도우 찾기
        
        Args:
            title_pattern: 윈도우 제목에 포함될 문자열
        
        Returns:
            윈도우 핸들 (찾지 못하면 0)
        """
        if not WIN32_AVAILABLE:
            logger.warning("win32gui not available")
            return 0
        
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title_pattern.lower() in title.lower():
                    windows.append(hwnd)
            return True
        
        windows = []
        win32gui.EnumWindows(callback, windows)
        
        if windows:
            logger.debug(f"Found window with title containing '{title_pattern}': {windows[0]}")
            return windows[0]
        
        logger.warning(f"Window not found with title pattern: {title_pattern}")
        return 0
    
    @staticmethod
    def activate_window(hwnd: int) -> bool:
        """
        윈도우 활성화
        
        Args:
            hwnd: 윈도우 핸들
        
        Returns:
            성공 여부
        """
        if not WIN32_AVAILABLE or hwnd == 0:
            return False
        
        try:
            # 최소화 상태면 복원
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            # 윈도우를 맨 앞으로
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)  # 활성화 대기
            
            logger.debug(f"Window activated: {hwnd}")
            return True
        except Exception as e:
            logger.error(f"Failed to activate window: {e}")
            return False
    
    @staticmethod
    def is_process_running(process_name: str) -> bool:
        """
        프로세스가 실행 중인지 확인
        
        Args:
            process_name: 프로세스 이름
        
        Returns:
            실행 중이면 True
        """
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                    logger.debug(f"Process found: {process_name}")
                    return True
        except Exception as e:
            logger.error(f"Error checking process: {e}")
        
        return False
    
    @staticmethod
    def wait_for_window(title_pattern: str, timeout: int = 30) -> int:
        """
        윈도우가 나타날 때까지 대기
        
        Args:
            title_pattern: 윈도우 제목 패턴
            timeout: 최대 대기 시간 (초)
        
        Returns:
            윈도우 핸들 (타임아웃 시 0)
        """
        logger.info(f"Waiting for window: {title_pattern} (timeout: {timeout}s)")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            hwnd = WindowManager.find_window_by_title(title_pattern)
            if hwnd != 0:
                logger.info(f"Window found after {time.time() - start_time:.1f}s")
                return hwnd
            time.sleep(1)
        
        logger.warning(f"Window not found after {timeout}s")
        return 0
    
    @staticmethod
    def click_at_position(x: int, y: int, clicks: int = 1, interval: float = 0.1):
        """
        지정된 위치 클릭
        
        Args:
            x: X 좌표
            y: Y 좌표
            clicks: 클릭 횟수
            interval: 클릭 간격
        """
        pyautogui.click(x, y, clicks=clicks, interval=interval)
        logger.debug(f"Clicked at ({x}, {y})")
    
    @staticmethod
    def get_window_rect(hwnd: int) -> tuple:
        """
        윈도우의 위치와 크기 가져오기
        
        Args:
            hwnd: 윈도우 핸들
        
        Returns:
            (x, y, width, height) 또는 None
        """
        if not WIN32_AVAILABLE or hwnd == 0:
            return None
        
        try:
            rect = win32gui.GetWindowRect(hwnd)
            x, y, right, bottom = rect
            width = right - x
            height = bottom - y
            
            logger.debug(f"Window rect: x={x}, y={y}, w={width}, h={height}")
            return (x, y, width, height)
        except Exception as e:
            logger.error(f"Failed to get window rect: {e}")
            return None
    
    @staticmethod
    def get_relative_region(hwnd: int, x_ratio: float, y_ratio: float, 
                           width_ratio: float, height_ratio: float) -> tuple:
        """
        윈도우 기준 상대 좌표로 영역 계산
        
        Args:
            hwnd: 윈도우 핸들
            x_ratio: X 위치 비율 (0.0 ~ 1.0)
            y_ratio: Y 위치 비율 (0.0 ~ 1.0)
            width_ratio: 너비 비율 (0.0 ~ 1.0)
            height_ratio: 높이 비율 (0.0 ~ 1.0)
        
        Returns:
            (absolute_x, absolute_y, width, height) 또는 None
        """
        rect = WindowManager.get_window_rect(hwnd)
        if rect is None:
            return None
        
        win_x, win_y, win_width, win_height = rect
        
        # 절대 좌표 계산
        abs_x = int(win_x + win_width * x_ratio)
        abs_y = int(win_y + win_height * y_ratio)
        region_width = int(win_width * width_ratio)
        region_height = int(win_height * height_ratio)
        
        logger.debug(f"Relative region: ({abs_x}, {abs_y}, {region_width}, {region_height})")
        return (abs_x, abs_y, region_width, region_height)
    
    @staticmethod
    def find_child_windows(parent_hwnd: int, class_name: str = None) -> list:
        """
        부모 윈도우의 자식 윈도우들 찾기
        
        Args:
            parent_hwnd: 부모 윈도우 핸들
            class_name: 찾을 윈도우 클래스명 (None이면 모두)
        
        Returns:
            자식 윈도우 핸들 리스트
        """
        if not WIN32_AVAILABLE or parent_hwnd == 0:
            return []
        
        children = []
        
        def callback(hwnd, param):
            if win32gui.IsWindowVisible(hwnd):
                if class_name is None:
                    children.append(hwnd)
                else:
                    try:
                        cls = win32gui.GetClassName(hwnd)
                        if class_name.lower() in cls.lower():
                            children.append(hwnd)
                    except:
                        pass
            return True
        
        try:
            win32gui.EnumChildWindows(parent_hwnd, callback, None)
            logger.debug(f"Found {len(children)} child windows")
        except Exception as e:
            logger.error(f"Failed to enumerate child windows: {e}")
        
        return children
    
    @staticmethod
    def get_all_windows_with_title(title_pattern: str) -> list:
        """
        제목 패턴과 일치하는 모든 윈도우 찾기
        
        Args:
            title_pattern: 윈도우 제목 패턴
        
        Returns:
            (hwnd, title) 튜플 리스트
        """
        if not WIN32_AVAILABLE:
            return []
        
        windows = []
        
        def callback(hwnd, param):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and title_pattern.lower() in title.lower():
                    windows.append((hwnd, title))
            return True
        
        try:
            win32gui.EnumWindows(callback, None)
            logger.debug(f"Found {len(windows)} windows matching '{title_pattern}'")
        except Exception as e:
            logger.error(f"Failed to enumerate windows: {e}")
        
        return windows

