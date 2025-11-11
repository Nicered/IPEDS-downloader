"""
메타데이터 관리 모듈

이 모듈은 다운로드 메타데이터 및 파일 레지스트리를 관리합니다.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from ..utils.helpers import ensure_dir


logger = logging.getLogger(__name__)


class MetadataManager:
    """
    다운로드 메타데이터 및 파일 레지스트리를 관리하는 클래스입니다.
    """

    def __init__(
        self,
        metadata_dir: Union[str, Path],
        file_registry_name: str = "file_registry.json",
        download_log_name: str = "download_log.json"
    ):
        """
        MetadataManager를 초기화합니다.

        Args:
            metadata_dir: 메타데이터 저장 디렉토리
            file_registry_name: 파일 레지스트리 파일명
            download_log_name: 다운로드 로그 파일명
        """
        self.metadata_dir = Path(metadata_dir)
        ensure_dir(self.metadata_dir)

        self.file_registry_path = self.metadata_dir / file_registry_name
        self.download_log_path = self.metadata_dir / download_log_name

        # 레지스트리 로드
        self.file_registry = self._load_json(self.file_registry_path, default={})
        self.download_log = self._load_json(self.download_log_path, default=[])

        logger.info(f"MetadataManager 초기화: {self.metadata_dir}")

    def _load_json(self, file_path: Path, default: Union[dict, list]) -> Union[dict, list]:
        """
        JSON 파일을 로드합니다.

        Args:
            file_path: JSON 파일 경로
            default: 파일이 없을 때 반환할 기본값

        Returns:
            Union[dict, list]: 로드된 데이터
        """
        if not file_path.exists():
            logger.debug(f"메타데이터 파일이 없습니다: {file_path}")
            return default

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"메타데이터 로드 완료: {file_path}")
            return data

        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {file_path} - {e}")
            return default

        except Exception as e:
            logger.error(f"메타데이터 로드 실패: {file_path} - {e}")
            return default

    def _save_json(self, file_path: Path, data: Union[dict, list]) -> bool:
        """
        JSON 파일로 저장합니다.

        Args:
            file_path: JSON 파일 경로
            data: 저장할 데이터

        Returns:
            bool: 저장 성공 시 True
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"메타데이터 저장 완료: {file_path}")
            return True

        except Exception as e:
            logger.error(f"메타데이터 저장 실패: {file_path} - {e}")
            return False

    def register_file(
        self,
        survey: str,
        year: int,
        file_info: dict
    ) -> None:
        """
        파일을 레지스트리에 등록합니다.

        Args:
            survey: 서베이 코드
            year: 연도
            file_info: 파일 정보 딕셔너리
        """
        key = f"{survey}{year}"
        self.file_registry[key] = {
            'survey': survey,
            'year': year,
            'registered_at': datetime.now().isoformat(),
            **file_info
        }

        self._save_json(self.file_registry_path, self.file_registry)
        logger.info(f"파일 등록: {key}")

    def get_file_info(self, survey: str, year: int) -> Optional[dict]:
        """
        파일 정보를 조회합니다.

        Args:
            survey: 서베이 코드
            year: 연도

        Returns:
            dict: 파일 정보, 없으면 None
        """
        key = f"{survey}{year}"
        return self.file_registry.get(key)

    def is_file_registered(self, survey: str, year: int) -> bool:
        """
        파일이 레지스트리에 등록되어 있는지 확인합니다.

        Args:
            survey: 서베이 코드
            year: 연도

        Returns:
            bool: 등록되어 있으면 True
        """
        key = f"{survey}{year}"
        return key in self.file_registry

    def unregister_file(self, survey: str, year: int) -> bool:
        """
        파일을 레지스트리에서 제거합니다.

        Args:
            survey: 서베이 코드
            year: 연도

        Returns:
            bool: 제거 성공 시 True
        """
        key = f"{survey}{year}"

        if key in self.file_registry:
            del self.file_registry[key]
            self._save_json(self.file_registry_path, self.file_registry)
            logger.info(f"파일 등록 해제: {key}")
            return True

        logger.warning(f"파일이 등록되어 있지 않습니다: {key}")
        return False

    def get_all_registered_files(self) -> Dict[str, dict]:
        """
        모든 등록된 파일 정보를 반환합니다.

        Returns:
            Dict[str, dict]: 파일 레지스트리
        """
        return self.file_registry.copy()

    def log_download(
        self,
        survey: str,
        year: int,
        url: str,
        status: str,
        file_size: Optional[int] = None,
        checksum: Optional[str] = None,
        error_message: Optional[str] = None,
        retry_count: int = 0
    ) -> None:
        """
        다운로드 이력을 로그에 기록합니다.

        Args:
            survey: 서베이 코드
            year: 연도
            url: 다운로드 URL
            status: 다운로드 상태 (COMPLETED, FAILED, SKIPPED 등)
            file_size: 파일 크기 (바이트)
            checksum: 파일 체크섬
            error_message: 에러 메시지 (실패 시)
            retry_count: 재시도 횟수
        """
        log_entry = {
            'file_name': f"{survey}{year}.zip",
            'survey': survey,
            'year': year,
            'url': url,
            'download_date': datetime.now().isoformat(),
            'status': status,
            'file_size': file_size,
            'checksum': checksum,
            'retry_count': retry_count,
            'error_message': error_message
        }

        self.download_log.append(log_entry)
        self._save_json(self.download_log_path, self.download_log)

        logger.debug(f"다운로드 로그 기록: {survey}{year} - {status}")

    def get_download_history(
        self,
        survey: Optional[str] = None,
        year: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[dict]:
        """
        다운로드 이력을 조회합니다.

        Args:
            survey: 서베이 코드 필터 (None이면 모두)
            year: 연도 필터 (None이면 모두)
            status: 상태 필터 (None이면 모두)

        Returns:
            List[dict]: 필터링된 다운로드 이력
        """
        filtered_log = self.download_log

        if survey:
            filtered_log = [entry for entry in filtered_log if entry.get('survey') == survey]

        if year:
            filtered_log = [entry for entry in filtered_log if entry.get('year') == year]

        if status:
            filtered_log = [entry for entry in filtered_log if entry.get('status') == status]

        return filtered_log

    def get_download_statistics(self) -> dict:
        """
        다운로드 통계를 반환합니다.

        Returns:
            dict: 다운로드 통계 정보
        """
        total_downloads = len(self.download_log)

        status_counts = {}
        for entry in self.download_log:
            status = entry.get('status', 'UNKNOWN')
            status_counts[status] = status_counts.get(status, 0) + 1

        total_size = sum(entry.get('file_size', 0) for entry in self.download_log if entry.get('file_size'))

        failed_downloads = [
            entry for entry in self.download_log
            if entry.get('status') == 'FAILED'
        ]

        return {
            'total_downloads': total_downloads,
            'status_counts': status_counts,
            'total_size_bytes': total_size,
            'failed_count': len(failed_downloads),
            'success_rate': (status_counts.get('COMPLETED', 0) / total_downloads * 100)
                           if total_downloads > 0 else 0,
            'failed_downloads': failed_downloads
        }

    def get_files_by_year(self, year: int) -> List[dict]:
        """
        특정 연도의 모든 파일 정보를 반환합니다.

        Args:
            year: 연도

        Returns:
            List[dict]: 파일 정보 리스트
        """
        files = []
        for key, info in self.file_registry.items():
            if info.get('year') == year:
                files.append(info)

        return files

    def get_files_by_survey(self, survey: str) -> List[dict]:
        """
        특정 서베이의 모든 파일 정보를 반환합니다.

        Args:
            survey: 서베이 코드

        Returns:
            List[dict]: 파일 정보 리스트
        """
        files = []
        for key, info in self.file_registry.items():
            if info.get('survey') == survey:
                files.append(info)

        return files

    def clear_registry(self) -> None:
        """
        파일 레지스트리를 초기화합니다.
        """
        self.file_registry = {}
        self._save_json(self.file_registry_path, self.file_registry)
        logger.warning("파일 레지스트리 초기화됨")

    def clear_download_log(self) -> None:
        """
        다운로드 로그를 초기화합니다.
        """
        self.download_log = []
        self._save_json(self.download_log_path, self.download_log)
        logger.warning("다운로드 로그 초기화됨")

    def export_registry(self, export_path: Union[str, Path]) -> bool:
        """
        파일 레지스트리를 외부 파일로 내보냅니다.

        Args:
            export_path: 내보낼 파일 경로

        Returns:
            bool: 내보내기 성공 시 True
        """
        export_path = Path(export_path)

        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.file_registry, f, indent=2, ensure_ascii=False)

            logger.info(f"레지스트리 내보내기 완료: {export_path}")
            return True

        except Exception as e:
            logger.error(f"레지스트리 내보내기 실패: {e}")
            return False

    def import_registry(self, import_path: Union[str, Path]) -> bool:
        """
        외부 파일에서 파일 레지스트리를 가져옵니다.

        Args:
            import_path: 가져올 파일 경로

        Returns:
            bool: 가져오기 성공 시 True
        """
        import_path = Path(import_path)

        if not import_path.exists():
            logger.error(f"파일을 찾을 수 없습니다: {import_path}")
            return False

        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_registry = json.load(f)

            self.file_registry.update(imported_registry)
            self._save_json(self.file_registry_path, self.file_registry)

            logger.info(f"레지스트리 가져오기 완료: {import_path}")
            return True

        except Exception as e:
            logger.error(f"레지스트리 가져오기 실패: {e}")
            return False
