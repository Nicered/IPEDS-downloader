"""
로깅 유틸리티 모듈

이 모듈은 IPEDS 다운로더를 위한 로깅 설정 및 로거 생성 기능을 제공합니다.
"""

import logging
import logging.config
import os
from pathlib import Path
from typing import Optional

import yaml


def setup_logging(
    config_path: Optional[str] = None,
    default_level: int = logging.INFO,
    log_dir: Optional[str] = None
) -> None:
    """
    로깅 설정을 초기화합니다.

    Args:
        config_path: 로깅 설정 파일 경로 (YAML)
        default_level: 기본 로그 레벨
        log_dir: 로그 파일 저장 디렉토리
    """
    # 로그 디렉토리 생성
    if log_dir:
        Path(log_dir).mkdir(parents=True, exist_ok=True)

    # 설정 파일이 제공되고 존재하는 경우
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logging.config.dictConfig(config)
            logging.info(f"로깅 설정 파일 로드됨: {config_path}")
        except Exception as e:
            # 설정 파일 로드 실패 시 기본 설정 사용
            _setup_default_logging(default_level, log_dir)
            logging.warning(f"로깅 설정 파일 로드 실패, 기본 설정 사용: {e}")
    else:
        # 설정 파일이 없으면 기본 설정 사용
        _setup_default_logging(default_level, log_dir)


def _setup_default_logging(level: int, log_dir: Optional[str] = None) -> None:
    """
    기본 로깅 설정을 구성합니다.

    Args:
        level: 로그 레벨
        log_dir: 로그 파일 저장 디렉토리
    """
    # 로그 포맷 설정
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # 기본 설정
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=[]
    )

    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(log_format, date_format)
    console_handler.setFormatter(console_formatter)

    # 루트 로거에 핸들러 추가
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)

    # 파일 핸들러 (log_dir이 제공된 경우)
    if log_dir:
        log_file = os.path.join(log_dir, "ipeds_downloader.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    지정된 이름으로 로거를 가져옵니다.

    Args:
        name: 로거 이름 (일반적으로 모듈 이름)

    Returns:
        Logger: 로거 인스턴스
    """
    return logging.getLogger(name)


def set_log_level(logger_name: str, level: int) -> None:
    """
    특정 로거의 로그 레벨을 설정합니다.

    Args:
        logger_name: 로거 이름
        level: 로그 레벨 (logging.DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)


def disable_external_loggers() -> None:
    """
    외부 라이브러리의 로거를 비활성화하거나 레벨을 낮춥니다.

    urllib3, requests 등의 로거가 너무 많은 로그를 출력하는 것을 방지합니다.
    """
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
