"""Topaz Gigapixel AI controller"""
import time
from pathlib import Path
from loguru import logger
import pyautogui

from .base_controller import BaseController
from config.gigapixel_config import GigapixelConfig
from utils.state_monitor import StateMonitor


class GigapixelController(BaseController):
    
    def __init__(self):
        super().__init__(GigapixelConfig)
        self.state_monitor = StateMonitor()
        logger.info("GigapixelController initialized")
    
    def open_image(self, image_path: Path) -> bool:
        
        if not image_path.exists():
            logger.error(f"Image file not found: {image_path}")
            return False
        
        logger.info(f"Opening image: {image_path.name}")
        
        # 앱 활성화
        if not self.activate_app_window():
            logger.error("Failed to activate application window")
            return False
        
        time.sleep(0.5)
        
        # Ctrl+O로 파일 열기 대화상자 열기
        logger.debug("Pressing Ctrl+O to open file dialog...")
        self.press_shortcut(self.config.SHORTCUT_OPEN, delay=1.5)
        
        # 파일 다이얼로그가 열렸는지 확인 (선택사항이지만 권장)
        time.sleep(0.5)  # 다이얼로그 열릴 시간
        
        # 파일 경로 입력 (클립보드 사용으로 모든 문자 지원)
        absolute_path = str(image_path.absolute())
        logger.info(f"Opening file: {absolute_path}")
        
        # 파일명 필드 초기화 (여러 방법 시도)
        logger.debug("Clearing file path field...")
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.3)
        pyautogui.press('delete')
        time.sleep(0.2)
        
        # 경로 입력 (클립보드 사용)
        logger.debug("Typing path via clipboard...")
        self.type_text(absolute_path, use_clipboard=True)
        time.sleep(1)  # 경로 입력 완료 대기
        
        # Enter로 열기
        logger.debug("Pressing Enter to open...")
        pyautogui.press('enter')
        
        # 이미지 로드 완료 확인 (타이틀바에 파일명 표시됨)
        logger.debug(f"Waiting for image to load...")
        if self.state_monitor.verify_image_loaded(image_path.name, timeout=15):
            logger.info(f"Image loaded: {image_path.name}")
            return True
        else:
            logger.warning(f"Image load verification timeout (continuing anyway)")
            time.sleep(1)  # 추가 대기
            return True  # 타임아웃이어도 계속 진행
    
    def save_image(self, output_path: Path) -> bool:
        """
        이미지 저장 (경로 지정)
        
        Args:
            output_path: 저장할 파일 경로
        
        Returns:
            성공 여부
        """
        logger.info(f"Saving image to: {output_path.name}")
        
        # 앱 활성화
        if not self.activate_app_window():
            logger.error("Failed to activate application window")
            return False
        
        time.sleep(0.5)
        
        # Ctrl+S로 저장 대화상자 열기
        self.press_shortcut(self.config.SHORTCUT_SAVE, delay=1)
        
        # 파일 경로 입력 (클립보드 사용으로 모든 문자 지원)
        absolute_path = str(output_path.absolute())
        logger.debug(f"Typing save path: {absolute_path}")
        
        # 경로 입력
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        self.type_text(absolute_path, use_clipboard=True)
        time.sleep(0.5)
        
        # Enter로 저장
        pyautogui.press('enter')
        time.sleep(2)  # 저장 대기
        
        # 파일이 생성되었는지 확인
        if self.file_handler.wait_for_file(output_path, timeout=30):
            # 파일이 완전히 쓰여졌는지 확인
            if self.file_handler.is_file_ready(output_path):
                logger.info(f"Image saved successfully: {output_path.name}")
                return True
        
        logger.error(f"Failed to save image: {output_path.name}")
        return False
    
    def save_image_auto(self) -> bool:
        """
        이미지 자동 저장 (Ctrl+S + Enter + 대기 + Close Window)
        
        Returns:
            성공 여부
        """
        logger.info("Saving image (Ctrl+S)...")
        
        # 앱 활성화
        if not self.activate_app_window():
            logger.error("Failed to activate application window")
            return False
        
        time.sleep(0.5)
        
        # Ctrl+S로 저장 다이얼로그 열기
        logger.debug("Pressing Ctrl+S to open save dialog...")
        self.press_shortcut(self.config.SHORTCUT_SAVE, delay=2)
        
        # 저장 다이얼로그가 열렸는지 확인
        time.sleep(0.5)
        
        # Enter로 저장 확인
        logger.debug("Pressing Enter to confirm save...")
        pyautogui.press('enter')
        
        # Export Settings 창이 나타날 때까지 대기
        logger.debug("Waiting for Export Settings dialog to appear...")
        time.sleep(2.0)
        
        # ===== 저장 처리 대기 (고정 시간) =====
        logger.info("=" * 60)
        logger.info("Waiting for save processing to complete...")
        logger.info("=" * 60)
        
        # 고정 시간 대기 (config에서 설정)
        save_wait_time = self.config.SAVE_PROCESSING_WAIT_TIME
        
        logger.info(f"Waiting {save_wait_time} seconds for processing...")
        for i in range(save_wait_time):
            remaining = save_wait_time - i
            if i % 3 == 0:
                logger.info(f"  Processing... ({remaining}s remaining)")
            time.sleep(1)
        
        logger.info("Save wait complete")
        logger.info("=" * 60)
        
        # Export Settings 창 닫기
        logger.debug("Closing Export Settings window (Esc)...")
        time.sleep(1)  # 잠깐 대기
        pyautogui.press('esc')
        time.sleep(1)
        
        # 한 번 더 Esc 시도 (안전장치)
        pyautogui.press('esc')
        time.sleep(1)
        
        # 창이 닫혔는지 확인
        logger.debug("Verifying dialog closed...")
        current_title = self.state_monitor.get_active_window_title()
        logger.debug(f"Current window: {current_title}")
        
        if "Topaz Gigapixel" in current_title:
            logger.info("Image saved and dialog closed")
            return True
        else:
            logger.warning(f"Dialog may not be closed (title: {current_title})")
            # 추가 Esc 시도
            pyautogui.press('esc')
            time.sleep(1)
            return True  # 계속 진행
    
    def wait_for_processing(self) -> bool:
        """
        업스케일링 처리 완료 대기 (시간 기반)
        
        Returns:
            성공 여부
        """
        wait_time = self.config.PROCESSING_WAIT_TIME
        logger.info(f"Waiting {wait_time}s for processing to complete...")
        time.sleep(wait_time)
        logger.info(f"Processing wait complete")
        return True
    
    def process_single_image(self, input_path: Path, output_path: Path) -> bool:
        
        logger.info(f"Processing image: {input_path.name}")
        
        # 1. 이미지 열기
        if not self.open_image(input_path):
            return False
        
        # 2. 처리 대기
        if not self.wait_for_processing():
            return False
        
        # 3. 이미지 저장
        if not self.save_image(output_path):
            return False
        
        logger.info(f"Image processing completed: {input_path.name} -> {output_path.name}")
        return True
    
    def process_batch(self, input_dir: Path = None, output_dir: Path = None) -> dict:
        """
        배치 처리
        
        Args:
            input_dir: 입력 디렉토리 (None이면 config의 INPUT_DIR 사용)
            output_dir: 출력 디렉토리 (None이면 config의 OUTPUT_DIR 사용)
        
        Returns:
            처리 결과 딕셔너리 {'success': 성공 개수, 'failed': 실패 개수, 'total': 전체 개수}
        """
        input_dir = input_dir or self.config.INPUT_DIR
        output_dir = output_dir or self.config.OUTPUT_DIR
        
        # 디렉토리 확인
        self.config.ensure_directories()
        
        # 이미지 파일 목록
        image_files = self.config.get_image_files(input_dir)
        
        if not image_files:
            logger.warning(f"No images found in {input_dir}")
            return {'success': 0, 'failed': 0, 'total': 0}
        
        logger.info(f"Found {len(image_files)} images to process")
        
        results = {'success': 0, 'failed': 0, 'total': len(image_files)}
        
        for idx, input_path in enumerate(image_files, 1):
            logger.info(f"[{idx}/{len(image_files)}] Processing: {input_path.name}")
            
            # 출력 파일명 생성
            output_filename = f"{input_path.stem}_upscaled{input_path.suffix}"
            output_path = output_dir / output_filename
            
            # 중복 파일명 처리
            output_path = self.file_handler.get_unique_filename(
                output_dir, 
                f"{input_path.stem}_upscaled", 
                input_path.suffix
            )
            
            # 이미지 처리
            try:
                if self.process_single_image(input_path, output_path):
                    results['success'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                logger.error(f"Error processing {input_path.name}: {e}")
                results['failed'] += 1
        
        logger.info(f"Batch processing completed: {results['success']}/{results['total']} succeeded, {results['failed']} failed")
        return results
    
    def zoom_to_fit(self):
        """
        Zoom to fit (Ctrl+0) - 전체 이미지를 화면에 맞춤
        모든 이미지 처리 시 필요
        """
        logger.debug("Zoom to fit (Ctrl+0)")
        
        # 앱 윈도우 활성화
        if not self.activate_app_window():
            return False
        
        time.sleep(0.3)
        
        # Ctrl+0으로 Zoom to fit
        self.press_shortcut(self.config.SHORTCUT_ZOOM_TO_FIT, delay=0.5)
        
        logger.debug("Zoom to fit applied")
        return True
    
    def process_single_image_auto_save(self, input_path: Path) -> bool:
        """
        단일 이미지 처리 (자동 저장)
        
        Args:
            input_path: 입력 이미지 경로
        
        Returns:
            성공 여부
        """
        logger.info("="*60)
        logger.info(f"STARTING: {input_path.name}")
        logger.info("="*60)
        
        # 1. 이미지 열기 (절대 경로 사용)
        logger.info("Step 1: Opening image...")
        if not self.open_image(input_path):
            logger.error("Failed to open image")
            return False
        logger.info("Image opened")
        
        # 2. Zoom to fit (전체 이미지 화면에 맞춤)
        logger.info("Step 2: Zoom to fit...")
        time.sleep(1.5)  # 이미지가 완전히 로드될 때까지 대기
        self.zoom_to_fit()
        time.sleep(1)  # Zoom 적용 대기
        logger.info("Zoom applied")
        
        # 3. 처리 대기 (고정 시간 - 업스케일은 저장 시 처리됨)
        logger.info("Step 3: Waiting for initial processing...")
        if not self.wait_for_processing():
            logger.warning("Processing wait returned False")
            return False
        logger.info("Initial processing complete")
        
        # 4. 이미지 자동 저장 (고정 시간 대기)
        logger.info("Step 4: Saving image...")
        if not self.save_image_auto():
            logger.error("Failed to save image")
            return False
        logger.info("  Save complete")
        
        logger.info("="*60)
        logger.info(f"  COMPLETED: {input_path.name}")
        logger.info("="*60)
        logger.info("")  # 빈 줄
        
        return True
    
    def process_batch_auto_save(self, input_dir: Path, run_history=None) -> dict:
        """
        배치 처리 (자동 저장)
        
        Args:
            input_dir: 입력 디렉토리
            run_history: RunHistory 객체 (실행 기록 저장용)
        
        Returns:
            처리 결과 딕셔너리 {'success': 성공 개수, 'failed': 실패 개수, 'total': 전체 개수, 'skipped': 건너뛴 개수}
        """
        # 이미지 파일 목록 (처리된 파일 제외)
        logger.info("Scanning for images...")
        image_files = self.config.get_image_files(
            input_dir, 
            exclude_suffixes=self.config.PROCESSED_SUFFIXES
        )
        
        if not image_files:
            logger.warning(f"No unprocessed images found in {input_dir}")
            logger.info("(Already processed files are excluded)")
            return {'success': 0, 'failed': 0, 'total': 0, 'skipped': 0}
        
        logger.info(f"Found {len(image_files)} unprocessed images")
        logger.info(f"Save mode: Ctrl+S (output folder from settings)")
        logger.info("")
        logger.info("Image list:")
        for idx, img in enumerate(image_files, 1):
            logger.info(f"  {idx}. {img.name}")
        logger.info("")
        
        results = {'success': 0, 'failed': 0, 'total': len(image_files), 'skipped': 0}
        
        for idx, input_path in enumerate(image_files, 1):
            logger.info("")
            logger.info(f"╔{'═'*58}╗")
            logger.info(f"║ IMAGE {idx}/{len(image_files)}: {input_path.name:<45} ║")
            logger.info(f"║ Path: {str(input_path):<51} ║")
            logger.info(f"╚{'═'*58}╝")
            
            # 이미지 처리
            try:
                logger.info(f"  Starting processing of image #{idx}: {input_path.name}")
                
                import time as time_module
                start_time = time_module.time()
                
                success = self.process_single_image_auto_save(input_path)
                
                duration = time_module.time() - start_time
                
                if success:
                    results['success'] += 1
                    logger.info(f"")
                    logger.info(f"  IMAGE #{idx} SUCCESS (took {duration:.1f}s)")
                    logger.info(f"   Total progress: {results['success']}/{len(image_files)}")
                    logger.info(f"")
                    
                    # 실행 기록에 추가
                    if run_history:
                        run_history.add_image_result(
                            str(input_path),
                            success=True,
                            duration=duration
                        )
                else:
                    results['failed'] += 1
                    logger.error(f"")
                    logger.error(f"IMAGE #{idx} FAILED (took {duration:.1f}s)")
                    logger.error(f"   Total failed: {results['failed']}")
                    logger.error(f"")
                    
                    # 실행 기록에 추가
                    if run_history:
                        run_history.add_image_result(
                            str(input_path),
                            success=False,
                            duration=duration,
                            error="Processing failed"
                        )
            except Exception as e:
                logger.error(f"")
                logger.error(f"IMAGE #{idx} ERROR: {e}")
                logger.exception("Full traceback:")
                results['failed'] += 1
                logger.error(f"")
                
                # 실행 기록에 추가
                if run_history:
                    run_history.add_image_result(
                        str(input_path),
                        success=False,
                        error=str(e)
                    )
        
        return results

