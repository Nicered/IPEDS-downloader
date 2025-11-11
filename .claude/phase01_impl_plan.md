# Phase 01 다운로더 구현 계획

## 개요

이 문서는 IPEDS Complete Data Files 다운로더의 구현 계획을 정의합니다. 모듈화된 구조로 설계하며, `src/modules/` 내에 기능별로 분리된 모듈을 배치합니다.

## 1. 디렉토리 구조

```
IPEDS-downloader/
├── .claude/                      # Claude 규칙 및 문서
│   ├── global_purpose.md
│   ├── coding_standards.md
│   ├── commit_conventions.md
│   ├── naming_conventions.md
│   ├── phase01_spec_downloader.md
│   ├── phase01_research_download_methods.md
│   └── phase01_impl_plan.md      # 이 문서
│
├── src/                          # 메인 소스 코드
│   ├── __init__.py
│   └── modules/                  # 모듈화된 컴포넌트
│       ├── __init__.py
│       │
│       ├── downloader/           # 다운로더 모듈
│       │   ├── __init__.py
│       │   ├── ipeds_downloader.py      # 메인 다운로더 클래스
│       │   └── download_manager.py      # 다운로드 관리
│       │
│       ├── client/               # HTTP 클라이언트 모듈
│       │   ├── __init__.py
│       │   └── ipeds_client.py          # IPEDS API 클라이언트
│       │
│       ├── storage/              # 파일 저장 모듈
│       │   ├── __init__.py
│       │   ├── file_manager.py          # 파일 관리
│       │   └── metadata_manager.py      # 메타데이터 관리
│       │
│       ├── config/               # 설정 모듈
│       │   ├── __init__.py
│       │   └── config_loader.py         # 설정 로더
│       │
│       ├── utils/                # 유틸리티 모듈
│       │   ├── __init__.py
│       │   ├── logger.py                # 로깅 유틸리티
│       │   ├── validators.py            # 검증 함수
│       │   ├── helpers.py               # 헬퍼 함수
│       │   └── year_detector.py         # 최신 연도 자동 감지
│       │
│       └── cli/                  # CLI 모듈
│           ├── __init__.py
│           ├── download_cmd.py          # download 명령어
│           ├── verify_cmd.py            # verify 명령어
│           ├── extract_cmd.py           # extract 명령어
│           ├── metadata_cmd.py          # metadata 명령어
│           └── list_cmd.py              # list 명령어
│
├── scripts/                      # 실행 스크립트
│   └── ipeds_cli.py              # 통합 CLI 진입점
│
├── config/                       # 설정 파일
│   ├── downloader_config.yaml    # 다운로더 설정
│   ├── surveys.yaml              # 서베이 정의
│   └── logging_config.yaml       # 로깅 설정
│
├── data/                         # 데이터 폴더
│   ├── raw/                      # 원본 다운로드 파일
│   │   ├── 2022/
│   │   ├── 2021/
│   │   └── ...
│   ├── extracted/                # 압축 해제 파일
│   └── metadata/                 # 메타데이터
│       ├── ipeds_files.json      # 파일 목록
│       ├── file_registry.json    # 파일 레지스트리
│       └── download_logs/        # 다운로드 로그
│
├── tests/                        # 테스트 코드
│   ├── __init__.py
│   ├── test_downloader.py
│   ├── test_ipeds_client.py
│   ├── test_file_manager.py
│   └── test_config_loader.py
│
├── logs/                         # 로그 파일
│   └── (자동 생성)
│
├── docs/                         # 프로젝트 문서
│
├── requirements.txt              # Python 의존성
├── .gitignore
└── README.md
```

## 2. 모듈 설계

### 2.1 downloader 모듈 (`src/modules/downloader/`)

**책임:** IPEDS 데이터 다운로드 전체 프로세스 관리

#### 주요 클래스

**IPEDSDownloader** (`ipeds_downloader.py`)
- 다운로드 워크플로우 전체 조정
- 설정 기반 다운로드 실행
- 진행상황 추적 및 보고
- 에러 처리 및 복구

**DownloadManager** (`download_manager.py`)
- 개별 다운로드 작업 관리
- 다운로드 큐 관리
- 동시 다운로드 제어 (필요시)
- 다운로드 상태 추적
- 재시도 로직 구현

#### 주요 기능
- 연도별/서베이별 다운로드
- 우선순위 기반 다운로드
- 중단/재개 기능
- 다운로드 통계 수집

### 2.2 client 모듈 (`src/modules/client/`)

**책임:** IPEDS 웹사이트와의 HTTP 통신

#### 주요 클래스

**IPEDSClient** (`ipeds_client.py`)
- HTTP 요청 관리 (requests 라이브러리)
- URL 생성 (서베이 코드 + 연도)
- 파일 다운로드 (스트리밍 방식)
- 파일 존재 확인 (HEAD 요청)
- 재시도 로직 (지수 백오프)
- 타임아웃 관리
- User-Agent 설정

#### 주요 기능
- `download_file()` - 파일 다운로드
- `check_file_exists()` - 파일 존재 확인
- `get_file_size()` - 파일 크기 조회
- `build_url()` - URL 생성

### 2.3 storage 모듈 (`src/modules/storage/`)

**책임:** 파일 시스템 및 메타데이터 관리

#### 주요 클래스

