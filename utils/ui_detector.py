"""UI element detection using image template matching"""
import pyautogui
from pathlib import Path
from loguru import logger
from typing import Optional, Tuple

# 템플릿 이미지 디렉토리
TEMPLATE_DIR = Path(__file__).parent.parent / "assets" / "photoai"


class UIDetector:
    """이미지 템플릿 매칭을 사용한 UI 요소 검출"""
    
    def __init__(self, confidence: float = 0.8):
        """
        Args:
            confidence: 매칭 신뢰도 (0.0 ~ 1.0, 기본 0.8)
        """
        self.confidence = confidence
        self.template_dir = TEMPLATE_DIR
        
        # 템플릿 디렉토리 생성
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"UIDetector initialized (confidence={confidence})")
        logger.debug(f"Template directory: {self.template_dir}")
    
    def find_button(self, template_name: str, confidence: float = None) -> Optional[Tuple[int, int]]:
        """
        화면에서 버튼 찾기
        
        Args:
            template_name: 템플릿 이미지 파일명 (확장자 제외)
            confidence: 매칭 신뢰도 (None이면 기본값 사용)
        
        Returns:
            (x, y) 버튼 중심 좌표 또는 None
        """
        # 템플릿별 낮은 confidence 설정 (투명/오버레이 이미지용)
        low_confidence_templates = {
            "complete_check": 0.6,      # 체크 아이콘 (투명 배경)
            "analyzing_spinner": 0.6,   # 회전 스피너
        }
        
        # confidence 결정
        if confidence is None:
            confidence = low_confidence_templates.get(template_name, self.confidence)
        
        # 템플릿 파일 찾기 (png, jpg 지원)
        template_path = None
        for ext in ['.png', '.jpg', '.jpeg']:
            path = self.template_dir / f"{template_name}{ext}"
            if path.exists():
                template_path = path
                break
        
        if not template_path:
            logger.warning(f"Template not found: {template_name}")
            logger.warning(f"  Expected location: {self.template_dir / template_name}.png")
            return None
        
        logger.debug(f"Searching for: {template_path.name} (confidence={confidence})")
        
        try:
            # 화면에서 템플릿 찾기
            location = pyautogui.locateOnScreen(
                str(template_path),
                confidence=confidence
            )
            
            if location:
                # 중심 좌표 계산
                x = location.left + location.width // 2
                y = location.top + location.height // 2
                logger.info(f"  Found '{template_name}' at ({x}, {y})")
                return (x, y)
            else:
                # 못 찾음 (정상 - 아직 나타나지 않음)
                return None
                
        except pyautogui.ImageNotFoundException:
            # 이미지를 찾지 못함 (정상 - 아직 나타나지 않음)
            return None
        except Exception as e:
            logger.error(f"Error finding '{template_name}': {type(e).__name__}: {e}")
            return None
    
    def click_button(self, template_name: str, wait_after: float = 0.5) -> bool:
        """
        화면에서 버튼을 찾아서 클릭
        
        Args:
            template_name: 템플릿 이미지 파일명 (확장자 제외)
            wait_after: 클릭 후 대기 시간
        
        Returns:
            성공 여부
        """
        import time
        
        pos = self.find_button(template_name)
        if pos:
            x, y = pos
            logger.info(f"Clicking '{template_name}' at ({x}, {y})")
            pyautogui.click(x, y)
            time.sleep(wait_after)
            return True
        
        return False
    
    def wait_and_click(self, template_name: str, timeout: int = 10, 
                       interval: float = 0.5, wait_after: float = 0.5) -> bool:
        """
        버튼이 나타날 때까지 대기 후 클릭
        
        Args:
            template_name: 템플릿 이미지 파일명
            timeout: 최대 대기 시간 (초)
            interval: 검색 간격 (초)
            wait_after: 클릭 후 대기 시간
        
        Returns:
            성공 여부
        """
        import time
        
        logger.info(f"Waiting for '{template_name}' (timeout: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.click_button(template_name, wait_after):
                return True
            time.sleep(interval)
        
        logger.error(f"Timeout waiting for '{template_name}'")
        return False


def capture_button_template(output_name: str):
    """
    현재 화면에서 버튼 영역을 캡처하여 템플릿으로 저장
    
    사용법:
        1. 캡처할 버튼이 보이는 상태로 만들기
        2. 이 함수 실행
        3. 3초 후 현재 마우스 위치 주변 영역 캡처
    """
    import time
    
    print("=" * 50)
    print("버튼 템플릿 캡처 도구")
    print("=" * 50)
    print("")
    print("1. 캡처할 버튼 위에 마우스를 올리세요")
    print("2. 3초 후 버튼 영역이 캡처됩니다")
    print("")
    
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    # 현재 마우스 위치
    x, y = pyautogui.position()
    
    # 버튼 크기 (대략적인 크기, 필요시 조정)
    width, height = 150, 40
    
    # 캡처 영역 계산 (마우스 위치 중심)
    left = x - width // 2
    top = y - height // 2
    
    # 스크린샷 캡처
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    
    # 저장
    output_path = TEMPLATE_DIR / f"{output_name}.png"
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    screenshot.save(output_path)
    
    print("")
    print("=" * 50)
    print(f"  템플릿 저장됨: {output_path}")
    print(f"  크기: {width}x{height}")
    print(f"  위치: ({left}, {top})")
    print("=" * 50)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        capture_button_template(sys.argv[1])
    else:
        print("사용법: python ui_detector.py <템플릿_이름>")
        print("")
        print("예시:")
        print("  python ui_detector.py apply_autopilot")
        print("  python ui_detector.py export_button")

