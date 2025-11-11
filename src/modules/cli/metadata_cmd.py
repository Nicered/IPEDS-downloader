"""
메타데이터 CLI 명령 모듈

이 모듈은 'metadata' CLI 명령을 구현합니다.
"""

import argparse
import json
import logging

from ..config.config_loader import load_default_config
from ..downloader.ipeds_downloader import IPEDSDownloader


logger = logging.getLogger(__name__)


def add_metadata_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """
    메타데이터 서브커맨드를 추가합니다.

    Args:
        subparsers: argparse 서브파서
    """
    parser = subparsers.add_parser(
        'metadata',
        help='메타데이터 및 통계 조회',
        description='다운로드 메타데이터 및 통계를 조회합니다.'
    )

    subcommands = parser.add_subparsers(dest='metadata_command', help='메타데이터 명령')

    # stats 서브커맨드
    stats_parser = subcommands.add_parser('stats', help='다운로드 통계 조회')
    stats_parser.set_defaults(metadata_func=show_statistics)

    # history 서브커맨드
    history_parser = subcommands.add_parser('history', help='다운로드 이력 조회')
    history_parser.add_argument(
        '--survey',
        type=str,
        metavar='SURVEY',
        help='특정 서베이로 필터링'
    )
    history_parser.add_argument(
        '--year',
        type=int,
        metavar='YEAR',
        help='특정 연도로 필터링'
    )
    history_parser.add_argument(
        '--status',
        type=str,
        choices=['COMPLETED', 'FAILED', 'SKIPPED'],
        help='특정 상태로 필터링'
    )
    history_parser.set_defaults(metadata_func=show_history)

    # files 서브커맨드
    files_parser = subcommands.add_parser('files', help='등록된 파일 목록 조회')
    files_parser.add_argument(
        '--year',
        type=int,
        metavar='YEAR',
        help='특정 연도로 필터링'
    )
    files_parser.add_argument(
        '--survey',
        type=str,
        metavar='SURVEY',
        help='특정 서베이로 필터링'
    )
    files_parser.set_defaults(metadata_func=show_files)

    # export 서브커맨드
    export_parser = subcommands.add_parser('export', help='메타데이터 내보내기')
    export_parser.add_argument(
        'output_file',
        type=str,
        help='출력 파일 경로'
    )
    export_parser.set_defaults(metadata_func=export_metadata)

    parser.add_argument(
        '--config',
        type=str,
        metavar='PATH',
        default='config',
        help='설정 파일 디렉토리 경로 (기본: config)'
    )

    parser.set_defaults(func=handle_metadata_command)


def handle_metadata_command(args: argparse.Namespace) -> int:
    """
    메타데이터 명령을 처리합니다.

    Args:
        args: 명령줄 인자

    Returns:
        int: 종료 코드
    """
    try:
        if not hasattr(args, 'metadata_func'):
            print("메타데이터 명령을 지정해주세요:")
            print("  stats    - 통계 조회")
            print("  history  - 다운로드 이력")
            print("  files    - 파일 목록")
            print("  export   - 메타데이터 내보내기")
            return 1

        # 설정 로드
        config = load_default_config(args.config)

        # 다운로더 초기화
        downloader = IPEDSDownloader(config)

        # 메타데이터 함수 실행
        result = args.metadata_func(args, downloader)

        # 다운로더 종료
        downloader.close()

        return result

    except Exception as e:
        logger.error(f"메타데이터 조회 중 오류 발생: {e}")
        print(f"\n오류: {e}")
        return 1