**FileManager** (`file_manager.py`)
- 디렉토리 구조 생성 및 관리
- 파일 저장 (바이너리 쓰기)
- ZIP 압축 해제 (zipfile 모듈)
- 파일 무결성 검증 (SHA256 체크섬)
- 디스크 공간 확인

**MetadataManager** (`metadata_manager.py`)
- 파일 레지스트리 관리 (JSON)
- 다운로드 로그 기록
- 파일 상태 추적 (PENDING, IN_PROGRESS, COMPLETED, FAILED)
- 다운로드 이력 관리
- 메타데이터 조회 및 필터링

#### 주요 기능
- 파일 저장 및 검증
- 메타데이터 CRUD 작업
- 상태 추적 및 업데이트

### 2.4 config 모듈 (`src/modules/config/`)

**책임:** 설정 파일 로드 및 관리

#### 주요 클래스

**ConfigLoader** (`config_loader.py`)
- YAML 파일 파싱 (PyYAML)
- 설정 검증 (필수 필드 확인)
- 기본값 설정
- 설정 병합 (기본값 + 사용자 설정)
- 환경 변수 지원 (선택사항)

#### 주요 기능
- 설정 로드 및 검증
- 설정 객체 제공
- 설정 값 접근 인터페이스

### 2.5 utils 모듈 (`src/modules/utils/`)

**책임:** 공통 유틸리티 함수 제공

#### 주요 모듈

**logger.py**
- 로깅 설정 초기화
- 로거 팩토리 함수
- 로그 포맷 설정
- 파일/콘솔 핸들러 설정

**validators.py**
- 파일 체크섬 계산 및 검증
- ZIP 파일 무결성 검증
- URL 유효성 검증
- 경로 유효성 검증

**helpers.py**
- 날짜/시간 유틸리티
- 파일 크기 포맷팅
- 문자열 처리 함수
- 진행률 계산 함수

**year_detector.py**
- 최신 IPEDS 데이터 연도 자동 감지
- IPEDS 웹사이트 탐색 (또는 시도 기반)
- 연도 범위 유효성 검증
- 현재 연도 기반 추정

### 2.6 cli 모듈 (`src/modules/cli/`)

**책임:** CLI 서브커맨드 구현

#### 주요 모듈

**download_cmd.py**
- `download` 명령어 구현
- 다운로드 관련 옵션 처리
- 다운로더 모듈 호출

**verify_cmd.py**
- `verify` 명령어 구현
- 파일 무결성 검증
- 다운로드 완료 여부 확인

**extract_cmd.py**
- `extract` 명령어 구현
- ZIP 파일 일괄 압축 해제
- 파일 관리자 호출

**metadata_cmd.py**
- `metadata` 명령어 구현
- 메타데이터 조회 및 관리
- 통계 표시

**list_cmd.py**
- `list` 명령어 구현
- 다운로드 가능한 파일 목록
- 다운로드된 파일 목록

## 3. 구현 단계별 계획

### Phase 01-A: 기본 다운로더 구현 (1주차)

#### 목표
핵심 다운로드 기능을 구현하여 IPEDS 데이터를 다운로드할 수 있는 기본 시스템 구축

#### 작업 항목

**1. 프로젝트 구조 설정**
- [ ] 디렉토리 구조 생성
- [ ] `__init__.py` 파일 작성 (모든 모듈)
- [ ] `.gitignore` 작성
- [ ] `requirements.txt` 작성

**2. 설정 시스템 구현**
- [ ] `ConfigLoader` 클래스 구현
- [ ] `config/downloader_config.yaml` 작성
- [ ] `config/surveys.yaml` 작성
- [ ] 설정 검증 로직 구현

**3. 유틸리티 구현**
- [ ] `utils/logger.py` 구현
- [ ] `utils/validators.py` 기본 함수 구현
- [ ] `utils/helpers.py` 기본 함수 구현

**4. HTTP 클라이언트 구현**
- [ ] `IPEDSClient` 클래스 기본 구조
- [ ] URL 생성 로직 (`build_url()`)
- [ ] 기본 다운로드 기능 (`download_file()`)
- [ ] 파일 존재 확인 (`check_file_exists()`)

**5. 파일 관리 구현**
- [ ] `FileManager` 클래스 기본 구조
- [ ] 디렉토리 생성 로직
- [ ] 파일 저장 로직
- [ ] 경로 생성 함수

**6. 메타데이터 관리 구현**
- [ ] `MetadataManager` 클래스 기본 구조
- [ ] JSON 기반 파일 레지스트리
- [ ] 다운로드 로그 기록 기능
- [ ] 상태 추적 기능

**7. 다운로드 매니저 구현**
- [ ] `DownloadManager` 클래스 구현
- [ ] 단일 파일 다운로드 로직
- [ ] 기본 에러 처리

**8. 메인 다운로더 구현**
- [ ] `IPEDSDownloader` 클래스 구현
- [ ] 다운로드 워크플로우 조정
- [ ] 설정 기반 다운로드 실행

**9. CLI 모듈 구현**
- [ ] `cli/download_cmd.py` 구현
- [ ] `cli/list_cmd.py` 구현
- [ ] `scripts/ipeds_cli.py` 통합 진입점 작성
- [ ] argparse 기반 서브커맨드 구조

**10. 연도 감지 유틸리티 구현**
- [ ] `utils/year_detector.py` 구현
- [ ] 최신 연도 자동 감지 로직
- [ ] 연도 범위 검증 함수

**11. 초기 테스트**
- [ ] 소규모 데이터셋으로 다운로드 테스트
- [ ] 에러 처리 확인
- [ ] CLI 명령어 테스트

