"""Capture button templates for UI detection"""
import pyautogui
import time
from pathlib import Path
import sys

# 템플릿 저장 경로
TEMPLATE_DIR = Path(__file__).parent.parent / "assets" / "photoai"


def capture_button(button_name: str, width: int = 150, height: int = 40):
    """
    버튼 템플릿 캡처
    
    Args:
        button_name: 저장할 파일명 (확장자 제외)
        width: 캡처 너비
        height: 캡처 높이
    """
    print("=" * 60)
    print(f"버튼 템플릿 캡처: {button_name}")
    print("=" * 60)
    print("")
    print(f"캡처할 버튼 위에 마우스를 올리세요")
    print(f"캡처 크기: {width}x{height} 픽셀")
    print("")
    
    for i in range(5, 0, -1):
        print(f"  {i}초 후 캡처...")
        time.sleep(1)
    
    # 현재 마우스 위치
    x, y = pyautogui.position()
    
    # 캡처 영역 (마우스 위치 중심)
    left = x - width // 2
    top = y - height // 2
    
    # 스크린샷
    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    
    # 저장
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    output_path = TEMPLATE_DIR / f"{button_name}.png"
    screenshot.save(output_path)
    
    print("")
    print("=" * 60)
    print(f"  저장 완료!")
    print(f"  파일: {output_path}")
    print(f"  크기: {width}x{height}")
    print(f"  마우스 위치: ({x}, {y})")
    print("=" * 60)
    
    return output_path


def main():
    print("")
    print("=" * 60)
    print("Photo AI 버튼 템플릿 캡처 도구")
    print("=" * 60)
    print("")
    print("필요한 템플릿:")
    print("  1. apply_autopilot - 'Apply Autopilot' 버튼")
    print("  2. apply_confirm   - '적용' 버튼 (다이얼로그)")
    print("  3. export_button   - 'Export N images' 버튼")
    print("")
    
    if len(sys.argv) > 1:
        button_name = sys.argv[1]
        width = int(sys.argv[2]) if len(sys.argv) > 2 else 150
        height = int(sys.argv[3]) if len(sys.argv) > 3 else 40
        capture_button(button_name, width, height)
    else:
        print("사용법:")
        print("  python capture_button.py <버튼이름> [너비] [높이]")
        print("")
        print("예시:")
        print("  python capture_button.py apply_autopilot 150 40")
        print("  python capture_button.py apply_confirm 80 35")
        print("  python capture_button.py export_button 150 35")
        print("")
        
        # 대화형 모드
        print("-" * 60)
        choice = input("지금 캡처하시겠습니까? (1/2/3/n): ").strip()
        
        templates = {
            '1': ('apply_autopilot', 150, 40),
            '2': ('apply_confirm', 80, 35),
            '3': ('export_button', 150, 35),
        }
        
        if choice in templates:
            name, w, h = templates[choice]
            capture_button(name, w, h)
        elif choice.lower() != 'n':
            print("취소됨")


if __name__ == "__main__":
    main()

