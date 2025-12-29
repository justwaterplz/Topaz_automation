"""
간단한 아이콘 템플릿 캡처 도구

전체 화면을 캡처한 후 사용자가 이미지 편집기로 폴더 아이콘을 자르도록 안내
"""
import sys
import time
from pathlib import Path
import pyautogui
import cv2
import numpy as np

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """메인 함수"""
    
    print("=" * 70)
    print("아이콘 템플릿 캡처 도구 (간단 버전)")
    print("=" * 70)
    print()
    print("📋 준비 사항:")
    print("  1. Topaz Gigapixel AI 실행")
    print("  2. 이미지 열기 (Ctrl+O)")
    print("  3. 저장하기 (Ctrl+S + Enter)")
    print("  4. Export Settings 다이얼로그 열림")
    print("  5. Processing 완료되어 'Done' + 폴더 아이콘 보임 ✅")
    print()
    
    input("✅ 위 상태가 준비되었으면 Enter를 누르세요...")
    
    print()
    print("3초 후 전체 화면을 캡처합니다...")
    print("(Export Settings 다이얼로그가 최상단에 있어야 합니다)")
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    print()
    print("📸 화면 캡처 중...")
    
    # 전체 화면 캡처
    screenshot = pyautogui.screenshot()
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # 저장 디렉토리 생성
    output_dir = Path("assets/templates")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 전체 화면 저장
    fullscreen_path = output_dir / "fullscreen_capture.png"
    cv2.imwrite(str(fullscreen_path), screenshot_cv)
    
    print(f"✓ 전체 화면 캡처 완료: {fullscreen_path}")
    print()
    
    # 화면 크기
    width, height = screenshot.size
    print(f"📏 화면 크기: {width} x {height}")
    print()
    
    print("=" * 70)
    print("📝 다음 단계: 폴더 아이콘을 직접 잘라주세요")
    print("=" * 70)
    print()
    print(f"1. 이미지 편집기로 다음 파일을 여세요:")
    print(f"   {fullscreen_path.absolute()}")
    print()
    print("2. Queue 영역에서 'Done' 옆의 📁 폴더 아이콘만 정확하게 자르세요")
    print("   - 아이콘만 선택 (Done 텍스트 제외)")
    print("   - 크기: 약 20-40 픽셀 정도의 작은 아이콘")
    print()
    print("3. 잘라낸 이미지를 다음 경로에 저장하세요:")
    print(f"   {output_dir.absolute()}\\done_folder_icon.png")
    print()
    print("4. 저장 완료 후 자동화를 실행하세요:")
    print("   python main.py --input-dir \"D:\\Images\"")
    print()
    
    # Windows에서 탐색기로 폴더 열기
    try:
        import subprocess
        subprocess.Popen(f'explorer /select,"{fullscreen_path.absolute()}"')
        print("✓ 탐색기에서 파일을 열었습니다.")
    except:
        pass
    
    print()
    print("=" * 70)
    print("💡 팁:")
    print("  - Windows 그림판, Paint.NET, Photoshop 등 아무 도구나 사용")
    print("  - 폴더 아이콘만 정확하게 선택하는 것이 중요합니다")
    print("  - 주변에 약간의 여백을 포함해도 괜찮습니다")
    print("=" * 70)
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

