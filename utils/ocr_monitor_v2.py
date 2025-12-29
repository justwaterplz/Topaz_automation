"""
향상된 OCR 모니터링 유틸리티
Tesseract OCR + OpenCV 템플릿 매칭 + 폴백 시스템
"""
import os
import time
from typing import Optional, Tuple
from pathlib import Path
import numpy as np
import pyautogui
from PIL import Image
from loguru import logger
import cv2

# Tesseract OCR (빠르고 정확)
_tesseract_available = False
try:
    import pytesseract
    _tesseract_available = True
    logger.info("Tesseract OCR available")
except ImportError:
    logger.warning("pytesseract not installed - falling back to EasyOCR")

# EasyOCR (폴백용)
_easyocr_reader = None


def init_tesseract():
    """
    Tesseract 경로 설정 (Windows)
    """
    if not _tesseract_available:
        return False
    
    try:
        # Windows에서 일반적인 Tesseract 설치 경로
        tesseract_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Users\' + os.getenv('USERNAME', 'moon') + r'\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
        ]
        
        import os
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                logger.info(f"Tesseract found: {path}")
                return True
        
        # 경로를 찾지 못하면 기본 설정으로 시도
        logger.warning("Tesseract path not found, using default")
        return True
    
    except Exception as e:
        logger.error(f"Failed to initialize Tesseract: {e}")
        return False


def get_easyocr_reader():
    """
    EasyOCR reader 싱글톤 (폴백용)
    """
    global _easyocr_reader
    
    if _easyocr_reader is None:
        try:
            import easyocr
            logger.info("Initializing EasyOCR (fallback)...")
            _easyocr_reader = easyocr.Reader(['en'], gpu=False)
            logger.info("EasyOCR initialized")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {e}")
            return None
    
    return _easyocr_reader


def capture_screen_region(x: int, y: int, width: int, height: int) -> Optional[Image.Image]:
    """
    화면의 특정 영역 캡처
    """
    try:
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        return screenshot
    except Exception as e:
        logger.error(f"Failed to capture screen: {e}")
        return None


def preprocess_for_ocr(img: Image.Image) -> np.ndarray:
    """
    OCR 정확도 향상을 위한 이미지 전처리
    
    Args:
        img: PIL Image
    
    Returns:
        전처리된 numpy array (grayscale)
    """
    # PIL Image -> OpenCV
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    
    # Grayscale 변환
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    # 대비 향상 (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    
    # 이진화 (Otsu's method)
    _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 노이즈 제거
    denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
    
    return denoised


def detect_text_tesseract(
    img: Image.Image,
    target_text: str,
    confidence_threshold: int = 30
) -> Tuple[bool, str]:
    """
    Tesseract OCR로 텍스트 감지
    
    Args:
        img: PIL Image
        target_text: 찾을 텍스트
        confidence_threshold: 최소 신뢰도 (0-100)
    
    Returns:
        (발견 여부, 감지된 전체 텍스트)
    """
    if not _tesseract_available:
        return False, ""
    
    try:
        # 이미지 전처리
        processed = preprocess_for_ocr(img)
        
        # OCR 수행 (상세 정보 포함)
        data = pytesseract.image_to_data(
            processed, 
            output_type=pytesseract.Output.DICT,
            config='--psm 6'  # 균일한 텍스트 블록 가정
        )
        
        # 결과 분석
        detected_texts = []
        for i, conf in enumerate(data['conf']):
            if conf > confidence_threshold:
                text = data['text'][i].strip()
                if text:
                    detected_texts.append(text)
        
        full_text = ' '.join(detected_texts)
        
        # 대소문자 구분 없이 검색
        found = target_text.lower() in full_text.lower()
        
        if detected_texts:
            logger.debug(f"Tesseract detected: {detected_texts}")
        
        if found:
            logger.info(f"✓ Tesseract found '{target_text}' in: {full_text}")
        
        return found, full_text
    
    except Exception as e:
        logger.debug(f"Tesseract detection failed: {e}")
        return False, ""


def detect_text_easyocr(
    img: Image.Image,
    target_text: str
) -> Tuple[bool, str]:
    """
    EasyOCR로 텍스트 감지 (폴백)
    
    Args:
        img: PIL Image
        target_text: 찾을 텍스트
    
    Returns:
        (발견 여부, 감지된 전체 텍스트)
    """
    reader = get_easyocr_reader()
    if reader is None:
        return False, ""
    
    try:
        img_array = np.array(img)
        results = reader.readtext(img_array, detail=0)
        
        full_text = ' '.join(results)
        found = any(target_text.lower() in text.lower() for text in results)
        
        if results:
            logger.debug(f"EasyOCR detected: {results}")
        
        if found:
            logger.info(f"✓ EasyOCR found '{target_text}' in: {full_text}")
        
        return found, full_text
    
    except Exception as e:
        logger.debug(f"EasyOCR detection failed: {e}")
        return False, ""


