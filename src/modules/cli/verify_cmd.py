"""
검증 CLI 명령 모듈

이 모듈은 'verify' CLI 명령을 구현합니다.
"""

import argparse
import logging

from ..config.config_loader import load_default_config
from ..downloader.ipeds_downloader import IPEDSDownloader


logger = logging.getLogger(__name__)


def add_verify_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """
    검증 서브커맨드를 추가합니다.

    Args:
        subparsers: argparse 서브파서
    """
    parser = subparsers.add_parser(
        'verify',
        help='다운로드된 파일 검증',
        description='다운로드된 파일의 무결성을 검증합니다.'
    )

    parser.add_argument(
        '--config',
        type=str,
        metavar='PATH',
        default='config',
        help='설정 파일 디렉토리 경로 (기본: config)'
    )

    parser.set_defaults(func=handle_verify_command)


def handle_verify_command(args: argparse.Namespace) -> int:
    """
    검증 명령을 처리합니다.

    Args:
        args: 명령줄 인자

    Returns:
        int: 종료 코드 (0: 성공, 1: 실패)
    """
    try:
        # 설정 로드
        config = load_default_config(args.config)

        # 다운로더 초기화
        downloader = IPEDSDownloader(config)

        print("\n다운로드된 파일을 검증합니다...\n")

        # 검증 실행
        result = downloader.verify_all()

        # 결과 출력
        print("\n" + "=" * 60)
        print("검증 결과")
        print(f"  - 총 파일: {result['total']}")
        print(f"  - 검증 성공: {result['verified']}")
        print(f"  - 검증 실패: {result['failed']}")
        print("=" * 60 + "\n")

        if result['failed'] > 0:
            print("검증 실패한 파일:")
            for file_name in result['failed_files']:
                print(f"  - {file_name}")
            print()

        # 다운로더 종료
        downloader.close()

        return 0 if result['failed'] == 0 else 1

    except Exception as e:
        logger.error(f"검증 중 오류 발생: {e}")
        print(f"\n오류: {e}")
        return 1
