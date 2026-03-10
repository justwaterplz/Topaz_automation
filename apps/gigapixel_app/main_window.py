"""
Topaz Gigapixel AI GUI - Main Window

메인 윈도우 UI 구성
"""
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog,
    QProgressBar, QTextEdit, QGroupBox, QSpinBox,
    QMessageBox, QStatusBar, QCheckBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

from core.gigapixel import GigapixelController, GigapixelConfig
from core.common import setup_logger, RunHistory


class WorkerThread(QThread):
    """백그라운드에서 자동화 작업 수행"""
    progress = Signal(int, int)  # current, total
    log_message = Signal(str)
    finished_signal = Signal(dict)  # results
    
    def __init__(self, input_dir: Path, output_dir: Path, wait_time: int, save_wait_time: int, smart_detect: bool = True, done_detect: bool = True):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.wait_time = wait_time
        self.save_wait_time = save_wait_time
        self.smart_detect = smart_detect
        self.done_detect = done_detect
        self._is_cancelled = False
    
    def run(self):
        """작업 실행"""
        try:
            controller = GigapixelController()
            
            # 설정 적용
            if self.wait_time:
                controller.config.PROCESSING_WAIT_TIME = self.wait_time
            if self.save_wait_time:
                controller.config.SAVE_PROCESSING_WAIT_TIME = self.save_wait_time
            
            # 스마트 감지 모드 설정
            controller.use_smart_detection = self.smart_detect
            self.log_message.emit(f"스마트 감지 모드: {'활성화' if self.smart_detect else '비활성화'}")
            
            # 앱 윈도우 확인
            self.log_message.emit("Topaz 앱 윈도우 확인 중...")
            if not controller.activate_app_window():
                self.log_message.emit("ERROR: Topaz 앱을 찾을 수 없습니다.")
                self.log_message.emit("Topaz Gigapixel AI를 먼저 실행해주세요.")
                self.finished_signal.emit({'success': 0, 'failed': 0, 'total': 0})
                return
            
            self.log_message.emit("Topaz 앱이 활성화되었습니다.")
            
            # 실행 기록 초기화
            run_history = RunHistory()
            run_history.set_config({
                "mode": "upscale",
                "wait_time": controller.config.PROCESSING_WAIT_TIME,
                "save_wait_time": controller.config.SAVE_PROCESSING_WAIT_TIME
            })
            run_history.set_input_directory(str(self.input_dir))
            
            # 배치 처리
            self.log_message.emit(f"입력 폴더: {self.input_dir}")
            self.log_message.emit(f"출력 폴더: {self.output_dir}")
            results = controller.process_batch_auto_save(
                self.input_dir,
                run_history=run_history
            )
            
            # 처리된 이미지를 output_dir로 이동
            if self.output_dir and results.get('success', 0) > 0:
                self.log_message.emit("")
                self.log_message.emit("=" * 50)
                self.log_message.emit("처리된 이미지 이동 중...")
                self.log_message.emit("=" * 50)
                moved_count = self.move_processed_images()
                self.log_message.emit(f"이동 완료: {moved_count}개 파일")
                results['moved'] = moved_count
            
            # 기록 저장
            history_file = run_history.finalize()
            self.log_message.emit(f"실행 기록: {history_file}")
            
            self.finished_signal.emit(results)
            
        except Exception as e:
            self.log_message.emit(f"ERROR: {str(e)}")
            self.finished_signal.emit({'success': 0, 'failed': 0, 'total': 0, 'error': str(e)})
    
    def move_processed_images(self) -> int:
        """처리된 이미지를 output_dir로 이동"""
        import shutil
        
        moved_count = 0
        
        # output_dir이 없으면 생성
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 처리된 이미지 식별용 suffix 목록 (config에서 가져옴)
        processed_suffixes = GigapixelConfig.PROCESSED_SUFFIXES
        
        # input_dir에서 처리된 이미지 찾기
        for file_path in self.input_dir.iterdir():
            if not file_path.is_file():
                continue
            
            # 이미지 파일인지 확인
            if file_path.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.webp']:
                continue
            
            # 처리된 이미지인지 확인 (suffix로 판별)
            filename_lower = file_path.stem.lower()
            is_processed = any(suffix.lower() in filename_lower for suffix in processed_suffixes)
            
            if is_processed:
                dest_path = self.output_dir / file_path.name
                
                # 중복 파일명 처리
                if dest_path.exists():
                    base_name = file_path.stem
                    ext = file_path.suffix
                    counter = 1
                    while dest_path.exists():
                        dest_path = self.output_dir / f"{base_name}_{counter}{ext}"
                        counter += 1
                
                try:
                    shutil.move(str(file_path), str(dest_path))
                    self.log_message.emit(f"  이동: {file_path.name} -> {dest_path.name}")
                    moved_count += 1
                except Exception as e:
                    self.log_message.emit(f"  이동 실패: {file_path.name} - {e}")
        
        return moved_count
    
    def cancel(self):
        """작업 취소"""
        self._is_cancelled = True