#### 산출물
- 동작하는 기본 다운로더
- 1-2개 서베이 다운로드 가능
- 기본 로깅 및 메타데이터 기록

### Phase 01-B: 고급 기능 구현 (2주차)

#### 목표
안정성, 편의성, 효율성을 높이는 고급 기능 추가

#### 작업 항목

**1. 재시도 로직 강화**
- [ ] 지수 백오프 구현
- [ ] 재시도 횟수 제한
- [ ] 재시도 가능 에러 vs 치명적 에러 구분

**2. 진행상황 표시**
- [ ] tqdm 라이브러리 통합
- [ ] 실시간 진행률 표시
- [ ] 다운로드 속도 표시
- [ ] 남은 시간 추정

**3. ZIP 자동 압축 해제**
- [ ] `extract_zip()` 함수 구현
- [ ] 압축 해제 검증
- [ ] 자동/수동 모드 지원

**4. 파일 무결성 검증**
- [ ] SHA256 체크섬 계산
- [ ] ZIP 파일 무결성 확인
- [ ] 손상된 파일 재다운로드

**5. 중단/재개 기능**
- [ ] 다운로드 상태 저장
- [ ] 중단 지점부터 재개
- [ ] 부분 다운로드 이어받기 (Range 헤더)

**6. 전체 서베이 지원**
- [ ] 모든 서베이 코드 정의
- [ ] 서베이 변형 처리 (예: EF_A, EF_B)
- [ ] 우선순위 기반 다운로드

**7. CLI 확장 구현**
- [ ] `cli/verify_cmd.py` 구현
- [ ] `cli/extract_cmd.py` 구현
- [ ] `cli/metadata_cmd.py` 구현
- [ ] 다운로드 완료 확인
- [ ] 파일 무결성 일괄 검증
- [ ] 누락 파일 리포트

**8. 최신 데이터 지원**
- [ ] `year_detector.py` 개선
- [ ] "latest" 키워드 지원
- [ ] 자동 업데이트 확인

**9. 에러 처리 개선**
- [ ] 상세한 에러 메시지
- [ ] 에러 로그 파일 생성
- [ ] 에러 복구 전략

#### 산출물
- 안정적이고 편리한 다운로더
- 전체 서베이 다운로드 가능
- 중단/재개 지원
- 모듈별 CLI 접근 가능
- 최신 데이터 자동 감지

### Phase 01-C: 테스트 및 최적화 (3주차)

#### 목표
품질 보증, 문서화, 성능 최적화

#### 작업 항목

**1. 단위 테스트 작성**
- [ ] pytest 설정
- [ ] `test_ipeds_client.py` 작성
- [ ] `test_file_manager.py` 작성
- [ ] `test_metadata_manager.py` 작성
- [ ] `test_config_loader.py` 작성
- [ ] Mock 객체 활용

**2. 통합 테스트**
- [ ] 전체 워크플로우 테스트
- [ ] 실제 IPEDS 사이트 테스트 (소규모)
- [ ] 에러 시나리오 테스트
- [ ] 네트워크 오류 시뮬레이션

**3. 코드 문서화**
- [ ] 모든 클래스/함수에 docstring 추가
- [ ] 타입 힌트 추가
- [ ] 인라인 주석 (복잡한 로직)

**4. 사용자 문서 작성**
- [ ] `docs/user_guide.md` 작성
- [ ] 설치 가이드
- [ ] 사용 예제
- [ ] 문제 해결 가이드

**5. 성능 최적화**
- [ ] 메모리 사용 프로파일링
- [ ] 불필요한 파일 읽기/쓰기 제거
- [ ] 효율적인 데이터 구조 사용

**6. 코드 리팩토링**
- [ ] 중복 코드 제거
- [ ] 함수 분리 (큰 함수 → 작은 함수)
- [ ] 네이밍 개선
- [ ] PEP 8 준수 확인

**7. 최종 검증**
- [ ] 전체 서베이 다운로드 테스트
- [ ] 10년치 데이터 다운로드 테스트
- [ ] 에러 복구 테스트
- [ ] 성능 벤치마크

#### 산출물
- 프로덕션 레벨 다운로더
- 완전한 테스트 커버리지
- 포괄적인 문서

## 4. 주요 클래스 인터페이스 설계

### 4.1 IPEDSDownloader (메인 다운로더)

```python
class IPEDSDownloader:
    """
    IPEDS 데이터 다운로더 메인 클래스

    전체 다운로드 프로세스를 조정하고 관리합니다.
    """

    def __init__(self, config_path: str = None):
        """
        다운로더 초기화

        Args:
            config_path: 설정 파일 경로 (기본값: config/downloader_config.yaml)
        """
        pass

    def download_all(self) -> None:
        """
        설정된 모든 연도 및 서베이 다운로드

        Raises:
            DownloadError: 다운로드 실패 시
        """
        pass

    def download_year(self, year: int) -> None:
        """
        특정 연도의 모든 서베이 다운로드

        Args:
            year: 다운로드할 연도 (예: 2022)
        """
        pass

    def download_survey(self, survey_code: str, year: int) -> None:
        """
        특정 서베이 다운로드

        Args:
            survey_code: 서베이 코드 (예: 'HD', 'IC')
            year: 연도
        """
        pass

    def get_status(self) -> dict:
        """
        다운로드 상태 조회

        Returns:
            상태 정보 딕셔너리 (총 파일 수, 완료, 실패 등)
        """
        pass

    def resume(self) -> None:
        """
        중단된 다운로드 재개
        """
        pass
```

