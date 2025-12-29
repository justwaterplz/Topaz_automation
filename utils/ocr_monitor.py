"""OCR monitoring utilities for detecting processing status"""
import time
from typing import Optional, Tuple
import numpy as np
import pyautogui
from PIL import Image
from loguru import logger

# EasyOCR은 느리게 로드되므로 필요할 때만 import
_reader = None


def get_ocr_reader():
    """
    EasyOCR reader 싱글톤 인스턴스 가져오기
    첫 호출 시에만 초기화 (시간이 걸림)
    """
    global _reader
    
    if _reader is None:
        try:
            import easyocr
            logger.info("Initializing EasyOCR (this may take a moment)...")
            _reader = easyocr.Reader(['en'], gpu=False)  # 영어만, CPU 사용
            logger.info("EasyOCR initialized")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            return None
    
    return _reader


def capture_screen_region(x: int, y: int, width: int, height: int) -> Optional[Image.Image]:
    """
    화면의 특정 영역 캡처
    
    Args:
        x, y: 캡처 시작 위치
        width, height: 캡처 크기
    
    Returns:
        PIL Image 또는 None
    """
    try:
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        return screenshot
    except Exception as e:
        logger.error(f"Failed to capture screen: {e}")
        return None


def detect_text_in_region(
    x: int, 
    y: int, 
    width: int, 
    height: int, 
    target_text: str = "Enhancing",
    debug: bool = False,
    debug_path: str = None
) -> bool:
    """
    화면 특정 영역에서 텍스트 감지
    
    Args:
        x, y: 감지할 영역의 좌상단 좌표
        width, height: 감지할 영역 크기
        target_text: 찾을 텍스트
        debug: True면 캡처 이미지 저장
        debug_path: 디버그 이미지 저장 경로
    
    Returns:
        텍스트가 발견되면 True
    """
    reader = get_ocr_reader()
    if reader is None:
        logger.warning("OCR not available")
        return False
    
    # 화면 캡처
    img = capture_screen_region(x, y, width, height)
    if img is None:
        return False
    
    try:
        # PIL Image를 numpy array로 변환 (EasyOCR 요구사항)
        img_array = np.array(img)
        
        # 디버그: 캡처 이미지 저장
        if debug and debug_path:
            img.save(debug_path)
            logger.debug(f"Debug image saved: {debug_path}")
        
        # OCR 수행
        results = reader.readtext(img_array, detail=0)  # detail=0: 텍스트만 반환
        
        # 모든 감지된 텍스트 로깅 (디버깅용)
        if results:
            logger.debug(f"OCR detected {len(results)} text(s): {results}")
        else:
            logger.debug("OCR detected no text")
        
        # 결과에서 target_text 찾기
        for text in results:
            if target_text.lower() in text.lower():
                logger.info(f"✓ Found '{target_text}' in text: '{text}'")
                return True
        
        return False
    
    except Exception as e:
        logger.error(f"OCR detection failed: {e}")
        return False


def get_preview_region_coords(expanded: bool = True) -> Tuple[int, int, int, int]:
    """
    Topaz 앱의 프리뷰 영역 좌표 반환
    우측 상단의 작은 프리뷰 이미지 및 상태 텍스트 영역
    
    Args:
        expanded: True면 더 넓은 영역 캡처 (더 안정적)
    
    Returns:
        (x, y, width, height)
    
    Note:
        해상도에 따라 조정이 필요할 수 있음
        기본값은 1920x1080 기준
    """
    # 화면 크기 가져오기
    screen_width, screen_height = pyautogui.size()
    
    if expanded:
        # 우측 패널 전체를 넓게 캡처 (더 안정적)
        width = 450  # 더 넓게
        height = 300  # 프리뷰 + 상태 텍스트 전체
        x = screen_width - width - 10  # 우측 끝
        y = 30  # 상단
    else:
        # 상태 텍스트 영역만 집중
        width = 400
        height = 100
        x = screen_width - width - 20
        y = 50
    
    logger.debug(f"Preview region: ({x}, {y}, {width}, {height})")
    return (x, y, width, height)


def get_queue_region_coords() -> Tuple[int, int, int, int]:
    """
    Topaz 앱의 Queue 영역 좌표 반환
    Export Settings 다이얼로그 좌측 상단의 Queue 영역
    
    Returns:
        (x, y, width, height)
    
    Note:
        Export Settings 다이얼로그가 열린 상태에서만 사용
    """
    # 기본 좌표 (Export Settings 다이얼로그 기준)
    x = 140
    y = 130
    width = 720
    height = 150
    
    logger.debug(f"Queue region: ({x}, {y}, {width}, {height})")
    return (x, y, width, height)


