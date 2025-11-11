# 네이밍 규칙 (Naming Conventions)

이 문서는 IPEDS-downloader 프로젝트에서 사용하는 파일, 폴더, 문서의 네이밍 규칙을 정의합니다. **Claude는 파일 및 문서 작성 시 이 규칙을 반드시 준수해야 합니다.**

## 1. 기본 원칙

### 1.1 언어 규칙
- ✅ **파일명**: 영어 소문자 + 언더바(_) 사용 (snake_case)
- ✅ **폴더명**: 영어 소문자 + 언더바(_) 사용 (snake_case)
- ✅ **문서 내용**: 한글 작성
- ✅ **변수/함수명**: 영어 snake_case

### 1.2 금지사항
- ❌ 파일명에 한글 사용 금지
- ❌ 파일명에 공백 사용 금지
- ❌ 파일명에 하이픈(-) 사용 지양 (언더바 사용)
- ❌ 대소문자 혼용 금지 (CamelCase, PascalCase)

## 2. 문서 네이밍 규칙

### 2.1 프로젝트 전역 문서

**패턴**: `global_{목적}.md`

프로젝트 전체에 적용되는 중요한 문서에 사용합니다.

**예시:**
- `global_purpose.md` - 프로젝트 전체 목적
- `global_architecture.md` - 전체 아키텍처
- `global_roadmap.md` - 프로젝트 로드맵

**용도:**
- 프로젝트 비전 및 목표
- 전체 설계 문서
- 장기 계획 및 마일스톤

### 2.2 Phase별 명세서

**패턴**: `phase{번호}_spec_{주제}.md`

각 Phase의 요구사항 및 명세를 정의하는 문서입니다.

**형식:**
- `phase##`: 두 자리 숫자 (01, 02, 03...)
- `spec`: 명세서임을 나타냄
- `{주제}`: 명세 대상 (snake_case)

**예시:**
- `phase01_spec_downloader.md` - Phase 01 다운로더 명세
- `phase02_spec_transformer.md` - Phase 02 변환기 명세
- `phase03_spec_database.md` - Phase 03 데이터베이스 명세

**용도:**
- 기능 요구사항 정의
- 기술 명세 작성
- 구현 가이드라인
- 성공 기준 정의

### 2.3 Phase별 연구 문서

**패턴**: `phase{번호}_research_{주제}.md`

구현 전 조사 및 연구 내용을 정리하는 문서입니다.

**형식:**
- `phase##`: 두 자리 숫자 (01, 02, 03...)
- `research`: 연구 문서임을 나타냄
- `{주제}`: 연구 대상 (snake_case)

**예시:**
- `phase01_research_download_methods.md` - 다운로드 방법 조사
- `phase02_research_nlp_conversion.md` - 자연어 변환 기술 연구
- `phase03_research_database_options.md` - 데이터베이스 옵션 비교

**용도:**
- 기술 조사 결과
- 구현 방법론 연구
- 도구 및 라이브러리 비교
- 참고 자료 정리

### 2.4 Phase별 구현 문서

**패턴**: `phase{번호}_impl_{주제}.md`

실제 구현 내용 및 개발 노트를 기록하는 문서입니다.

**형식:**
- `phase##`: 두 자리 숫자 (01, 02, 03...)
- `impl`: 구현 문서임을 나타냄
- `{주제}`: 구현 내용 (snake_case)

**예시:**
- `phase01_impl_downloader.md` - 다운로더 구현 노트
- `phase02_impl_parser.md` - 파서 구현 상세
- `phase03_impl_schema.md` - 스키마 구현 내역

**용도:**
- 구현 과정 기록
- 기술적 의사결정 내역
- 발생한 이슈 및 해결방안
- 코드 구조 설명

### 2.5 규칙 및 표준 문서

**패턴**: `{주제}_standards.md` 또는 `{주제}_conventions.md`

프로젝트 규칙, 표준, 컨벤션을 정의하는 문서입니다.