### 4.2 DownloadManager (다운로드 관리)

```python
class DownloadManager:
    """
    개별 다운로드 작업 관리
    """

    def __init__(self, client: IPEDSClient, file_manager: FileManager,
                 metadata_manager: MetadataManager):
        """
        다운로드 매니저 초기화

        Args:
            client: IPEDS 클라이언트
            file_manager: 파일 관리자
            metadata_manager: 메타데이터 관리자
        """
        pass

    def download_file(self, survey_code: str, year: int,
                     file_type: str = 'data') -> bool:
        """
        단일 파일 다운로드

        Args:
            survey_code: 서베이 코드
            year: 연도
            file_type: 파일 타입 ('data' 또는 'dict')

        Returns:
            성공 여부
        """
        pass

    def download_with_retry(self, url: str, output_path: str,
                           max_attempts: int = 3) -> bool:
        """
        재시도 로직을 포함한 다운로드

        Args:
            url: 다운로드 URL
            output_path: 저장 경로
            max_attempts: 최대 재시도 횟수

        Returns:
            성공 여부
        """
        pass
```

### 4.3 IPEDSClient (HTTP 클라이언트)

```python
class IPEDSClient:
    """
    IPEDS 웹사이트 HTTP 클라이언트
    """

    def __init__(self, base_url: str, timeout: tuple = (10, 300)):
        """
        클라이언트 초기화

        Args:
            base_url: IPEDS 기본 URL
            timeout: (연결 타임아웃, 읽기 타임아웃)
        """
        pass

    def build_url(self, survey_code: str, year: int,
                  file_type: str = 'data') -> str:
        """
        다운로드 URL 생성

        Args:
            survey_code: 서베이 코드
            year: 연도
            file_type: 'data' 또는 'dict'

        Returns:
            완전한 다운로드 URL
        """
        pass

    def download_file(self, url: str, output_path: str,
                     show_progress: bool = True) -> bool:
        """
        파일 다운로드 (스트리밍 방식)

        Args:
            url: 다운로드 URL
            output_path: 저장 경로
            show_progress: 진행률 표시 여부

        Returns:
            성공 여부

        Raises:
            requests.RequestException: HTTP 오류 시
        """
        pass

    def check_file_exists(self, url: str) -> bool:
        """
        파일 존재 확인 (HEAD 요청)

        Args:
            url: 확인할 URL

        Returns:
            파일 존재 여부
        """
        pass

    def get_file_size(self, url: str) -> int:
        """
        파일 크기 조회

        Args:
            url: 파일 URL

        Returns:
            파일 크기 (바이트)
        """
        pass
```

### 4.4 FileManager (파일 관리)

```python
class FileManager:
    """
    파일 시스템 관리
    """

    def __init__(self, base_dir: str):
        """
        파일 관리자 초기화

        Args:
            base_dir: 기본 저장 디렉토리
        """
        pass

    def save_file(self, data: bytes, filepath: str) -> None:
        """
        파일 저장

        Args:
            data: 파일 데이터
            filepath: 저장 경로

        Raises:
            IOError: 파일 쓰기 실패 시
        """
        pass

    def get_file_path(self, survey_code: str, year: int,
                     file_type: str = 'data') -> str:
        """
        파일 저장 경로 생성

        Args:
            survey_code: 서베이 코드
            year: 연도
            file_type: 파일 타입

        Returns:
            파일 저장 경로
        """
        pass

    def extract_zip(self, zip_path: str, extract_dir: str = None) -> None:
        """
        ZIP 파일 압축 해제

        Args:
            zip_path: ZIP 파일 경로
            extract_dir: 압축 해제 디렉토리 (기본값: 자동 생성)

        Raises:
            zipfile.BadZipFile: ZIP 파일 손상 시
        """
        pass

    def verify_file(self, filepath: str, expected_checksum: str = None) -> bool:
        """
        파일 무결성 검증

        Args:
            filepath: 파일 경로
            expected_checksum: 예상 체크섬 (SHA256)

        Returns:
            검증 성공 여부
        """
        pass

    def file_exists(self, filepath: str) -> bool:
        """
        파일 존재 확인

        Args:
            filepath: 파일 경로

        Returns:
            파일 존재 여부
        """
        pass
```

### 4.5 MetadataManager (메타데이터 관리)

```python
class MetadataManager:
    """
    다운로드 메타데이터 관리
    """

    def __init__(self, metadata_dir: str):
        """
        메타데이터 관리자 초기화

        Args:
            metadata_dir: 메타데이터 저장 디렉토리
        """
        pass

    def register_file(self, metadata: dict) -> None:
        """
        파일 등록

        Args:
            metadata: 파일 메타데이터 딕셔너리
                - survey_code: str
                - year: int
                - file_type: str
                - filename: str
                - url: str
                - file_size: int
                - status: str
        """
        pass

    def update_status(self, filename: str, status: str,
                     error_message: str = None) -> None:
        """
        파일 상태 업데이트

        Args:
            filename: 파일명
            status: 상태 (PENDING, IN_PROGRESS, COMPLETED, FAILED)
            error_message: 에러 메시지 (실패 시)
        """
        pass

    def get_downloaded_files(self) -> list:
        """
        다운로드된 파일 목록 조회

        Returns:
            파일 메타데이터 리스트
        """
        pass

    def get_pending_files(self) -> list:
        """
        대기 중인 파일 목록 조회

        Returns:
            대기 중인 파일 메타데이터 리스트
        """
        pass

    def log_download(self, log_entry: dict) -> None:
        """
        다운로드 로그 기록

        Args:
            log_entry: 로그 엔트리 딕셔너리
                - timestamp: str
                - survey_code: str
                - year: int
                - file_type: str
                - status: str
                - file_size: int
                - duration: float
                - retry_count: int
                - error_message: str (선택)
        """
        pass

    def get_statistics(self) -> dict:
        """
        다운로드 통계 조회

        Returns:
            통계 딕셔너리 (총 파일, 완료, 실패, 대기 등)
        """
        pass
```

