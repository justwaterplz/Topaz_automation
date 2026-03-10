"""
Desktop Duplication API를 사용한 화면 캡처 (dxcam)

GPU 렌더링된 앱(Topaz 등)도 캡처 가능
- pip install dxcam

python tools/capture_with_dxcam.py
"""
import time
import os
import sys

def get_cursor_pos():
    import ctypes
    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

def main():
    try:
        import dxcam
        from PIL import Image
    except ImportError as e:
        print("dxcam이 필요합니다:")
        print("  pip install dxcam")
        print()
        print(f"오류: {e}")
        return
    
    print("=" * 60)
    print("dxcam - Desktop Duplication API 캡처")
    print("(GPU 렌더링 앱 캡처 가능)")
    print("=" * 60)
    print()
    print("1. Topaz Export 다이얼로그에서 'Done' 텍스트가 보이게")
    print("2. 마우스를 'Done' 텍스트 중앙에 올려놓으세요")
    print("3. 5초 후 캡처합니다")
    print()
    
    for i in range(5, 0, -1):
        x, y = get_cursor_pos()
        print(f"  {i}초... (마우스: {x}, {y})")
        time.sleep(1)
    
    x, y = get_cursor_pos()
    print()
    
    # dxcam 초기화 (Desktop Duplication API)
    print("dxcam 초기화 중...")
    try:
        # output_idx: 다중 모니터 시 0=주 모니터, 1=보조 모니터
        try:
            camera = dxcam.create(output_color="RGB")
        except TypeError:
            camera = dxcam.create()
    except Exception as e:
        print(f"dxcam 초기화 실패: {e}")
        return
    
    if camera is None:
        print("dxcam 초기화 실패")
        return
    
    # 전체 화면 캡처
    print("전체 화면 캡처 중...")
    frame = None
    for _ in range(5):  # 최대 5회 시도
        try:
            frame = camera.grab(new_frame_only=False)
        except TypeError:
            frame = camera.grab()
        if frame is not None:
            break
        time.sleep(0.2)
    
    if frame is None:
        print("캡처 실패 (None 반환)")
        print("다중 모니터인 경우: output_idx=1 등으로 시도해보세요")
        return
    
    # numpy -> PIL (dxcam 0.0.5는 BGR, 0.1.0은 output_color로 RGB 지정 가능)
    import numpy as np
    if len(frame.shape) == 3 and frame.shape[2] == 3:
        # BGR -> RGB (PIL은 RGB 기대)
        frame_rgb = frame[:, :, ::-1].copy()
        img = Image.fromarray(frame_rgb, mode='RGB')
    else:
        img = Image.fromarray(frame)
    
    output_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(os.path.dirname(output_dir), "assets", "templates")
    os.makedirs(template_dir, exist_ok=True)
    
    # 전체 화면 저장
    full_path = os.path.join(output_dir, "dxcam_full_screen.png")
    img.save(full_path)
    print(f"전체 화면: {full_path}")
    print(f"  크기: {img.size}")
    
    # 마우스 주변 영역 crop
    wide_w, wide_h = 250, 120
    left = max(0, x - wide_w // 2)
    top = max(0, y - wide_h // 2)
    right = min(img.width, left + wide_w)
    bottom = min(img.height, top + wide_h)
    
    crop = img.crop((left, top, right, bottom))
    preview_path = os.path.join(output_dir, "dxcam_preview.png")
    crop.save(preview_path)
    print(f"미리보기: {preview_path}")
    
    # Done 템플릿
    done_w, done_h = 80, 30
    d_left = max(0, x - done_w // 2)
    d_top = max(0, y - done_h // 2)
    d_right = min(img.width, d_left + done_w)
    d_bottom = min(img.height, d_top + done_h)
    
    done_crop = img.crop((d_left, d_top, d_right, d_bottom))
    done_path = os.path.join(template_dir, "done_text.png")
    done_crop.save(done_path)
    print(f"Done 템플릿: {done_path}")
    
    print()
    print("=" * 60)
    print("완료! dxcam_full_screen.png에서 Topaz가 보이는지 확인하세요.")
    print("=" * 60)

if __name__ == "__main__":
    main()
