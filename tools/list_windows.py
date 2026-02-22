"""List all visible windows"""
import win32gui

def list_all_windows():
    windows = []
    
    def callback(hwnd, param):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                windows.append((hwnd, title))
        return True
    
    win32gui.EnumWindows(callback, None)
    
    print("=" * 80)
    print("All visible windows:")
    print("=" * 80)
    
    for hwnd, title in windows:
        print(f"  {hwnd}: {repr(title)}")
    
    print("")
    print("=" * 80)
    print("Windows containing 'photo' (case insensitive):")
    print("=" * 80)
    
    for hwnd, title in windows:
        if 'photo' in title.lower():
            print(f"  {hwnd}: {repr(title)}")

if __name__ == "__main__":
    list_all_windows()
