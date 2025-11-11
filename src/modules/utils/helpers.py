"""
헬퍼 함수 모듈

이 모듈은 프로젝트 전반에서 사용되는 공통 유틸리티 함수를 제공합니다.
"""

import hashlib
import os
from pathlib import Path
from typing import Optional, Union


def ensure_dir(directory: Union[str, Path]) -> Path:
    """
    디렉토리가 존재하지 않으면 생성합니다.

    Args:
        directory: 디렉토리 경로

    Returns:
        Path: 생성된 디렉토리 경로
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_file_size(file_path: Union[str, Path]) -> int:
    """
    파일 크기를 바이트 단위로 반환합니다.

    Args:
        file_path: 파일 경로

    Returns:
        int: 파일 크기 (바이트)

    Raises:
        FileNotFoundError: 파일이 존재하지 않는 경우
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
    return path.stat().st_size


def format_bytes(bytes_size: int) -> str:
    """
    바이트 크기를 사람이 읽기 쉬운 형식으로 변환합니다.

    Args:
        bytes_size: 바이트 크기

    Returns:
        str: 포맷된 크기 문자열 (예: "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def calculate_checksum(
    file_path: Union[str, Path],
    algorithm: str = 'sha256'
) -> str:
    """
    파일의 체크섬을 계산합니다.

    Args:
        file_path: 파일 경로
        algorithm: 해시 알고리즘 ('md5', 'sha1', 'sha256' 등)

    Returns:
        str: 체크섬 문자열

    Raises:
        FileNotFoundError: 파일이 존재하지 않는 경우
        ValueError: 지원하지 않는 알고리즘인 경우
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

    # 해시 객체 생성
    try:
        hash_obj = hashlib.new(algorithm)
    except ValueError:
        raise ValueError(f"지원하지 않는 해시 알고리즘: {algorithm}")

    # 파일을 청크 단위로 읽어서 해시 계산
    chunk_size = 8192
    with open(path, 'rb') as f:
        while chunk := f.read(chunk_size):
            hash_obj.update(chunk)

    return hash_obj.hexdigest()


def safe_filename(filename: str) -> str:
    """
    안전한 파일명으로 변환합니다.

    위험한 문자를 제거하거나 대체합니다.

    Args:
        filename: 원본 파일명

    Returns:
        str: 안전한 파일명
    """
    # 위험한 문자 제거 또는 대체
    unsafe_chars = '<>:"/\\|?*'
    safe_name = filename
    for char in unsafe_chars:
        safe_name = safe_name.replace(char, '_')
    return safe_name


def parse_filename(filename: str) -> dict:
    """
    IPEDS 파일명을 파싱하여 정보를 추출합니다.

    예: "HD2022.zip" -> {"survey": "HD", "year": 2022, "extension": "zip"}

    Args:
        filename: IPEDS 파일명

    Returns:
        dict: 파싱된 정보 (survey, year, extension 등)
    """
    # 확장자 분리
    name, extension = os.path.splitext(filename)
    extension = extension.lstrip('.')

    # 연도 추출 (마지막 4자리 숫자)
    year_str = None
    survey_code = name

    # 파일명 끝에서 연도 찾기
    for i in range(len(name) - 1, -1, -1):
        if name[i].isdigit():
            # 4자리 연속 숫자 찾기
            if i >= 3 and name[i-3:i+1].isdigit():
                year_str = name[i-3:i+1]
                survey_code = name[:i-3]
                break

    year = int(year_str) if year_str else None

    return {
        'survey': survey_code,
        'year': year,
        'extension': extension,
        'filename': filename
    }


def build_url(base_url: str, survey: str, year: int, extension: str = 'zip') -> str:
    """
    IPEDS 다운로드 URL을 생성합니다.

    Args:
        base_url: 기본 URL
        survey: 서베이 코드 (예: "HD", "IC")
        year: 연도 (예: 2022)
        extension: 파일 확장자 (기본: 'zip')

    Returns:
        str: 완전한 다운로드 URL
    """
    # 기본 URL 끝에 슬래시 확인
    if not base_url.endswith('/'):
        base_url += '/'

    # 파일명 생성
    filename = f"{survey}{year}.{extension}"

    return base_url + filename


def retry_on_exception(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    함수에 재시도 로직을 추가하는 데코레이터입니다.

    Args:
        max_attempts: 최대 시도 횟수
        delay: 초기 지연 시간 (초)
        backoff: 지연 시간 배율
        exceptions: 재시도할 예외 튜플

    Returns:
        function: 데코레이트된 함수
    """
    import time
    from functools import wraps

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        raise
                    time.sleep(current_delay)
                    current_delay *= backoff
            return None
        return wrapper
    return decorator
