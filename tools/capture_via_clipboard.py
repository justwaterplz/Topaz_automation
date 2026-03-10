"""
클립보드 경유 캡처 (PrintScreen 시뮬레이션)

Windows가 PrintScreen으로 캡처할 때 사용하는 경로는
GDI/Desktop Duplication과 다를 수 있어 GPU 앱도 잡을 수 있음.

사용법:
    1. Topaz Export 다이얼로그에서 'Done'이 보이게
    2. 이 스크립트 실행
    3. 3초 후 PrintScreen 시뮬레이션 → 클립보드에서 읽기

    python tools/capture_via_clipboard.py
"""
import time
import os
import sys

def main():
    try:
        import pyautogui
        from PIL import ImageGrab
    except ImportError as e:
        print(f"필요: pip install pyautogui Pillow")
        print(f"오류: {e}")
        return
    
    print("=" * 60)
    print("클립보드 경유 캡처 (PrintScreen)")
    print("=" * 60)
    print()
    print("1. Topaz Export 다이얼로그에서 'Done'이 보이게")
    print("2. Topaz 창이 활성화된 상태로")
    print("3. 3초 후 PrintScreen 시뮬레이션")
    print()
    
    for i in range(3, 0, -1):
        print(f"  {i}초...")
        time.sleep(1)
    
    print()
    print("PrintScreen 시뮬레이션...")
    
    # PrintScreen 키 누르기 (전체 화면 → 클립보드)
    pyautogui.press('printscreen')
    time.sleep(0.5)
    
    # 클립보드에서 이미지 읽기
    img = ImageGrab.grabclipboard()
    
    if img is None:
        print("클립보드에 이미지가 없습니다.")
        print("PrintScreen이 제대로 동작하지 않았을 수 있습니다.")
        return
    
    print(f"캡처 성공! 크기: {img.size}")
    
    output_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(os.path.dirname(output_dir), "assets", "templates")
    os.makedirs(template_dir, exist_ok=True)
    
    # 전체 화면 저장
    full_path = os.path.join(output_dir, "clipboard_full.png")
    img.save(full_path)
    print(f"저장: {full_path}")
    
    # 마우스 위치 기준 crop
    x, y = pyautogui.position()
    wide_w, wide_h = 250, 120
    left = max(0, x - wide_w // 2)
    top = max(0, y - wide_h // 2)
    right = min(img.width, left + wide_w)
    bottom = min(img.height, top + wide_h)
    
    crop = img.crop((left, top, right, bottom))
    preview_path = os.path.join(output_dir, "clipboard_preview.png")
    crop.save(preview_path)
    print(f"미리보기: {preview_path}")
    
    # Done 템플릿
    done_w, done_h = 80, 30
    d_left = max(0, x - done_w // 2)
    d_top = max(0, y - done_h // 2)
    d_right = min(img.width, d_left + done_w)
    d_bottom = min(img.height, d_top + done_h)
    
    done_crop = img.crop((d_left, d_top, d_right, d_bottom))
    done_path = os.path.join(template_dir, "done_text.png")
    done_crop.save(done_path)
    print(f"Done 템플릿: {done_path}")
    
    print()
    print("=" * 60)
    print("clipboard_full.png에서 Topaz가 보이는지 확인하세요.")
    print("=" * 60)

def manual_mode():
    """수동 모드: 사용자가 직접 PrintScreen 누른 후 클립보드 읽기"""
    from PIL import ImageGrab
    
    print("=" * 60)
    print("수동 모드 - PrintScreen 후 클립보드 읽기")
    print("=" * 60)
    print()
    print("1. Topaz가 보이는 상태로 준비")
    print("2. PrintScreen 키를 직접 누르세요")
    print("3. Enter를 누르면 클립보드에서 읽습니다")
    print()
    input("PrintScreen 누른 후 Enter...")
    
    img = ImageGrab.grabclipboard()
    if img is None:
        print("클립보드에 이미지 없음")
        return
    
    output_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(output_dir, "clipboard_manual.png")
    img.save(path)
    print(f"저장: {path}")
    print("Topaz가 보이는지 확인하세요.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--manual':
        manual_mode()
    else:
        main()
