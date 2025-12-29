"""
현재 열려있는 모든 윈도우 목록 출력
Export Settings 다이얼로그의 실제 제목 확인용
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import win32gui
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("❌ pywin32 not available")
    sys.exit(1)


def list_all_windows():
    """모든 윈도우 목록 출력"""
    windows = []
    
    def callback(hwnd, param):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:  # 제목이 있는 윈도우만
                windows.append((hwnd, title))
        return True
    
    win32gui.EnumWindows(callback, None)
    return windows


def main():
    """메인 함수"""
    
    print("=" * 80)
    print("현재 열려있는 윈도우 목록")
    print("=" * 80)
    print()
    
    windows = list_all_windows()
    
    print(f"총 {len(windows)}개의 윈도우가 발견되었습니다.")
    print()
    
    # Topaz 관련 윈도우만 필터링
    topaz_windows = [w for w in windows if 'topaz' in w[1].lower() or 'gigapixel' in w[1].lower() or 'export' in w[1].lower()]
    
    if topaz_windows:
        print("🎯 Topaz/Export 관련 윈도우:")
        print("-" * 80)
        for hwnd, title in topaz_windows:
            print(f"  HWND: {hwnd}")
            print(f"  제목: {title}")
            print()
    else:
        print("⚠️  Topaz 관련 윈도우를 찾을 수 없습니다.")
        print()
    
    print("📋 전체 윈도우 목록:")
    print("-" * 80)
    for hwnd, title in windows:
        print(f"  [{hwnd}] {title}")
    
    print()
    print("=" * 80)
    print("💡 Export Settings 다이얼로그를 찾았나요?")
    print("   - 위 목록에서 해당 윈도우의 정확한 제목을 확인하세요")
    print("   - 제목이 'Export Settings'가 아닐 수 있습니다")
    print("=" * 80)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