**예시:**
- `coding_standards.md` - 코딩 규칙
- `commit_conventions.md` - 커밋 규칙
- `naming_conventions.md` - 네이밍 규칙
- `api_conventions.md` - API 규칙
- `testing_standards.md` - 테스트 표준

**용도:**
- 팀 협업 규칙
- 코드 스타일 가이드
- 문서 작성 규칙
- 프로세스 표준

### 2.6 가이드 문서

**패턴**: `{주제}_guide.md`

사용법, 설치법 등의 가이드 문서입니다.

**예시:**
- `installation_guide.md` - 설치 가이드
- `user_guide.md` - 사용자 가이드
- `development_guide.md` - 개발 가이드
- `deployment_guide.md` - 배포 가이드

**용도:**
- 설치 및 설정 방법
- 사용 방법 설명
- 개발 환경 구축
- 배포 절차

## 3. 코드 파일 네이밍

### 3.1 Python 스크립트

**패턴**: `{기능}_[타입].py`

**예시:**
- `downloader.py` - 메인 다운로더
- `ipeds_client.py` - IPEDS 클라이언트
- `file_manager.py` - 파일 관리자
- `metadata_manager.py` - 메타데이터 관리자
- `config_loader.py` - 설정 로더
- `utils.py` - 유틸리티 함수

**타입 접미사 (선택사항):**
- `_client` - API/웹 클라이언트
- `_manager` - 관리자 클래스
- `_handler` - 핸들러
- `_parser` - 파서
- `_validator` - 검증기
- `_builder` - 빌더

### 3.2 설정 파일

**패턴**: `{대상}_config.{확장자}`

**예시:**
- `downloader_config.yaml` - 다운로더 설정
- `database_config.json` - 데이터베이스 설정
- `logging_config.yaml` - 로깅 설정

### 3.3 테스트 파일

**패턴**: `test_{대상}.py`

**예시:**
- `test_downloader.py` - 다운로더 테스트
- `test_ipeds_client.py` - 클라이언트 테스트
- `test_file_manager.py` - 파일 관리자 테스트

## 4. 데이터 파일 네이밍

### 4.1 원본 데이터

**패턴**: IPEDS 원본 파일명 그대로 유지

**예시:**
- `HD2022.zip` - IPEDS 원본 파일
- `IC2022_AY.zip` - IPEDS 원본 파일
- `HD2022_Dict.zip` - IPEDS 사전 파일

**규칙:**
- ✅ 원본 파일명 변경 금지
- ✅ 다운로드 출처 추적 가능

### 4.2 메타데이터 파일

**패턴**: `{목적}_[대상].json`

**예시:**
- `download_log.json` - 다운로드 로그
- `file_registry.json` - 파일 목록
- `ipeds_files.json` - IPEDS 파일 메타데이터
- `mapping_dictionary.json` - 매핑 사전

### 4.3 처리된 데이터

**패턴**: `{서베이코드}_{연도}_processed.{확장자}`

**예시:**
- `hd_2022_processed.csv` - 처리된 HD 데이터
- `ic_2022_processed.parquet` - 처리된 IC 데이터
- `ef_2022_processed.csv` - 처리된 EF 데이터

**규칙:**
- ✅ 소문자 사용
- ✅ 연도 4자리 표기
- ✅ `_processed` 접미사

## 5. 폴더 네이밍

### 5.1 최상위 폴더

```
.claude/          # Claude 규칙 및 문서
docs/             # 프로젝트 문서
scripts/          # Python 스크립트
src/              # 메인 소스 코드
tests/            # 테스트 코드
data/             # 데이터 폴더
config/           # 설정 파일
logs/             # 로그 파일
```

### 5.2 데이터 하위 폴더

```
data/
├── raw/          # 원본 데이터
├── extracted/    # 압축 해제된 데이터
├── processed/    # 처리된 데이터
├── metadata/     # 메타데이터
└── mappings/     # 매핑 사전
```

### 5.3 연도별 폴더

