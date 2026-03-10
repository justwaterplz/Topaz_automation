"""
Topaz Automation - Main Entry Point

GUI 앱 실행:
    python main.py
    
CLI 모드 (레거시):
    python main.py --cli --input-dir "D:\\Images"
"""
import sys
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description='Topaz Gigapixel Automation',
        add_help=False
    )
    parser.add_argument('--cli', action='store_true', help='CLI 모드로 실행 (레거시)')
    parser.add_argument('-h', '--help', action='store_true', help='도움말 표시')
    
    # 먼저 --cli 플래그만 확인
    args, remaining = parser.parse_known_args()
    
    if args.cli:
        # CLI 모드 (레거시)
        sys.argv = [sys.argv[0]] + remaining
        from legacy.main_cli import main as cli_main
        return cli_main()
    
    if args.help and not remaining:
        print("""
Topaz Gigapixel Automation
==========================

GUI 모드 (기본):
    python main.py

CLI 모드 (레거시):
    python main.py --cli [옵션들...]
    
CLI 옵션:
    --input-dir PATH     입력 디렉토리
    --single FILE        단일 파일 처리
    --wait-time SEC      초기 대기 시간 (기본: 5초)
    --save-wait-time SEC 저장 대기 시간 (기본: 18초)

예시:
    python main.py                              # GUI 실행
    python main.py --cli --input-dir "D:\\img"  # CLI로 배치 처리
        """)
        return 0
    
    # GUI 모드 (기본)
    from apps.gigapixel_app.main import main as gui_main
    return gui_main()


if __name__ == '__main__':
    sys.exit(main() or 0)
