"""
아이콘 감지 유틸리티
OpenCV 템플릿 매칭을 사용한 UI 요소 감지
"""
import time
from typing import Optional, Tuple
from pathlib import Path
import numpy as np
import cv2
import pyautogui
from PIL import Image
from loguru import logger

from .window_manager import WindowManager


class IconDetector:
    """아이콘 및 UI 요소 감지 클래스"""
    
    def __init__(self, template_dir: str = "assets/templates"):
        """
        Args:
            template_dir: 템플릿 이미지 디렉토리
        """
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.templates = {}  # 캐시
        
        logger.debug(f"IconDetector initialized with template_dir: {self.template_dir}")
    
    def load_template(self, template_name: str) -> Optional[np.ndarray]:
        """
        템플릿 이미지 로드 (캐싱)
        
        Args:
            template_name: 템플릿 이름 (확장자 제외)
        
        Returns:
            템플릿 이미지 (BGR) 또는 None
        """
        # 캐시 확인
        if template_name in self.templates:
            return self.templates[template_name]
        
        # 파일 찾기
        template_path = self.template_dir / f"{template_name}.png"
        if not template_path.exists():
            logger.warning(f"Template not found: {template_path}")
            return None
        
        # 로드
        try:
            template = cv2.imread(str(template_path))
            if template is None:
                logger.error(f"Failed to load template: {template_path}")
                return None
            
            self.templates[template_name] = template
            logger.debug(f"Template loaded: {template_name} ({template.shape})")
            return template
        
        except Exception as e:
            logger.error(f"Error loading template {template_name}: {e}")
            return None
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
        """
        화면 영역 캡처
        
        Args:
            x, y: 캡처 시작 좌표
            width, height: 캡처 크기
        
        Returns:
            캡처된 이미지 (BGR) 또는 None
        """
        try:
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            # PIL Image -> OpenCV BGR
            img_rgb = np.array(screenshot)
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
            return img_bgr
        except Exception as e:
            logger.error(f"Failed to capture region: {e}")
            return None
    
    def match_template(
        self,
        image: np.ndarray,
        template: np.ndarray,
        threshold: float = 0.7,
        method: int = cv2.TM_CCOEFF_NORMED
    ) -> Tuple[bool, float, Tuple[int, int]]:
        """
        템플릿 매칭 수행
        
        Args:
            image: 검색할 이미지 (BGR)
            template: 템플릿 이미지 (BGR)
            threshold: 매칭 임계값 (0.0 ~ 1.0)
            method: OpenCV 매칭 방법
        
        Returns:
            (발견 여부, 신뢰도, (x, y) 위치)
        """
        try:
            # Grayscale 변환
            img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
            # 템플릿 매칭
            result = cv2.matchTemplate(img_gray, template_gray, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # 매칭 방법에 따라 위치 선택
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                match_loc = min_loc
                confidence = 1.0 - min_val
            else:
                match_loc = max_loc
                confidence = max_val
            
            found = confidence >= threshold
            
            if found:
                logger.debug(f"Template matched: method={method}, confidence={confidence:.3f}, loc={match_loc}")
            else:
                logger.debug(f"Template not matched: method={method}, confidence={confidence:.3f} < threshold={threshold}")
            
            return found, confidence, match_loc
        
        except Exception as e:
            logger.error(f"Template matching failed: {e}")
            return False, 0.0, (0, 0)
    
    def match_template_multi_method(
        self,
        image: np.ndarray,
        template: np.ndarray,
        threshold: float = 0.7
    ) -> Tuple[bool, float, Tuple[int, int]]:
        """
        여러 매칭 방법을 시도하여 가장 좋은 결과 반환
        
        Args:
            image: 검색할 이미지
            template: 템플릿 이미지
            threshold: 매칭 임계값
        
        Returns:
            (발견 여부, 최고 신뢰도, (x, y) 위치)
        """
        methods = [
            cv2.TM_CCOEFF_NORMED,
            cv2.TM_CCORR_NORMED,
            cv2.TM_SQDIFF_NORMED
        ]
        
        best_confidence = 0.0
        best_location = (0, 0)
        found = False
        
        for method in methods:
            is_found, confidence, location = self.match_template(
                image, template, threshold, method
            )
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_location = location
                if is_found:
                    found = True
        
        return found, best_confidence, best_location
    
    def match_template_multiscale(
        self,
        image: np.ndarray,
        template: np.ndarray,
        threshold: float = 0.7,
        scales: list = [0.3, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0]
    ) -> Tuple[bool, float, Tuple[int, int], float]:
        """
        다양한 크기로 템플릿 매칭 (해상도 대응)
        
        Args:
            image: 검색할 이미지
            template: 템플릿 이미지
            threshold: 매칭 임계값
            scales: 시도할 스케일 리스트
        
        Returns:
            (발견 여부, 최고 신뢰도, (x, y) 위치, 스케일)
        """
        best_confidence = 0.0
        best_location = (0, 0)
        best_scale = 1.0
        found = False
        
        logger.debug(f"Trying {len(scales)} different scales...")
        
        for scale in scales:
            # 템플릿 크기 조정
            width = int(template.shape[1] * scale)
            height = int(template.shape[0] * scale)
            
            # 너무 작거나 큰 경우 스킵
            if width < 5 or height < 5 or width > image.shape[1] or height > image.shape[0]:
                continue
            
            resized_template = cv2.resize(template, (width, height))
            
            # 여러 매칭 방법 시도
            is_found, confidence, location = self.match_template_multi_method(
                image, resized_template, threshold
            )
            
            logger.debug(f"  Scale {scale:.2f}: confidence={confidence:.3f}")
            
            # 최고 신뢰도 업데이트
            if confidence > best_confidence:
                best_confidence = confidence
                best_location = location
                best_scale = scale
                if is_found:
                    found = True
        
        if found:
            logger.info(f"  Multiscale match: confidence={best_confidence:.3f}, scale={best_scale}")
        else:
            logger.warning(f"✗ No match found. Best confidence: {best_confidence:.3f} at scale {best_scale}")
        
        return found, best_confidence, best_location, best_scale
    
    def detect_icon_in_region(
        self,
        x: int, y: int, width: int, height: int,
        icon_name: str,
        threshold: float = 0.7,
        multiscale: bool = True
    ) -> Tuple[bool, float]:
        """
        특정 영역에서 아이콘 감지
        
        Args:
            x, y: 검색 영역 시작 좌표
            width, height: 검색 영역 크기
            icon_name: 아이콘 템플릿 이름
            threshold: 매칭 임계값
            multiscale: 다양한 크기로 시도
        
        Returns:
            (발견 여부, 신뢰도)
        """
        # 템플릿 로드
        template = self.load_template(icon_name)
        if template is None:
            logger.warning(f"Template '{icon_name}' not available")
            return False, 0.0
        
        # 화면 캡처
        image = self.capture_region(x, y, width, height)
        if image is None:
            return False, 0.0
        
        # 매칭 수행
        if multiscale:
            found, confidence, _, _ = self.match_template_multiscale(
                image, template, threshold
            )
        else:
            found, confidence, _ = self.match_template(
                image, template, threshold
            )
        
        return found, confidence
    
    def save_template_from_region(
        self,
        x: int, y: int, width: int, height: int,
        template_name: str
    ) -> bool:
        """
        화면 영역을 캡처해서 템플릿으로 저장
        
        Args:
            x, y: 캡처 영역 시작 좌표
            width, height: 캡처 크기
            template_name: 저장할 템플릿 이름
        
        Returns:
            성공 여부
        """
        image = self.capture_region(x, y, width, height)
        if image is None:
            return False
        
        template_path = self.template_dir / f"{template_name}.png"
        
        try:
            cv2.imwrite(str(template_path), image)
            logger.info(f"Template saved: {template_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save template: {e}")
            return False


def wait_for_icon_appear(
    dialog_title: str,
    icon_name: str,
    region_ratios: dict,
    check_interval: float = 1.0,
    timeout: int = 300,
    threshold: float = 0.7,
    debug: bool = False,
    fallback_title: str = None
) -> bool:
    """
    다이얼로그 내에서 아이콘이 나타날 때까지 대기
    
    Args:
        dialog_title: 다이얼로그 윈도우 제목
        icon_name: 찾을 아이콘 템플릿 이름
        region_ratios: 검색 영역 비율 {'x_ratio', 'y_ratio', 'width_ratio', 'height_ratio'}
        check_interval: 체크 간격 (초)
        timeout: 최대 대기 시간 (초)
        threshold: 매칭 임계값
        debug: 디버그 모드
        fallback_title: dialog_title을 찾지 못할 때 대신 사용할 윈도우 제목
    
    Returns:
        발견되면 True
    """
    logger.info(f"Waiting for icon '{icon_name}' to appear in '{dialog_title}'...")
    if fallback_title:
        logger.info(f"  (Fallback: '{fallback_title}')")
    
    detector = IconDetector()
    elapsed = 0.0
    check_count = 0
    target_title = dialog_title  # 현재 찾을 윈도우 제목
    fallback_attempted = False
    
    while elapsed < timeout:
        check_count += 1
        
        # 윈도우 찾기 (현재 target_title 사용)
        hwnd = WindowManager.find_window_by_title(target_title)
        
        # 원래 다이얼로그를 찾지 못하고 폴백이 있으면
        if hwnd == 0 and target_title == dialog_title and fallback_title and not fallback_attempted:
            logger.warning(f"'{dialog_title}' not found after {check_count} attempts")
            logger.warning(f"→ Switching to fallback window: '{fallback_title}'")
            target_title = fallback_title  # 이제부터 폴백 사용
            fallback_attempted = True
            hwnd = WindowManager.find_window_by_title(target_title)
            if hwnd != 0:
                logger.info(f"  Fallback window found: '{target_title}'")
        
        if hwnd == 0:
            if check_count == 1:
                logger.debug(f"Waiting for window '{target_title}'...")
            time.sleep(check_interval)
            elapsed += check_interval
            continue
        
        # 검색 영역 계산 (상대 좌표)
        region = WindowManager.get_relative_region(
            hwnd,
            region_ratios['x_ratio'],
            region_ratios['y_ratio'],
            region_ratios['width_ratio'],
            region_ratios['height_ratio']
        )
        
        if region is None:
            logger.debug("Failed to get region")
            time.sleep(check_interval)
            elapsed += check_interval
            continue
        
        x, y, width, height = region
        
        # 디버그: 검색 영역 저장
        if debug:
            debug_dir = Path("logs/icon_debug")
            debug_dir.mkdir(parents=True, exist_ok=True)
            debug_img = detector.capture_region(x, y, width, height)
            if debug_img is not None:
                debug_path = debug_dir / f"search_{check_count:03d}.png"
                cv2.imwrite(str(debug_path), debug_img)
                logger.debug(f"Debug image saved: {debug_path}")
        
        # 아이콘 감지
        found, confidence = detector.detect_icon_in_region(
            x, y, width, height,
            icon_name,
            threshold=threshold,
            multiscale=True
        )
        
        if found:
            logger.info(f"  Icon '{icon_name}' detected! (confidence: {confidence:.3f})")
            return True
        
        # 상태 로깅
        if check_count % 3 == 0:
            logger.info(f"Still waiting for icon... ({elapsed:.1f}s, best confidence: {confidence:.3f})")
        else:
            logger.debug(f"Icon not found (confidence: {confidence:.3f})")
        
        # 대기
        time.sleep(check_interval)
        elapsed += check_interval
    
    logger.warning(f"Timeout waiting for icon '{icon_name}' after {timeout}s")
    return False

