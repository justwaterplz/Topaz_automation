"""
이미지에서 "Done" 텍스트 찾기

OCR(pytesseract) 또는 템플릿 매칭 사용
- pip install pytesseract
- Tesseract OCR 설치 필요: https://github.com/UB-Mannheim/tesseract/wiki

python tools/find_done_in_image.py [이미지경로]
"""
import sys
import os

def _setup_tesseract_path():
    """Windows에서 Tesseract 경로 설정"""
    import pytesseract
    
    # 환경변수로 명시적 지정 (최우선)
    env_path = os.environ.get('TESSERACT_CMD')
    if env_path and os.path.isfile(env_path):
        pytesseract.pytesseract.tesseract_cmd = env_path
        return
    
    # 이미 설정되어 있고 해당 파일이 존재하면 스킵
    existing = getattr(pytesseract.pytesseract, 'tesseract_cmd', None)
    if existing and os.path.isfile(existing):
        return
    
    # Windows 기본 설치 경로 (사용자 dir 결과 기준)
    win_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    
    # PATH에 추가한 경로들 확인 (tesseract.exe가 있는 디렉터리)
    path_env = os.environ.get('PATH', '')
    for part in path_env.split(os.pathsep):
        part = part.strip().strip('"')
        if 'tesseract' in part.lower():
            exe_path = os.path.join(part, 'tesseract.exe')
            if os.path.isfile(exe_path):
                win_paths.insert(0, exe_path)
    
    for path in win_paths:
        if path and os.path.isfile(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return
    
    # shutil.which (PATH에서 tesseract 검색)
    import shutil
    tesseract_exe = shutil.which('tesseract') or shutil.which('tesseract.exe')
    if tesseract_exe:
        pytesseract.pytesseract.tesseract_cmd = tesseract_exe
        return


def find_done_ocr(img_path: str, search_region: str = "all"):
    """OCR로 Done 텍스트 찾기
    
    search_region: "all" | "left" | "right" - 다중 모니터 시 검색 영역
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError as e:
        print(f"필요: pip install pytesseract Pillow")
        print(f"Tesseract OCR도 설치 필요")
        return None
    
    _setup_tesseract_path()
    
    img = Image.open(img_path).convert('RGB')
    w, h = img.size
    
    print(f"이미지 크기: {w}x{h}")
    
    # 다중 모니터: 한쪽만 검색 (Topaz가 보통 한 모니터에 있음)
    if search_region == "left" and w > 1920:
        img = img.crop((0, 0, w // 2, h))
        print(f"  검색 영역: 왼쪽 절반")
    elif search_region == "right" and w > 1920:
        img = img.crop((w // 2, 0, w, h))
        print(f"  검색 영역: 오른쪽 절반")
    print()
    
    # 작은 텍스트를 위해 2배 확대 후 OCR
    scale = 2 if min(img.width, img.height) > 1500 else 1
    if scale > 1:
        img_scaled = img.resize((img.width * scale, img.height * scale), Image.Resampling.LANCZOS)
        print(f"OCR용 확대: {scale}x")
    else:
        img_scaled = img
    
    # OCR 실행 (영어만 - Done 검색용)
    try:
        data = pytesseract.image_to_data(img_scaled, lang='eng', output_type=pytesseract.Output.DICT)
    except Exception as e:
        err_msg = str(e)
        print(f"OCR 오류: {err_msg}")
        if "tesseract" in err_msg.lower() or "not found" in err_msg.lower() or "is not installed" in err_msg.lower():
            print()
            print("Tesseract 경로 확인:")
            cmd = getattr(pytesseract.pytesseract, 'tesseract_cmd', '미설정')
            print(f"  현재 경로: {cmd}")
            print("  수동 설정: 환경변수 TESSERACT_CMD 또는 코드에서 pytesseract.pytesseract.tesseract_cmd = '경로'")
        return None
    
    # 원본 이미지 기준 좌표 오프셋 (오른쪽 절반 검색 시)
    offset_x = w // 2 if (search_region == "right" and w > 1920) else 0
    
    found = []
    for i, text in enumerate(data['text']):
        if text.strip().upper() == 'DONE':
            x = data['left'][i] // scale + offset_x
            y = data['top'][i] // scale
            ww = data['width'][i] // scale
            hh = data['height'][i] // scale
            conf = data['conf'][i]
            found.append((x, y, ww, hh, conf))
            print(f"  발견: 'Done' at ({x}, {y}) size={ww}x{hh} conf={conf}")
    
    if not found:
        print("OCR로 'Done'을 찾지 못했습니다.")
        print("  - 텍스트가 너무 작을 수 있음 (이미지 확대 후 재시도)")
        print("  - 한글/영어 혼합 환경에서 인식 실패 가능")
        return None
    
    return found

def find_done_template(img_path: str, template_path: str = None):
    """템플릿 매칭으로 Done 찾기"""
    try:
        import cv2
        import numpy as np
    except ImportError:
        print("필요: pip install opencv-python numpy")
        return None
    
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "templates")
    template_path = template_path or os.path.join(template_dir, "done_text.png")
    
    if not os.path.exists(template_path):
        print(f"템플릿 없음: {template_path}")
        print("먼저 capture_via_clipboard.py로 Done 영역을 캡처하세요")
        return None
    
    img = cv2.imread(img_path)
    template = cv2.imread(template_path)
    
    if img is None or template is None:
        print("이미지 로드 실패")
        return None
    
    # 다중 스케일 시도 (작은 텍스트 대응)
    scales = [0.5, 0.75, 1.0, 1.25, 1.5]
    best_match = None
    best_val = 0
    
    for scale in scales:
        w = int(template.shape[1] * scale)
        h = int(template.shape[0] * scale)
        if w < 10 or h < 10:
            continue
        
        resized = cv2.resize(template, (w, h))
        result = cv2.matchTemplate(img, resized, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val > best_val:
            best_val = max_val
            best_match = (max_loc[0], max_loc[1], w, h, max_val)
    
    if best_match and best_val > 0.6:
        x, y, w, h, conf = best_match
        print(f"템플릿 매칭: 'Done' at ({x}, {y}) size={w}x{h} confidence={best_val:.2f}")
        return [(x, y, w, h, int(best_val * 100))]
    
    print(f"템플릿 매칭 실패 (최고 confidence: {best_val:.2f})")
    return None

def create_template_from_bbox(img_path: str, x: int, y: int, w: int = 80, h: int = 30):
    """찾은 위치에서 템플릿 생성"""
    from PIL import Image
    
    img = Image.open(img_path).convert('RGB')
    # bbox 중심으로 crop
    left = max(0, x - w//2)
    top = max(0, y - h//2)
    right = min(img.width, left + w)
    bottom = min(img.height, top + h)
    
    crop = img.crop((left, top, right, bottom))
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "templates")
    out_path = os.path.join(template_dir, "done_text.png")
    crop.save(out_path)
    print(f"템플릿 저장: {out_path}")
    return out_path

def main():
    img_path = sys.argv[1] if len(sys.argv) > 1 else "clipboard_manual.png"
    search_region = sys.argv[2] if len(sys.argv) > 2 else "all"  # all | left | right
    
    img_path = os.path.join(os.path.dirname(__file__), img_path) if not os.path.isabs(img_path) else img_path
    
    if not os.path.exists(img_path):
        print(f"파일 없음: {img_path}")
        return
    
    print("=" * 60)
    print(f"이미지: {img_path}")
    print("=" * 60)
    print()
    
    print("[1] OCR로 검색...")
    ocr_result = find_done_ocr(img_path, search_region)
    
    print()
    print("[2] 템플릿 매칭...")
    tmpl_result = find_done_template(img_path)
    
    print()
    if ocr_result:
        # 첫 번째 결과로 템플릿 생성
        x, y, w, h, _ = ocr_result[0]
        print("OCR 결과로 템플릿 생성...")
        create_template_from_bbox(img_path, x + w//2, y + h//2, w + 20, h + 10)
    elif tmpl_result:
        print("템플릿 매칭으로 찾음 (자동화에 사용 가능)")
    else:
        print("두 방법 모두 실패.")
        print()
        print("수동으로 템플릿 생성:")
        print("  1. capture_via_clipboard.py 실행")
        print("  2. 마우스를 'Done' 텍스트 위에 올리고 3초 대기")
        print("  3. 생성된 clipboard_preview.png에서 Done 영역 확인")

def check_tesseract():
    """Tesseract 설치 확인"""
    try:
        import pytesseract
    except ImportError:
        print("pytesseract 미설치: pip install pytesseract")
        return
    
    # 경로 확인
    default_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    print(f"기본 경로 존재 여부: {os.path.isfile(default_path)}")
    
    _setup_tesseract_path()
    cmd = getattr(pytesseract.pytesseract, 'tesseract_cmd', None)
    print(f"사용 경로: {cmd}")
    print(f"파일 존재: {os.path.isfile(cmd) if cmd else False}")
    
    try:
        ver = pytesseract.get_tesseract_version()
        print(f"버전: {ver}")
        print("✓ Tesseract 정상")
    except Exception as e:
        print(f"✗ 오류: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--check':
        check_tesseract()
    else:
        main()
