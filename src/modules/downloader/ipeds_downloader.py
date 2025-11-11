"""
IPEDS 다운로더 메인 모듈

이 모듈은 IPEDS 데이터 다운로드의 전체 프로세스를 조율합니다.
"""

import logging
from typing import List, Optional

from ..client.ipeds_client import IPEDSClient
from ..config.config_loader import ConfigLoader
from ..storage.file_manager import FileManager
from ..storage.metadata_manager import MetadataManager
from ..utils.logger import setup_logging, get_logger
from ..utils.year_detector import get_year_range
from .download_manager import DownloadManager, DownloadTask


logger = get_logger(__name__)


class IPEDSDownloader:
    """
    IPEDS 데이터 다운로더의 메인 클래스입니다.

    모든 다운로드 작업을 조율하고 관리합니다.
    """

    def __init__(self, config_loader: ConfigLoader):
        """
        IPEDSDownloader를 초기화합니다.

        Args:
            config_loader: 설정 로더
        """
        self.config = config_loader

        # 로깅 설정
        self._setup_logging()

        # 컴포넌트 초기화
        self.client = self._create_client()
        self.file_manager = self._create_file_manager()
        self.metadata_manager = self._create_metadata_manager()
        self.download_manager = self._create_download_manager()

        # 연도 범위 설정
        self.start_year, self.end_year = self._get_year_range()

        # 서베이 목록
        self.surveys = self._get_survey_list()

        logger.info("=" * 60)
        logger.info("IPEDS 다운로더 초기화 완료")
        logger.info(f"  - 연도 범위: {self.start_year} ~ {self.end_year}")
        logger.info(f"  - 서베이 개수: {len(self.surveys)}")
        logger.info("=" * 60)

    def _setup_logging(self) -> None:
        """
        로깅을 설정합니다.
        """
        log_level = self.config.get('logging.level', 'INFO')
        log_dir = self.config.get('storage.log_dir', './logs')

        # 로그 레벨 변환
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        level = level_map.get(log_level.upper(), logging.INFO)

        setup_logging(default_level=level, log_dir=log_dir)

    def _create_client(self) -> IPEDSClient:
        """
        IPEDS 클라이언트를 생성합니다.
        """
        base_url = self.config.get('ipeds.base_url')
        user_agent = self.config.get('ipeds.user_agent')
        timeout = (
            self.config.get('timeout.connect', 10),
            self.config.get('timeout.read', 300)
        )
        max_retries = self.config.get('retry.max_attempts', 3)
        backoff_factor = self.config.get('retry.backoff_factor', 2.0)

        return IPEDSClient(
            base_url=base_url,
            user_agent=user_agent,
            timeout=timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor
        )

    def _create_file_manager(self) -> FileManager:
        """
        파일 관리자를 생성합니다.
        """
        raw_dir = self.config.get('storage.raw_dir')
        extracted_dir = self.config.get('storage.extracted_dir')
        metadata_dir = self.config.get('storage.metadata_dir')

        return FileManager(
            raw_dir=raw_dir,
            extracted_dir=extracted_dir,
            metadata_dir=metadata_dir
        )

    def _create_metadata_manager(self) -> MetadataManager:
        """
        메타데이터 관리자를 생성합니다.
        """
        metadata_dir = self.config.get('storage.metadata_dir')
        file_registry = self.config.get('storage.file_registry', 'file_registry.json')
        download_log = self.config.get('storage.download_log', 'download_log.json')

        return MetadataManager(
            metadata_dir=metadata_dir,
            file_registry_name=file_registry,
            download_log_name=download_log
        )

    def _create_download_manager(self) -> DownloadManager:
        """
        다운로드 관리자를 생성합니다.
        """
        skip_existing = self.config.get('download.skip_existing', True)
        verify_checksum = self.config.get('download.verify_checksum', True)
        auto_extract = self.config.get('download.auto_extract', False)

        return DownloadManager(
            client=self.client,
            file_manager=self.file_manager,
            metadata_manager=self.metadata_manager,
            skip_existing=skip_existing,
            verify_checksum=verify_checksum,
            auto_extract=auto_extract
        )

    def _get_year_range(self) -> tuple[int, int]:
        """
        다운로드할 연도 범위를 결정합니다.
        """
        start_year = self.config.get('ipeds.years.start')
        end_year = self.config.get('ipeds.years.end')
        base_url = self.config.get('ipeds.base_url')
        timeout = self.config.get('timeout.connect', 10)

        return get_year_range(
            base_url=base_url,
            start_year=start_year,
            end_year=end_year,
            timeout=timeout
        )

    def _get_survey_list(self) -> List[str]:
        """
        다운로드할 서베이 목록을 가져옵니다.
        """
        surveys = self.config.get('ipeds.surveys')

        if surveys is None:
            # 모든 서베이 다운로드
            surveys = self.config.get_all_survey_codes()

        return surveys

    def download_all(self, show_progress: bool = True) -> List[DownloadTask]:
        """
        모든 데이터를 다운로드합니다.

        Args:
            show_progress: 진행률 표시 여부

        Returns:
            List[DownloadTask]: 다운로드 작업 리스트
        """
        logger.info("=" * 60)
        logger.info("전체 다운로드 시작")
        logger.info(f"  - 연도: {self.start_year} ~ {self.end_year}")
        logger.info(f"  - 서베이: {', '.join(self.surveys)}")
        logger.info("=" * 60)

        # 다운로드 작업 목록 생성
        tasks = []
        for year in range(self.start_year, self.end_year + 1):
            for survey in self.surveys:
                # 서베이 변형(variants) 포함
                variants = self.config.get_survey_variants(survey)
                for variant in variants:
                    tasks.append((variant, year))

        logger.info(f"총 {len(tasks)}개 파일 다운로드 예정")

        # 배치 다운로드
        results = self.download_manager.download_batch(tasks, show_progress)

        # 결과 요약
        self._print_summary(results)

        return results

    def download_by_year(self, year: int, show_progress: bool = True) -> List[DownloadTask]:
        """
        특정 연도의 모든 데이터를 다운로드합니다.

        Args:
            year: 다운로드할 연도
            show_progress: 진행률 표시 여부

        Returns:
            List[DownloadTask]: 다운로드 작업 리스트
        """
        logger.info(f"{year}년 데이터 다운로드 시작")

        tasks = []
        for survey in self.surveys:
            variants = self.config.get_survey_variants(survey)
            for variant in variants:
                tasks.append((variant, year))

        results = self.download_manager.download_batch(tasks, show_progress)

        self._print_summary(results)

        return results

    def download_by_survey(
        self,
        survey: str,
        show_progress: bool = True
    ) -> List[DownloadTask]:
        """
        특정 서베이의 모든 연도 데이터를 다운로드합니다.

        Args:
            survey: 서베이 코드
            show_progress: 진행률 표시 여부

        Returns:
            List[DownloadTask]: 다운로드 작업 리스트
        """
        logger.info(f"{survey} 서베이 다운로드 시작")

        variants = self.config.get_survey_variants(survey)

        tasks = []
        for year in range(self.start_year, self.end_year + 1):
            for variant in variants:
                tasks.append((variant, year))

        results = self.download_manager.download_batch(tasks, show_progress)

        self._print_summary(results)

        return results

    def download_single(
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
            DownloadTask: 다운로드 작업
        """
        logger.info(f"{survey}{year} 파일 다운로드")

        result = self.download_manager.download(survey, year, show_progress)

        logger.info(f"다운로드 완료: {result.status}")

        return result

    def verify_all(self) -> dict:
        """
        다운로드된 모든 파일을 검증합니다.

        Returns:
            dict: 검증 결과 통계
        """
        logger.info("다운로드된 파일 검증 시작")

        registered_files = self.metadata_manager.get_all_registered_files()
        total = len(registered_files)
        verified = 0
        failed = []

        for key, file_info in registered_files.items():
            survey = file_info['survey']
            year = file_info['year']

            if self.download_manager.verify_downloaded_file(survey, year):
                verified += 1
            else:
                failed.append(f"{survey}{year}")

        result = {
            'total': total,
            'verified': verified,
            'failed': len(failed),
            'failed_files': failed
        }

        logger.info(f"검증 완료: 성공={verified}/{total}, 실패={len(failed)}")

        return result

    def extract_all(self, overwrite: bool = False) -> dict:
        """
        다운로드된 모든 ZIP 파일의 압축을 해제합니다.

        Args:
            overwrite: 기존 파일 덮어쓰기 여부

        Returns:
            dict: 압축 해제 결과 통계
        """
        logger.info("압축 해제 시작")

        registered_files = self.metadata_manager.get_all_registered_files()
        total = len(registered_files)
        extracted = 0
        failed = []

        for key, file_info in registered_files.items():
            survey = file_info['survey']
            year = file_info['year']

            result = self.download_manager.extract_downloaded_file(survey, year, overwrite)

            if result:
                extracted += 1
            else:
                failed.append(f"{survey}{year}")

        result = {
            'total': total,
            'extracted': extracted,
            'failed': len(failed),
            'failed_files': failed
        }

        logger.info(f"압축 해제 완료: 성공={extracted}/{total}, 실패={len(failed)}")

        return result

    def get_statistics(self) -> dict:
        """
        다운로드 통계를 반환합니다.

        Returns:
            dict: 통계 정보
        """
        download_stats = self.metadata_manager.get_download_statistics()
        disk_usage = self.file_manager.get_disk_usage()

        return {
            'download_statistics': download_stats,
            'disk_usage': disk_usage,
            'year_range': {
                'start': self.start_year,
                'end': self.end_year,
                'total_years': self.end_year - self.start_year + 1
            },
            'surveys': {
                'count': len(self.surveys),
                'list': self.surveys
            }
        }

    def _print_summary(self, results: List[DownloadTask]) -> None:
        """
        다운로드 결과 요약을 출력합니다.

        Args:
            results: 다운로드 작업 리스트
        """
        completed = sum(1 for t in results if t.status == "COMPLETED")
        failed = sum(1 for t in results if t.status == "FAILED")
        skipped = sum(1 for t in results if t.status == "SKIPPED")

        logger.info("=" * 60)
        logger.info("다운로드 결과 요약")
        logger.info(f"  - 총 작업: {len(results)}")
        logger.info(f"  - 성공: {completed}")
        logger.info(f"  - 실패: {failed}")
        logger.info(f"  - 건너뜀: {skipped}")

        if failed > 0:
            logger.info("\n실패한 파일:")
            for task in results:
                if task.status == "FAILED":
                    logger.info(f"  - {task.survey}{task.year}: {task.error_message}")

        logger.info("=" * 60)

    def close(self) -> None:
        """
        다운로더를 종료하고 리소스를 정리합니다.
        """
        self.client.close()
        logger.info("IPEDS 다운로더 종료")
