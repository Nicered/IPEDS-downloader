"""
목록 조회 CLI 명령 모듈

이 모듈은 'list' CLI 명령을 구현합니다.
"""

import argparse
import logging

from ..config.config_loader import load_default_config
from ..downloader.ipeds_downloader import IPEDSDownloader


logger = logging.getLogger(__name__)


def add_list_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """
    목록 조회 서브커맨드를 추가합니다.

    Args:
        subparsers: argparse 서브파서
    """
    parser = subparsers.add_parser(
        'list',
        help='서베이 및 연도 목록 조회',
        description='사용 가능한 서베이 및 연도 목록을 조회합니다.'
    )

    subcommands = parser.add_subparsers(dest='list_command', help='목록 조회 명령')

    # surveys 서브커맨드
    surveys_parser = subcommands.add_parser('surveys', help='서베이 목록 조회')
    surveys_parser.add_argument(
        '--priority',
        type=int,
        choices=[1, 2, 3],
        help='우선순위별 필터링'
    )
    surveys_parser.set_defaults(list_func=list_surveys)

    # years 서브커맨드
    years_parser = subcommands.add_parser('years', help='연도 범위 조회')
    years_parser.set_defaults(list_func=list_years)

    parser.add_argument(
        '--config',
        type=str,
        metavar='PATH',
        default='config',
        help='설정 파일 디렉토리 경로 (기본: config)'
    )

    parser.set_defaults(func=handle_list_command)


def handle_list_command(args: argparse.Namespace) -> int:
    """
    목록 조회 명령을 처리합니다.

    Args:
        args: 명령줄 인자

    Returns:
        int: 종료 코드
    """
    try:
        if not hasattr(args, 'list_func'):
            print("목록 조회 명령을 지정해주세요:")
            print("  surveys - 서베이 목록")
            print("  years   - 연도 범위")
            return 1

        # 설정 로드
        config = load_default_config(args.config)

        # 다운로더 초기화
        downloader = IPEDSDownloader(config)

        # 목록 조회 함수 실행
        result = args.list_func(args, downloader)

        # 다운로더 종료
        downloader.close()

        return result

    except Exception as e:
        logger.error(f"목록 조회 중 오류 발생: {e}")
        print(f"\n오류: {e}")
        return 1


def list_surveys(args: argparse.Namespace, downloader: IPEDSDownloader) -> int:
    """
    서베이 목록을 표시합니다.

    Args:
        args: 명령줄 인자
        downloader: IPEDS 다운로더

    Returns:
        int: 종료 코드
    """
    print("\n" + "=" * 60)
    print("IPEDS 서베이 목록")
    print("=" * 60 + "\n")

    if args.priority:
        # 우선순위별 필터링
        surveys = downloader.config.get_surveys_by_priority(args.priority)
        print(f"[우선순위 {args.priority}]\n")

        for survey in surveys:
            survey_info = downloader.config.get_survey_info(survey)
            if survey_info:
                print(f"{survey}: {survey_info.get('name', 'N/A')}")
                print(f"  설명: {survey_info.get('description', 'N/A')}")
                print(f"  카테고리: {survey_info.get('category', 'N/A')}")

                # 변형(variants) 표시
                variants = survey_info.get('variants')
                if variants:
                    print(f"  변형: {', '.join(variants)}")
                print()

    else:
        # 모든 서베이 표시
        all_surveys = downloader.config.get_all_survey_codes()

        # 우선순위별로 그룹화
        for priority in [1, 2, 3]:
            priority_surveys = downloader.config.get_surveys_by_priority(priority)

            if priority_surveys:
                print(f"[우선순위 {priority}]")

                for survey in priority_surveys:
                    survey_info = downloader.config.get_survey_info(survey)
                    if survey_info:
                        print(f"  {survey}: {survey_info.get('name', 'N/A')}")

                print()

    print(f"총 {len(downloader.surveys)}개 서베이\n")

    return 0


def list_years(args: argparse.Namespace, downloader: IPEDSDownloader) -> int:
    """
    연도 범위를 표시합니다.

    Args:
        args: 명령줄 인자
        downloader: IPEDS 다운로더

    Returns:
        int: 종료 코드
    """
    print("\n" + "=" * 60)
    print("다운로드 연도 범위")
    print("=" * 60 + "\n")

    print(f"시작 연도: {downloader.start_year}")
    print(f"종료 연도: {downloader.end_year}")
    print(f"총 연도 수: {downloader.end_year - downloader.start_year + 1}")

    print("\n연도 목록:")
    years = list(range(downloader.start_year, downloader.end_year + 1))

    # 10개씩 끊어서 표시
    for i in range(0, len(years), 10):
        year_chunk = years[i:i+10]
        print(f"  {', '.join(map(str, year_chunk))}")

    print()

    return 0