### 4.6 ConfigLoader (설정 로더)

```python
class ConfigLoader:
    """
    YAML 설정 파일 로더
    """

    def __init__(self, config_path: str):
        """
        설정 로더 초기화

        Args:
            config_path: 설정 파일 경로

        Raises:
            FileNotFoundError: 설정 파일이 없을 때
            ValueError: 설정 검증 실패 시
        """
        pass

    def load(self) -> dict:
        """
        설정 로드

        Returns:
            설정 딕셔너리
        """
        pass

    def validate(self, config: dict) -> bool:
        """
        설정 검증

        Args:
            config: 설정 딕셔너리

        Returns:
            검증 성공 여부

        Raises:
            ValueError: 필수 필드 누락 또는 잘못된 값
        """
        pass

    def get(self, key: str, default: any = None) -> any:
        """
        설정 값 조회

        Args:
            key: 설정 키 (점 표기법 지원, 예: 'download.output_dir')
            default: 기본값

        Returns:
            설정 값
        """
        pass
```

## 5. 설정 파일 구조

### 5.1 downloader_config.yaml

```yaml
# IPEDS 다운로더 설정 파일

ipeds:
  # IPEDS 기본 URL
  base_url: "http://nces.ed.gov/ipeds/datacenter/data/"

download:
  # 출력 디렉토리
  output_dir: "./data/raw"
  extract_dir: "./data/extracted"
  metadata_dir: "./data/metadata"

  # 다운로드 연도 범위
  years:
    start: 2013
    end: "latest"     # "latest" 사용 시 최신 연도 자동 감지, 또는 2023 등 특정 연도

  # 다운로드할 서베이 (우선순위별)
  surveys:
    # 1순위: 필수 서베이
    priority_1:
      - HD      # Institutional Characteristics - Directory Information
      - IC      # Institutional Characteristics
      - EF      # Fall Enrollment
      - EFFY    # 12-month Enrollment

    # 2순위: 중요 서베이
    priority_2:
      - F       # Finance
      - C       # Completions
      - GR      # Graduation Rates

    # 3순위: 추가 서베이
    priority_3:
      - SAL     # Salaries
      - ADM     # Admissions
      - SFA     # Student Financial Aid
      - AL      # Academic Libraries
      - S       # Staff

  # 다운로드 옵션
  options:
    download_data_files: true      # 데이터 파일 다운로드 여부
    download_dict_files: true      # 사전 파일 다운로드 여부
    auto_extract: false            # 자동 압축 해제 여부
    skip_existing: true            # 기존 파일 건너뛰기
    verify_integrity: true         # 파일 무결성 검증

# 재시도 설정
retry:
  max_attempts: 3                  # 최대 재시도 횟수
  backoff_factor: 2                # 백오프 배수
  initial_delay: 2                 # 초기 대기 시간 (초)
  # 재시도 간격: 2초, 4초, 8초

# 타임아웃 설정
timeout:
  connect: 10                      # 연결 타임아웃 (초)
  read: 300                        # 읽기 타임아웃 (초, 5분)

# 성능 설정
performance:
  max_concurrent_downloads: 1     # 동시 다운로드 수 (서버 부하 방지)
  request_delay: 1                # 요청 간 대기 시간 (초)
  chunk_size: 8192                # 다운로드 청크 크기 (바이트)

# 로깅 설정
logging:
  level: "INFO"                    # 로그 레벨 (DEBUG, INFO, WARNING, ERROR)
  console_output: true             # 콘솔 출력 여부
  file_output: true                # 파일 출력 여부
  log_dir: "./logs"                # 로그 디렉토리
```

### 5.2 surveys.yaml

