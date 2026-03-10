"""
"Done" 템플릿 캡처 v3 - Topaz 창 직접 캡처

다중 모니터 / GPU 렌더링 문제 해결:
- 화면 캡처 대신 Topaz 윈도우를 직접 캡처
- win32 API 사용

python tools/capture_done_template_v3.py
"""
import time
import os
import sys

def capture_topaz_window():
    """Topaz Gigapixel AI 창을 직접 캡처"""
    try:
        import win32gui
        import win32ui
        import win32con
        from PIL import Image
    except ImportError as e:
        print(f"필요한 라이브러리: pip install pywin32 Pillow")
        print(f"오류: {e}")
        return None
    
    def find_topaz_window():
        result = []
        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if 'Topaz Gigapixel' in title:
                    result.append(hwnd)
            return True
        win32gui.EnumWindows(callback, None)
        return result[0] if result else None
    
    hwnd = find_topaz_window()
    if not hwnd:
        print("Topaz Gigapixel AI 창을 찾을 수 없습니다.")
        print("앱을 실행하고 Export 다이얼로그를 열어두세요.")
        return None
    
    # 창 위치/크기
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top
    
    # 창 DC 가져오기
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(bitmap)
    
    # 창 내용 복사 (PrintWindow는 win32에 없어서 ctypes 사용)
    import ctypes
    result = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)
    
    # PIL Image로 변환
    bmpinfo = bitmap.GetInfo()
    bmpstr = bitmap.GetBitmapBits(True)
    img = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1
    )
    
    # 정리
    win32gui.DeleteObject(bitmap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)
    
    return img, (left, top, right, bottom)

def get_cursor_pos():
    import ctypes
    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

def main():
    print("=" * 60)
    print("Done 템플릿 캡처 v3 (Topaz 창 직접 캡처)")
    print("=" * 60)
    print()
    print("1. Topaz Export 다이얼로그에서 'Done' 텍스트가 보이게")
    print("2. 마우스를 'Done' 텍스트 중앙에 올려놓으세요")
    print("3. 5초 후 Topaz 창을 캡처합니다")
    print()
    
    for i in range(5, 0, -1):
        x, y = get_cursor_pos()
        print(f"  {i}초... (마우스: {x}, {y})")
        time.sleep(1)
    
    x, y = get_cursor_pos()
    print()
    
    result = capture_topaz_window()
    if not result:
        return
    
    img, (win_left, win_top, win_right, win_bottom) = result
    
    # 마우스 위치를 창 내부 좌표로 변환
    rel_x = x - win_left
    rel_y = y - win_top
    
    print(f"Topaz 창: ({win_left}, {win_top}) ~ ({win_right}, {win_bottom})")
    print(f"마우스 (창 기준): ({rel_x}, {rel_y})")
    print()
    
    output_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(os.path.dirname(output_dir), "assets", "templates")
    os.makedirs(template_dir, exist_ok=True)
    
    # 전체 창 저장
    full_path = os.path.join(output_dir, "topaz_window_full.png")
    img.save(full_path)
    print(f"전체 창 저장: {full_path}")
    
    # 마우스 주변 crop (창 좌표 기준)
    crop_w, crop_h = 120, 50
    c_left = max(0, rel_x - crop_w // 2)
    c_top = max(0, rel_y - crop_h // 2)
    c_right = min(img.width, c_left + crop_w)
    c_bottom = min(img.height, c_top + crop_h)
    
    crop = img.crop((c_left, c_top, c_right, c_bottom))
    done_path = os.path.join(template_dir, "done_text.png")
    crop.save(done_path)
    print(f"Done 템플릿: {done_path}")
    
    # 미리보기 (넓은 영역)
    wide_w, wide_h = 250, 120
    w_left = max(0, rel_x - wide_w // 2)
    w_top = max(0, rel_y - wide_h // 2)
    w_right = min(img.width, w_left + wide_w)
    w_bottom = min(img.height, w_top + wide_h)
    wide_crop = img.crop((w_left, w_top, w_right, w_bottom))
    preview_path = os.path.join(output_dir, "topaz_preview.png")
    wide_crop.save(preview_path)
    print(f"미리보기: {preview_path}")
    
    print()
    print("=" * 60)
    print("완료! topaz_window_full.png에서 전체 창이 제대로 보이는지 확인하세요.")
    print("=" * 60)

if __name__ == "__main__":
    main()
