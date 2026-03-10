"""
Topaz Gigapixel AI 저장 처리 상태 모니터링 도구

사용법:
    1. Topaz 앱에서 Ctrl+S를 눌러 Export 다이얼로그를 먼저 열기
    2. 이 스크립트 실행
    3. Queue 영역의 "Done" 또는 "Processing" 상태를 모니터링

    python tools/inspect_topaz_ui.py
"""
import sys
import time
import re

def monitor_save_processing():
    """저장 처리 상태 모니터링"""
    
    try:
        from pywinauto import Application
        from pywinauto.findwindows import ElementNotFoundError
    except ImportError:
        print("ERROR: pywinauto가 설치되지 않았습니다.")
        print("설치: pip install pywinauto")
        return
    
    print("=" * 70)
    print("Topaz Gigapixel AI - 저장 처리 상태 모니터링")
    print("=" * 70)
    print()
    
    # Topaz 앱 연결
    print("Topaz Gigapixel AI 앱을 찾는 중...")
    
    try:
        app = Application(backend='uia').connect(title_re='.*Topaz Gigapixel.*', timeout=5)
        main_window = app.window(title_re='.*Topaz Gigapixel.*')
        print(f"✓ 연결됨: {main_window.window_text()}")
    except ElementNotFoundError:
        print("✗ Topaz Gigapixel AI를 찾을 수 없습니다.")
        return
    except Exception as e:
        print(f"✗ 연결 실패: {e}")
        return
    
    print()
    print("=" * 70)
    print("Export 다이얼로그가 열린 상태에서 실행하세요!")
    print("(Ctrl+S → Enter 후 이 스크립트 실행)")
    print("=" * 70)
    print()
    print("3초 후 모니터링 시작...")
    
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    print()
    print("=" * 70)
    print("실시간 모니터링 시작 (60초간 또는 Ctrl+C로 종료)")
    print("=" * 70)
    print()
    
    start_time = time.time()
    prev_title = ""
    prev_progress_texts = set()
    prev_status_texts = set()
    
    try:
        while time.time() - start_time < 60:
            elapsed = time.time() - start_time
            
            try:
                # 현재 활성 윈도우 (Export 다이얼로그 포함)
                try:
                    # Export/Save 다이얼로그가 열렸는지 확인
                    all_windows = app.windows()
                    for win in all_windows:
                        try:
                            title = win.window_text()
                            if title and title != prev_title:
                                print(f"[{elapsed:5.1f}s] 윈도우: {title}")
                                prev_title = title
                        except:
                            pass
                except:
                    pass
                
                # 모든 윈도우에서 상태 정보 수집
                for win in app.windows():
                    try:
                        # 프로그레스바 검색
                        progress_bars = win.descendants(control_type='ProgressBar')
                        for pb in progress_bars:
                            try:
                                # 프로그레스바 상세 정보 수집
                                details = []
                                
                                # 기본 정보
                                try:
                                    details.append(f"class={pb.class_name()}")
                                except:
                                    pass
                                
                                try:
                                    details.append(f"name={pb.window_text()}")
                                except:
                                    pass
                                
                                # 위치/크기
                                try:
                                    rect = pb.rectangle()
                                    details.append(f"rect=({rect.left},{rect.top},{rect.right},{rect.bottom})")
                                except:
                                    pass
                                
                                # 여러 방법으로 값 읽기 시도
                                try:
                                    legacy = pb.legacy_properties()
                                    for k, v in legacy.items():
                                        if v:
                                            details.append(f"legacy.{k}={v}")
                                except:
                                    pass
                                
                                try:
                                    val = pb.get_value()
                                    details.append(f"get_value={val}")
                                except:
                                    pass
                                
                                try:
                                    if hasattr(pb, 'iface_value'):
                                        val = pb.iface_value.CurrentValue
                                        details.append(f"iface_value={val}")
                                except:
                                    pass
                                
                                # 범위 값 (RangeValue 패턴)
                                try:
                                    if hasattr(pb, 'iface_range_value'):
                                        rv = pb.iface_range_value
                                        details.append(f"range_value={rv.CurrentValue}")
                                        details.append(f"range_min={rv.CurrentMinimum}")
                                        details.append(f"range_max={rv.CurrentMaximum}")
                                except:
                                    pass
                                
                                info_str = ", ".join(details) if details else "(정보없음)"
                                if info_str not in prev_progress_texts:
                                    print(f"[{elapsed:5.1f}s] 프로그레스바 발견:")
                                    print(f"         자동화ID: '{pb.automation_id()}'")
                                    for d in details:
                                        print(f"         {d}")
                                    prev_progress_texts.add(info_str)
                                        
                            except Exception as e:
                                print(f"[{elapsed:5.1f}s] 프로그레스바 오류: {e}")
                        
                        # 텍스트 요소에서 상태 검색
                        texts = win.descendants(control_type='Text')
                        keywords = ['processing', 'saving', 'export', 'done', 'complete', 
                                   'waiting', 'queue', '%', 'enhancing', 'progress']
                        
                        for text in texts:
                            try:
                                text_value = text.window_text()
                                if text_value:
                                    text_lower = text_value.lower()
                                    if any(kw in text_lower for kw in keywords):
                                        if text_value not in prev_status_texts:
                                            print(f"[{elapsed:5.1f}s] 상태 텍스트: '{text_value}'")
                                            print(f"         자동화ID: {text.automation_id()}")
                                            prev_status_texts.add(text_value)
                            except:
                                pass
                                
                    except:
                        pass
                
            except Exception as e:
                print(f"[{elapsed:5.1f}s] 오류: {e}")
            
            time.sleep(0.3)
            
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단됨")
    
    print()
    print("=" * 70)
    print("모니터링 완료")
    print("=" * 70)
    print()
    print("발견된 상태 정보:")
    print(f"  - 프로그레스 정보: {len(prev_progress_texts)}개")
    print(f"  - 상태 텍스트: {len(prev_status_texts)}개")
    
    if prev_status_texts:
        print()
        print("감지된 상태 텍스트 목록:")
        for t in sorted(prev_status_texts):
            print(f"  - {t}")
    
    # 화면 캡처 기반 감지 테스트
    print()
    print("=" * 70)
    print("화면 캡처 기반 감지 테스트")
    print("=" * 70)
    test_screen_capture()


