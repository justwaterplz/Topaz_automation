"""
Topaz Gigapixel AI GUI - Main Entry Point

사용법:
    python -m apps.gigapixel_app.main
    또는
    python apps/gigapixel_app/main.py
"""
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가 (PyInstaller 빌드 시 불필요)
if not getattr(sys, 'frozen', False):
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

# COM 충돌 방지: QApplication을 pywinauto/win32 import 전에 생성
# RPC_E_CHANGED_MODE 오류 해결 - MainWindow import가 core(pyautogui 등)를 로드하므로
# QApplication을 먼저 생성한 뒤 MainWindow import
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt


def main():
    """GUI 앱 실행"""
    # High DPI 지원
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Topaz Gigapixel Automation")
    app.setApplicationVersion("1.0.0")
    
    # 스타일시트 로드 (PyInstaller 빌드 시 _MEIPASS 사용)
    if getattr(sys, 'frozen', False):
        base = Path(sys._MEIPASS)
        style_path = base / "apps" / "gigapixel_app" / "styles.qss"
    else:
        style_path = Path(__file__).parent / "styles.qss"
    if style_path.exists():
        with open(style_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    
    # MainWindow는 QApplication 생성 후 import (COM 충돌 방지)
    from apps.gigapixel_app.main_window import MainWindow
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