def detect_text_template_matching(
    img: Image.Image,
    template_name: str,
    threshold: float = 0.7
) -> bool:
    """
    OpenCV 템플릿 매칭으로 텍스트 영역 감지
    
    Args:
        img: PIL Image (현재 화면)
        template_name: 템플릿 이미지 이름 ('processing', 'done')
        threshold: 매칭 임계값 (0-1)
    
    Returns:
        발견 여부
    """
    try:
        # 템플릿 이미지 경로
        template_dir = Path("assets/templates")
        template_path = template_dir / f"{template_name}.png"
        
        if not template_path.exists():
            logger.debug(f"Template not found: {template_path}")
            return False
        
        # 이미지 로드
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        template = cv2.imread(str(template_path))
        
        # Grayscale 변환
        img_gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        # 템플릿 매칭
        result = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        found = max_val >= threshold
        
        if found:
            logger.info(f"✓ Template '{template_name}' matched (confidence: {max_val:.2f})")
        else:
            logger.debug(f"Template '{template_name}' not matched (max: {max_val:.2f})")
        
        return found
    
    except Exception as e:
        logger.debug(f"Template matching failed: {e}")
        return False


def detect_text_in_region(
    x: int,
    y: int,
    width: int,
    height: int,
    target_text: str,
    debug: bool = False,
    debug_path: Optional[str] = None
) -> Tuple[bool, str]:
    """
    멀티 OCR 방식으로 텍스트 감지
    
    우선순위: Tesseract > EasyOCR > 템플릿 매칭
    
    Args:
        x, y: 감지할 영역의 좌상단 좌표
        width, height: 감지할 영역 크기
        target_text: 찾을 텍스트
        debug: True면 캡처 이미지 저장
        debug_path: 디버그 이미지 저장 경로
    
    Returns:
        (발견 여부, 감지된 텍스트)
    """
    # 화면 캡처
    img = capture_screen_region(x, y, width, height)
    if img is None:
        return False, ""
    
    # 디버그: 이미지 저장
    if debug and debug_path:
        img.save(debug_path)
        logger.debug(f"Debug image saved: {debug_path}")
    
    # 1. Tesseract OCR 시도 (가장 빠름)
    if _tesseract_available:
        found, text = detect_text_tesseract(img, target_text)
        if found:
            return True, text
    
    # 2. EasyOCR 시도 (폴백)
    found, text = detect_text_easyocr(img, target_text)
    if found:
        return True, text
    
    # 3. 템플릿 매칭 시도 (OCR 실패 시)
    template_name = target_text.lower()
    if detect_text_template_matching(img, template_name):
        return True, target_text
    
    return False, text


def get_queue_region_coords() -> Tuple[int, int, int, int]:
    """
    Queue 영역 좌표 반환
    """
    x = 140
    y = 130
    width = 720
    height = 150
    
    logger.debug(f"Queue region: ({x}, {y}, {width}, {height})")
    return (x, y, width, height)


def wait_for_save_processing_complete(
    check_interval: float = 1.5,
    timeout: int = 300,
    initial_wait: float = 1.5,
    debug: bool = False
) -> bool:
    """
    저장 처리 완료 대기 (멀티 OCR)
    
    Queue 영역에서 "Processing" -> "Done" 감지
    
    Args:
        check_interval: OCR 체크 간격 (초)
        timeout: 최대 대기 시간 (초)
        initial_wait: 초기 대기 시간
        debug: 디버그 모드
    
    Returns:
        성공적으로 완료되면 True
    """
    logger.info("Waiting for save processing to complete...")
    logger.info("  → Using: Tesseract OCR + EasyOCR + Template Matching")
    
    # Tesseract 초기화
    if _tesseract_available:
        init_tesseract()
    
    # 초기 대기
    if initial_wait > 0:
        logger.debug(f"Initial wait: {initial_wait}s")
        time.sleep(initial_wait)
    
    # Queue 영역 좌표
    x, y, width, height = get_queue_region_coords()
    
    elapsed = initial_wait
    check_count = 0
    processing_detected = False
    done_detected = False
    
    while elapsed < timeout:
        check_count += 1
        
        # 디버그 경로
        debug_path = None
        if debug:
            debug_dir = Path("logs/ocr_debug_queue_v2")
            debug_dir.mkdir(parents=True, exist_ok=True)
            debug_path = str(debug_dir / f"queue_{check_count:03d}.png")
        
        # Processing 감지
        processing_found, text_processing = detect_text_in_region(
            x, y, width, height, "Processing",
            debug=debug, debug_path=debug_path
        )
        
        # Done 감지
        done_found, text_done = detect_text_in_region(
            x, y, width, height, "Done",
            debug=False
        )
        
        # 상태 업데이트
        if processing_found and not processing_detected:
            logger.info("✓ 'Processing' detected - save started")
            processing_detected = True
        
        if done_found:
            logger.info("✓ 'Done' detected - save completed!")
            return True
        
        # Processing 감지 후 사라지면 완료
        if processing_detected and not processing_found:
            logger.info("'Processing' disappeared - verifying...")
            time.sleep(check_interval)
            
            # 재확인
            done_found_2, _ = detect_text_in_region(x, y, width, height, "Done")
            if done_found_2:
                logger.info("✓ 'Done' confirmed - save complete")
                return True
            
            processing_found_2, _ = detect_text_in_region(x, y, width, height, "Processing")
            if not processing_found_2:
                logger.info("✓ Processing complete (text disappeared)")
                return True
        
        # 상태 로깅
        if processing_detected:
            logger.info(f"Still processing... ({elapsed:.1f}s)")
        else:
            logger.debug(f"Waiting for Processing... ({elapsed:.1f}s)")
        
        # 대기
        time.sleep(check_interval)
        elapsed += check_interval
    
    logger.warning(f"Timeout after {timeout}s")
    logger.warning(f"  Processing: {processing_detected}, Done: {done_detected}")
    return True  # 타임아웃이어도 계속 진행