def test_screen_capture():
    """화면 캡처 기반 상태 감지 테스트"""
    try:
        import pyautogui
        from PIL import Image
        import os
    except ImportError as e:
        print(f"필요한 라이브러리가 없습니다: {e}")
        return
    
    print()
    print("Queue 영역 (좌측 상단)을 캡처하여 분석합니다...")
    print()
    
    # 전체 화면 캡처
    screenshot = pyautogui.screenshot()
    width, height = screenshot.size
    
    print(f"화면 크기: {width}x{height}")
    
    # Queue 영역 추정 (좌측 상단 - 스크린샷 기준으로 조정 필요)
    # Export 다이얼로그의 Queue 영역은 대략 왼쪽 1/3, 상단 1/3 정도
    queue_region = (
        int(width * 0.05),   # left
        int(height * 0.1),   # top  
        int(width * 0.45),   # right
        int(height * 0.4)    # bottom
    )
    
    queue_crop = screenshot.crop(queue_region)
    
    # 저장
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, "queue_capture.png")
    queue_crop.save(output_path)
    print(f"Queue 영역 캡처 저장: {output_path}")
    print(f"Queue 영역: {queue_region}")
    print()
    print("이 이미지를 확인하여 Queue 영역이 올바르게 캡처되었는지 확인하세요.")
    print("'Done' 또는 'Processing' 텍스트가 보이면 이 영역을 모니터링할 수 있습니다.")
    print()
    
    # OCR 시도 (pytesseract가 있는 경우)
    try:
        import pytesseract
        print("OCR로 텍스트 추출 중...")
        text = pytesseract.image_to_string(queue_crop)
        print("추출된 텍스트:")
        print("-" * 40)
        print(text)
        print("-" * 40)
        
        # Done/Processing 키워드 검색
        text_lower = text.lower()
        if 'done' in text_lower:
            print("✓ 'Done' 감지됨!")
        if 'processing' in text_lower:
            print("✓ 'Processing' 감지됨!")
            
    except ImportError:
        print("pytesseract가 설치되지 않아 OCR을 건너뜁니다.")
        print("OCR 사용: pip install pytesseract")
        print("+ Tesseract OCR 설치 필요")
    except Exception as e:
        print(f"OCR 실패: {e}")


def monitor_with_screen():
    """화면 캡처 기반 실시간 모니터링"""
    try:
        import pyautogui
        from PIL import Image, ImageChops
        import numpy as np
    except ImportError as e:
        print(f"필요한 라이브러리가 없습니다: {e}")
        return
    
    print("=" * 70)
    print("화면 캡처 기반 실시간 모니터링 (30초)")
    print("=" * 70)
    print()
    print("Queue 영역의 변화를 감지합니다...")
    print("Export 다이얼로그가 열린 상태에서 Enter를 눌러 저장을 시작하세요.")
    print()
    
    # 전체 화면 크기 확인
    screenshot = pyautogui.screenshot()
    width, height = screenshot.size
    
    # Queue 영역 (조정 가능)
    queue_region = (
        int(width * 0.05),
        int(height * 0.1),
        int(width * 0.45),
        int(height * 0.35)
    )
    
    print(f"모니터링 영역: {queue_region}")
    print()
    
    start_time = time.time()
    prev_img = None
    change_count = 0
    stable_count = 0
    
    while time.time() - start_time < 30:
        elapsed = time.time() - start_time
        
        # Queue 영역 캡처
        screenshot = pyautogui.screenshot(region=queue_region)
        
        if prev_img is not None:
            # 이미지 변화 감지
            diff = ImageChops.difference(screenshot, prev_img)
            diff_sum = np.array(diff).sum()
            
            if diff_sum > 5000:  # 변화 감지 임계값
                print(f"[{elapsed:5.1f}s] 화면 변화 감지 (diff={diff_sum})")
                change_count += 1
                stable_count = 0
            else:
                stable_count += 1
                if stable_count == 5:  # 2.5초간 변화 없음
                    print(f"[{elapsed:5.1f}s] 화면 안정화됨 (처리 완료?)")
        
        prev_img = screenshot
        time.sleep(0.5)
    
    print()
    print(f"총 변화 감지 횟수: {change_count}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--screen':
        monitor_with_screen()
    else:
        monitor_save_processing()
