"""
IPEDS HTTP 클라이언트 모듈

이 모듈은 IPEDS 웹사이트와의 HTTP 통신을 담당합니다.
"""

import logging
import time
from pathlib import Path
from typing import Optional, Callable

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tqdm import tqdm


logger = logging.getLogger(__name__)


class IPEDSClient:
    """
    IPEDS 데이터 다운로드를 위한 HTTP 클라이언트입니다.
    """

    def __init__(
        self,
        base_url: str,
        user_agent: Optional[str] = None,
        timeout: tuple = (10, 300),
        max_retries: int = 3,
        backoff_factor: float = 2.0
    ):
        """
        IPEDSClient를 초기화합니다.

        Args:
            base_url: IPEDS 기본 URL
            user_agent: User-Agent 헤더
            timeout: (연결 타임아웃, 읽기 타임아웃) 튜플
            max_retries: 최대 재시도 횟수
            backoff_factor: 재시도 간격 배율
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

        # 세션 설정
        self.session = self._create_session(user_agent)

        logger.info(f"IPEDS 클라이언트 초기화: {self.base_url}")

    def _create_session(self, user_agent: Optional[str]) -> requests.Session:
        """
        HTTP 세션을 생성하고 설정합니다.

        Args:
            user_agent: User-Agent 헤더

        Returns:
            requests.Session: 설정된 세션
        """
        session = requests.Session()

        # User-Agent 설정
        if user_agent:
            session.headers.update({'User-Agent': user_agent})

        # 재시도 전략 설정
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def build_url(self, survey: str, year: int, extension: str = 'zip') -> str:
        """
        다운로드 URL을 생성합니다.

        Args:
            survey: 서베이 코드
            year: 연도
            extension: 파일 확장자

        Returns:
            str: 완전한 다운로드 URL
        """
        filename = f"{survey}{year}.{extension}"
        url = f"{self.base_url}/{filename}"
        return url

    def check_file_exists(self, url: str) -> bool:
        """
        파일이 서버에 존재하는지 확인합니다.

        Args:
            url: 확인할 URL

        Returns:
            bool: 파일이 존재하면 True
        """
        try:
            response = self.session.head(url, timeout=self.timeout[0], allow_redirects=True)
            exists = response.status_code == 200

            if exists:
                logger.debug(f"파일 존재 확인: {url}")
            else:
                logger.debug(f"파일 없음 (HTTP {response.status_code}): {url}")

            return exists

        except requests.exceptions.RequestException as e:
            logger.warning(f"파일 존재 확인 실패: {url} - {e}")
            return False

    def get_file_size(self, url: str) -> Optional[int]:
        """
        원격 파일의 크기를 가져옵니다.

        Args:
            url: 파일 URL

        Returns:
            int: 파일 크기 (바이트), 실패 시 None
        """
        try:
            response = self.session.head(url, timeout=self.timeout[0], allow_redirects=True)

            if response.status_code == 200:
                content_length = response.headers.get('Content-Length')
                if content_length:
                    return int(content_length)

            return None

        except requests.exceptions.RequestException as e:
            logger.warning(f"파일 크기 확인 실패: {url} - {e}")
            return None

    def download_file(
        self,
        url: str,
        output_path: Path,
        show_progress: bool = True,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> bool:
        """
        파일을 다운로드합니다.

        Args:
            url: 다운로드 URL
            output_path: 저장할 파일 경로
            show_progress: 진행률 바 표시 여부
            progress_callback: 진행률 콜백 함수 (downloaded_bytes, total_bytes)

        Returns:
            bool: 다운로드 성공 시 True

        Raises:
            requests.exceptions.RequestException: HTTP 오류 발생 시
        """
        logger.info(f"다운로드 시작: {url}")

        try:
            # 스트리밍 다운로드
            response = self.session.get(
                url,
                stream=True,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()

            # 파일 크기 가져오기
            total_size = int(response.headers.get('Content-Length', 0))

            # 출력 디렉토리 생성
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 다운로드 및 저장
            downloaded_size = 0
            chunk_size = 8192

            # 진행률 바 설정
            progress_bar = None
            if show_progress and total_size > 0:
                progress_bar = tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=output_path.name
                )

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        # 진행률 업데이트
                        if progress_bar:
                            progress_bar.update(len(chunk))

                        if progress_callback:
                            progress_callback(downloaded_size, total_size)

            if progress_bar:
                progress_bar.close()

            logger.info(f"다운로드 완료: {output_path} ({downloaded_size} bytes)")
            return True

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP 오류: {e}")
            # 부분 다운로드 파일 삭제
            if output_path.exists():
                output_path.unlink()
            raise

        except requests.exceptions.Timeout as e:
            logger.error(f"타임아웃: {e}")
            if output_path.exists():
                output_path.unlink()
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"다운로드 실패: {e}")
            if output_path.exists():
                output_path.unlink()
            raise

        except Exception as e:
            logger.error(f"예상치 못한 오류: {e}")
            if output_path.exists():
                output_path.unlink()
            raise

    def download_with_retry(
        self,
        url: str,
        output_path: Path,
        max_attempts: int = 3,
        show_progress: bool = True
    ) -> bool:
        """
        재시도 로직을 포함한 파일 다운로드입니다.

        Args:
            url: 다운로드 URL
            output_path: 저장할 파일 경로
            max_attempts: 최대 시도 횟수
            show_progress: 진행률 바 표시 여부

        Returns:
            bool: 다운로드 성공 시 True
        """
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"다운로드 시도 {attempt}/{max_attempts}: {url}")
                self.download_file(url, output_path, show_progress)
                return True

            except requests.exceptions.HTTPError as e:
                # 404는 재시도하지 않음
                if e.response.status_code == 404:
                    logger.error(f"파일을 찾을 수 없습니다: {url}")
                    return False

                logger.warning(f"시도 {attempt} 실패: {e}")

                if attempt < max_attempts:
                    delay = self.backoff_factor ** attempt
                    logger.info(f"{delay}초 후 재시도...")
                    time.sleep(delay)
                else:
                    logger.error(f"최대 재시도 횟수 초과: {url}")
                    return False

            except Exception as e:
                logger.warning(f"시도 {attempt} 실패: {e}")

                if attempt < max_attempts:
                    delay = self.backoff_factor ** attempt
                    logger.info(f"{delay}초 후 재시도...")
                    time.sleep(delay)
                else:
                    logger.error(f"최대 재시도 횟수 초과: {url}")
                    return False

        return False

    def close(self) -> None:
        """
        세션을 종료합니다.
        """
        if self.session:
            self.session.close()
            logger.debug("세션 종료")

    def __enter__(self):
        """
        컨텍스트 매니저 진입
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        컨텍스트 매니저 종료
        """
        self.close()
