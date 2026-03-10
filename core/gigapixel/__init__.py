"""
Topaz Gigapixel AI 자동화 핵심 로직

이 모듈은 Gigapixel AI 자동화의 비즈니스 로직을 담당합니다.
GUI와 분리되어 독립적으로 사용 가능합니다.
"""

from .controller import GigapixelController
from .config import GigapixelConfig

__all__ = ['GigapixelController', 'GigapixelConfig']