```yaml
# IPEDS 서베이 정의 파일

surveys:
  HD:
    name: "Institutional Characteristics - Directory Information"
    description: "기관 디렉토리 정보"
    priority: 1
    variants: []  # 변형 없음

  IC:
    name: "Institutional Characteristics"
    description: "기관 특성"
    priority: 1
    variants:
      - ""        # IC2022.zip
      - "_AY"     # IC2022_AY.zip (Academic Year)
      - "_PY"     # IC2022_PY.zip (Program Year)

  EF:
    name: "Fall Enrollment"
    description: "가을학기 등록"
    priority: 1
    variants:
      - "A"       # EF2022A.zip
      - "B"       # EF2022B.zip
      - "C"       # EF2022C.zip
      - "D"       # EF2022D.zip

  EFFY:
    name: "12-month Enrollment"
    description: "연간 등록"
    priority: 1
    variants: []

  F:
    name: "Finance"
    description: "재정"
    priority: 2
    variants:
      - ""        # F2022.zip
      - "_F1A"    # F2022_F1A.zip
      - "_F2"     # F2022_F2.zip
      - "_F3"     # F2022_F3.zip

  C:
    name: "Completions"
    description: "학위 수여"
    priority: 2
    variants:
      - ""        # C2022.zip
      - "_A"      # C2022_A.zip
      - "_B"      # C2022_B.zip
      - "_C"      # C2022_C.zip

  GR:
    name: "Graduation Rates"
    description: "졸업률"
    priority: 2
    variants:
      - ""        # GR2022.zip
      - "_L"      # GR2022_L.zip
      - "_PELL"   # GR2022_PELL.zip

  SAL:
    name: "Salaries"
    description: "급여"
    priority: 3
    variants:
      - "_IS"     # SAL2022_IS.zip (Instructional Staff)
      - "_NIS"    # SAL2022_NIS.zip (Non-instructional Staff)

  ADM:
    name: "Admissions"
    description: "입학"
    priority: 3
    variants: []

  SFA:
    name: "Student Financial Aid"
    description: "학자금 지원"
    priority: 3
    variants: []

  AL:
    name: "Academic Libraries"
    description: "학술 도서관"
    priority: 3
    variants: []

  S:
    name: "Staff"
    description: "교직원"
    priority: 3
    variants: []
```

### 5.3 logging_config.yaml

```yaml
# 로깅 설정 파일

version: 1
disable_existing_loggers: false

formatters:
  standard:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    datefmt: '%Y-%m-%d %H:%M:%S'

  detailed:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    datefmt: '%Y-%m-%d %H:%M:%S'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: standard
    stream: ext://sys.stdout

  file:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: detailed
    filename: logs/downloader.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

  error_file:
    class: logging.handlers.RotatingFileHandler
    level: ERROR
    formatter: detailed
    filename: logs/downloader_error.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

loggers:
  downloader:
    level: DEBUG
    handlers: [console, file, error_file]
    propagate: false

root:
  level: INFO
  handlers: [console, file]
```

## 6. CLI 인터페이스 설계

### 6.1 전체 CLI 구조

**통합 진입점**: `scripts/ipeds_cli.py`

```bash
python scripts/ipeds_cli.py <command> [options]
```

### 6.2 주요 서브커맨드

#### download - 데이터 다운로드
```bash
# 모든 데이터 다운로드
python scripts/ipeds_cli.py download --all

# 특정 연도 다운로드
python scripts/ipeds_cli.py download --year 2022

# 연도 범위 다운로드
python scripts/ipeds_cli.py download --start-year 2020 --end-year 2023

# 특정 서베이 다운로드
python scripts/ipeds_cli.py download --survey HD IC EF

# 특정 서베이 + 연도 조합
python scripts/ipeds_cli.py download --survey HD --year 2022

# 우선순위 기반 다운로드
python scripts/ipeds_cli.py download --priority 1

# 최신 데이터만 다운로드
python scripts/ipeds_cli.py download --latest

# 설정 파일 지정
python scripts/ipeds_cli.py download --all --config custom_config.yaml

# 자동 압축 해제 포함
python scripts/ipeds_cli.py download --all --extract
```

#### verify - 다운로드 검증
```bash
# 모든 다운로드 파일 검증
python scripts/ipeds_cli.py verify

# 특정 연도 검증
python scripts/ipeds_cli.py verify --year 2022

# 누락 파일 리포트
python scripts/ipeds_cli.py verify --report-missing

# 손상 파일 재다운로드
python scripts/ipeds_cli.py verify --fix
```

#### extract - 압축 해제
```bash
# 모든 ZIP 파일 압축 해제
python scripts/ipeds_cli.py extract --all

# 특정 연도 압축 해제
python scripts/ipeds_cli.py extract --year 2022

# 특정 파일 압축 해제
python scripts/ipeds_cli.py extract --file data/raw/2022/HD2022.zip
```

#### metadata - 메타데이터 관리
```bash
# 다운로드 통계 조회
python scripts/ipeds_cli.py metadata stats

# 파일 레지스트리 조회
python scripts/ipeds_cli.py metadata list

# 특정 파일 정보
python scripts/ipeds_cli.py metadata info HD2022.zip

# 다운로드 로그 조회
python scripts/ipeds_cli.py metadata logs --date 2025-11-11

# 메타데이터 초기화 (재구축)
python scripts/ipeds_cli.py metadata rebuild
```

#### list - 목록 조회
```bash
# 다운로드 가능한 모든 서베이 조회
python scripts/ipeds_cli.py list surveys

# 다운로드 가능한 연도 조회
python scripts/ipeds_cli.py list years

# 특정 연도의 파일 목록
python scripts/ipeds_cli.py list files --year 2022

# 다운로드된 파일 목록
python scripts/ipeds_cli.py list downloaded

# 대기 중인 다운로드 목록
python scripts/ipeds_cli.py list pending

# 실패한 다운로드 목록
python scripts/ipeds_cli.py list failed
```

### 6.3 공통 옵션

모든 명령어에서 사용 가능한 옵션:
```bash
--config PATH         # 설정 파일 경로
--verbose, -v         # 상세 출력
--quiet, -q           # 최소 출력
--log-level LEVEL     # 로그 레벨 (DEBUG, INFO, WARNING, ERROR)
--help, -h            # 도움말
```

### 6.4 CLI 구현 구조

