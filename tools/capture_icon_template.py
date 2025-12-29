"""
아이콘 템플릿 캡처 도구

사용법:
1. Topaz 앱에서 Export Settings 다이얼로그를 열고 "Done" 상태로 만듭니다
2. 이 스크립트를 실행합니다
3. 5초 후 Queue 영역이 자동으로 캡처됩니다
4. 저장된 이미지에서 폴더 아이콘 부분만 잘라서 done_folder_icon.png로 저장합니다
"""
import sys
import time
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.window_manager import WindowManager
from utils.icon_detector import IconDetector
from loguru import logger


def main():
    """메인 함수"""
    
    print("=" * 60)
    print("아이콘 템플릿 캡처 도구")
    print("=" * 60)
    print()
    print("📋 준비 사항:")
    print("  1. Topaz Gigapixel AI 실행")
    print("  2. 이미지 열기 (Ctrl+O)")
    print("  3. 저장하기 (Ctrl+S + Enter)")
    print("  4. Export Settings 다이얼로그가 열림")
    print("  5. Processing이 완료되어 'Done' 상태가 되면...")
    print()
    
    input("준비되었으면 Enter를 누르세요...")
    
    print()
    print("5초 후 캡처를 시작합니다...")
    for i in range(5, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    print()
    print("캡처 중...")
    
    # Export Settings 다이얼로그 찾기
    hwnd = WindowManager.find_window_by_title("Export Settings")
    
    if hwnd == 0:
        # Topaz 메인 윈도우에서 시도
        hwnd = WindowManager.find_window_by_title("Topaz Gigapixel")
        if hwnd == 0:
            print("❌ 윈도우를 찾을 수 없습니다!")
            print("   Topaz 앱이 실행 중이고 Export Settings 다이얼로그가 열려있는지 확인하세요.")
            return 1
        
        print("⚠️  Export Settings 다이얼로그를 찾을 수 없어 메인 윈도우를 사용합니다.")
    
    # Queue 영역 좌표 (상대)
    queue_region_ratios = {
        'x_ratio': 0.02,
        'y_ratio': 0.12,
        'width_ratio': 0.60,
        'height_ratio': 0.15
    }
    
    # 절대 좌표 계산
    region = WindowManager.get_relative_region(
        hwnd,
        queue_region_ratios['x_ratio'],
        queue_region_ratios['y_ratio'],
        queue_region_ratios['width_ratio'],
        queue_region_ratios['height_ratio']
    )
    
    if region is None:
        print("❌ 영역 좌표를 계산할 수 없습니다!")
        return 1
    
    x, y, width, height = region
    print(f"  캡처 영역: x={x}, y={y}, w={width}, h={height}")
    
    # 캡처
    detector = IconDetector()
    
    # 1. 전체 Queue 영역 캡처 (참고용)
    output_dir = Path("assets/templates")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    full_capture_path = output_dir / "queue_full_capture.png"
    if detector.save_template_from_region(x, y, width, height, "queue_full_capture"):
        print(f"✓ 전체 Queue 영역 캡처 완료: {full_capture_path}")
    
    # 2. 폴더 아이콘 영역 캡처 (Done 오른쪽)
    # Done 텍스트는 Queue 영역의 오른쪽에 위치
    icon_x = x + int(width * 0.75)  # Queue 영역의 75% 지점부터
    icon_y = y + int(height * 0.2)   # 상단에서 20% 아래
    icon_width = int(width * 0.15)   # 작은 영역
    icon_height = int(height * 0.6)  # 적당한 높이
    
    icon_capture_path = output_dir / "done_folder_icon_auto.png"
    if detector.save_template_from_region(icon_x, icon_y, icon_width, icon_height, "done_folder_icon_auto"):
        print(f"✓ 폴더 아이콘 영역 캡처 완료: {icon_capture_path}")
    
    print()
    print("=" * 60)
    print("✅ 캡처 완료!")
    print("=" * 60)
    print()
    print(f"📁 저장 위치: {output_dir}")
    print()
    print("📝 다음 단계:")
    print("  1. 'queue_full_capture.png'를 열어서 확인")
    print("  2. 'done_folder_icon_auto.png'를 열어서 확인")
    print("  3. 폴더 아이콘이 명확하게 보이는지 확인")
    print("  4. 필요하면 이미지 편집기로 정확하게 자르기")
    print("  5. 최종 파일을 'done_folder_icon.png'로 저장")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