class MainWindow(QMainWindow):
    """메인 윈도우"""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.setup_ui()
        self.load_defaults()
    
    def setup_ui(self):
        """UI 구성"""
        self.setWindowTitle("Topaz Gigapixel Automation")
        self.setMinimumSize(600, 500)
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # === 폴더 설정 섹션 ===
        folder_group = QGroupBox("폴더 설정")
        folder_group_layout = QVBoxLayout(folder_group)
        
        # 입력 폴더 선택
        input_folder_layout = QHBoxLayout()
        input_folder_layout.addWidget(QLabel("입력 폴더:"))
        self.input_dir_edit = QLineEdit()
        self.input_dir_edit.setPlaceholderText("처리할 이미지가 있는 폴더를 선택하세요...")
        input_folder_layout.addWidget(self.input_dir_edit)
        self.browse_input_btn = QPushButton("찾아보기")
        self.browse_input_btn.clicked.connect(self.browse_input_folder)
        input_folder_layout.addWidget(self.browse_input_btn)
        folder_group_layout.addLayout(input_folder_layout)
        
        # 출력 폴더 선택
        output_folder_layout = QHBoxLayout()
        output_folder_layout.addWidget(QLabel("출력 폴더:"))
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setPlaceholderText("처리된 이미지를 저장할 폴더를 선택하세요...")
        output_folder_layout.addWidget(self.output_dir_edit)
        self.browse_output_btn = QPushButton("찾아보기")
        self.browse_output_btn.clicked.connect(self.browse_output_folder)
        output_folder_layout.addWidget(self.browse_output_btn)
        folder_group_layout.addLayout(output_folder_layout)
        
        main_layout.addWidget(folder_group)
        
        # === 설정 섹션 ===
        settings_group = QGroupBox("처리 설정")
        settings_layout = QVBoxLayout(settings_group)
        
        # 첫 번째 행: 대기 시간 설정
        time_layout = QHBoxLayout()
        
        # 최소 처리 대기 시간
        time_layout.addWidget(QLabel("최소 처리 대기(초):"))
        self.wait_time_spin = QSpinBox()
        self.wait_time_spin.setRange(3, 120)
        self.wait_time_spin.setValue(10)  # 기본값 10초로 증가
        self.wait_time_spin.setToolTip("이미지 로드 후 업스케일링이 시작되기까지 최소 대기 시간")
        time_layout.addWidget(self.wait_time_spin)
        
        time_layout.addSpacing(20)
        
        # 저장 처리 대기 시간
        time_layout.addWidget(QLabel("저장 대기(초):"))
        self.save_wait_spin = QSpinBox()
        self.save_wait_spin.setRange(5, 180)
        self.save_wait_spin.setValue(18)
        self.save_wait_spin.setToolTip("저장 버튼 클릭 후 파일이 저장되기까지 대기 시간")
        time_layout.addWidget(self.save_wait_spin)
        
        time_layout.addStretch()
        settings_layout.addLayout(time_layout)
        
        # 두 번째 행: 스마트 감지 옵션
        detect_layout = QHBoxLayout()
        
        self.smart_detect_check = QCheckBox("스마트 처리 완료 감지")
        self.smart_detect_check.setChecked(True)
        self.smart_detect_check.setToolTip(
            "체크 시: 화면 변화를 감지하여 처리 완료 여부를 자동으로 판단\n"
            "해제 시: 고정된 대기 시간만큼만 대기 (빠르지만 처리 중 저장될 수 있음)"
        )
        detect_layout.addWidget(self.smart_detect_check)
        
        self.done_detect_check = QCheckBox("저장 완료 감지 (Done)")
        self.done_detect_check.setChecked(True)
        self.done_detect_check.setToolTip(
            "체크 시: PrintScreen으로 'Done' 텍스트 감지 (클립보드 덮어쓰기됨)\n"
            "해제 시: 저장 대기 시간만큼 고정 대기 (클립보드 사용 안 함)"
        )
        detect_layout.addWidget(self.done_detect_check)
        
        detect_layout.addStretch()
        settings_layout.addLayout(detect_layout)
        
        main_layout.addWidget(settings_group)
        
        # === 컨트롤 버튼 ===
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("자동화 시작")
        self.start_btn.setObjectName("primaryButton")
        self.start_btn.clicked.connect(self.start_automation)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("중지")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_automation)
        control_layout.addWidget(self.stop_btn)
        
        main_layout.addLayout(control_layout)
        
        # === 진행률 ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v / %m")
        main_layout.addWidget(self.progress_bar)
        
        # === 로그 출력 ===
        log_group = QGroupBox("로그")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log_text)
        
        main_layout.addWidget(log_group)
        
        # === 상태바 ===
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("준비됨")
    
    def load_defaults(self):
        """기본값 로드 - 입/출력 폴더는 비워둠 (placeholder만 표시, 자동 지정 방지)"""
        self.input_dir_edit.clear()
        self.output_dir_edit.clear()
    
    def browse_input_folder(self):
        """입력 폴더 선택"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "입력 폴더 선택",
            self.input_dir_edit.text() or str(Path.home())
        )
        if folder:
            self.input_dir_edit.setText(folder)
    
    def browse_output_folder(self):
        """출력 폴더 선택"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "출력 폴더 선택",
            self.output_dir_edit.text() or str(Path.home())
        )
        if folder:
            self.output_dir_edit.setText(folder)
    
    def log(self, message: str):
        """로그 메시지 추가"""
        self.log_text.append(message)
        # 스크롤을 최하단으로
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def start_automation(self):
        """자동화 시작"""
        input_dir = self.input_dir_edit.text().strip()
        output_dir = self.output_dir_edit.text().strip()
        
        if not input_dir:
            QMessageBox.warning(self, "경고", "입력 폴더를 선택해주세요.")
            return
        
        input_path = Path(input_dir)
        if not input_path.exists():
            QMessageBox.warning(self, "경고", "입력 폴더가 존재하지 않습니다.")
            return
        
        if not output_dir:
            QMessageBox.warning(self, "경고", "출력 폴더를 선택해주세요.")
            return
        
        output_path = Path(output_dir)
        
        # Topaz 앱 실행 여부 확인 (프로세스로 확인)
        from core.common import WindowManager
        window_manager = WindowManager()
        
        # 프로세스가 실행 중인지 확인
        if not window_manager.is_process_running('Topaz Gigapixel AI.exe'):
            QMessageBox.warning(
                self, 
                "Topaz 앱 미실행",
                "Topaz Gigapixel AI가 실행 중이 아닙니다.\n\n"
                "자동화를 시작하기 전에 Topaz Gigapixel AI를 먼저 실행하고,\n"
                "원하는 설정(모델, 배율 등)을 적용해주세요."
            )
            return
        
        # UI 상태 변경
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.browse_input_btn.setEnabled(False)
        self.browse_output_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_text.clear()
        
        self.log("=" * 50)
        self.log("자동화 시작")
        self.log("=" * 50)
        self.log(f"입력 폴더: {input_dir}")
        self.log(f"출력 폴더: {output_dir}")
        self.log(f"최소 처리 대기: {self.wait_time_spin.value()}초")
        self.log(f"저장 대기 시간: {self.save_wait_spin.value()}초")
        self.log(f"스마트 감지: {'ON' if self.smart_detect_check.isChecked() else 'OFF'}")
        self.log("")
        
        self.status_bar.showMessage("처리 중...")
        
        # 워커 스레드 시작
        self.worker = WorkerThread(
            input_path,
            output_path,
            self.wait_time_spin.value(),
            self.save_wait_spin.value(),
            self.smart_detect_check.isChecked()
        )
        self.worker.log_message.connect(self.log)
        self.worker.finished_signal.connect(self.on_automation_finished)
        self.worker.start()
    
    def stop_automation(self):
        """자동화 중지"""
        if self.worker:
            self.worker.cancel()
            self.log("중지 요청됨...")
    
    def on_automation_finished(self, results: dict):
        """자동화 완료 처리"""
        # UI 상태 복원
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.browse_input_btn.setEnabled(True)
        self.browse_output_btn.setEnabled(True)
        
        # 결과 표시
        self.log("")
        self.log("=" * 50)
        self.log("모든 작업 완료")
        self.log("=" * 50)
        
        success = results.get('success', 0)
        failed = results.get('failed', 0)
        total = results.get('total', 0)
        moved = results.get('moved', 0)
        
        self.log(f"처리 성공: {success}/{total}")
        if failed > 0:
            self.log(f"처리 실패: {failed}")
        if moved > 0:
            self.log(f"파일 이동: {moved}개")
        
        if 'error' in results:
            self.log(f"오류: {results['error']}")
        
        self.progress_bar.setMaximum(total if total > 0 else 1)
        self.progress_bar.setValue(success)
        
        self.status_bar.showMessage(f"완료 - 처리: {success}/{total}, 이동: {moved}개")
        
        self.worker = None
