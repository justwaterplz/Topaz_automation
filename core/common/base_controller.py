"""Base controller for Topaz applications"""
import time
import subprocess
from pathlib import Path
from abc import ABC, abstractmethod
from loguru import logger
import pyautogui
import keyboard
import pyperclip

from .window_manager import WindowManager
from .file_handler import FileHandler


class BaseController(ABC):
    """Topaz 앱 제어를 위한 베이스 컨트롤러"""
    
    def __init__(self, config):
        """
        Args:
            config: 설정 클래스 (GigapixelConfig 등)
        """
        self.config = config
        self.window_manager = WindowManager()
        self.file_handler = FileHandler()
        
        # PyAutoGUI 안전 설정
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
    
    @abstractmethod
    def open_image(self, image_path: Path) -> bool:
        """이미지 열기 (하위 클래스에서 구현)"""
        pass
    
    @abstractmethod
    def save_image(self, output_path: Path) -> bool:
        """이미지 저장 (하위 클래스에서 구현)"""
        pass
    
    def launch_app(self) -> bool:
        """애플리케이션 실행"""
        if self.window_manager.is_process_running(self.config.PROCESS_NAME):
            logger.info(f"{self.config.PROCESS_NAME} is already running")
            hwnd = self.window_manager.find_window_by_title(self.config.WINDOW_TITLE_PATTERN)
            if hwnd:
                self.window_manager.activate_window(hwnd)
                return True
        
        logger.info(f"Launching {self.config.APP_PATH}")
        
        try:
            subprocess.Popen([self.config.APP_PATH])
            
            hwnd = self.window_manager.wait_for_window(
                self.config.WINDOW_TITLE_PATTERN, 
                timeout=30
            )
            
            if hwnd:
                time.sleep(2)
                self.window_manager.activate_window(hwnd)
                logger.info("Application launched successfully")
                return True
            else:
                logger.error("Failed to find application window after launch")
                return False
                
        except Exception as e:
            logger.error(f"Failed to launch application: {e}")
            return False
    
    def activate_app_window(self) -> bool:
        """앱 윈도우 활성화"""
        hwnd = self.window_manager.find_window_by_title(self.config.WINDOW_TITLE_PATTERN)
        if hwnd:
            result = self.window_manager.activate_window(hwnd)
            if result:
                # 활성화 후 실제로 해당 앱이 포커스되었는지 확인
                time.sleep(0.3)
                try:
                    import win32gui
                    active_hwnd = win32gui.GetForegroundWindow()
                    active_title = win32gui.GetWindowText(active_hwnd)
                    
                    if self.config.WINDOW_TITLE_PATTERN.lower() not in active_title.lower():
                        logger.warning(f"Window activated but wrong app focused: {active_title}")
                        # 한 번 더 시도
                        self.window_manager.activate_window(hwnd)
                        time.sleep(0.5)
                except Exception as e:
                    logger.debug(f"Focus verification failed: {e}")
            return result
        
        logger.error(f"Cannot find window: {self.config.WINDOW_TITLE_PATTERN}")
        return False
    
    def press_shortcut(self, shortcut: str, delay: float = 0.5):
        """키보드 단축키 입력"""
        logger.debug(f"Pressing shortcut: {shortcut}")
        keyboard.press_and_release(shortcut)
        time.sleep(delay)
    
    def type_text(self, text: str, use_clipboard: bool = True):
        """텍스트 입력"""
        logger.debug(f"Typing text: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        if use_clipboard:
            try:
                old_clipboard = pyperclip.paste()
                pyperclip.copy(text)
                time.sleep(0.1)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.2)
                pyperclip.copy(old_clipboard)
            except Exception as e:
                logger.warning(f"Clipboard method failed, using keyboard input: {e}")
                pyautogui.write(text, interval=0.01)
        else:
            pyautogui.write(text, interval=0.01)
    
    def wait_for_processing(self, timeout: int = None) -> bool:
        """처리 완료 대기"""
        if timeout is None:
            timeout = self.config.MAX_WAIT_TIME
        
        logger.info(f"Waiting for processing to complete (timeout: {timeout}s)")
        time.sleep(self.config.PROCESSING_WAIT_TIME)
        return True
