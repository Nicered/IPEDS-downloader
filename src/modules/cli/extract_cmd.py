"""
압축 해제 CLI 명령 모듈

이 모듈은 'extract' CLI 명령을 구현합니다.
"""

import argparse
import logging

from ..config.config_loader import load_default_config
from ..downloader.ipeds_downloader import IPEDSDownloader


logger = logging.getLogger(__name__)


def add_extract_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """
    압축 해제 서브커맨드를 추가합니다.

    Args:
        subparsers: argparse 서브파서
    """
    parser = subparsers.add_parser(
        'extract',
        help='ZIP 파일 압축 해제',
        description='다운로드된 ZIP 파일의 압축을 해제합니다.'
    )

    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='기존 파일 덮어쓰기'
    )

    parser.add_argument(
        '--year',
        type=int,
        metavar='YEAR',
        help='특정 연도의 파일만 압축 해제'
    )

    parser.add_argument(
        '--survey',
        type=str,
        metavar='SURVEY',
        help='특정 서베이의 파일만 압축 해제'
    )

    parser.add_argument(
        '--config',
        type=str,
        metavar='PATH',
        default='config',
        help='설정 파일 디렉토리 경로 (기본: config)'
    )

    parser.set_defaults(func=handle_extract_command)


def handle_extract_command(args: argparse.Namespace) -> int:
    """
    압축 해제 명령을 처리합니다.

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

        print("\nZIP 파일 압축을 해제합니다...\n")

        # 압축 해제 실행
        if args.year or args.survey:
            # 필터링된 압축 해제
            print("필터링된 압축 해제 기능은 아직 구현되지 않았습니다.")
            print("현재는 모든 파일의 압축을 해제합니다.\n")

        result = downloader.extract_all(overwrite=args.overwrite)

        # 결과 출력
        print("\n" + "=" * 60)
        print("압축 해제 결과")
        print(f"  - 총 파일: {result['total']}")
        print(f"  - 압축 해제 성공: {result['extracted']}")
        print(f"  - 압축 해제 실패: {result['failed']}")
        print("=" * 60 + "\n")

        if result['failed'] > 0:
            print("압축 해제 실패한 파일:")
            for file_name in result['failed_files']:
                print(f"  - {file_name}")
            print()

        # 다운로더 종료
        downloader.close()

        return 0 if result['failed'] == 0 else 1

    except Exception as e:
        logger.error(f"압축 해제 중 오류 발생: {e}")
        print(f"\n오류: {e}")
        return 1