**패턴**: 4자리 연도 사용

**예시:**
```
data/raw/
├── 2022/
├── 2021/
└── 2020/
```

## 6. 로그 파일 네이밍

### 6.1 일반 로그

**패턴**: `{모듈}_{YYYYMMDD}_[HHMMSS].log`

**예시:**
- `downloader_20251111_103000.log`
- `transformer_20251111_143022.log`
- `database_20251111_180500.log`

### 6.2 에러 로그

**패턴**: `{모듈}_error_{YYYYMMDD}.log`

**예시:**
- `downloader_error_20251111.log`
- `parser_error_20251111.log`

## 7. 변수 및 함수 네이밍 (Python)

### 7.1 변수명

**패턴**: `snake_case`

**예시:**
```python
# 좋은 예
file_path = "/data/raw/HD2022.zip"
download_status = "COMPLETED"
retry_count = 0
base_url = "http://nces.ed.gov/ipeds/"

# 나쁜 예
filePath = "/data/raw/HD2022.zip"  # camelCase
DownloadStatus = "COMPLETED"        # PascalCase
retry-count = 0                     # 하이픈 사용
```

### 7.2 함수명

**패턴**: `동사_명사` 형태의 snake_case

**예시:**
```python
# 좋은 예
def download_file(url, output_path):
    pass

def parse_metadata(json_file):
    pass

def validate_checksum(file_path, expected_hash):
    pass

def extract_zip_file(zip_path, extract_dir):
    pass

# 나쁜 예
def downloadFile(url, output_path):  # camelCase
    pass

def ParseMetadata(json_file):        # PascalCase
    pass
```

### 7.3 클래스명

**패턴**: `PascalCase`

**예시:**
```python
# 좋은 예
class IPEDSDownloader:
    pass

class FileManager:
    pass

class MetadataManager:
    pass

# 나쁜 예
class ipeds_downloader:    # snake_case
    pass

class file_Manager:        # 혼용
    pass
```

### 7.4 상수명

**패턴**: `UPPER_SNAKE_CASE`

**예시:**
```python
# 좋은 예
BASE_URL = "http://nces.ed.gov/ipeds/datacenter/data/"
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 300
START_YEAR = 2013
END_YEAR = 2023

# 나쁜 예
baseUrl = "http://..."      # camelCase
max_retry_count = 3         # 소문자
```

## 8. Git 브랜치 네이밍

### 8.1 기능 브랜치

**패턴**: `feature/{기능명}`

**예시:**
- `feature/downloader`
- `feature/metadata_parser`
- `feature/database_schema`

### 8.2 수정 브랜치

**패턴**: `fix/{이슈명}`

**예시:**
- `fix/download_timeout`
- `fix/encoding_error`
- `fix/missing_files`

### 8.3 문서 브랜치

**패턴**: `docs/{문서명}`

**예시:**
- `docs/api_documentation`
- `docs/user_guide`

## 9. 예외 사항

### 9.1 유지해야 하는 파일명
- `README.md` - 관례상 대문자 유지
- `LICENSE` - 관례상 대문자 유지
- `.gitignore` - Git 표준
- `requirements.txt` - Python 표준

### 9.2 제3자 파일
- IPEDS 원본 파일명은 그대로 유지
- 외부 라이브러리 파일은 원본 유지

## 10. 네이밍 체크리스트

파일/폴더 생성 전 확인사항:
- [ ] 영어 소문자 사용
- [ ] 언더바(_)로 단어 구분 (snake_case)
- [ ] 하이픈(-) 사용하지 않음
- [ ] 공백 사용하지 않음
- [ ] 명확하고 설명적인 이름
- [ ] 일관된 패턴 적용
- [ ] 적절한 접두사/접미사 사용

---

**이 네이밍 규칙은 프로젝트 전체에서 일관성을 유지하기 위한 필수 가이드라인입니다. Claude는 모든 파일 및 코드 작성 시 이 규칙을 반드시 따라야 합니다.**