**ipeds_cli.py (메인 진입점)**
```python
import argparse
from src.modules.cli import (
    download_cmd,
    verify_cmd,
    extract_cmd,
    metadata_cmd,
    list_cmd
)

def main():
    """메인 CLI 진입점"""
    parser = argparse.ArgumentParser(
        description="IPEDS 데이터 다운로더 CLI"
    )

    subparsers = parser.add_subparsers(dest='command', help='사용 가능한 명령어')

    # download 서브커맨드
    download_cmd.setup_parser(subparsers)

    # verify 서브커맨드
    verify_cmd.setup_parser(subparsers)

    # extract 서브커맨드
    extract_cmd.setup_parser(subparsers)

    # metadata 서브커맨드
    metadata_cmd.setup_parser(subparsers)

    # list 서브커맨드
    list_cmd.setup_parser(subparsers)

    args = parser.parse_args()

    # 명령어 실행
    if args.command == 'download':
        download_cmd.execute(args)
    elif args.command == 'verify':
        verify_cmd.execute(args)
    elif args.command == 'extract':
        extract_cmd.execute(args)
    elif args.command == 'metadata':
        metadata_cmd.execute(args)
    elif args.command == 'list':
        list_cmd.execute(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
```

**download_cmd.py (예시)**
```python
"""download 명령어 구현"""

def setup_parser(subparsers):
    """download 서브파서 설정"""
    parser = subparsers.add_parser('download', help='IPEDS 데이터 다운로드')

    parser.add_argument('--all', action='store_true', help='모든 데이터 다운로드')
    parser.add_argument('--year', type=int, help='특정 연도 다운로드')
    parser.add_argument('--start-year', type=int, help='시작 연도')
    parser.add_argument('--end-year', type=int, help='종료 연도')
    parser.add_argument('--survey', nargs='+', help='서베이 코드 목록')
    parser.add_argument('--priority', type=int, help='우선순위 (1, 2, 3)')
    parser.add_argument('--latest', action='store_true', help='최신 데이터만')
    parser.add_argument('--extract', action='store_true', help='자동 압축 해제')
    parser.add_argument('--config', help='설정 파일 경로')

    return parser

def execute(args):
    """download 명령어 실행"""
    from src.modules.downloader import IPEDSDownloader
    from src.modules.utils.year_detector import detect_latest_year

    # 설정 로드
    config_path = args.config or 'config/downloader_config.yaml'
    downloader = IPEDSDownloader(config_path)

    # 최신 연도 감지
    if args.latest:
        latest_year = detect_latest_year()
        print(f"최신 연도 감지: {latest_year}")
        downloader.download_year(latest_year)

    # 전체 다운로드
    elif args.all:
        downloader.download_all()

    # 특정 연도
    elif args.year:
        downloader.download_year(args.year)

    # 연도 범위
    elif args.start_year and args.end_year:
        for year in range(args.start_year, args.end_year + 1):
            downloader.download_year(year)

    # 특정 서베이
    elif args.survey:
        for survey_code in args.survey:
            if args.year:
                downloader.download_survey(survey_code, args.year)
            else:
                # 설정된 모든 연도
                downloader.download_survey_all_years(survey_code)

    else:
        print("다운로드 옵션을 지정해주세요. --help로 도움말을 확인하세요.")
```

### 6.5 YearDetector 클래스 설계

**year_detector.py**
```python
"""최신 IPEDS 데이터 연도 자동 감지"""

import requests
from datetime import datetime

def detect_latest_year(base_url: str = "http://nces.ed.gov/ipeds/datacenter/data/") -> int:
    """
    최신 IPEDS 데이터 연도 감지

    전략:
    1. 현재 연도부터 역순으로 HD 파일 존재 확인
    2. 존재하는 가장 최근 연도 반환

    Args:
        base_url: IPEDS 기본 URL

    Returns:
        최신 연도
    """
    current_year = datetime.now().year

    # 현재 연도부터 3년 전까지 확인
    for year in range(current_year, current_year - 4, -1):
        test_url = f"{base_url}HD{year}.zip"

        try:
            response = requests.head(test_url, timeout=5)
            if response.status_code == 200:
                return year
        except requests.RequestException:
            continue

    # 감지 실패 시 현재 연도 - 1 반환
    return current_year - 1

def validate_year_range(start_year: int, end_year: int) -> bool:
    """
    연도 범위 유효성 검증

    Args:
        start_year: 시작 연도
        end_year: 종료 연도

    Returns:
        유효 여부
    """
    if start_year > end_year:
        return False

    if start_year < 1980:  # IPEDS 데이터 최소 연도
        return False

    current_year = datetime.now().year
    if end_year > current_year:
        return False

    return True
```

### 6.6 사용 예시

#### 전체 워크플로우
```bash
# 1. 사용 가능한 서베이 확인
python scripts/ipeds_cli.py list surveys

# 2. 최신 데이터 다운로드
python scripts/ipeds_cli.py download --latest --survey HD IC EF

# 3. 다운로드 검증
python scripts/ipeds_cli.py verify --year 2023

# 4. 압축 해제
python scripts/ipeds_cli.py extract --year 2023

# 5. 통계 확인
python scripts/ipeds_cli.py metadata stats
```

#### 대량 다운로드
```bash
# 모든 데이터 다운로드 (최신까지)
python scripts/ipeds_cli.py download --all --verbose

# 우선순위 1 서베이만 (핵심 데이터)
python scripts/ipeds_cli.py download --priority 1 --start-year 2013 --end-year latest
```

