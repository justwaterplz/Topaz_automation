"""
DEPRECATED: 이 모듈은 더 이상 사용되지 않습니다.

새로운 import 경로:
    from core.common import WindowManager, StateMonitor, FileHandler, setup_logger, RunHistory
"""
import warnings
warnings.warn(
    "utils 모듈은 deprecated입니다. core.common을 사용하세요.",
    DeprecationWarning,
    stacklevel=2
)

# 하위 호환성을 위한 re-export
from core.common.window_manager import WindowManager
from core.common.state_monitor import StateMonitor
from core.common.file_handler import FileHandler
from core.common.logger import setup_logger
from core.common.run_history import RunHistory

__all__ = [
    'WindowManager',
    'StateMonitor', 
    'FileHandler',
    'setup_logger',
    'RunHistory',
]
