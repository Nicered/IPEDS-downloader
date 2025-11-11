"""
다운로드 CLI 명령 모듈

이 모듈은 'download' CLI 명령을 구현합니다.
"""

import argparse
import logging

from ..config.config_loader import load_default_config
from ..downloader.ipeds_downloader import IPEDSDownloader


logger = logging.getLogger(__name__)


def add_download_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """
    다운로드 서브커맨드를 추가합니다.

    Args:
        subparsers: argparse 서브파서
    """
    parser = subparsers.add_parser(
        'download',
        help='IPEDS 데이터 다운로드',
        description='IPEDS 데이터를 다운로드합니다.'
    )

    # 다운로드 옵션
    download_group = parser.add_mutually_exclusive_group()

    download_group.add_argument(
        '--all',
        action='store_true',
        help='모든 데이터 다운로드'
    )

    download_group.add_argument(
        '--year',
        type=int,
        metavar='YEAR',
        help='특정 연도의 모든 데이터 다운로드 (예: 2022)'
    )

    download_group.add_argument(
        '--survey',
        type=str,
        metavar='SURVEY',
        help='특정 서베이의 모든 연도 데이터 다운로드 (예: HD)'
    )

    download_group.add_argument(
        '--single',
        nargs=2,
        metavar=('SURVEY', 'YEAR'),
        help='단일 파일 다운로드 (예: --single HD 2022)'
    )

    # 추가 옵션
    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='진행률 표시 안 함'
    )

    parser.add_argument(
        '--config',
        type=str,
        metavar='PATH',
        default='config',
        help='설정 파일 디렉토리 경로 (기본: config)'
    )

    parser.set_defaults(func=handle_download_command)


def handle_download_command(args: argparse.Namespace) -> int:
    """
    다운로드 명령을 처리합니다.

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

        # 진행률 표시 여부
        show_progress = not args.no_progress

        # 다운로드 실행
        if args.all:
            print("\n모든 데이터를 다운로드합니다...\n")
            results = downloader.download_all(show_progress=show_progress)

        elif args.year:
            print(f"\n{args.year}년 데이터를 다운로드합니다...\n")
            results = downloader.download_by_year(args.year, show_progress=show_progress)

        elif args.survey:
            print(f"\n{args.survey} 서베이 데이터를 다운로드합니다...\n")
            results = downloader.download_by_survey(args.survey, show_progress=show_progress)

        elif args.single:
            survey, year = args.single
            year = int(year)
            print(f"\n{survey}{year} 파일을 다운로드합니다...\n")
            result = downloader.download_single(survey, year, show_progress=show_progress)
            results = [result]

        else:
            print("다운로드 옵션을 지정해주세요.")
            print("  --all: 모든 데이터")
            print("  --year YEAR: 특정 연도")
            print("  --survey SURVEY: 특정 서베이")
            print("  --single SURVEY YEAR: 단일 파일")
            return 1

        # 결과 출력
        completed = sum(1 for r in results if r.status == "COMPLETED")
        failed = sum(1 for r in results if r.status == "FAILED")
        skipped = sum(1 for r in results if r.status == "SKIPPED")

        print("\n" + "=" * 60)
        print("다운로드 완료")
        print(f"  - 성공: {completed}")
        print(f"  - 실패: {failed}")
        print(f"  - 건너뜀: {skipped}")
        print("=" * 60 + "\n")

        # 통계 출력
        stats = downloader.get_statistics()
        print("다운로드 통계:")
        print(f"  - 총 다운로드: {stats['download_statistics']['total_downloads']}")
        print(f"  - 성공률: {stats['download_statistics']['success_rate']:.1f}%")
        print(f"  - 디스크 사용량: {stats['disk_usage']['total_size_human']}")
        print()

        # 다운로더 종료
        downloader.close()

        return 0 if failed == 0 else 1

    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
        return 1

    except Exception as e:
        logger.error(f"다운로드 중 오류 발생: {e}")
        print(f"\n오류: {e}")
        return 1
