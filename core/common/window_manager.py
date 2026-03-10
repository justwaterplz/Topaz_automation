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
    def find_window_by_title(title_pattern: str, exclude_explorer: bool = True) -> int:
        """제목으로 윈도우 찾기"""
        if not WIN32_AVAILABLE:
            logger.warning("win32gui not available")
            return 0
        
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title_pattern.lower() in title.lower():
                    # 파일 탐색기 제외 (선택적)
                    if exclude_explorer:
                        try:
                            class_name = win32gui.GetClassName(hwnd)
                            # 파일 탐색기의 클래스명은 CabinetWClass 또는 ExploreWClass
                            if class_name in ['CabinetWClass', 'ExploreWClass']:
                                logger.debug(f"Excluding explorer window: {title}")
                                return True  # 건너뛰기
                        except:
                            pass
                    windows.append((hwnd, title))
            return True
        
        windows = []
        win32gui.EnumWindows(callback, windows)
        
        if windows:
            # 가장 적합한 윈도우 선택 (정확한 앱 이름 우선)
            for hwnd, title in windows:
                # "Topaz Gigapixel AI"가 정확히 포함된 것 우선
                if 'Topaz Gigapixel AI' in title:
                    logger.debug(f"Found exact match window: {title}")
                    return hwnd
            
            # 없으면 첫 번째 반환
            logger.debug(f"Found window with title containing '{title_pattern}': {windows[0][1]}")
            return windows[0][0]
        
        logger.warning(f"Window not found with title pattern: {title_pattern}")
        return 0
    
    @staticmethod
    def activate_window(hwnd: int) -> bool:
        """윈도우 활성화"""
        if not WIN32_AVAILABLE or hwnd == 0:
            return False
        
        try:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
            
            logger.debug(f"Window activated: {hwnd}")
            return True
        except Exception as e:
            logger.error(f"Failed to activate window: {e}")
            return False
    
    @staticmethod
    def is_process_running(process_name: str) -> bool:
        """프로세스가 실행 중인지 확인"""
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
        """윈도우가 나타날 때까지 대기"""
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
        """지정된 위치 클릭"""
        pyautogui.click(x, y, clicks=clicks, interval=interval)
        logger.debug(f"Clicked at ({x}, {y})")
    
    @staticmethod
    def get_window_rect(hwnd: int) -> tuple:
        """윈도우의 위치와 크기 가져오기"""
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
        """윈도우 기준 상대 좌표로 영역 계산"""
        rect = WindowManager.get_window_rect(hwnd)
        if rect is None:
            return None
        
        win_x, win_y, win_width, win_height = rect
        
        abs_x = int(win_x + win_width * x_ratio)
        abs_y = int(win_y + win_height * y_ratio)
        region_width = int(win_width * width_ratio)
        region_height = int(win_height * height_ratio)
        
        logger.debug(f"Relative region: ({abs_x}, {abs_y}, {region_width}, {region_height})")
        return (abs_x, abs_y, region_width, region_height)
    
    @staticmethod
    def find_child_windows(parent_hwnd: int, class_name: str = None) -> list:
        """부모 윈도우의 자식 윈도우들 찾기"""
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
        """제목 패턴과 일치하는 모든 윈도우 찾기"""
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
