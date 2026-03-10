"""
"Done" 텍스트 템플릿 캡처 도구 v2

pyautogui 대신 PIL ImageGrab 사용
DPI 스케일링 문제 해결

python tools/capture_done_template_v2.py
"""
import time
import os
import sys
import ctypes

def get_cursor_pos():
    """윈도우 API로 정확한 마우스 위치 가져오기"""
    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
    
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

def capture_template():
    try:
        from PIL import ImageGrab
    except ImportError:
        print("Pillow가 필요합니다: pip install Pillow")
        return
    
    # DPI 인식 설정
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware
    except:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except:
            pass
    
    print("=" * 60)
    print("Done 템플릿 캡처 도구 v2 (DPI 보정)")
    print("=" * 60)
    print()
    print("1. Topaz Export 다이얼로그에서 'Done' 텍스트가 보이는지 확인")
    print("2. 마우스를 'Done' 텍스트 중앙에 올려놓으세요")
    print("3. 5초 후 해당 위치 주변을 캡처합니다")
    print()
    
    for i in range(5, 0, -1):
        x, y = get_cursor_pos()
        print(f"  {i}초... (현재 마우스: {x}, {y})")
        time.sleep(1)
    
    # 정확한 마우스 위치 (Windows API)
    x, y = get_cursor_pos()
    print()
    print(f"캡처 위치 (Windows API): ({x}, {y})")
    
    # 출력 디렉토리
    output_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(os.path.dirname(output_dir), "assets", "templates")
    os.makedirs(template_dir, exist_ok=True)
    
    # 방법 1: 전체 화면 캡처 후 crop
    print()
    print("전체 화면 캡처 중...")
    full_screen = ImageGrab.grab()
    full_path = os.path.join(output_dir, "full_screen.png")
    full_screen.save(full_path)
    print(f"전체 화면 저장됨: {full_path}")
    print(f"화면 크기: {full_screen.size}")
    
    # 마우스 주변 넓은 영역 crop
    wide_width, wide_height = 300, 150
    wide_left = max(0, x - wide_width // 2)
    wide_top = max(0, y - wide_height // 2)
    wide_right = wide_left + wide_width
    wide_bottom = wide_top + wide_height
    
    wide_crop = full_screen.crop((wide_left, wide_top, wide_right, wide_bottom))
    preview_path = os.path.join(output_dir, "capture_preview_v2.png")
    wide_crop.save(preview_path)
    print(f"미리보기 저장됨: {preview_path}")
    print(f"  영역: ({wide_left}, {wide_top}) ~ ({wide_right}, {wide_bottom})")
    
    # Done 템플릿 crop
    width, height = 80, 30
    left = max(0, x - width // 2)
    top = max(0, y - height // 2)
    right = left + width
    bottom = top + height
    
    done_crop = full_screen.crop((left, top, right, bottom))
    done_path = os.path.join(template_dir, "done_text.png")
    done_crop.save(done_path)
    print(f"Done 템플릿 저장됨: {done_path}")
    print(f"  영역: ({left}, {top}) ~ ({right}, {bottom})")
    
    print()
    print("=" * 60)
    print("캡처 완료!")
    print("=" * 60)
    print()
    print("확인해주세요:")
    print(f"  1. {preview_path} - 마우스 주변 영역")
    print(f"  2. {done_path} - Done 템플릿")
    print()
    print("'Done' 텍스트가 제대로 캡처되었으면 테스트:")
    print("  python tools/capture_done_template_v2.py --test")


def test_template():
    """저장된 템플릿으로 화면에서 찾기 테스트"""
    try:
        import pyautogui
    except ImportError:
        print("pyautogui가 필요합니다")
        return
    
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "templates")
    done_template = os.path.join(template_dir, "done_text.png")
    
    if not os.path.exists(done_template):
        print(f"템플릿이 없습니다: {done_template}")
        return
    
    print("=" * 60)
    print("템플릿 매칭 테스트")
    print("=" * 60)
    print()
    print("화면에서 'Done' 템플릿을 찾는 중...")
    
    try:
        location = pyautogui.locateOnScreen(done_template, confidence=0.8)
        if location:
            print(f"✓ 'Done' 발견! 위치: {location}")
            return True
        else:
            print("✗ 'Done'을 찾을 수 없습니다")
            print("  confidence를 낮춰서 다시 시도...")
            location = pyautogui.locateOnScreen(done_template, confidence=0.6)
            if location:
                print(f"✓ 'Done' 발견 (confidence=0.6)! 위치: {location}")
                return True
            return False
    except Exception as e:
        print(f"오류: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_template()
    else:
        capture_template()
