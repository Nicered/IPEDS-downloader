"""
연도 감지 모듈

이 모듈은 IPEDS에서 제공하는 최신 연도를 자동으로 감지하는 기능을 제공합니다.
"""

import logging
from datetime import datetime
from typing import Optional

import requests


logger = logging.getLogger(__name__)


def detect_latest_year(
    base_url: str,
    reference_survey: str = 'HD',
    timeout: int = 10,
    start_year: Optional[int] = None
) -> Optional[int]:
    """
    IPEDS에서 제공하는 최신 연도를 자동으로 감지합니다.

    현재 연도부터 시작하여 역순으로 HEAD 요청을 보내서
    파일이 존재하는 가장 최근 연도를 찾습니다.

    Args:
        base_url: IPEDS 기본 URL
        reference_survey: 참조할 서베이 코드 (기본: 'HD')
        timeout: HTTP 요청 타임아웃 (초)
        start_year: 검색 시작 연도 (None이면 현재 연도)

    Returns:
        int: 감지된 최신 연도, 실패 시 None
    """
    # 시작 연도 설정 (현재 연도 또는 지정된 연도)
    if start_year is None:
        start_year = datetime.now().year

    # 현재 연도부터 과거로 검색 (최대 5년)
    max_attempts = 5

    logger.info(f"최신 연도 감지 시작: 참조 서베이 = {reference_survey}")

    for year in range(start_year, start_year - max_attempts - 1, -1):
        try:
            # URL 생성
            if not base_url.endswith('/'):
                base_url += '/'
            url = f"{base_url}{reference_survey}{year}.zip"

            # HEAD 요청으로 파일 존재 확인
            logger.debug(f"연도 {year} 확인 중: {url}")
            response = requests.head(url, timeout=timeout, allow_redirects=True)

            if response.status_code == 200:
                logger.info(f"최신 연도 감지 성공: {year}")
                return year
            else:
                logger.debug(f"연도 {year} 없음 (HTTP {response.status_code})")

        except requests.exceptions.Timeout:
            logger.warning(f"연도 {year} 확인 중 타임아웃")
            continue
        except requests.exceptions.RequestException as e:
            logger.warning(f"연도 {year} 확인 중 오류: {e}")
            continue

    logger.error(f"최신 연도를 감지하지 못했습니다 (시도한 범위: {start_year-max_attempts} ~ {start_year})")
    return None


def validate_year_range(
    base_url: str,
    start_year: int,
    end_year: int,
    reference_survey: str = 'HD',
    timeout: int = 10
) -> list[int]:
    """
    지정된 연도 범위에서 실제로 사용 가능한 연도 목록을 반환합니다.

    Args:
        base_url: IPEDS 기본 URL
        start_year: 시작 연도
        end_year: 종료 연도
        reference_survey: 참조할 서베이 코드
        timeout: HTTP 요청 타임아웃 (초)

    Returns:
        list[int]: 사용 가능한 연도 목록
    """
    available_years = []

    logger.info(f"연도 범위 검증: {start_year} ~ {end_year}")

    for year in range(start_year, end_year + 1):
        try:
            # URL 생성
            if not base_url.endswith('/'):
                base_url += '/'
            url = f"{base_url}{reference_survey}{year}.zip"

            # HEAD 요청으로 파일 존재 확인
            response = requests.head(url, timeout=timeout, allow_redirects=True)

            if response.status_code == 200:
                available_years.append(year)
                logger.debug(f"연도 {year} 사용 가능")
            else:
                logger.debug(f"연도 {year} 사용 불가 (HTTP {response.status_code})")

        except requests.exceptions.RequestException as e:
            logger.warning(f"연도 {year} 확인 중 오류: {e}")
            continue

    logger.info(f"사용 가능한 연도 {len(available_years)}개 발견: {available_years}")
    return available_years


def get_year_range(
    base_url: str,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    reference_survey: str = 'HD',
    timeout: int = 10
) -> tuple[int, int]:
    """
    시작 연도와 종료 연도를 결정합니다.

    None인 경우 자동으로 감지하거나 기본값을 사용합니다.

    Args:
        base_url: IPEDS 기본 URL
        start_year: 시작 연도 (None이면 기본값 사용)
        end_year: 종료 연도 (None이면 자동 감지)
        reference_survey: 참조할 서베이 코드
        timeout: HTTP 요청 타임아웃 (초)

    Returns:
        tuple[int, int]: (시작 연도, 종료 연도)

    Raises:
        ValueError: 연도 범위를 결정할 수 없는 경우
    """
    # 시작 연도 처리
    if start_year is None:
        start_year = 2013  # 기본 시작 연도
        logger.info(f"시작 연도 미지정, 기본값 사용: {start_year}")

    # 종료 연도 처리
    if end_year is None:
        logger.info("종료 연도 미지정, 최신 연도 자동 감지")
        end_year = detect_latest_year(base_url, reference_survey, timeout)

        if end_year is None:
            # 감지 실패 시 현재 연도 사용
            end_year = datetime.now().year
            logger.warning(f"최신 연도 감지 실패, 현재 연도 사용: {end_year}")

    # 유효성 검증
    if start_year > end_year:
        raise ValueError(f"시작 연도({start_year})가 종료 연도({end_year})보다 큽니다")

    logger.info(f"연도 범위 결정: {start_year} ~ {end_year}")
    return start_year, end_year


def check_survey_availability(
    base_url: str,
    survey: str,
    year: int,
    timeout: int = 10
) -> bool:
    """
    특정 서베이와 연도의 데이터가 사용 가능한지 확인합니다.

    Args:
        base_url: IPEDS 기본 URL
        survey: 서베이 코드
        year: 연도
        timeout: HTTP 요청 타임아웃 (초)

    Returns:
        bool: 사용 가능하면 True
    """
    try:
        # URL 생성
        if not base_url.endswith('/'):
            base_url += '/'
        url = f"{base_url}{survey}{year}.zip"

        # HEAD 요청으로 파일 존재 확인
        response = requests.head(url, timeout=timeout, allow_redirects=True)

        return response.status_code == 200

    except requests.exceptions.RequestException as e:
        logger.debug(f"서베이 {survey} 연도 {year} 확인 중 오류: {e}")
        return False
