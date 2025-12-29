"""Base controller for Topaz applications"""
import time
import subprocess
from pathlib import Path
from abc import ABC, abstractmethod
from loguru import logger
import pyautogui
import keyboard
import pyperclip

from utils.window_manager import WindowManager
from utils.file_handler import FileHandler


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
        pyautogui.FAILSAFE = True  # 마우스를 화면 모서리로 이동하면 중단
        pyautogui.PAUSE = 0.5  # 각 명령 후 0.5초 대기
    
    @abstractmethod
    def open_image(self, image_path: Path) -> bool:
        """
        이미지 열기 (하위 클래스에서 구현)
        
        Args:
            image_path: 열 이미지 파일 경로
        
        Returns:
            성공 여부
        """
        pass
    
    @abstractmethod
    def save_image(self, output_path: Path) -> bool:
        """
        이미지 저장 (하위 클래스에서 구현)
        
        Args:
            output_path: 저장할 파일 경로
        
        Returns:
            성공 여부
        """
        pass
    
    def launch_app(self) -> bool:
        """
        애플리케이션 실행
        
        Returns:
            성공 여부
        """
        if self.window_manager.is_process_running(self.config.PROCESS_NAME):
            logger.info(f"{self.config.PROCESS_NAME} is already running")
            hwnd = self.window_manager.find_window_by_title(self.config.WINDOW_TITLE_PATTERN)
            if hwnd:
                self.window_manager.activate_window(hwnd)
                return True
        
        logger.info(f"Launching {self.config.APP_PATH}")
        
        try:
            subprocess.Popen([self.config.APP_PATH])
            
            # 앱이 실행될 때까지 대기
            hwnd = self.window_manager.wait_for_window(
                self.config.WINDOW_TITLE_PATTERN, 
                timeout=30
            )
            
            if hwnd:
                time.sleep(2)  # UI가 완전히 로드될 때까지 추가 대기
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
        """
        앱 윈도우 활성화
        
        Returns:
            성공 여부
        """
        hwnd = self.window_manager.find_window_by_title(self.config.WINDOW_TITLE_PATTERN)
        if hwnd:
            return self.window_manager.activate_window(hwnd)
        
        logger.error(f"Cannot find window: {self.config.WINDOW_TITLE_PATTERN}")
        return False
    
    def press_shortcut(self, shortcut: str, delay: float = 0.5):
        """
        키보드 단축키 입력
        
        Args:
            shortcut: 단축키 (예: 'ctrl+o', 'ctrl+s')
            delay: 입력 후 대기 시간
        """
        logger.debug(f"Pressing shortcut: {shortcut}")
        keyboard.press_and_release(shortcut)
        time.sleep(delay)
    
    def type_text(self, text: str, use_clipboard: bool = True):
        """
        텍스트 입력
        
        Args:
            text: 입력할 텍스트
            use_clipboard: True면 클립보드 사용 (모든 문자 지원), False면 키보드 입력
        """
        logger.debug(f"Typing text: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        if use_clipboard:
            # 클립보드 사용 (특수 문자, 한글 등 모든 문자 지원)
            try:
                # 기존 클립보드 내용 백업
                old_clipboard = pyperclip.paste()
                
                # 텍스트를 클립보드에 복사
                pyperclip.copy(text)
                time.sleep(0.1)
                
                # Ctrl+V로 붙여넣기
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.2)
                
                # 클립보드 복원
                pyperclip.copy(old_clipboard)
                
            except Exception as e:
                logger.warning(f"Clipboard method failed, using keyboard input: {e}")
                # 클립보드 실패 시 기존 방식 사용
                pyautogui.write(text, interval=0.01)
        else:
            # 기존 키보드 입력 방식
            pyautogui.write(text, interval=0.01)
    
    def wait_for_processing(self, timeout: int = None) -> bool:
        """
        처리 완료 대기 (하위 클래스에서 오버라이드 가능)
        
        Args:
            timeout: 최대 대기 시간 (None이면 config의 MAX_WAIT_TIME 사용)
        
        Returns:
            성공 여부
        """
        if timeout is None:
            timeout = self.config.MAX_WAIT_TIME
        
        logger.info(f"Waiting for processing to complete (timeout: {timeout}s)")
        time.sleep(self.config.PROCESSING_WAIT_TIME)
        return True

