"""Get current mouse position"""
import pyautogui
import time

print("=" * 50)
print("마우스 좌표 확인 도구")
print("=" * 50)
print("")
print("버튼 위에 마우스를 올린 후 3초 대기...")
print("")

for i in range(3, 0, -1):
    print(f"  {i}...")
    time.sleep(1)

x, y = pyautogui.position()
print("")
print("=" * 50)
print(f"현재 마우스 좌표: X={x}, Y={y}")
print("=" * 50)
print("")
print("이 좌표를 config/photoai_config.py에 설정하세요:")
print("")
print(f"    APPLY_AUTOPILOT_BUTTON_X = {x}")
print(f"    APPLY_AUTOPILOT_BUTTON_Y = {y}")
print("")
print("또는 Export 버튼:")
print("")
print(f"    EXPORT_BUTTON_X = {x}")
print(f"    EXPORT_BUTTON_Y = {y}")

