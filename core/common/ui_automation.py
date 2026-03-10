"""
Windows UI Automation을 사용한 앱 상태 감지

pywinauto를 사용하여 Topaz 앱의 UI 요소에 직접 접근하여
처리 상태를 정확하게 감지합니다.
"""
import time
import re
from typing import Optional, Tuple, Dict, Any
from loguru import logger

try:
    from pywinauto import Application
    from pywinauto.findwindows import ElementNotFoundError
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False
    logger.warning("pywinauto not available - UI Automation disabled")


class TopazUIAutomation:
    """Topaz 앱 UI Automation 클래스"""
    
    def __init__(self, app_title_pattern: str = '.*Topaz Gigapixel.*'):
        """
        Args:
            app_title_pattern: 앱 윈도우 타이틀 패턴 (정규식)
        """
        self.app_title_pattern = app_title_pattern
        self._app = None
        self._window = None
        self._connected = False
        
        if not PYWINAUTO_AVAILABLE:
            logger.error("pywinauto is not installed")
    
    def connect(self, timeout: int = 5) -> bool:
        """Topaz 앱에 연결
        
        Args:
            timeout: 연결 타임아웃 (초)
        
        Returns:
            연결 성공 여부
        """
        if not PYWINAUTO_AVAILABLE:
            return False
        
        try:
            # UIA backend 사용 (더 풍부한 정보 제공)
            self._app = Application(backend='uia').connect(
                title_re=self.app_title_pattern,
                timeout=timeout
            )
            self._window = self._app.window(title_re=self.app_title_pattern)
            self._connected = True
            logger.info("Connected to Topaz app via UI Automation")
            return True
            
        except ElementNotFoundError:
            logger.warning("Topaz app not found")
            self._connected = False
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Topaz app: {e}")
            self._connected = False
            return False
    
    def is_connected(self) -> bool:
        """연결 상태 확인"""
        if not self._connected or not self._window:
            return False
        
        try:
            # 윈도우가 아직 유효한지 확인
            self._window.window_text()
            return True
        except:
            self._connected = False
            return False
    
    def ensure_connected(self) -> bool:
        """연결 확인 및 재연결"""
        if self.is_connected():
            return True
        return self.connect()
    
    def get_window_title(self) -> str:
        """현재 윈도우 타이틀 가져오기"""
        if not self.ensure_connected():
            return ""
        
        try:
            return self._window.window_text()
        except Exception as e:
            logger.debug(f"Failed to get window title: {e}")
            return ""
    
    def get_progress_info(self) -> Dict[str, Any]:
        """처리 진행 상태 정보 가져오기
        
        Returns:
            {
                'is_processing': bool,
                'progress_percent': int or None,
                'status_text': str or None,
                'window_title': str
            }
        """
        result = {
            'is_processing': False,
            'progress_percent': None,
            'status_text': None,
            'window_title': ''
        }
        
        if not self.ensure_connected():
            return result
        
        try:
            # 윈도우 타이틀에서 정보 추출
            title = self._window.window_text()
            result['window_title'] = title
            
            # 타이틀에서 진행률 추출 (예: "Processing 45%")
            percent_match = re.search(r'(\d+)\s*%', title)
            if percent_match:
                result['progress_percent'] = int(percent_match.group(1))
                result['is_processing'] = True
            
            # 처리 중 키워드 확인
            processing_keywords = ['processing', 'enhancing', 'upscaling', 'loading', 'analyzing']
            title_lower = title.lower()
            for keyword in processing_keywords:
                if keyword in title_lower:
                    result['is_processing'] = True
                    break
            
            # 프로그레스바 찾기
            try:
                progress_bars = self._window.descendants(control_type='ProgressBar')
                for pb in progress_bars:
                    try:
                        # value pattern에서 진행률 추출
                        legacy = pb.legacy_properties()
                        value_str = legacy.get('Value', '')
                        if value_str:
                            # "45%" 또는 "45" 형식
                            match = re.search(r'(\d+)', str(value_str))
                            if match:
                                progress = int(match.group(1))
                                if 0 < progress <= 100:
                                    result['progress_percent'] = progress
                                    result['is_processing'] = (progress < 100)
                    except:
                        pass
            except:
                pass
            
            # 상태 텍스트 찾기
            try:
                texts = self._window.descendants(control_type='Text')
                status_keywords = ['processing', 'enhancing', 'saving', 'loading', 'done', 'complete']
                
                for text in texts:
                    try:
                        text_value = text.window_text()
                        if text_value and any(kw in text_value.lower() for kw in status_keywords):
                            result['status_text'] = text_value
                            if any(kw in text_value.lower() for kw in ['processing', 'enhancing', 'loading']):
                                result['is_processing'] = True
                            break
                    except:
                        pass
            except:
                pass
            
        except Exception as e:
            logger.debug(f"Failed to get progress info: {e}")
        
        return result
    
    def wait_for_processing_complete(
        self,
        timeout: int = 300,
        check_interval: float = 1.0,
        stable_count: int = 3
    ) -> bool:
        """처리 완료 대기 (UI Automation 기반)
        
        Args:
            timeout: 최대 대기 시간 (초)
            check_interval: 상태 확인 간격 (초)
            stable_count: '처리 완료' 상태가 연속으로 확인되어야 하는 횟수
        
        Returns:
            처리 완료 여부
        """
        if not self.ensure_connected():
            logger.warning("Not connected to Topaz app, using fallback")
            return False
        
        logger.info(f"Waiting for processing to complete (UI Automation, timeout: {timeout}s)...")
        
        start_time = time.time()
        last_progress = -1
        not_processing_count = 0
        
        while time.time() - start_time < timeout:
            info = self.get_progress_info()
            
            # 진행률 로깅
            if info['progress_percent'] is not None:
                if info['progress_percent'] != last_progress:
                    logger.info(f"  Processing: {info['progress_percent']}%")
                    last_progress = info['progress_percent']
                    not_processing_count = 0
                
                # 100%면 완료
                if info['progress_percent'] >= 100:
                    logger.info("Processing complete (100%)")
                    return True
            
            # 처리 중이 아닌 상태가 연속으로 확인되면 완료
            if not info['is_processing']:
                not_processing_count += 1
                if not_processing_count >= stable_count:
                    elapsed = time.time() - start_time
                    logger.info(f"Processing complete (stable state detected, {elapsed:.1f}s)")
                    return True
            else:
                not_processing_count = 0
            
            # 상태 텍스트가 'done' 또는 'complete'면 완료
            if info['status_text']:
                status_lower = info['status_text'].lower()
                if 'done' in status_lower or 'complete' in status_lower:
                    logger.info(f"Processing complete (status: {info['status_text']})")
                    return True
            
            time.sleep(check_interval)
        
        logger.warning(f"Processing wait timeout after {timeout}s")
        return False
    
    def is_save_dialog_open(self) -> bool:
        """저장 다이얼로그가 열려있는지 확인"""
        if not self.ensure_connected():
            return False
        
        try:
            title = self._window.window_text().lower()
            save_keywords = ['save', 'export', '저장', '내보내기']
            return any(kw in title for kw in save_keywords)
        except:
            return False
    
    def find_and_click_button(self, button_text: str, timeout: int = 5) -> bool:
        """버튼 찾아서 클릭
        
        Args:
            button_text: 버튼 텍스트 (부분 매칭)
            timeout: 검색 타임아웃
        
        Returns:
            클릭 성공 여부
        """
        if not self.ensure_connected():
            return False
        
        try:
            button = self._window.child_window(
                title_re=f'.*{button_text}.*',
                control_type='Button'
            ).wait('visible', timeout=timeout)
            
            button.click()
            logger.info(f"Clicked button: {button_text}")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to click button '{button_text}': {e}")
            return False


# 싱글톤 인스턴스
_topaz_ui = None

def get_topaz_ui() -> TopazUIAutomation:
    """TopazUIAutomation 싱글톤 인스턴스 가져오기"""
    global _topaz_ui
    if _topaz_ui is None:
        _topaz_ui = TopazUIAutomation()
    return _topaz_ui
