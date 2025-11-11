"""
파일 관리 모듈

이 모듈은 파일 저장, 압축 해제, 검증 등의 기능을 제공합니다.
"""

import logging
import shutil
import zipfile
from pathlib import Path
from typing import Optional, Union

from ..utils.helpers import ensure_dir, get_file_size, calculate_checksum, format_bytes
from ..utils.validators import is_zip_file


logger = logging.getLogger(__name__)


class FileManager:
    """
    파일 저장 및 관리를 담당하는 클래스입니다.
    """

    def __init__(
        self,
        raw_dir: Union[str, Path],
        extracted_dir: Union[str, Path],
        metadata_dir: Union[str, Path]
    ):
        """
        FileManager를 초기화합니다.

        Args:
            raw_dir: 원본 파일 저장 디렉토리
            extracted_dir: 압축 해제 파일 저장 디렉토리
            metadata_dir: 메타데이터 저장 디렉토리
        """
        self.raw_dir = Path(raw_dir)
        self.extracted_dir = Path(extracted_dir)
        self.metadata_dir = Path(metadata_dir)

        # 디렉토리 생성
        ensure_dir(self.raw_dir)
        ensure_dir(self.extracted_dir)
        ensure_dir(self.metadata_dir)

        logger.info(f"FileManager 초기화")
        logger.info(f"  - 원본: {self.raw_dir}")
        logger.info(f"  - 압축해제: {self.extracted_dir}")
        logger.info(f"  - 메타데이터: {self.metadata_dir}")

    def get_raw_file_path(self, survey: str, year: int) -> Path:
        """
        원본 파일 경로를 반환합니다.

        Args:
            survey: 서베이 코드
            year: 연도

        Returns:
            Path: 원본 파일 경로
        """
        year_dir = self.raw_dir / str(year)
        ensure_dir(year_dir)
        return year_dir / f"{survey}{year}.zip"

    def get_extracted_dir_path(self, survey: str, year: int) -> Path:
        """
        압축 해제 디렉토리 경로를 반환합니다.

        Args:
            survey: 서베이 코드
            year: 연도

        Returns:
            Path: 압축 해제 디렉토리 경로
        """
        year_dir = self.extracted_dir / str(year)
        extracted_path = year_dir / f"{survey}{year}"
        return extracted_path

    def file_exists(self, file_path: Union[str, Path]) -> bool:
        """
        파일이 존재하는지 확인합니다.

        Args:
            file_path: 파일 경로

        Returns:
            bool: 파일이 존재하면 True
        """
        path = Path(file_path)
        return path.exists() and path.is_file()

    def get_file_info(self, file_path: Union[str, Path]) -> dict:
        """
        파일 정보를 반환합니다.

        Args:
            file_path: 파일 경로

        Returns:
            dict: 파일 정보 (크기, 체크섬 등)
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        file_size = get_file_size(path)
        checksum = calculate_checksum(path, 'sha256')

        return {
            'file_name': path.name,
            'file_path': str(path.absolute()),
            'file_size': file_size,
            'file_size_human': format_bytes(file_size),
            'checksum_sha256': checksum,
            'is_zip': is_zip_file(path)
        }

    def verify_file(
        self,
        file_path: Union[str, Path],
        expected_checksum: Optional[str] = None,
        algorithm: str = 'sha256'
    ) -> bool:
        """
        파일을 검증합니다.

        Args:
            file_path: 파일 경로
            expected_checksum: 예상 체크섬 (None이면 체크섬 검증 생략)
            algorithm: 해시 알고리즘

        Returns:
            bool: 검증 성공 시 True
        """
        path = Path(file_path)

        if not path.exists():
            logger.error(f"파일을 찾을 수 없습니다: {file_path}")
            return False

        # 파일 크기 확인
        file_size = get_file_size(path)
        if file_size == 0:
            logger.error(f"파일이 비어있습니다: {file_path}")
            return False

        # ZIP 파일 검증
        if path.suffix.lower() == '.zip':
            if not is_zip_file(path):
                logger.error(f"유효하지 않은 ZIP 파일: {file_path}")
                return False

        # 체크섬 검증
        if expected_checksum:
            actual_checksum = calculate_checksum(path, algorithm)
            if actual_checksum.lower() != expected_checksum.lower():
                logger.error(f"체크섬 불일치: {file_path}")
                logger.error(f"  예상: {expected_checksum}")
                logger.error(f"  실제: {actual_checksum}")
                return False

        logger.info(f"파일 검증 성공: {file_path}")
        return True

    def extract_zip(
        self,
        zip_path: Union[str, Path],
        extract_to: Optional[Union[str, Path]] = None,
        overwrite: bool = False
    ) -> Path:
        """
        ZIP 파일을 압축 해제합니다.

        Args:
            zip_path: ZIP 파일 경로
            extract_to: 압축 해제 대상 디렉토리 (None이면 자동 설정)
            overwrite: 기존 파일 덮어쓰기 여부

        Returns:
            Path: 압축 해제된 디렉토리 경로

        Raises:
            ValueError: ZIP 파일이 아닌 경우
            zipfile.BadZipFile: 손상된 ZIP 파일인 경우
        """
        zip_path = Path(zip_path)

        if not is_zip_file(zip_path):
            raise ValueError(f"유효하지 않은 ZIP 파일: {zip_path}")

        # 압축 해제 경로 설정
        if extract_to is None:
            # 파일명에서 연도와 서베이 코드 추출
            file_name = zip_path.stem  # 예: HD2022
            extract_to = self.extracted_dir / file_name
        else:
            extract_to = Path(extract_to)

        # 기존 디렉토리 확인
        if extract_to.exists() and not overwrite:
            logger.info(f"이미 압축 해제되어 있습니다: {extract_to}")
            return extract_to

        # 디렉토리 생성
        ensure_dir(extract_to)

        logger.info(f"ZIP 압축 해제 중: {zip_path} -> {extract_to}")

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # 전체 파일 목록
                file_list = zip_ref.namelist()
                logger.info(f"압축 파일 개수: {len(file_list)}")

                # 압축 해제
                zip_ref.extractall(extract_to)

            logger.info(f"압축 해제 완료: {extract_to}")
            return extract_to

        except zipfile.BadZipFile as e:
            logger.error(f"손상된 ZIP 파일: {zip_path} - {e}")
            raise

        except Exception as e:
            logger.error(f"압축 해제 실패: {zip_path} - {e}")
            raise

    def delete_file(self, file_path: Union[str, Path]) -> bool:
        """
        파일을 삭제합니다.

        Args:
            file_path: 파일 경로

        Returns:
            bool: 삭제 성공 시 True
        """
        path = Path(file_path)

        if not path.exists():
            logger.warning(f"파일이 존재하지 않습니다: {file_path}")
            return False

        try:
            path.unlink()
            logger.info(f"파일 삭제 완료: {file_path}")
            return True

        except Exception as e:
            logger.error(f"파일 삭제 실패: {file_path} - {e}")
            return False

    def delete_directory(self, dir_path: Union[str, Path]) -> bool:
        """
        디렉토리를 삭제합니다.

        Args:
            dir_path: 디렉토리 경로

        Returns:
            bool: 삭제 성공 시 True
        """
        path = Path(dir_path)

        if not path.exists():
            logger.warning(f"디렉토리가 존재하지 않습니다: {dir_path}")
            return False

        try:
            shutil.rmtree(path)
            logger.info(f"디렉토리 삭제 완료: {dir_path}")
            return True

        except Exception as e:
            logger.error(f"디렉토리 삭제 실패: {dir_path} - {e}")
            return False

    def get_disk_usage(self) -> dict:
        """
        디스크 사용량 정보를 반환합니다.

        Returns:
            dict: 디스크 사용량 정보
        """
        def get_dir_size(directory: Path) -> int:
            """디렉토리 전체 크기를 계산합니다."""
            total_size = 0
            for file in directory.rglob('*'):
                if file.is_file():
                    total_size += file.stat().st_size
            return total_size

        raw_size = get_dir_size(self.raw_dir) if self.raw_dir.exists() else 0
        extracted_size = get_dir_size(self.extracted_dir) if self.extracted_dir.exists() else 0
        metadata_size = get_dir_size(self.metadata_dir) if self.metadata_dir.exists() else 0

        total_size = raw_size + extracted_size + metadata_size

        return {
            'raw_dir_size': raw_size,
            'raw_dir_size_human': format_bytes(raw_size),
            'extracted_dir_size': extracted_size,
            'extracted_dir_size_human': format_bytes(extracted_size),
            'metadata_dir_size': metadata_size,
            'metadata_dir_size_human': format_bytes(metadata_size),
            'total_size': total_size,
            'total_size_human': format_bytes(total_size)
        }

    def list_files(
        self,
        directory: Optional[Union[str, Path]] = None,
        pattern: str = '*'
    ) -> list[Path]:
        """
        디렉토리 내 파일 목록을 반환합니다.

        Args:
            directory: 디렉토리 경로 (None이면 raw_dir)
            pattern: 파일 패턴 (예: '*.zip', 'HD*.zip')

        Returns:
            list[Path]: 파일 경로 리스트
        """
        if directory is None:
            directory = self.raw_dir
        else:
            directory = Path(directory)

        if not directory.exists():
            logger.warning(f"디렉토리가 존재하지 않습니다: {directory}")
            return []

        files = list(directory.rglob(pattern))
        files = [f for f in files if f.is_file()]

        return sorted(files)
