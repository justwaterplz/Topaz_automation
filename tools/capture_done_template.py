"""
"Done" 텍스트 템플릿 캡처 도구

사용법:
    1. Topaz에서 저장 완료된 상태로 Export 다이얼로그를 열어둠
    2. "Done" 텍스트가 보이는 상태에서 이 스크립트 실행
    3. 마우스를 "Done" 텍스트 위에 올리고 대기
    4. 자동으로 해당 영역 캡처

    python tools/capture_done_template.py
"""
import time
import os
import sys

def capture_template():
    try:
        import pyautogui
    except ImportError:
        print("pyautogui가 필요합니다: pip install pyautogui")
        return
    
    print("=" * 60)
    print("Done 템플릿 캡처 도구")
    print("=" * 60)
    print()
    print("1. Topaz Export 다이얼로그에서 'Done' 텍스트가 보이는지 확인")
    print("2. 마우스를 'Done' 텍스트 중앙에 올려놓으세요")
    print("3. 5초 후 해당 위치 주변을 캡처합니다")
    print()
    
    for i in range(5, 0, -1):
        x, y = pyautogui.position()
        print(f"  {i}초... (현재 마우스: {x}, {y})")
        time.sleep(1)
    
    # 현재 마우스 위치
    x, y = pyautogui.position()
    print()
    print(f"캡처 위치: ({x}, {y})")
    
    # 먼저 넓은 영역을 캡처해서 확인용으로 저장
    wide_width, wide_height = 200, 100
    wide_left = max(0, x - wide_width // 2)
    wide_top = max(0, y - wide_height // 2)
    
    wide_screenshot = pyautogui.screenshot(region=(wide_left, wide_top, wide_width, wide_height))
    
    # 확인용 이미지 저장
    output_dir = os.path.dirname(os.path.abspath(__file__))
    preview_path = os.path.join(output_dir, "capture_preview.png")
    wide_screenshot.save(preview_path)
    print(f"미리보기 저장됨: {preview_path}")
    print("(이 이미지를 확인하여 마우스 위치가 맞는지 확인하세요)")
    print()
    
    # "Done" 텍스트 크기 (더 크게)
    width, height = 80, 30
    
    # 캡처 영역 (마우스 중심)
    left = max(0, x - width // 2)
    top = max(0, y - height // 2)
    
    # 스크린샷
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    
    # 저장 경로
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "templates")
    os.makedirs(template_dir, exist_ok=True)
    
    output_path = os.path.join(template_dir, "done_text.png")
    screenshot.save(output_path)
    
    print()
    print("=" * 60)
    print(f"✓ 템플릿 저장됨: {output_path}")
    print(f"  크기: {width}x{height}")
    print(f"  위치: ({left}, {top})")
    print("=" * 60)
    print()
    print("이제 이 템플릿으로 'Done' 상태를 감지할 수 있습니다.")
    print()
    
    # Processing 템플릿도 캡처할지 물어봄
    print("'Processing' 텍스트도 캡처하시겠습니까?")
    print("(처리 중인 이미지가 있을 때 마우스를 올려놓고 Enter)")
    input("Enter를 누르면 5초 후 캡처합니다 (건너뛰려면 Ctrl+C)...")
    
    print()
    for i in range(5, 0, -1):
        x, y = pyautogui.position()
        print(f"  {i}초... (현재 마우스: {x}, {y})")
        time.sleep(1)
    
    x, y = pyautogui.position()
    width, height = 100, 25  # Processing은 더 길 수 있음
    left = x - width // 2
    top = y - height // 2
    
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    output_path = os.path.join(template_dir, "processing_text.png")
    screenshot.save(output_path)
    
    print()
    print(f"✓ Processing 템플릿 저장됨: {output_path}")


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
        print("먼저 capture_done_template.py를 실행하세요")
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
            return False
    except Exception as e:
        print(f"오류: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_template()
    else:
        capture_template()
