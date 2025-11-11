#!/usr/bin/env python3
"""
IPEDS 다운로더 CLI 메인 스크립트

이 스크립트는 IPEDS 데이터 다운로더의 커맨드 라인 인터페이스를 제공합니다.

사용법:
    python scripts/ipeds_cli.py download --all
    python scripts/ipeds_cli.py download --year 2022
    python scripts/ipeds_cli.py verify
    python scripts/ipeds_cli.py extract
    python scripts/ipeds_cli.py metadata stats
    python scripts/ipeds_cli.py list surveys
"""

import argparse
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.modules.cli.download_cmd import add_download_subcommand
from src.modules.cli.verify_cmd import add_verify_subcommand
from src.modules.cli.extract_cmd import add_extract_subcommand
from src.modules.cli.metadata_cmd import add_metadata_subcommand
from src.modules.cli.list_cmd import add_list_subcommand


def create_parser() -> argparse.ArgumentParser:
    """
    CLI 파서를 생성합니다.

    Returns:
        argparse.ArgumentParser: 생성된 파서
    """
    parser = argparse.ArgumentParser(
        prog='ipeds_cli',
        description='IPEDS 데이터 다운로더 CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  # 모든 데이터 다운로드
  %(prog)s download --all

  # 특정 연도 다운로드
  %(prog)s download --year 2022

  # 특정 서베이 다운로드
  %(prog)s download --survey HD

  # 단일 파일 다운로드
  %(prog)s download --single HD 2022

  # 파일 검증
  %(prog)s verify

  # 압축 해제
  %(prog)s extract

  # 다운로드 통계
  %(prog)s metadata stats

  # 다운로드 이력
  %(prog)s metadata history

  # 서베이 목록
  %(prog)s list surveys

  # 연도 범위
  %(prog)s list years

더 많은 정보는 각 명령어에 --help 옵션을 사용하세요.
예: %(prog)s download --help
        """
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    # 서브커맨드 생성
    subparsers = parser.add_subparsers(
        dest='command',
        help='사용 가능한 명령',
        metavar='COMMAND'
    )

    # 각 CLI 명령 추가
    add_download_subcommand(subparsers)
    add_verify_subcommand(subparsers)
    add_extract_subcommand(subparsers)
    add_metadata_subcommand(subparsers)
    add_list_subcommand(subparsers)

    return parser


def main() -> int:
    """
    CLI 메인 함수입니다.

    Returns:
        int: 종료 코드
    """
    parser = create_parser()
    args = parser.parse_args()

    # 명령이 지정되지 않은 경우
    if not args.command:
        parser.print_help()
        return 1

    # 명령 실행
    if hasattr(args, 'func'):
        return args.func(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
