"""
Topaz Automation - Main Entry Point

실행:
    python main.py
"""
import sys


def main():
    from apps.gigapixel_app.main import main as gui_main
    return gui_main()


if __name__ == '__main__':
    sys.exit(main() or 0)
