"""
DEPRECATED: 이 모듈은 더 이상 사용되지 않습니다.

새로운 import 경로:
    from core.gigapixel import GigapixelController
    from core.common import BaseController
"""
import warnings
warnings.warn(
    "controllers 모듈은 deprecated입니다. core.gigapixel 또는 core.common을 사용하세요.",
    DeprecationWarning,
    stacklevel=2
)

# 하위 호환성을 위한 re-export
from core.common.base_controller import BaseController
from core.gigapixel.controller import GigapixelController

__all__ = ['BaseController', 'GigapixelController']
