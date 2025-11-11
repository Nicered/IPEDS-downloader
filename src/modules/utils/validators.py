"""
검증 유틸리티 모듈

이 모듈은 데이터 검증을 위한 함수를 제공합니다.
"""

import re
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """
    URL이 유효한지 검증합니다.

    Args:
        url: 검증할 URL

    Returns:
        bool: URL이 유효하면 True
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def is_valid_year(year: int, min_year: int = 1980, max_year: Optional[int] = None) -> bool:
    """
    연도가 유효한 범위 내에 있는지 검증합니다.

    Args:
        year: 검증할 연도
        min_year: 최소 연도
        max_year: 최대 연도 (None이면 현재 연도 + 1)

    Returns:
        bool: 연도가 유효하면 True
    """
    from datetime import datetime

    if max_year is None:
        max_year = datetime.now().year + 1

    return min_year <= year <= max_year


def is_valid_survey_code(survey_code: str, valid_surveys: Optional[list] = None) -> bool:
    """
    서베이 코드가 유효한지 검증합니다.

    Args:
        survey_code: 검증할 서베이 코드
        valid_surveys: 유효한 서베이 코드 리스트 (None이면 기본 리스트 사용)

    Returns:
        bool: 서베이 코드가 유효하면 True
    """
    if valid_surveys is None:
        # 기본 유효한 서베이 코드 (일부만 나열)
        valid_surveys = [
            'HD', 'IC', 'IC_AY', 'EF', 'EFA', 'EFB', 'EFC', 'EFD',
            'EFFY', 'F', 'F1A', 'F2', 'F3', 'GR', 'GR200', 'GR_L2',
            'SAL', 'SAL_A', 'SAL_NIS', 'S', 'ADM', 'SFA', 'AL',
            'C', 'C_A', 'C_B', 'OM'
        ]

    # 대소문자 구분 없이 검증
    return survey_code.upper() in [s.upper() for s in valid_surveys]


def is_valid_file_path(file_path: Union[str, Path]) -> bool:
    """
    파일 경로가 유효하고 파일이 존재하는지 검증합니다.

    Args:
        file_path: 검증할 파일 경로

    Returns:
        bool: 파일이 존재하면 True
    """
    try:
        path = Path(file_path)
        return path.exists() and path.is_file()
    except Exception:
        return False


def is_valid_directory(directory: Union[str, Path]) -> bool:
    """
    디렉토리 경로가 유효하고 디렉토리가 존재하는지 검증합니다.

    Args:
        directory: 검증할 디렉토리 경로

    Returns:
        bool: 디렉토리가 존재하면 True
    """
    try:
        path = Path(directory)
        return path.exists() and path.is_dir()
    except Exception:
        return False


def is_zip_file(file_path: Union[str, Path]) -> bool:
    """
    파일이 ZIP 파일인지 검증합니다.

    Args:
        file_path: 검증할 파일 경로

    Returns:
        bool: ZIP 파일이면 True
    """
    import zipfile

    try:
        path = Path(file_path)
        if not path.exists():
            return False
        return zipfile.is_zipfile(path)
    except Exception:
        return False


def validate_checksum(
    file_path: Union[str, Path],
    expected_checksum: str,
    algorithm: str = 'sha256'
) -> bool:
    """
    파일의 체크섬을 검증합니다.

    Args:
        file_path: 검증할 파일 경로
        expected_checksum: 예상 체크섬
        algorithm: 해시 알고리즘

    Returns:
        bool: 체크섬이 일치하면 True
    """
    from .helpers import calculate_checksum

    try:
        actual_checksum = calculate_checksum(file_path, algorithm)
        return actual_checksum.lower() == expected_checksum.lower()
    except Exception:
        return False


def is_valid_ipeds_filename(filename: str) -> bool:
    """
    IPEDS 파일명 형식이 유효한지 검증합니다.

    예상 형식: {SURVEY}{YEAR}.{EXT}
    예: HD2022.zip, IC2021_AY.zip

    Args:
        filename: 검증할 파일명

    Returns:
        bool: 파일명이 유효하면 True
    """
    # IPEDS 파일명 패턴: 서베이코드 + 4자리 연도 + 선택적 접미사 + 확장자
    pattern = r'^[A-Z_]+\d{4}[A-Z_]*\.(zip|csv|xlsx)$'
    return bool(re.match(pattern, filename, re.IGNORECASE))


def validate_config(config: dict) -> tuple[bool, Optional[str]]:
    """
    설정 딕셔너리가 유효한지 검증합니다.

    Args:
        config: 검증할 설정 딕셔너리

    Returns:
        tuple: (유효 여부, 에러 메시지)
    """
    # 필수 키 확인
    required_keys = ['ipeds', 'storage', 'download']

    for key in required_keys:
        if key not in config:
            return False, f"필수 설정 키 누락: {key}"

    # IPEDS 설정 검증
    ipeds_config = config.get('ipeds', {})
    if 'base_url' not in ipeds_config:
        return False, "IPEDS base_url 설정이 필요합니다"

    if not is_valid_url(ipeds_config['base_url']):
        return False, f"유효하지 않은 base_url: {ipeds_config['base_url']}"

    # 연도 범위 검증
    years_config = ipeds_config.get('years', {})
    start_year = years_config.get('start')
    end_year = years_config.get('end')

    if start_year and not is_valid_year(start_year):
        return False, f"유효하지 않은 시작 연도: {start_year}"

    if end_year and not is_valid_year(end_year):
        return False, f"유효하지 않은 종료 연도: {end_year}"

    if start_year and end_year and start_year > end_year:
        return False, f"시작 연도({start_year})가 종료 연도({end_year})보다 큽니다"

    # 스토리지 설정 검증
    storage_config = config.get('storage', {})
    required_storage_keys = ['raw_dir', 'extracted_dir', 'metadata_dir']

    for key in required_storage_keys:
        if key not in storage_config:
            return False, f"필수 스토리지 설정 누락: {key}"

    return True, None


def validate_metadata(metadata: dict) -> tuple[bool, Optional[str]]:
    """
    메타데이터 딕셔너리가 유효한지 검증합니다.

    Args:
        metadata: 검증할 메타데이터 딕셔너리

    Returns:
        tuple: (유효 여부, 에러 메시지)
    """
    # 필수 키 확인
    required_keys = ['file_name', 'url', 'download_date', 'status']

    for key in required_keys:
        if key not in metadata:
            return False, f"필수 메타데이터 키 누락: {key}"

    # 파일명 검증
    if not is_valid_ipeds_filename(metadata['file_name']):
        return False, f"유효하지 않은 파일명: {metadata['file_name']}"

    # URL 검증
    if not is_valid_url(metadata['url']):
        return False, f"유효하지 않은 URL: {metadata['url']}"

    # 상태 검증
    valid_statuses = ['PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'SKIPPED']
    if metadata['status'] not in valid_statuses:
        return False, f"유효하지 않은 상태: {metadata['status']}"

    return True, None
