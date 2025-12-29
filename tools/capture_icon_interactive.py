"""
인터랙티브 아이콘 템플릿 캡처 도구

사용자가 마우스로 영역을 선택하여 템플릿 생성
"""
import sys
import time
from pathlib import Path
import pyautogui
import cv2
import numpy as np
from PIL import Image

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def capture_full_screen():
    """전체 화면 캡처"""
    screenshot = pyautogui.screenshot()
    return np.array(screenshot)


def select_region_interactive(image):
    """
    사용자가 마우스로 영역 선택
    
    Returns:
        (x, y, width, height) 또는 None
    """
    # OpenCV 윈도우 생성
    window_name = "Select Icon Region - Draw rectangle and press ENTER"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    # 화면 크기에 맞춰 윈도우 크기 조정
    screen_height, screen_width = image.shape[:2]
    display_width = min(1920, screen_width)
    display_height = int(screen_height * (display_width / screen_width))
    cv2.resizeWindow(window_name, display_width, display_height)
    
    # 이미지 복사 (그리기용)
    img_display = image.copy()
    img_display = cv2.cvtColor(img_display, cv2.COLOR_RGB2BGR)
    
    # 선택 영역 저장
    roi = {"x": 0, "y": 0, "w": 0, "h": 0}
    drawing = False
    
    def mouse_callback(event, x, y, flags, param):
        nonlocal drawing, img_display
        
        # 실제 좌표 계산 (윈도우 크기와 이미지 크기 비율)
        scale_x = screen_width / display_width
        scale_y = screen_height / display_height
        actual_x = int(x * scale_x)
        actual_y = int(y * scale_y)
        
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            roi["x"] = actual_x
            roi["y"] = actual_y
        
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                img_temp = image.copy()
                img_temp = cv2.cvtColor(img_temp, cv2.COLOR_RGB2BGR)
                cv2.rectangle(
                    img_temp,
                    (roi["x"], roi["y"]),
                    (actual_x, actual_y),
                    (0, 255, 0),
                    3
                )
                # 윈도우 크기에 맞춰 리사이즈
                img_resized = cv2.resize(img_temp, (display_width, display_height))
                cv2.imshow(window_name, img_resized)
        
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            roi["w"] = actual_x - roi["x"]
            roi["h"] = actual_y - roi["y"]
            
            # 최종 사각형 그리기
            img_display = image.copy()
            img_display = cv2.cvtColor(img_display, cv2.COLOR_RGB2BGR)
            cv2.rectangle(
                img_display,
                (roi["x"], roi["y"]),
                (roi["x"] + roi["w"], roi["y"] + roi["h"]),
                (0, 255, 0),
                3
            )
            # 윈도우 크기에 맞춰 리사이즈
            img_resized = cv2.resize(img_display, (display_width, display_height))
            cv2.imshow(window_name, img_resized)
    
    cv2.setMouseCallback(window_name, mouse_callback)
    
    # 초기 이미지 표시 (윈도우 크기에 맞춰 리사이즈)
    img_resized = cv2.resize(img_display, (display_width, display_height))
    cv2.imshow(window_name, img_resized)
    
    print("\n마우스로 폴더 아이콘 영역을 드래그하세요.")
    print("  - 드래그: 왼쪽 마우스 버튼")
    print("  - 확인: Enter 키")
    print("  - 취소: ESC 키")
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        
        if key == 13:  # Enter
            if roi["w"] > 0 and roi["h"] > 0:
                cv2.destroyAllWindows()
                return (roi["x"], roi["y"], roi["w"], roi["h"])
        
        elif key == 27:  # ESC
            cv2.destroyAllWindows()
            return None
    
    cv2.destroyAllWindows()
    return None


def main():
    """메인 함수"""
    
    print("=" * 60)
    print("인터랙티브 아이콘 템플릿 캡처 도구")
    print("=" * 60)
    print()
    print("📋 준비 사항:")
    print("  1. Topaz Gigapixel AI 실행")
    print("  2. 이미지 열기 (Ctrl+O)")
    print("  3. 저장하기 (Ctrl+S + Enter)")
    print("  4. Export Settings 다이얼로그가 열림")
    print("  5. Processing이 완료되어 'Done' + 폴더 아이콘이 보이면...")
    print()
    
    input("준비되었으면 Enter를 누르세요...")
    
    print()
    print("3초 후 전체 화면을 캡처합니다...")
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    print()
    print("화면 캡처 중...")
    
    # 전체 화면 캡처
    screenshot = capture_full_screen()
    
    # 임시 파일로 저장 (확인용)
    temp_dir = Path("logs/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / "fullscreen_capture.png"
    cv2.imwrite(str(temp_path), cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR))
    print(f"✓ 전체 화면 캡처: {temp_path}")
    
    # 사용자가 영역 선택
    print()
    print("영역 선택 윈도우가 열립니다...")
    time.sleep(0.5)
    
    region = select_region_interactive(screenshot)
    
    if region is None:
        print("\n❌ 취소되었습니다.")
        return 1
    
    x, y, w, h = region
    
    # 음수 너비/높이 처리
    if w < 0:
        x = x + w
        w = abs(w)
    if h < 0:
        y = y + h
        h = abs(h)
    
    print()
    print(f"✓ 선택된 영역: x={x}, y={y}, w={w}, h={h}")
    
    # 영역 추출
    icon_image = screenshot[y:y+h, x:x+w]
    
    # 저장
    output_dir = Path("assets/templates")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "done_folder_icon.png"
    cv2.imwrite(str(output_path), cv2.cvtColor(icon_image, cv2.COLOR_RGB2BGR))
    
    print()
    print("=" * 60)
    print("✅ 템플릿 저장 완료!")
    print("=" * 60)
    print()
    print(f"📁 저장 위치: {output_path}")
    print(f"📏 크기: {w} x {h} 픽셀")
    print()
    print("🎉 이제 자동화를 실행할 수 있습니다:")
    print("   python main.py --input-dir \"D:\\Images\"")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

