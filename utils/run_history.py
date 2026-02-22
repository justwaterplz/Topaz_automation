"""실행 기록 저장 유틸리티"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from loguru import logger


class RunHistory:
    """실행 기록을 JSON으로 저장하는 클래스"""
    
    def __init__(self, history_dir: Path = None):
        """
        Args:
            history_dir: 기록을 저장할 디렉토리
        """
        if history_dir is None:
            history_dir = Path("logs/run_history")
        
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
        # 실행 정보 저장
        self.run_data = {
            "run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration_seconds": None,
            "config": {},
            "input_directory": None,
            "total_images": 0,
            "processed_images": [],
            "summary": {
                "success": 0,
                "failed": 0,
                "skipped": 0
            }
        }
        
        self.start_time = datetime.now()
    
    def set_config(self, config: Dict[str, Any]):
        """실행 설정 저장"""
        self.run_data["config"] = config
    
    def set_input_directory(self, input_dir: str):
        """입력 디렉토리 저장"""
        self.run_data["input_directory"] = str(input_dir)
    
    def set_total_images(self, total: int):
        """전체 이미지 개수 저장"""
        self.run_data["total_images"] = total
    
    def add_image_result(
        self, 
        image_path: str, 
        success: bool, 
        duration: float = None,
        error: str = None
    ):
        """
        이미지 처리 결과 추가
        
        Args:
            image_path: 이미지 파일 경로
            success: 성공 여부
            duration: 처리 시간 (초)
            error: 에러 메시지 (실패 시)
        """
        result = {
            "image_path": str(image_path),
            "image_name": Path(image_path).name,
            "success": success,
            "duration_seconds": duration,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        
        self.run_data["processed_images"].append(result)
        
        # 요약 업데이트
        if success:
            self.run_data["summary"]["success"] += 1
        else:
            self.run_data["summary"]["failed"] += 1
    
    def finalize(self):
        """실행 종료 - 시간 계산 및 저장"""
        end_time = datetime.now()
        self.run_data["end_time"] = end_time.isoformat()
        self.run_data["duration_seconds"] = (end_time - self.start_time).total_seconds()
        
        # JSON 파일로 저장
        filename = f"run_{self.run_data['run_id']}.json"
        filepath = self.history_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.run_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"  Run history saved: {filepath}")
        
        return filepath
    
    def get_summary(self) -> Dict:
        """현재 요약 정보 반환"""
        return self.run_data["summary"].copy()


def load_run_history(run_id: str, history_dir: Path = None) -> Dict:
    """
    이전 실행 기록 로드
    
    Args:
        run_id: 실행 ID (YYYYMMDD_HHMMSS)
        history_dir: 기록 디렉토리
    
    Returns:
        실행 기록 딕셔너리
    """
    if history_dir is None:
        history_dir = Path("logs/run_history")
    
    filename = f"run_{run_id}.json"
    filepath = history_dir / filename
    
    if not filepath.exists():
        raise FileNotFoundError(f"Run history not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def list_run_histories(history_dir: Path = None, limit: int = 10) -> List[Dict]:
    """
    최근 실행 기록 목록 반환
    
    Args:
        history_dir: 기록 디렉토리
        limit: 반환할 최대 개수
    
    Returns:
        실행 기록 목록 (최신순)
    """
    if history_dir is None:
        history_dir = Path("logs/run_history")
    
    if not history_dir.exists():
        return []
    
    # JSON 파일 찾기
    json_files = sorted(
        history_dir.glob("run_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    histories = []
    for filepath in json_files[:limit]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 요약 정보만 추출
                summary = {
                    "run_id": data.get("run_id"),
                    "start_time": data.get("start_time"),
                    "duration_seconds": data.get("duration_seconds"),
                    "total_images": data.get("total_images"),
                    "success": data.get("summary", {}).get("success", 0),
                    "failed": data.get("summary", {}).get("failed", 0),
                    "filepath": str(filepath)
                }
                histories.append(summary)
        except Exception as e:
            logger.warning(f"Failed to load {filepath}: {e}")
    
    return histories

