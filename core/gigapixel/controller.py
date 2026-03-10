"""Topaz Gigapixel AI controller"""
import time
from pathlib import Path
from loguru import logger
import pyautogui

from core.common.base_controller import BaseController
from core.common.state_monitor import StateMonitor
from core.common.ui_automation import TopazUIAutomation, get_topaz_ui
from utils.ocr_monitor import wait_for_save_processing_complete
from .config import GigapixelConfig


class GigapixelController(BaseController):
    """Topaz Gigapixel AI 제어 클래스"""
    
    def __init__(self):
        super().__init__(GigapixelConfig)
        self.state_monitor = StateMonitor()
        self.ui_automation = get_topaz_ui()  # UI Automation 인스턴스
        self.use_smart_detection = True  # 스마트 처리 완료 감지 사용 여부
        logger.info("GigapixelController initialized")
    
    def open_image(self, image_path: Path) -> bool:
        """이미지 열기"""
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
        
        time.sleep(0.5)
        
        # 파일 경로 입력 (클립보드 사용으로 모든 문자 지원)
        absolute_path = str(image_path.absolute())
        logger.info(f"Opening file: {absolute_path}")
        
        # 파일명 필드 초기화
        logger.debug("Clearing file path field...")
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.3)
        pyautogui.press('delete')
        time.sleep(0.2)
        
        # 경로 입력 (클립보드 사용)
        logger.debug("Typing path via clipboard...")
        self.type_text(absolute_path, use_clipboard=True)
        time.sleep(1)
        
        # Enter로 열기
        logger.debug("Pressing Enter to open...")
        pyautogui.press('enter')
        
        # 다이얼로그 닫힘 + 이미지 로드 시작까지 짧은 고정 대기
        # (타이틀 검증은 건너뜀 - 화면 변화/타이틀 지연으로 오탐 가능)
        time.sleep(2.5)
        logger.info(f"Opening file: {image_path.name}")
        return True
    
    def save_image(self, output_path: Path) -> bool:
        """이미지 저장 (경로 지정)"""
        logger.info(f"Saving image to: {output_path.name}")
        
        if not self.activate_app_window():
            logger.error("Failed to activate application window")
            return False
        
        time.sleep(0.5)
        
        self.press_shortcut(self.config.SHORTCUT_SAVE, delay=1)
        
        absolute_path = str(output_path.absolute())
        logger.debug(f"Typing save path: {absolute_path}")
        
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        self.type_text(absolute_path, use_clipboard=True)
        time.sleep(0.5)
        
        pyautogui.press('enter')
        time.sleep(2)
        
        if self.file_handler.wait_for_file(output_path, timeout=30):
            if self.file_handler.is_file_ready(output_path):
                logger.info(f"Image saved successfully: {output_path.name}")
                return True
        
        logger.error(f"Failed to save image: {output_path.name}")
        return False
    
    def save_image_auto(self) -> bool:
        """이미지 자동 저장 (Ctrl+S + Enter + 대기 + Close Window)"""
        logger.info("Saving image (Ctrl+S)...")
        
        if not self.activate_app_window():
            logger.error("Failed to activate application window")
            return False
        
        time.sleep(0.5)
        
        logger.debug("Pressing Ctrl+S to open save dialog...")
        self.press_shortcut(self.config.SHORTCUT_SAVE, delay=2)
        
        time.sleep(0.5)
        
        logger.debug("Pressing Enter to confirm save...")
        pyautogui.press('enter')
        
        logger.debug("Waiting for Export Settings dialog to appear...")
        time.sleep(2.0)
        
        # 저장 처리 대기 (OCR로 Done 감지 또는 고정 시간)
        logger.info("=" * 60)
        logger.info("Waiting for save processing to complete...")
        logger.info("=" * 60)
        
        save_wait_time = self.config.SAVE_PROCESSING_WAIT_TIME
        use_done_detection = getattr(self.config, 'USE_DONE_DETECTION', True)
        
        # OCR로 Done 감지 (템플릿 매칭 대신 - 더 빠르고 해상도 독립적)
        if use_done_detection:
            use_window_relative = getattr(self.config, 'OCR_USE_WINDOW_RELATIVE', False)
            ratios = getattr(self.config, 'OCR_REGION_RATIOS', None)
            region = getattr(self.config, 'OCR_REGION_QUEUE', None)
            
            # 창 기준 상대 좌표 사용 시 region_provider 전달 (해상도/위치 무관)
            region_provider = None
            if use_window_relative and ratios and all(k in ratios for k in ('x', 'y', 'width', 'height')):
                def _get_region():
                    hwnd = self.window_manager.find_window_by_title(self.config.WINDOW_TITLE_PATTERN)
                    if hwnd:
                        return self.window_manager.get_relative_region(
                            hwnd, ratios['x'], ratios['y'], ratios['width'], ratios['height']
                        )
                    return None
                region_provider = _get_region
            
            done_found = wait_for_save_processing_complete(
                check_interval=1.5,
                timeout=120,
                initial_wait=5.0,
                region=region if not region_provider else None,
                region_provider=region_provider
            )
            if not done_found:
                logger.warning("Done not detected, using remaining fixed wait...")
                time.sleep(min(10, save_wait_time))
        else:
            logger.info(f"Done detection disabled, using fixed wait ({save_wait_time}s)...")
            for i in range(save_wait_time):
                remaining = save_wait_time - i
                if i % 3 == 0:
                    logger.info(f"  Processing... ({remaining}s remaining)")
                time.sleep(1)
        
        logger.info("Save wait complete")
        logger.info("=" * 60)
        
        # Export Settings 창 닫기
        logger.debug("Closing Export Settings window (Esc)...")
        time.sleep(1)
        pyautogui.press('esc')
        time.sleep(1)
        
        pyautogui.press('esc')
        time.sleep(1)
        
        logger.debug("Verifying dialog closed...")
        current_title = self.state_monitor.get_active_window_title()
        logger.debug(f"Current window: {current_title}")
        
        if "Topaz Gigapixel" in current_title:
            logger.info("Image saved and dialog closed")
            return True
        else:
            logger.warning(f"Dialog may not be closed (title: {current_title})")
            pyautogui.press('esc')
            time.sleep(1)
            return True
    
    def wait_for_processing(self) -> bool:
        """업스케일링 처리 완료 대기
        
        self.use_smart_detection이 True면 Preview Updated 템플릿 또는 UI Automation,
        False면 고정 시간 대기
        """
        min_wait = self.config.PROCESSING_WAIT_TIME  # 최소 대기 시간
        
        if self.use_smart_detection:
            logger.info("Waiting for processing (smart detection mode)...")
            logger.info(f"  Minimum wait: {min_wait}s")
            
            # 최소 대기 시간 (이미지가 로드되고 처리가 시작되기까지)
            time.sleep(min_wait)
            
            # 1순위: Preview Updated 템플릿 (오른쪽 위 UI - 업스케일링 완료 시 표시)
            preview_template = getattr(self.config, 'PREVIEW_UPDATED_TEMPLATE_PATH', None)
            use_preview = getattr(self.config, 'USE_PREVIEW_UPDATED_DETECTION', True)
            if use_preview and preview_template and preview_template.exists():
                logger.info("Using 'Preview Updated' template for processing detection...")
                result = self.state_monitor.wait_for_done_via_clipboard(
                    template_path=preview_template,
                    timeout=300,
                    check_interval=2.0,
                    min_wait=0,
                    confidence=0.6
                )
                if result:
                    logger.info("Processing complete (Preview Updated detected)")
                    return True
                logger.warning("Preview Updated not detected")
            
            # 2순위: UI Automation 사용
            if self.ui_automation.ensure_connected():
                logger.info("Using UI Automation for processing detection...")
                
                result = self.ui_automation.wait_for_processing_complete(
                    timeout=300,  # 최대 5분
                    check_interval=1.0,
                    stable_count=3  # 3회 연속 '완료' 상태면 완료
                )
                
                if result:
                    logger.info("Processing complete (UI Automation)")
                    return True
                else:
                    logger.warning("UI Automation detection timeout")
            
            # 2순위: 화면 변화 + 타이틀 모니터링 (fallback)
            logger.info("Falling back to screen-based detection...")
            max_timeout = 180  # 최대 3분
            result = self.state_monitor.wait_for_processing_complete(
                timeout=max_timeout,
                stable_time=3.0,
                check_interval=0.5
            )
            
            if result:
                logger.info("Processing detected as complete (screen-based)")
            else:
                logger.warning("Processing detection timeout, continuing anyway...")
            
            return True
        else:
            # 기존 방식: 고정 시간 대기
            logger.info(f"Waiting {min_wait}s for processing to complete (fixed mode)...")
            time.sleep(min_wait)
            logger.info("Processing wait complete")
            return True
    
    def zoom_to_fit(self):
        """Zoom to fit (Ctrl+0) - 전체 이미지를 화면에 맞춤"""
        logger.debug("Zoom to fit (Ctrl+0)")
        
        if not self.activate_app_window():
            return False
        
        time.sleep(0.3)
        
        self.press_shortcut(self.config.SHORTCUT_ZOOM_TO_FIT, delay=0.5)
        
        logger.debug("Zoom to fit applied")
        return True
    
    def process_single_image_auto_save(self, input_path: Path) -> bool:
        """단일 이미지 처리 (자동 저장)"""
        logger.info("="*60)
        logger.info(f"STARTING: {input_path.name}")
        logger.info("="*60)
        
        # 1. 이미지 열기
        logger.info("Step 1: Opening image...")
        if not self.open_image(input_path):
            logger.error("Failed to open image")
            return False
        logger.info("Image opened")
        
        # 2. Zoom to fit
        logger.info("Step 2: Zoom to fit (Ctrl+0)...")
        time.sleep(1)
        self.zoom_to_fit()
        time.sleep(0.5)
        logger.info("Zoom applied")
        
        # 3. 이미지 자동 저장 (업스케일링은 저장 과정에서 적용됨)
        logger.info("Step 3: Saving image (Ctrl+S)...")
        if not self.save_image_auto():
            logger.error("Failed to save image")
            return False
        logger.info("  Save complete")
        
        logger.info("="*60)
        logger.info(f"  COMPLETED: {input_path.name}")
        logger.info("="*60)
        logger.info("")
        
        return True
    
    def process_batch_auto_save(self, input_dir: Path, run_history=None) -> dict:
        """배치 처리 (자동 저장)"""
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
                
                if run_history:
                    run_history.add_image_result(
                        str(input_path),
                        success=False,
                        error=str(e)
                    )
        
        return results