## 7. 구현 시작 순서

### 단계별 구현 순서 (권장)

#### 1단계: 기반 구축
1. ✅ 디렉토리 구조 생성
2. ✅ `requirements.txt` 작성
3. ✅ `.gitignore` 작성
4. ✅ 설정 파일 작성 (YAML)

#### 2단계: 유틸리티 구현
1. ✅ `utils/logger.py` 구현
2. ✅ `utils/helpers.py` 구현
3. ✅ `utils/validators.py` 구현

#### 3단계: 설정 로더 구현
1. ✅ `config/config_loader.py` 구현
2. ✅ 설정 검증 로직
3. ✅ 테스트

#### 4단계: HTTP 클라이언트 구현
1. ✅ `client/ipeds_client.py` 기본 구조
2. ✅ URL 생성 (`build_url()`)
3. ✅ 파일 다운로드 (`download_file()`)
4. ✅ 파일 존재 확인 (`check_file_exists()`)
5. ✅ 테스트

#### 5단계: 파일 관리 구현
1. ✅ `storage/file_manager.py` 기본 구조
2. ✅ 디렉토리 생성 로직
3. ✅ 파일 저장 로직
4. ✅ 경로 생성 함수
5. ✅ 테스트

#### 6단계: 메타데이터 관리 구현
1. ✅ `storage/metadata_manager.py` 기본 구조
2. ✅ JSON 파일 레지스트리
3. ✅ 상태 추적 기능
4. ✅ 로그 기록 기능
5. ✅ 테스트

#### 7단계: 다운로드 매니저 구현
1. ✅ `downloader/download_manager.py` 기본 구조
2. ✅ 단일 파일 다운로드
3. ✅ 재시도 로직
4. ✅ 에러 처리
5. ✅ 테스트

#### 8단계: 메인 다운로더 구현
1. ✅ `downloader/ipeds_downloader.py` 기본 구조
2. ✅ 워크플로우 조정
3. ✅ 설정 기반 실행
4. ✅ 상태 관리
5. ✅ 테스트

#### 9단계: 실행 스크립트 작성
1. ✅ `scripts/download_ipeds.py` 작성
2. ✅ CLI 인터페이스 (argparse)
3. ✅ 명령어 구현
4. ✅ 테스트

#### 10단계: 통합 테스트
1. ✅ 소규모 데이터 다운로드 테스트
2. ✅ 에러 시나리오 테스트
3. ✅ 전체 워크플로우 검증

## 8. 의존성 (requirements.txt)

```
# HTTP 클라이언트
requests>=2.31.0

# YAML 파싱
pyyaml>=6.0

# 진행률 표시
tqdm>=4.66.0

# 테스트
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.1

# 코드 품질
flake8>=6.1.0
black>=23.7.0

# 타입 체크 (선택)
mypy>=1.5.0

# 로깅 (내장 logging 사용, 필요 시)
# python-json-logger>=2.0.7
```

## 9. 성공 기준

### Phase 01-A 완료 기준
- ✅ 기본 다운로더 동작
- ✅ HD, IC 서베이 다운로드 성공
- ✅ 최근 1-2년 데이터 다운로드 가능
- ✅ 메타데이터 기록 동작
- ✅ 기본 에러 처리
- ✅ CLI 기본 명령어 (download, list) 동작

### Phase 01-B 완료 기준
- ✅ 모든 우선순위 서베이 지원
- ✅ 재시도 로직 동작
- ✅ 진행률 표시
- ✅ 중단/재개 기능
- ✅ 파일 무결성 검증
- ✅ 전체 CLI 서브커맨드 구현
- ✅ 최신 연도 자동 감지 기능

### Phase 01-C 완료 기준
- ✅ 단위 테스트 80% 이상 커버리지
- ✅ 통합 테스트 통과
- ✅ 10년치 데이터 다운로드 성공
- ✅ 문서 완성
- ✅ 성능 최적화 완료

### 전체 Phase 01 완료 기준
- ✅ 모든 IPEDS Complete Data Files 다운로드 가능
- ✅ 95% 이상 다운로드 성공률
- ✅ 안정적인 에러 처리 및 복구
- ✅ 포괄적인 테스트 및 문서
- ✅ Phase 02로 넘어갈 준비 완료

## 10. 리스크 및 대응 방안

### 리스크 1: IPEDS 웹사이트 구조 변경
**대응:**
- URL 패턴을 설정 파일에 분리
- 정기적인 URL 유효성 검증
- 웹 스크래핑 대안 준비

### 리스크 2: 네트워크 불안정
**대응:**
- 강력한 재시도 로직
- 부분 다운로드 재개
- 타임아웃 설정 조정

### 리스크 3: 디스크 공간 부족
**대응:**
- 다운로드 전 공간 확인
- 경고 메시지 출력
- 자동 중단 및 복구

### 리스크 4: 예상치 못한 파일 형식
**대응:**
- 파일 형식 검증
- 에러 로깅
- 수동 처리 가이드

## 11. 다음 Phase 준비사항

Phase 02 (데이터 변환)을 위한 준비:
- 다운로드된 모든 파일 목록
- 데이터 사전 파일 (Dict.zip)
- 파일 메타데이터 (레지스트리)
- 다운로드 로그 (문제 파악용)

---

**이 구현 계획은 Phase 01 다운로더 개발의 청사진입니다. 실제 구현 과정에서 발견되는 이슈에 따라 유연하게 조정될 수 있습니다.**
