"""Topaz Photo AI controller"""
import time
from pathlib import Path
from loguru import logger
import pyautogui

from .base_controller import BaseController
from config.photoai_config import PhotoAIConfig
from utils.state_monitor import StateMonitor
from utils.ui_detector import UIDetector


class PhotoAIController(BaseController):
    """Topaz Photo AI 제어 클래스"""
    
    def __init__(self):
        super().__init__(PhotoAIConfig)
        self.state_monitor = StateMonitor()
        self.ui_detector = UIDetector(confidence=0.8)
        logger.info("PhotoAIController initialized")
    
    def force_activate_app(self) -> bool:
        """
        앱을 강제로 활성화 (여러 번 시도 + 마우스 클릭)
        
        Returns:
            성공 여부
        """
        logger.debug("Force activating Photo AI window...")
        
        # 디버깅: 현재 열린 윈도우 목록 확인
        try:
            import win32gui
            all_windows = self.window_manager.get_all_windows_with_title('Photo')
            if all_windows:
                logger.debug(f"Windows containing 'Photo': {all_windows}")
            else:
                logger.warning("No windows containing 'Photo' found!")
        except Exception as e:
            logger.debug(f"Debug window list failed: {e}")
        
        # 1. 윈도우 매니저로 활성화 시도
        for attempt in range(3):
            if self.activate_app_window():
                logger.debug(f"Window activated on attempt {attempt + 1}")
                break
            time.sleep(0.3)
        
        time.sleep(0.5)
        
        # 2. 앱 창을 찾아서 중앙 클릭
        hwnd = self.window_manager.find_window_by_title(self.config.WINDOW_TITLE_PATTERN)
        if hwnd:
            try:
                import win32gui
                # 창 좌표 가져오기
                rect = win32gui.GetWindowRect(hwnd)
                x = rect[0] + (rect[2] - rect[0]) // 2  # 중앙 X
                y = rect[1] + 100  # 상단에서 100px 아래 (타이틀바 아래)
                
                logger.debug(f"Clicking window at ({x}, {y})")
                pyautogui.click(x, y)
                time.sleep(0.3)
            except Exception as e:
                logger.warning(f"Failed to click window: {e}")
        
        # 3. 다시 한번 활성화
        self.activate_app_window()
        time.sleep(0.3)
        
        logger.info("  Photo AI window should now be focused")
        return True
    
    def click_relative_to_window(self, x_offset: int, y_offset: int) -> bool:
        """
        윈도우 기준 상대 좌표 클릭
        
        Args:
            x_offset: 윈도우 좌측에서의 X 오프셋 (양수)
            y_offset: 윈도우 상단에서의 Y 오프셋 (음수면 하단 기준)
        
        Returns:
            성공 여부
        """
        hwnd = self.window_manager.find_window_by_title(self.config.WINDOW_TITLE_PATTERN)
        if not hwnd:
            logger.error("Cannot find window for relative click")
            return False
        
        try:
            import win32gui
            rect = win32gui.GetWindowRect(hwnd)
            left, top, right, bottom = rect
            width = right - left
            height = bottom - top
            
            # 좌표 계산
            if x_offset >= 0:
                x = left + x_offset
            else:
                x = right + x_offset  # 음수면 우측 기준
            
            if y_offset >= 0:
                y = top + y_offset
            else:
                y = bottom + y_offset  # 음수면 하단 기준
            
            logger.debug(f"Clicking at ({x}, {y}) [window: {width}x{height}]")
            pyautogui.click(x, y)
            return True
            
        except Exception as e:
            logger.error(f"Failed to click relative to window: {e}")
            return False
    
    # BaseController의 abstract methods 구현
    def open_image(self, image_path: Path) -> bool:
        """
        단일 이미지 열기 (Photo AI는 다중 이미지 처리를 사용하므로 open_images 사용)
        
        Args:
            image_path: 열 이미지 파일 경로
        
        Returns:
            성공 여부
        """
        return self.open_images([image_path])
    
    def save_image(self, output_path: Path) -> bool:
        """
        단일 이미지 저장 (Photo AI는 export_images 사용)
        
        Args:
            output_path: 저장할 파일 경로
        
        Returns:
            성공 여부
        """
        logger.warning("save_image not used in Photo AI (use export_images instead)")
        return True
    
    def open_images(self, image_paths: list) -> bool:
        """
        이미지 열기 (다중 선택 가능)
        
        Args:
            image_paths: 열 이미지 파일 경로 리스트
        
        Returns:
            성공 여부
        """
        if not image_paths:
            logger.error("No images to open")
            return False
        
        logger.info(f"Opening {len(image_paths)} images...")
        
        # 앱 활성화
        if not self.activate_app_window():
            logger.error("Failed to activate application window")
            return False
        
        time.sleep(0.5)
        
        # Ctrl+O로 파일 열기 대화상자 열기
        logger.debug("Pressing Ctrl+O to open file dialog...")
        self.press_shortcut(self.config.SHORTCUT_OPEN, delay=2.0)
        
        # 파일 다이얼로그가 열렸는지 확인
        time.sleep(1.5)
        
        # 디렉토리 경로만 입력 (파일명은 입력하지 않음!)
        input_dir_path = str(image_paths[0].parent.absolute())
        logger.info(f"Navigating to directory: {input_dir_path}")
        
        # 파일명 필드 초기화
        logger.debug("Clearing file name field...")
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.3)
        
        # 디렉토리 경로 입력 (클립보드 사용)
        logger.debug("Entering directory path...")
        self.type_text(input_dir_path, use_clipboard=True)
        time.sleep(0.8)
        
        # Enter로 디렉토리로 이동
        logger.debug("Pressing Enter to navigate to directory...")
        pyautogui.press('enter')
        time.sleep(2.5)  # 디렉토리 로드 대기 (충분히 길게)
        
        # 파일 다이얼로그가 여전히 열려있는지 확인
        logger.debug("File dialog should now show all files in the directory")
        
        # 파일명 필드 비우기
        logger.debug("Clearing file name field...")
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('delete')
        time.sleep(0.3)
        
        # 핵심: Shift+Tab으로 파일 리스트로 포커스 이동!
        # Windows 파일 대화상자: 파일명 필드 -> Shift+Tab -> 파일 리스트
        logger.info("Moving focus to file list with Shift+Tab...")
        pyautogui.hotkey('shift', 'tab')
        time.sleep(0.5)
        
        # 파일 리스트에서 Ctrl+A로 모든 파일 선택
        logger.info("Selecting all files with Ctrl+A...")
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(1.0)
        
        logger.debug("All files should now be selected (highlighted in blue)")
        
        # Enter로 선택한 파일들 열기
        logger.info("Pressing Enter to open all selected files...")
        pyautogui.press('enter')
        
        # 이미지 로드 완료 대기
        load_wait_time = 3 + len(image_paths) * 0.5
        logger.debug(f"Waiting {load_wait_time:.1f}s for images to load...")
        time.sleep(load_wait_time)
        
        # 파일 로드 후 앱을 강제로 포커스!
        logger.info("Reactivating Photo AI window after file load...")
        self.force_activate_app()
        
        logger.info(f"  All files in directory should be loaded")
        logger.info("   Note: This method loads ALL files in the directory")
        logger.info("   Make sure only target images are in the directory!")
        
        return True
    
    def apply_autopilot(self, num_images: int) -> bool:
        """
        모든 이미지에 Autopilot 적용
        
        Args:
            num_images: 이미지 개수
        
        Returns:
            성공 여부
        """
        logger.info("Applying Autopilot to all images...")
        
        time.sleep(1.0)
        
        # Step 1: Ctrl+A로 모든 이미지 선택
        logger.info("Step 1: Pressing Ctrl+A to select all images...")
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(1.5)
        
        # Step 2: Apply Autopilot 버튼 클릭 (이미지 템플릿 매칭)
        logger.info("Step 2: Finding and clicking 'Apply Autopilot' button...")
        
        # 방법 1: 이미지 템플릿으로 버튼 찾기
        if self.ui_detector.click_button("apply_autopilot", wait_after=2.0):
            logger.info("    Button found via template matching")
        else:
            # 방법 2: 절대 좌표 사용 (폴백)
            btn_x = self.config.APPLY_AUTOPILOT_BUTTON_X
            btn_y = self.config.APPLY_AUTOPILOT_BUTTON_Y
            
            if btn_x and btn_y:
                logger.info(f"  Using fallback coordinates: ({btn_x}, {btn_y})")
                pyautogui.click(btn_x, btn_y)
                time.sleep(2.0)
            else:
                # 방법 3: 사용자에게 클릭 요청
                logger.warning("   버튼을 찾을 수 없습니다!")
                logger.warning("   5초 안에 'Apply Autopilot' 버튼을 수동으로 클릭하세요!")
                logger.warning("   또는 assets/photoai/apply_autopilot.png 템플릿을 추가하세요!")
                time.sleep(5.0)
        
        # Step 3: "적용" 버튼 클릭 (다이얼로그)
        logger.info("Step 3: Clicking '적용' button in dialog...")
        
        # 이미지 템플릿으로 "적용" 버튼 찾기
        time.sleep(1.0)
        if not self.ui_detector.click_button("apply_confirm", wait_after=1.0):
            # 폴백: Enter 키
            logger.info("  Using Enter key as fallback")
            pyautogui.press('enter')
        
        time.sleep(2.0)
        
        logger.info("  Autopilot applied to all images")
        return True
    
    def _is_processing_complete(self) -> bool:
        """
        이미지 처리가 완료되었는지 확인
        체크 아이콘(V)이 이미지 위에 나타나면 완료
        
        Returns:
            완료되었으면 True
        """
        # 완료 표시 체크 아이콘 확인
        if self.ui_detector.find_button("complete_check"):
            return True
        
        return False
    
    def _is_still_processing(self) -> bool:
        """
        이미지가 아직 처리 중인지 확인
        "Analyzing..." 등의 텍스트가 있으면 True
        
        Returns:
            처리 중이면 True
        """
        # 확인할 템플릿 목록 (하나라도 있으면 진행 중)
        processing_templates = [
            "analyzing_spinner",   # 로딩 스피너
            "analyzing_text",      # "Analyzing image..." 텍스트
        ]
        
        for template in processing_templates:
            if self.ui_detector.find_button(template):
                return True
        
        return False
    
    def process_each_image_sequentially(self, num_images: int) -> bool:
        """
        각 이미지를 순차적으로 클릭하며 필터 적용 대기
        
        Args:
            num_images: 처리할 이미지 개수
        
        Returns:
            성공 여부
        """
        logger.info("=" * 60)
        logger.info(f"  Processing each image sequentially ({num_images} images)")
        logger.info("=" * 60)
        
        # 앱 강제 활성화 (포커스 이탈 방지)
        self.force_activate_app()
        time.sleep(0.5)
        
        # 최대 대기 시간 (타임아웃)
        max_wait_time = 30  # 최대 30초
        check_interval = 2  # 2초마다 완료 체크
        
        for i in range(num_images):
            logger.info("")
            logger.info(f"  Image {i+1}/{num_images}")
            logger.info("-" * 60)
            
            # 이미지 이동 (오른쪽 방향키로 다음 이미지 선택)
            if i > 0:  # 첫 번째 이미지는 이미 선택되어 있음
                logger.info(f"  Moving to next image (Right arrow)...")
                pyautogui.press('right')
                time.sleep(1.0)  # 이미지 전환 대기
                
                # Zoom to Fit (Ctrl+0)
                logger.info(f"  Zoom to fit (Ctrl+0)...")
                pyautogui.hotkey('ctrl', '0')
                time.sleep(0.5)
            
            # 처리 완료 대기 (체크 아이콘이 나타날 때까지)
            logger.info(f"Waiting for processing to complete (max {max_wait_time}s)...")
            
            completed = False
            elapsed = 0
            
            # 처음 몇 초는 무조건 대기 (Analyzing 시작 대기)
            logger.info(f"  Waiting for analysis to start...")
            time.sleep(3)
            elapsed = 3
            
            while elapsed < max_wait_time:
                # 체크 아이콘(V)이 나타나면 완료!
                if self._is_processing_complete():
                    logger.info(f"    Check icon detected! Processing complete.")
                    
                    # 3초 대기 후 다시 확인 (더블 체크)
                    logger.info(f"  Waiting 3s to confirm completion...")
                    time.sleep(3)
                    elapsed += 3
                    
                    if self._is_processing_complete():
                        # 확인됨!
                        logger.info(f"    Confirmed! Image processing complete.")
                        completed = True
                        break
                
                # 10초마다 상태 로그
                if elapsed % 10 == 0:
                    remaining = max_wait_time - elapsed
                    # 현재 상태 표시
                    if self._is_still_processing():
                        logger.info(f"  Analyzing/Processing... ({remaining}s remaining)")
                    else:
                        logger.info(f"  Applying filters... ({remaining}s remaining)")
                
                time.sleep(check_interval)
                elapsed += check_interval
            
            if not completed:
                logger.warning(f"    Timeout! Moving to next image anyway...")
            
            logger.info(f"  Image {i+1}/{num_images} processed")
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("  All images processed sequentially")
        logger.info("=" * 60)
        
        return True
    
    def export_images(self, num_images: int) -> bool:
        """
        모든 이미지 Export
        
        Args:
            num_images: Export할 이미지 개수
        
        Returns:
            성공 여부
        """
        logger.info(f"Exporting {num_images} images...")
        
        # 앱 강제 활성화 (포커스 이탈 방지)
        self.force_activate_app()
        time.sleep(0.5)
        
        # Export 버튼 클릭 (이미지 템플릿 매칭)
        logger.info("Finding and clicking 'Export images' button...")
        
        # 방법 1: 이미지 템플릿으로 버튼 찾기
        if self.ui_detector.click_button("export_button", wait_after=2.0):
            logger.info("    Button found via template matching")
        else:
            # 방법 2: 절대 좌표 사용 (폴백)
            btn_x = self.config.EXPORT_BUTTON_X
            btn_y = self.config.EXPORT_BUTTON_Y
            
            if btn_x and btn_y:
                logger.info(f"  Using fallback coordinates: ({btn_x}, {btn_y})")
                pyautogui.click(btn_x, btn_y)
                time.sleep(2.0)
            else:
                # 방법 3: 사용자에게 클릭 요청
                logger.warning("   버튼을 찾을 수 없습니다!")
                logger.warning("   5초 안에 'Export images' 버튼을 수동으로 클릭하세요!")
                logger.warning("   또는 assets/photoai/export_button.png 템플릿을 추가하세요!")
                time.sleep(5.0)
        
        # Export 다이얼로그에서 Enter
        logger.info("Confirming export (Enter)...")
        pyautogui.press('enter')
        
        # Export 처리 대기
        logger.info("=" * 60)
        logger.info("  Waiting for export to complete...")
        logger.info("=" * 60)
        
        export_wait_time = self.config.EXPORT_PER_IMAGE_WAIT_TIME * num_images
        logger.info(f"Waiting {export_wait_time}s for {num_images} images...")
        
        for i in range(export_wait_time):
            remaining = export_wait_time - i
            if i % 5 == 0:
                logger.info(f"  Exporting... ({remaining}s remaining)")
            time.sleep(1)
        
        logger.info("=" * 60)
        logger.info("  Export complete")
        logger.info("=" * 60)
        
        return True
    
    def process_batch(self, input_dir: Path, run_history=None) -> dict:
        """
        배치 처리
        
        Args:
            input_dir: 입력 디렉토리
            run_history: RunHistory 객체 (실행 기록 저장용)
        
        Returns:
            처리 결과 딕셔너리
        """
        # 이미지 파일 목록
        logger.info("Scanning for images...")
        image_files = self.config.get_image_files(
            input_dir,
            exclude_suffixes=self.config.PROCESSED_SUFFIXES
        )
        
        if not image_files:
            logger.warning(f"No unprocessed images found in {input_dir}")
            return {'success': 0, 'failed': 0, 'total': 0}
        
        num_images = len(image_files)
        logger.info(f"Found {num_images} unprocessed images")
        logger.info("")
        logger.info("Image list:")
        for idx, img in enumerate(image_files, 1):
            logger.info(f"  {idx}. {img.name}")
        logger.info("")
        
        results = {'success': 0, 'failed': 0, 'total': num_images}
        
        try:
            import time as time_module
            start_time = time_module.time()
            
            # Step 1: Open images
            logger.info("=" * 60)
            logger.info("Step 1: Opening images")
            logger.info("=" * 60)
            if not self.open_images(image_files):
                logger.error("Failed to open images")
                results['failed'] = num_images
                return results
            
            # Step 2: Apply Autopilot
            logger.info("")
            logger.info("=" * 60)
            logger.info("Step 2: Applying Autopilot")
            logger.info("=" * 60)
            if not self.apply_autopilot(num_images):
                logger.error("Failed to apply Autopilot")
                results['failed'] = num_images
                return results
            
            # Step 3: Process each image sequentially
            logger.info("")
            logger.info("=" * 60)
            logger.info("Step 3: Processing each image")
            logger.info("=" * 60)
            if not self.process_each_image_sequentially(num_images):
                logger.error("Failed to process images")
                results['failed'] = num_images
                return results
            
            # Step 4: Export all images
            logger.info("")
            logger.info("=" * 60)
            logger.info("Step 4: Exporting images")
            logger.info("=" * 60)
            if not self.export_images(num_images):
                logger.error("Failed to export images")
                results['failed'] = num_images
                return results
            
            duration = time_module.time() - start_time
            
            # 모두 성공
            results['success'] = num_images
            logger.info("")
            logger.info("=" * 60)
            logger.info(f"  BATCH COMPLETE: {num_images} images (took {duration:.1f}s)")
            logger.info("=" * 60)
            
            # 실행 기록에 추가
            if run_history:
                for img_path in image_files:
                    run_history.add_image_result(
                        str(img_path),
                        success=True,
                        duration=duration / num_images
                    )
        
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            logger.exception("Full traceback:")
            results['failed'] = num_images
            
            if run_history:
                for img_path in image_files:
                    run_history.add_image_result(
                        str(img_path),
                        success=False,
                        error=str(e)
                    )
        
        return results

