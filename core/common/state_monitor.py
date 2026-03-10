"""화면 상태 모니터링 유틸리티"""
import time
import re
from typing import Optional, Tuple
from loguru import logger
import numpy as np

try:
    import win32gui
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

try:
    import pyautogui
    from PIL import ImageChops, ImageGrab
    SCREEN_CAPTURE_AVAILABLE = True
except ImportError:
    SCREEN_CAPTURE_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


class StateMonitor:
    """화면 상태를 모니터링하는 클래스"""
    
    @staticmethod
    def get_active_window_title() -> str:
        """현재 활성 윈도우의 타이틀 가져오기"""
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
        """윈도우 타이틀에 특정 텍스트가 포함될 때까지 대기"""
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
        """윈도우 타이틀에서 특정 텍스트가 사라질 때까지 대기"""
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
        """이미지가 로드되었는지 확인 (타이틀바에 파일명 표시됨)"""
        logger.debug(f"Verifying image loaded: {expected_filename}")
        
        name_without_ext = expected_filename.rsplit('.', 1)[0]
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            title = StateMonitor.get_active_window_title()
            
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
        """다이얼로그가 닫혔는지 확인"""
        logger.debug("Waiting for dialog to close...")
        
        start_time = time.time()
        prev_title = StateMonitor.get_active_window_title()
        
        while time.time() - start_time < timeout:
            time.sleep(0.5)
            current_title = StateMonitor.get_active_window_title()
            
            if current_title != prev_title and "Topaz Gigapixel" in current_title:
                logger.debug(f"  Dialog closed, back to: '{current_title}'")
                return True
            
            prev_title = current_title
        
        logger.warning("Timeout waiting for dialog to close")
        return True
    
    @staticmethod
    def is_processing_in_title() -> Tuple[bool, Optional[int]]:
        """윈도우 타이틀에서 처리 중인지 확인하고 진행률 반환
        
        Returns:
            (is_processing, progress_percent)
            - is_processing: True면 처리 중
            - progress_percent: 진행률 (0-100), 없으면 None
        """
        title = StateMonitor.get_active_window_title()
        
        # 진행률 패턴 검색 (예: "Processing 45%", "Enhancing 30%", "50%")
        percent_match = re.search(r'(\d+)\s*%', title)
        if percent_match:
            progress = int(percent_match.group(1))
            return (True, progress)
        
        # 처리 중 키워드 검색
        processing_keywords = ['processing', 'enhancing', 'upscaling', 'loading']
        title_lower = title.lower()
        for keyword in processing_keywords:
            if keyword in title_lower:
                return (True, None)
        
        return (False, None)
    
    @staticmethod
    def wait_for_processing_complete(
        timeout: int = 300,  # 최대 5분
        stable_time: float = 2.0,  # 변화 없이 유지되어야 하는 시간
        check_interval: float = 0.5
    ) -> bool:
        """처리 완료 대기 (화면 변화 + 타이틀 진행률 모니터링)
        
        화면이 stable_time 동안 변화가 없고, 타이틀에 진행률이 없으면 완료로 판단
        """
        if not SCREEN_CAPTURE_AVAILABLE:
            logger.warning("Screen capture not available, using fixed wait")
            time.sleep(timeout)
            return True
        
        logger.info(f"Waiting for processing to complete (timeout: {timeout}s)...")
        
        start_time = time.time()
        last_change_time = start_time
        prev_screenshot = None
        last_progress = -1
        
        while time.time() - start_time < timeout:
            # 타이틀에서 진행률 확인
            is_processing, progress = StateMonitor.is_processing_in_title()
            
            if progress is not None and progress != last_progress:
                logger.info(f"  Processing: {progress}%")
                last_progress = progress
                last_change_time = time.time()
            
            # 화면 캡처 (중앙 영역만 - 이미지 프리뷰 영역)
            try:
                screen = pyautogui.screenshot()
                width, height = screen.size
                
                # 중앙 영역 크롭 (이미지 프리뷰가 보통 중앙에 있음)
                crop_box = (
                    int(width * 0.2),
                    int(height * 0.2),
                    int(width * 0.8),
                    int(height * 0.8)
                )
                current_screenshot = screen.crop(crop_box)
                
                if prev_screenshot is not None:
                    # 이미지 차이 계산
                    diff = ImageChops.difference(current_screenshot, prev_screenshot)
                    diff_stat = np.array(diff).sum()
                    
                    if diff_stat > 1000:  # 의미 있는 변화가 있으면
                        last_change_time = time.time()
                    
                prev_screenshot = current_screenshot
                
            except Exception as e:
                logger.debug(f"Screenshot comparison failed: {e}")
            
            # stable_time 동안 변화가 없으면 완료
            stable_duration = time.time() - last_change_time
            if stable_duration >= stable_time and not is_processing:
                logger.info(f"Processing complete (stable for {stable_duration:.1f}s)")
                return True
            
            # 진행률이 100%면 완료
            if progress == 100:
                logger.info("Processing complete (100%)")
                time.sleep(1)  # 약간의 여유
                return True
            
            time.sleep(check_interval)
        
        logger.warning(f"Processing timeout after {timeout}s")
        return False
    
    @staticmethod
    def wait_for_title_stable(
        timeout: int = 120,
        stable_time: float = 3.0,
        check_interval: float = 0.5
    ) -> bool:
        """타이틀이 stable_time 동안 변하지 않을 때까지 대기
        
        Topaz 앱이 처리 중에 타이틀을 변경하는 경우 유용
        """
        logger.info(f"Waiting for title to stabilize (timeout: {timeout}s)...")
        
        start_time = time.time()
        last_change_time = start_time
        prev_title = ""
        
        while time.time() - start_time < timeout:
            current_title = StateMonitor.get_active_window_title()
            
            if current_title != prev_title:
                logger.debug(f"  Title changed: {current_title}")
                last_change_time = time.time()
                prev_title = current_title
            
            # stable_time 동안 타이틀이 변하지 않으면 완료
            stable_duration = time.time() - last_change_time
            if stable_duration >= stable_time:
                # 처리 중 표시가 없는지 확인
                is_processing, _ = StateMonitor.is_processing_in_title()
                if not is_processing:
                    logger.info(f"Title stable for {stable_duration:.1f}s: {current_title}")
                    return True
            
            time.sleep(check_interval)
        
        logger.warning(f"Title stabilization timeout after {timeout}s")
        return False
    
    @staticmethod
    def wait_for_done_via_clipboard(
        template_path,
        timeout: int = 120,
        check_interval: float = 2.0,
        min_wait: float = 5.0,
        confidence: float = 0.6
    ) -> bool:
        """PrintScreen → 클립보드 → Done 템플릿 매칭으로 저장 완료 감지
        
        GPU 렌더링 앱에서도 동작 (클립보드 경유 캡처)
        
        Args:
            template_path: Done 템플릿 이미지 경로
            timeout: 최대 대기 시간 (초)
            check_interval: 검사 간격 (초)
            min_wait: 최소 대기 시간 (처리 시작 전)
            confidence: 템플릿 매칭 임계값 (0~1)
        
        Returns:
            Done 발견 시 True, 타임아웃 시 False
        """
        if not SCREEN_CAPTURE_AVAILABLE or not CV2_AVAILABLE:
            logger.warning("Clipboard/OpenCV unavailable, using fixed wait")
            time.sleep(timeout)
            return True
        
        import os
        if not template_path or not os.path.isfile(template_path):
            logger.warning(f"Done template not found: {template_path}")
            return False
        
        logger.info("Waiting for 'Done' (clipboard + template matching)...")
        logger.info(f"  Template: {template_path}")
        
        # 최소 대기
        time.sleep(min_wait)
        
        template = cv2.imread(str(template_path))
        if template is None:
            logger.warning("Failed to load Done template")
            return False
        
        start_time = time.time()
        check_count = 0
        
        while time.time() - start_time < timeout:
            try:
                # Alt+PrintScreen: 활성 창만 클립보드에 캡처 (Snipping Tool 안 뜸)
                # Windows 11에서 PrintScreen 단독은 Snipping Tool을 열어서 사용 불가
                pyautogui.hotkey('alt', 'printscreen')
                time.sleep(0.5)
                
                img = ImageGrab.grabclipboard()
                if img is None:
                    time.sleep(check_interval - 0.5)
                    continue
                
                # PIL → OpenCV (BGR)
                img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                
                # 다중 스케일 매칭 (작은 템플릿 대응)
                best_val = 0
                for scale in [0.8, 1.0, 1.2]:
                    w = max(10, int(template.shape[1] * scale))
                    h = max(10, int(template.shape[0] * scale))
                    resized = cv2.resize(template, (w, h))
                    result = cv2.matchTemplate(img_cv, resized, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, _ = cv2.minMaxLoc(result)
                    best_val = max(best_val, max_val)
                
                if best_val >= confidence:
                    elapsed = time.time() - start_time
                    logger.info(f"  'Done' detected! (confidence={best_val:.2f}, {elapsed:.1f}s)")
                    return True
                
                check_count += 1
                if check_count % 5 == 0:
                    remaining = timeout - (time.time() - start_time)
                    logger.info(f"  Checking... ({remaining:.0f}s remaining)")
                
            except Exception as e:
                logger.debug(f"Clipboard check failed: {e}")
            
            time.sleep(check_interval)
        
        logger.warning(f"Done not detected within {timeout}s")
        return False
