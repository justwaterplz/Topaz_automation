"""
DEPRECATED: 이 모듈은 더 이상 사용되지 않습니다.

새로운 import 경로:
    from core.gigapixel import GigapixelConfig
    from core.common import BaseConfig
"""
import warnings
warnings.warn(
    "config 모듈은 deprecated입니다. core.gigapixel 또는 core.common을 사용하세요.",
    DeprecationWarning,
    stacklevel=2
)

# 하위 호환성을 위한 re-export
from core.common.base_config import BaseConfig
from core.gigapixel.config import GigapixelConfig

__all__ = ['BaseConfig', 'GigapixelConfig']
