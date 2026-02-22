"""
Topaz Automation - Main Entry Point

Topaz Gigapixel AI 및 Topaz Photo AI를 자동화하는 스크립트

사용법:
    1. Topaz 앱을 실행하고 원하는 설정(모델, 배율 등)을 적용
    2. python main.py --input-dir "D:\Images"  # 폴더 내 모든 이미지 처리
    3. python main.py --single input.jpg       # 단일 파일 처리
"""

import sys
import argparse
from pathlib import Path
from loguru import logger

from config.gigapixel_config import GigapixelConfig
from config.photoai_config import PhotoAIConfig
from controllers.gigapixel_controller import GigapixelController
from controllers.photoai_controller import PhotoAIController
from utils.logger import setup_logger
from utils.run_history import RunHistory


def main():
    """메인 함수"""
    
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(
        description='Topaz Automation - 이미지를 순차적으로 열고 저장하는 자동화 도구',
        epilog='사용 전에 Topaz 앱을 실행하고 원하는 설정을 적용해두세요.'
    )
    parser.add_argument(
        '--mode', 
        type=str, 
        choices=['upscale', 'photoai'], 
        default='upscale',
        help='처리 모드: upscale (Gigapixel AI) 또는 photoai (Photo AI) [기본값: upscale]'
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
        help='입력 디렉토리 (배치 처리 시, 미지정 시 기본 폴더 사용)'
    )
    parser.add_argument(
        '--wait-time',
        type=int,
        help='초기 처리 대기 시간(초) - 기본값은 5초'
    )
    parser.add_argument(
        '--save-wait-time',
        type=int,
        help='저장 처리 대기 시간(초) - 기본값은 18초 (Gigapixel AI 전용)'
    )
    parser.add_argument(
        '--filter-wait-time',
        type=int,
        help='필터 적용 대기 시간(초) - 기본값은 15초 (Photo AI 전용)'
    )
    parser.add_argument(
        '--export-wait-time',
        type=int,
        help='이미지당 export 대기 시간(초) - 기본값은 10초 (Photo AI 전용)'
    )
    
    args = parser.parse_args()
    
    # 로거 설정
    if args.mode == 'upscale':
        config = GigapixelConfig
        setup_logger(config.LOG_DIR, config.LOG_LEVEL, 'gigapixel')
    elif args.mode == 'photoai':
        config = PhotoAIConfig
        setup_logger(config.LOG_DIR, config.LOG_LEVEL, 'photoai')
    else:
        logger.error(f"Unknown mode: {args.mode}")
        return 1
    
    logger.info("=" * 60)
    logger.info(f"Topaz Automation Started - Mode: {args.mode}")
    logger.info("=" * 60)
    logger.info("Topaz 앱이 실행 중이고 원하는 설정이 적용되어 있는지 확인하세요!")
    logger.info("")
    
    try:
        if args.mode == 'upscale':
            controller = GigapixelController()
            
            # 대기 시간 설정
            if args.wait_time:
                controller.config.PROCESSING_WAIT_TIME = args.wait_time
            
            if args.save_wait_time:
                controller.config.SAVE_PROCESSING_WAIT_TIME = args.save_wait_time
            
            logger.info(f"초기 처리 대기 시간: {controller.config.PROCESSING_WAIT_TIME}초")
            logger.info(f"저장 처리 대기 시간: {controller.config.SAVE_PROCESSING_WAIT_TIME}초")
            logger.info("저장 방식: Ctrl+S (Topaz 설정의 output 폴더)")
            
            # 실행 기록 초기화
            run_history = RunHistory()
            run_history.set_config({
                "mode": args.mode,
                "wait_time": controller.config.PROCESSING_WAIT_TIME
            })
            
            # 앱 윈도우 확인 (자동 실행 안 함)
            logger.info("Topaz 앱 윈도우 확인 중...")
            if not controller.activate_app_window():
                logger.error("Topaz 앱을 찾을 수 없습니다.")
                logger.error("Topaz Gigapixel AI를 먼저 실행해주세요.")
                return 1
            
            logger.info("Topaz 앱이 활성화되었습니다.")
            logger.info("")
            
            # 단일 파일 처리 모드
            if args.single:
                input_path = Path(args.single)
                
                if not input_path.exists():
                    logger.error(f"파일을 찾을 수 없습니다: {input_path}")
                    return 1
                
                logger.info(f"단일 파일 처리: {input_path.name}")
                success = controller.process_single_image_auto_save(input_path)
                
                if success:
                    logger.info("처리 완료!")
                    return 0
                else:
                    logger.error("처리 실패")
                    return 1
            
            # 배치 처리 모드
            else:
                input_dir = Path(args.input_dir) if args.input_dir else config.INPUT_DIR
                
                if not input_dir.exists():
                    logger.error(f"입력 폴더를 찾을 수 없습니다: {input_dir}")
                    return 1
                
                logger.info(f"배치 처리 모드: {input_dir}")
                logger.info("")
                
                run_history.set_input_directory(str(input_dir))
                
                results = controller.process_batch_auto_save(
                    input_dir,
                    run_history=run_history
                )
                
                # 실행 기록 저장
                history_file = run_history.finalize()
                
                logger.info("")
                logger.info("=" * 60)
                logger.info(f"성공: {results['success']}/{results['total']}")
                if results['failed'] > 0:
                    logger.warning(f"실패: {results['failed']}")
                logger.info(f"실행 기록: {history_file}")
                logger.info("=" * 60)
                
                return 0 if results['failed'] == 0 else 1
        
        elif args.mode == 'photoai':
            controller = PhotoAIController()
            
            # 대기 시간 설정
            if args.filter_wait_time:
                controller.config.FILTER_APPLY_WAIT_TIME = args.filter_wait_time
            
            if args.export_wait_time:
                controller.config.EXPORT_PER_IMAGE_WAIT_TIME = args.export_wait_time
            
            logger.info(f"필터 적용 대기 시간: {controller.config.FILTER_APPLY_WAIT_TIME}초")
            logger.info(f"이미지당 Export 대기 시간: {controller.config.EXPORT_PER_IMAGE_WAIT_TIME}초")
            logger.info("처리 방식: Autopilot (각 이미지 순차 처리)")
            
            # 실행 기록 초기화
            run_history = RunHistory()
            run_history.set_config({
                "mode": args.mode,
                "filter_wait_time": controller.config.FILTER_APPLY_WAIT_TIME,
                "export_wait_time": controller.config.EXPORT_PER_IMAGE_WAIT_TIME
            })
            
            # 앱 윈도우 확인
            logger.info("Topaz Photo AI 앱 윈도우 확인 중...")
            if not controller.activate_app_window():
                logger.error("Topaz Photo AI 앱을 찾을 수 없습니다.")
                logger.error("Topaz Photo AI를 먼저 실행해주세요.")
                return 1
            
            logger.info("Topaz Photo AI 앱이 활성화되었습니다.")
            logger.info("")
            
            # 배치 처리만 지원 (다중 이미지 처리)
            input_dir = Path(args.input_dir) if args.input_dir else config.INPUT_DIR
            
            if not input_dir.exists():
                logger.error(f"입력 폴더를 찾을 수 없습니다: {input_dir}")
                return 1
            
            logger.info(f"배치 처리 모드: {input_dir}")
            logger.info("")
            
            run_history.set_input_directory(str(input_dir))
            
            results = controller.process_batch(
                input_dir,
                run_history=run_history
            )
            
            # 실행 기록 저장
            history_file = run_history.finalize()
            
            logger.info("")
            logger.info("=" * 60)
            logger.info(f"성공: {results['success']}/{results['total']}")
            if results['failed'] > 0:
                logger.warning(f"실패: {results['failed']}")
            logger.info(f"실행 기록: {history_file}")
            logger.info("=" * 60)
            
            return 0 if results['failed'] == 0 else 1
        
        else:
            logger.error(f"Mode '{args.mode}' is not implemented yet")
            return 1
    
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        return 1
    
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

