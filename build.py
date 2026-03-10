#!/usr/bin/env python
"""
Topaz Gigapixel Automation - 단일 exe 빌드 스크립트

사용법:
    python build.py

출력: dist/TopazGigapixelAutomation.exe
"""
import subprocess
import sys
from pathlib import Path


def main():
    project_root = Path(__file__).parent
    
    # PyInstaller 설치 확인
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller가 설치되어 있지 않습니다.")
        print("설치: pip install pyinstaller")
        sys.exit(1)
    
    # build.spec로 빌드
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--clean", "build.spec"],
        cwd=project_root,
    )
    
    if result.returncode == 0:
        exe_path = project_root / "dist" / "TopazGigapixelAutomation.exe"
        print("")
        print("=" * 50)
        print("빌드 완료!")
        print(f"출력: {exe_path}")
        print("=" * 50)
    else:
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