def show_statistics(args: argparse.Namespace, downloader: IPEDSDownloader) -> int:
    """
    다운로드 통계를 표시합니다.

    Args:
        args: 명령줄 인자
        downloader: IPEDS 다운로더

    Returns:
        int: 종료 코드
    """
    stats = downloader.get_statistics()

    print("\n" + "=" * 60)
    print("다운로드 통계")
    print("=" * 60)

    # 다운로드 통계
    download_stats = stats['download_statistics']
    print("\n[다운로드 현황]")
    print(f"  총 다운로드: {download_stats['total_downloads']}")
    print(f"  성공률: {download_stats['success_rate']:.1f}%")
    print(f"  총 데이터 크기: {download_stats['total_size_bytes']:,} bytes")

    print("\n[상태별 통계]")
    for status, count in download_stats['status_counts'].items():
        print(f"  {status}: {count}")

    # 연도 범위
    year_range = stats['year_range']
    print("\n[연도 범위]")
    print(f"  시작 연도: {year_range['start']}")
    print(f"  종료 연도: {year_range['end']}")
    print(f"  총 연도 수: {year_range['total_years']}")

    # 서베이 정보
    surveys_info = stats['surveys']
    print("\n[서베이 정보]")
    print(f"  서베이 개수: {surveys_info['count']}")
    print(f"  서베이 목록: {', '.join(surveys_info['list'])}")

    # 디스크 사용량
    disk_usage = stats['disk_usage']
    print("\n[디스크 사용량]")
    print(f"  원본 파일: {disk_usage['raw_dir_size_human']}")
    print(f"  압축 해제: {disk_usage['extracted_dir_size_human']}")
    print(f"  메타데이터: {disk_usage['metadata_dir_size_human']}")
    print(f"  총 사용량: {disk_usage['total_size_human']}")

    print("=" * 60 + "\n")

    return 0


def show_history(args: argparse.Namespace, downloader: IPEDSDownloader) -> int:
    """
    다운로드 이력을 표시합니다.

    Args:
        args: 명령줄 인자
        downloader: IPEDS 다운로더

    Returns:
        int: 종료 코드
    """
    history = downloader.metadata_manager.get_download_history(
        survey=args.survey,
        year=args.year,
        status=args.status
    )

    print("\n" + "=" * 60)
    print("다운로드 이력")
    print("=" * 60 + "\n")

    if not history:
        print("다운로드 이력이 없습니다.\n")
        return 0

    for entry in history:
        print(f"파일: {entry['file_name']}")
        print(f"  URL: {entry['url']}")
        print(f"  날짜: {entry['download_date']}")
        print(f"  상태: {entry['status']}")
        if entry.get('file_size'):
            print(f"  크기: {entry['file_size']:,} bytes")
        if entry.get('retry_count'):
            print(f"  재시도: {entry['retry_count']}회")
        if entry.get('error_message'):
            print(f"  오류: {entry['error_message']}")
        print()

    print(f"총 {len(history)}개 이력\n")

    return 0


def show_files(args: argparse.Namespace, downloader: IPEDSDownloader) -> int:
    """
    등록된 파일 목록을 표시합니다.

    Args:
        args: 명령줄 인자
        downloader: IPEDS 다운로더

    Returns:
        int: 종료 코드
    """
    if args.year:
        files = downloader.metadata_manager.get_files_by_year(args.year)
        title = f"{args.year}년 등록된 파일"
    elif args.survey:
        files = downloader.metadata_manager.get_files_by_survey(args.survey)
        title = f"{args.survey} 서베이 등록된 파일"
    else:
        all_files = downloader.metadata_manager.get_all_registered_files()
        files = list(all_files.values())
        title = "모든 등록된 파일"

    print("\n" + "=" * 60)
    print(title)
    print("=" * 60 + "\n")

    if not files:
        print("등록된 파일이 없습니다.\n")
        return 0

    for file_info in files:
        print(f"{file_info['survey']}{file_info['year']}")
        if 'file_size_human' in file_info:
            print(f"  크기: {file_info['file_size_human']}")
        if 'registered_at' in file_info:
            print(f"  등록일: {file_info['registered_at']}")
        print()

    print(f"총 {len(files)}개 파일\n")

    return 0


def export_metadata(args: argparse.Namespace, downloader: IPEDSDownloader) -> int:
    """
    메타데이터를 파일로 내보냅니다.

    Args:
        args: 명령줄 인자
        downloader: IPEDS 다운로더

    Returns:
        int: 종료 코드
    """
    output_file = args.output_file

    print(f"\n메타데이터를 내보냅니다: {output_file}\n")

    # 통계 수집
    stats = downloader.get_statistics()

    # JSON 파일로 저장
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)

        print(f"메타데이터 내보내기 완료: {output_file}\n")
        return 0

    except Exception as e:
        logger.error(f"메타데이터 내보내기 실패: {e}")
        print(f"오류: {e}\n")
        return 1
