"""
설정 로더 모듈

이 모듈은 YAML 설정 파일을 로드하고 관리하는 기능을 제공합니다.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from ..utils.validators import validate_config


logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    설정 파일을 로드하고 관리하는 클래스입니다.
    """

    def __init__(self, config_dir: str = "config"):
        """
        ConfigLoader를 초기화합니다.

        Args:
            config_dir: 설정 파일이 있는 디렉토리 경로
        """
        self.config_dir = Path(config_dir)
        self.config: Dict[str, Any] = {}
        self.surveys: Dict[str, Any] = {}

    def load_config(self, config_file: str = "downloader_config.yaml") -> Dict[str, Any]:
        """
        다운로더 설정 파일을 로드합니다.

        Args:
            config_file: 설정 파일명

        Returns:
            Dict: 설정 딕셔너리

        Raises:
            FileNotFoundError: 설정 파일이 없는 경우
            ValueError: 설정 파일이 유효하지 않은 경우
        """
        config_path = self.config_dir / config_file

        if not config_path.exists():
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)

            logger.info(f"설정 파일 로드 완료: {config_path}")

            # 설정 검증
            is_valid, error_msg = validate_config(self.config)
            if not is_valid:
                raise ValueError(f"설정 파일 검증 실패: {error_msg}")

            # 환경 변수로 경로 확장
            self._expand_paths()

            return self.config

        except yaml.YAMLError as e:
            raise ValueError(f"YAML 파싱 오류: {e}")

    def load_surveys(self, surveys_file: str = "surveys.yaml") -> Dict[str, Any]:
        """
        서베이 정의 파일을 로드합니다.

        Args:
            surveys_file: 서베이 파일명

        Returns:
            Dict: 서베이 딕셔너리

        Raises:
            FileNotFoundError: 서베이 파일이 없는 경우
        """
        surveys_path = self.config_dir / surveys_file

        if not surveys_path.exists():
            raise FileNotFoundError(f"서베이 파일을 찾을 수 없습니다: {surveys_path}")

        try:
            with open(surveys_path, 'r', encoding='utf-8') as f:
                self.surveys = yaml.safe_load(f)

            logger.info(f"서베이 파일 로드 완료: {surveys_path}")
            return self.surveys

        except yaml.YAMLError as e:
            raise ValueError(f"YAML 파싱 오류: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        설정 값을 가져옵니다.

        중첩된 키는 점(.)으로 구분합니다.
        예: "ipeds.base_url"

        Args:
            key: 설정 키 (점으로 구분된 경로)
            default: 키가 없을 때 반환할 기본값

        Returns:
            Any: 설정 값
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_survey_info(self, survey_code: str) -> Optional[Dict[str, Any]]:
        """
        특정 서베이의 정보를 가져옵니다.

        Args:
            survey_code: 서베이 코드

        Returns:
            Dict: 서베이 정보, 없으면 None
        """
        surveys = self.surveys.get('surveys', {})
        return surveys.get(survey_code)

    def get_all_survey_codes(self) -> list[str]:
        """
        모든 서베이 코드 목록을 반환합니다.

        Returns:
            list[str]: 서베이 코드 리스트
        """
        surveys = self.surveys.get('surveys', {})
        return list(surveys.keys())

    def get_survey_variants(self, survey_code: str) -> list[str]:
        """
        특정 서베이의 변형(variants) 목록을 반환합니다.

        예: IC -> ['IC', 'IC_AY']

        Args:
            survey_code: 서베이 코드

        Returns:
            list[str]: 변형 코드 리스트
        """
        survey_info = self.get_survey_info(survey_code)
        if not survey_info:
            return [survey_code]

        variants = survey_info.get('variants', [])
        return variants if variants else [survey_code]

    def get_surveys_by_priority(self, priority: int) -> list[str]:
        """
        우선순위별 서베이 코드 목록을 반환합니다.

        Args:
            priority: 우선순위 (1, 2, 3)

        Returns:
            list[str]: 서베이 코드 리스트
        """
        surveys = self.surveys.get('surveys', {})
        result = []

        for code, info in surveys.items():
            if info.get('priority') == priority:
                result.append(code)

        return result

    def _expand_paths(self) -> None:
        """
        설정의 경로 값을 환경 변수와 절대 경로로 확장합니다.
        """
        storage_config = self.config.get('storage', {})

        # 스토리지 경로 확장
        path_keys = ['raw_dir', 'extracted_dir', 'metadata_dir', 'log_dir']

        for key in path_keys:
            if key in storage_config:
                path = storage_config[key]
                # 환경 변수 확장
                path = os.path.expandvars(path)
                # 홈 디렉토리 확장
                path = os.path.expanduser(path)
                # 절대 경로로 변환
                path = os.path.abspath(path)
                storage_config[key] = path

    def save_config(self, config_file: str = "downloader_config.yaml") -> None:
        """
        현재 설정을 파일로 저장합니다.

        Args:
            config_file: 저장할 설정 파일명
        """
        config_path = self.config_dir / config_file

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)

            logger.info(f"설정 파일 저장 완료: {config_path}")

        except Exception as e:
            logger.error(f"설정 파일 저장 실패: {e}")
            raise

    def update_config(self, key: str, value: Any) -> None:
        """
        설정 값을 업데이트합니다.

        Args:
            key: 설정 키 (점으로 구분된 경로)
            value: 새로운 값
        """
        keys = key.split('.')
        config = self.config

        # 마지막 키를 제외한 모든 키를 탐색
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # 마지막 키에 값 설정
        config[keys[-1]] = value
        logger.debug(f"설정 업데이트: {key} = {value}")

    def merge_config(self, override_config: Dict[str, Any]) -> None:
        """
        현재 설정에 다른 설정을 병합합니다.

        Args:
            override_config: 병합할 설정 딕셔너리
        """
        self._deep_merge(self.config, override_config)
        logger.debug("설정 병합 완료")

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """
        두 딕셔너리를 깊이 우선으로 병합합니다.

        Args:
            base: 기본 딕셔너리
            override: 덮어쓸 딕셔너리

        Returns:
            dict: 병합된 딕셔너리
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

        return base

    def print_config(self) -> None:
        """
        현재 설정을 출력합니다 (디버깅용).
        """
        print("\n=== 현재 설정 ===")
        print(yaml.dump(self.config, default_flow_style=False, allow_unicode=True))


def load_default_config(config_dir: str = "config") -> ConfigLoader:
    """
    기본 설정을 로드하는 헬퍼 함수입니다.

    Args:
        config_dir: 설정 파일 디렉토리

    Returns:
        ConfigLoader: 설정이 로드된 ConfigLoader 인스턴스
    """
    loader = ConfigLoader(config_dir)
    loader.load_config()
    loader.load_surveys()
    return loader
