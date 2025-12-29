"""Logging utility using loguru"""
import sys
from pathlib import Path
from loguru import logger
from datetime import datetime


def setup_logger(log_dir: Path, level: str = 'INFO', app_name: str = 'topaz_automation'):
    """
    로거 설정
    
    Args:
        log_dir: 로그 파일을 저장할 디렉토리
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR)
        app_name: 애플리케이션 이름 (로그 파일명에 사용)
    
    Returns:
        logger: 설정된 로거 객체
    """
    # 기존 핸들러 제거
    logger.remove()
    
    # 콘솔 출력 추가 (컬러 포맷)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True
    )
    
    # 파일 출력 추가
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{app_name}_{datetime.now().strftime('%Y%m%d')}.log"
    
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=level,
        rotation="10 MB",  # 10MB마다 새 파일 생성
        retention="30 days",  # 30일간 보관
        compression="zip"  # 압축
    )
    
    logger.info(f"Logger initialized - Level: {level}, Log file: {log_file}")
    
    return logger

