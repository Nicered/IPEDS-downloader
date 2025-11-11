"""
다운로드 관리 모듈

이 모듈은 개별 파일 다운로드 작업을 관리합니다.
"""

import logging
from pathlib import Path
from typing import Optional

from ..client.ipeds_client import IPEDSClient
from ..storage.file_manager import FileManager
from ..storage.metadata_manager import MetadataManager


logger = logging.getLogger(__name__)


class DownloadTask:
    """
    개별 다운로드 작업을 나타내는 클래스입니다.
    """

    def __init__(self, survey: str, year: int, url: str):
        """
        DownloadTask를 초기화합니다.

        Args:
            survey: 서베이 코드
            year: 연도
            url: 다운로드 URL
        """
        self.survey = survey
        self.year = year
        self.url = url
        self.status = "PENDING"
        self.error_message: Optional[str] = None
        self.file_path: Optional[Path] = None
        self.file_size: Optional[int] = None
        self.checksum: Optional[str] = None
        self.retry_count = 0

    def __repr__(self) -> str:
        return f"DownloadTask({self.survey}{self.year}, status={self.status})"


class DownloadManager:
    """
    다운로드 작업을 관리하는 클래스입니다.
    """

    def __init__(
        self,
        client: IPEDSClient,
        file_manager: FileManager,
        metadata_manager: MetadataManager,
        skip_existing: bool = True,
        verify_checksum: bool = True,
        auto_extract: bool = False
    ):
        """
        DownloadManager를 초기화합니다.

        Args:
            client: IPEDS 클라이언트
            file_manager: 파일 관리자
            metadata_manager: 메타데이터 관리자
            skip_existing: 기존 파일 건너뛰기 여부
            verify_checksum: 체크섬 검증 여부
            auto_extract: 자동 압축 해제 여부
        """
        self.client = client
        self.file_manager = file_manager
        self.metadata_manager = metadata_manager
        self.skip_existing = skip_existing
        self.verify_checksum = verify_checksum
        self.auto_extract = auto_extract

        logger.info("DownloadManager 초기화")

    def download(
        self,
        survey: str,
        year: int,
        show_progress: bool = True
    ) -> DownloadTask:
        """
        단일 파일을 다운로드합니다.

        Args:
            survey: 서베이 코드
            year: 연도
            show_progress: 진행률 표시 여부

        Returns:
            DownloadTask: 다운로드 작업 정보
        """
        # 다운로드 작업 생성
        url = self.client.build_url(survey, year)
        task = DownloadTask(survey, year, url)

        logger.info(f"다운로드 작업 시작: {survey}{year}")

        # 파일 경로 설정
        output_path = self.file_manager.get_raw_file_path(survey, year)
        task.file_path = output_path

        # 기존 파일 확인
        if self.skip_existing and self.file_manager.file_exists(output_path):
            logger.info(f"파일이 이미 존재합니다. 건너뜀: {output_path}")
            task.status = "SKIPPED"

            # 메타데이터에 로그 기록
            self.metadata_manager.log_download(
                survey=survey,
                year=year,
                url=url,
                status="SKIPPED"
            )

            return task

        # 파일 존재 여부 확인 (IPEDS 서버가 HEAD 요청을 차단하므로 비활성화)
        # if not self.client.check_file_exists(url):
        #     logger.warning(f"파일을 찾을 수 없습니다: {url}")
        #     task.status = "FAILED"
        #     task.error_message = "파일을 찾을 수 없습니다 (404)"
        #
        #     # 메타데이터에 로그 기록
        #     self.metadata_manager.log_download(
        #         survey=survey,
        #         year=year,
        #         url=url,
        #         status="FAILED",
        #         error_message=task.error_message
        #     )
        #
        #     return task

        # 다운로드 시도
        try:
            task.status = "IN_PROGRESS"

            # 재시도 로직을 포함한 다운로드
            success = self.client.download_with_retry(
                url=url,
                output_path=output_path,
                show_progress=show_progress
            )

            if success:
                task.status = "COMPLETED"

                # 파일 정보 수집
                file_info = self.file_manager.get_file_info(output_path)
                task.file_size = file_info['file_size']
                task.checksum = file_info['checksum_sha256']

                # 파일 검증
                if self.verify_checksum:
                    is_valid = self.file_manager.verify_file(output_path)
                    if not is_valid:
                        logger.error(f"파일 검증 실패: {output_path}")
                        task.status = "FAILED"
                        task.error_message = "파일 검증 실패"

                # 메타데이터에 등록
                if task.status == "COMPLETED":
                    self.metadata_manager.register_file(survey, year, file_info)

                    logger.info(f"다운로드 완료: {survey}{year}")

                    # 자동 압축 해제
                    if self.auto_extract:
                        try:
                            extract_path = self.file_manager.extract_zip(output_path)
                            logger.info(f"압축 해제 완료: {extract_path}")
                        except Exception as e:
                            logger.warning(f"압축 해제 실패: {e}")

                # 다운로드 로그 기록
                self.metadata_manager.log_download(
                    survey=survey,
                    year=year,
                    url=url,
                    status=task.status,
                    file_size=task.file_size,
                    checksum=task.checksum,
                    error_message=task.error_message,
                    retry_count=task.retry_count
                )

            else:
                task.status = "FAILED"
                task.error_message = "다운로드 실패 (최대 재시도 횟수 초과)"

                # 다운로드 로그 기록
                self.metadata_manager.log_download(
                    survey=survey,
                    year=year,
                    url=url,
                    status="FAILED",
                    error_message=task.error_message,
                    retry_count=task.retry_count
                )

        except Exception as e:
            logger.error(f"다운로드 중 오류 발생: {e}")
            task.status = "FAILED"
            task.error_message = str(e)

            # 다운로드 로그 기록
            self.metadata_manager.log_download(
                survey=survey,
                year=year,
                url=url,
                status="FAILED",
                error_message=task.error_message
            )

        return task

    def download_batch(
        self,
        tasks: list[tuple[str, int]],
        show_progress: bool = True
    ) -> list[DownloadTask]:
        """
        여러 파일을 순차적으로 다운로드합니다.

        Args:
            tasks: (survey, year) 튜플 리스트
            show_progress: 진행률 표시 여부

        Returns:
            list[DownloadTask]: 다운로드 작업 리스트
        """
        results = []

        logger.info(f"배치 다운로드 시작: {len(tasks)}개 파일")

        for survey, year in tasks:
            task_result = self.download(survey, year, show_progress)
            results.append(task_result)

            # 요청 간 지연 (서버 부하 방지)
            import time
            time.sleep(1.0)

        # 통계 출력
        completed = sum(1 for t in results if t.status == "COMPLETED")
        failed = sum(1 for t in results if t.status == "FAILED")
        skipped = sum(1 for t in results if t.status == "SKIPPED")

        logger.info(f"배치 다운로드 완료: 성공={completed}, 실패={failed}, 건너뜀={skipped}")

        return results

    def verify_downloaded_file(
        self,
        survey: str,
        year: int
    ) -> bool:
        """
        다운로드된 파일을 검증합니다.

        Args:
            survey: 서베이 코드
            year: 연도

        Returns:
            bool: 검증 성공 시 True
        """
        file_path = self.file_manager.get_raw_file_path(survey, year)

        if not self.file_manager.file_exists(file_path):
            logger.error(f"파일이 존재하지 않습니다: {file_path}")
            return False

        return self.file_manager.verify_file(file_path)

    def extract_downloaded_file(
        self,
        survey: str,
        year: int,
        overwrite: bool = False
    ) -> Optional[Path]:
        """
        다운로드된 파일의 압축을 해제합니다.

        Args:
            survey: 서베이 코드
            year: 연도
            overwrite: 기존 파일 덮어쓰기 여부

        Returns:
            Path: 압축 해제된 디렉토리 경로, 실패 시 None
        """
        file_path = self.file_manager.get_raw_file_path(survey, year)

        if not self.file_manager.file_exists(file_path):
            logger.error(f"파일이 존재하지 않습니다: {file_path}")
            return None

        try:
            extract_dir = self.file_manager.get_extracted_dir_path(survey, year)
            return self.file_manager.extract_zip(file_path, extract_dir, overwrite)

        except Exception as e:
            logger.error(f"압축 해제 실패: {e}")
            return None