def wait_for_text_disappear(
    target_text: str = "Enhancing",
    check_interval: float = 2.0,
    timeout: int = 300,
    initial_wait: float = 3.0,
    debug: bool = False
) -> bool:
    """
    특정 텍스트가 사라질 때까지 대기
    
    Args:
        target_text: 감지할 텍스트
        check_interval: OCR 체크 간격 (초)
        timeout: 최대 대기 시간 (초)
        initial_wait: 초기 대기 시간 (처리 시작 대기)
        debug: 디버그 모드 (캡처 이미지 저장)
    
    Returns:
        성공적으로 완료되면 True
    """
    logger.info(f"Waiting for '{target_text}' to disappear...")
    
    # 초기 대기 (처리가 시작되도록)
    if initial_wait > 0:
        logger.debug(f"Initial wait: {initial_wait}s")
        time.sleep(initial_wait)
    
    # OCR 초기화
    reader = get_ocr_reader()
    if reader is None:
        logger.warning("OCR not available, falling back to time-based waiting")
        return False
    
    # 프리뷰 영역 좌표
    x, y, width, height = get_preview_region_coords()
    
    elapsed = initial_wait
    last_detected = time.time()
    consecutive_not_found = 0
    check_count = 0
    
    while elapsed < timeout:
        check_count += 1
        
        # 디버그 이미지 경로
        debug_path = None
        if debug:
            from pathlib import Path
            debug_dir = Path("logs/ocr_debug")
            debug_dir.mkdir(parents=True, exist_ok=True)
            debug_path = str(debug_dir / f"capture_{check_count:03d}.png")
        
        # 텍스트 감지
        text_found = detect_text_in_region(
            x, y, width, height, target_text,
            debug=debug, debug_path=debug_path
        )
        
        if text_found:
            logger.info(f"'{target_text}' still detected... (elapsed: {elapsed:.1f}s)")
            last_detected = time.time()
            consecutive_not_found = 0
        else:
            consecutive_not_found += 1
            logger.info(f"'{target_text}' not detected ({consecutive_not_found}/2)")
            
            # 연속 2번 감지 안 되면 완료로 판단
            if consecutive_not_found >= 2:
                logger.info(f"✓ '{target_text}' disappeared (processing complete)")
                return True
        
        # 대기
        time.sleep(check_interval)
        elapsed += check_interval
        
        # 진행 상황 로깅 (10초마다)
        if int(elapsed) % 10 == 0:
            logger.info(f"Still processing... ({elapsed:.0f}s elapsed)")
    
    logger.warning(f"Timeout after {timeout}s")
    return True  # 타임아웃이어도 계속 진행


def wait_for_save_processing_complete(
    check_interval: float = 2.0,
    timeout: int = 300,
    initial_wait: float = 2.0,
    debug: bool = False
) -> bool:
    """
    저장 처리 완료 대기 (Queue 영역의 "Processing" -> "Done" 감지)
    
    Export Settings 다이얼로그의 Queue 영역에서
    "Processing" 텍스트가 나타났다가 사라지고 "Done"이 나타날 때까지 대기
    
    Args:
        check_interval: OCR 체크 간격 (초)
        timeout: 최대 대기 시간 (초)
        initial_wait: 초기 대기 시간 (처리 시작 대기)
        debug: 디버그 모드 (캡처 이미지 저장)
    
    Returns:
        성공적으로 완료되면 True
    """
    logger.info("Waiting for save processing to complete...")
    logger.info("  → Looking for: 'Processing' -> 'Done' in Queue")
    
    # 초기 대기 (저장 처리가 시작되도록)
    if initial_wait > 0:
        logger.debug(f"Initial wait: {initial_wait}s (for save to start)")
        time.sleep(initial_wait)
    
    # OCR 초기화
    reader = get_ocr_reader()
    if reader is None:
        logger.warning("OCR not available, falling back to time-based waiting")
        time.sleep(10)  # 10초 대기 후 계속
        return True
    
    # Queue 영역 좌표
    x, y, width, height = get_queue_region_coords()
    
    elapsed = initial_wait
    check_count = 0
    processing_detected = False
    done_detected = False
    
    while elapsed < timeout:
        check_count += 1
        
        # 디버그 이미지 경로
        debug_path = None
        if debug:
            from pathlib import Path
            debug_dir = Path("logs/ocr_debug_queue")
            debug_dir.mkdir(parents=True, exist_ok=True)
            debug_path = str(debug_dir / f"queue_{check_count:03d}.png")
        
        # 텍스트 감지 (Processing과 Done 모두 확인)
        processing_found = detect_text_in_region(
            x, y, width, height, "Processing",
            debug=debug, debug_path=debug_path
        )
        
        done_found = detect_text_in_region(
            x, y, width, height, "Done",
            debug=False  # 한 번만 저장
        )
        
        # 상태 업데이트
        if processing_found:
            if not processing_detected:
                logger.info("✓ 'Processing' detected - save started")
                processing_detected = True
        
        if done_found:
            if not done_detected:
                logger.info("✓ 'Done' detected - save completed!")
                done_detected = True
                return True
        
        # Processing이 감지된 후 사라지면 완료로 간주
        if processing_detected and not processing_found and not done_found:
            logger.info("'Processing' disappeared - checking again...")
            time.sleep(check_interval)
            
            # 한 번 더 확인
            done_found_2 = detect_text_in_region(x, y, width, height, "Done")
            processing_found_2 = detect_text_in_region(x, y, width, height, "Processing")
            
            if done_found_2 or not processing_found_2:
                logger.info("✓ Save processing complete")
                return True
        
        # 상태 로깅
        if processing_detected:
            logger.info(f"Still processing... (elapsed: {elapsed:.1f}s)")
        else:
            logger.debug(f"Waiting for 'Processing' to appear... ({elapsed:.1f}s)")
        
        # 대기
        time.sleep(check_interval)
        elapsed += check_interval
        
        # 진행 상황 로깅 (10초마다)
        if int(elapsed) % 10 == 0 and processing_detected:
            logger.info(f"Still saving... ({elapsed:.0f}s elapsed)")
    
    logger.warning(f"Timeout after {timeout}s")
    logger.warning(f"  Processing detected: {processing_detected}, Done detected: {done_detected}")
    return True  # 타임아웃이어도 계속 진행

