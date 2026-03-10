"""
LEGACY: CLI 기반 자동화 스크립트

이 파일은 기존 CLI 방식의 자동화 스크립트입니다.
새로운 GUI 앱을 사용하려면 apps/gigapixel_app/main.py를 실행하세요.

사용법 (레거시):
    python legacy/main_cli.py --mode upscale --input-dir "D:\\Images"
"""
import sys
import argparse
from pathlib import Path

# 프로젝트 루트를 path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from core.gigapixel import GigapixelController, GigapixelConfig
from core.common import setup_logger, RunHistory


def main():
    """메인 함수 (CLI 버전)"""
    
    parser = argparse.ArgumentParser(
        description='Topaz Automation CLI - 레거시 커맨드라인 도구',
        epilog='GUI 버전은 python -m apps.gigapixel_app.main 으로 실행하세요.'
    )
    parser.add_argument(
        '--mode', 
        type=str, 
        choices=['upscale'], 
        default='upscale',
        help='처리 모드: upscale (Gigapixel AI) [기본값: upscale]'
    )
    parser.add_argument(
        '--single',
        type=str,
        metavar='INPUT',
        help='단일 파일 처리: --single input.jpg'
    )
    parser.add_argument(
        '--input-dir',
        type=str,
        help='입력 디렉토리 (배치 처리 시)'
    )
    parser.add_argument(
        '--wait-time',
        type=int,
        help='초기 처리 대기 시간(초) - 기본값은 5초'
    )
    parser.add_argument(
        '--save-wait-time',
        type=int,
        help='저장 처리 대기 시간(초) - 기본값은 18초'
    )
    
    args = parser.parse_args()
    
    # 로거 설정
    config = GigapixelConfig
    setup_logger(config.LOG_DIR, config.LOG_LEVEL, 'gigapixel_cli')
    
    logger.info("=" * 60)
    logger.info("Topaz Automation CLI (Legacy)")
    logger.info("=" * 60)
    
    try:
        controller = GigapixelController()
        
        if args.wait_time:
            controller.config.PROCESSING_WAIT_TIME = args.wait_time
        
        if args.save_wait_time:
            controller.config.SAVE_PROCESSING_WAIT_TIME = args.save_wait_time
        
        # 앱 윈도우 확인
        if not controller.activate_app_window():
            logger.error("Topaz 앱을 찾을 수 없습니다.")
            return 1
        
        # 실행 기록 초기화
        run_history = RunHistory()
        run_history.set_config({
            "mode": args.mode,
            "wait_time": controller.config.PROCESSING_WAIT_TIME
        })
        
        # 단일 파일 처리
        if args.single:
            input_path = Path(args.single)
            if not input_path.exists():
                logger.error(f"파일을 찾을 수 없습니다: {input_path}")
                return 1
            
            success = controller.process_single_image_auto_save(input_path)
            return 0 if success else 1
        
        # 배치 처리
        input_dir = Path(args.input_dir) if args.input_dir else config.INPUT_DIR
        
        if not input_dir.exists():
            logger.error(f"입력 폴더를 찾을 수 없습니다: {input_dir}")
            return 1
        
        run_history.set_input_directory(str(input_dir))
        
        results = controller.process_batch_auto_save(
            input_dir,
            run_history=run_history
        )
        
        run_history.finalize()
        
        logger.info(f"성공: {results['success']}/{results['total']}")
        return 0 if results['failed'] == 0 else 1
    
    except KeyboardInterrupt:
        logger.warning("사용자에 의해 중단됨")
        return 1
    
    except Exception as e:
        logger.exception(f"예기치 않은 오류: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
