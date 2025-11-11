# IPEDS Downloader

IPEDS(Integrated Postsecondary Education Data System) 데이터를 자동으로 다운로드하고 관리하는 Python 기반 도구입니다.

## 프로젝트 목적

- IPEDS 웹사이트에서 데이터 자동 다운로드
- 컬럼명 및 코드값을 자연어로 변환
- 연도/학기별 데이터 분리 및 시계열 데이터베이스 구축

자세한 내용은 [`.claude/global_purpose.md`](.claude/global_purpose.md)를 참조하세요.

## 설치

### 필요 요구사항

- Python 3.8 이상
- pip

### 의존성 설치

```bash
pip install -r requirements.txt
```

## 사용법

### 기본 사용법

IPEDS 다운로더는 CLI(Command Line Interface)를 통해 사용할 수 있습니다.

```bash
python scripts/ipeds_cli.py <명령> [옵션]
```

### 주요 명령

#### 1. 다운로드 (download)

**모든 데이터 다운로드:**
```bash
python scripts/ipeds_cli.py download --all
```

**특정 연도 다운로드:**
```bash
python scripts/ipeds_cli.py download --year 2022
```

**특정 서베이 다운로드:**
```bash
python scripts/ipeds_cli.py download --survey HD
```

**단일 파일 다운로드:**
```bash
python scripts/ipeds_cli.py download --single HD 2022
```

#### 2. 검증 (verify)

다운로드된 파일의 무결성을 검증합니다.

```bash
python scripts/ipeds_cli.py verify
```

#### 3. 압축 해제 (extract)

다운로드된 ZIP 파일의 압축을 해제합니다.

```bash
python scripts/ipeds_cli.py extract
```

기존 파일 덮어쓰기:
```bash
python scripts/ipeds_cli.py extract --overwrite
```

#### 4. 메타데이터 조회 (metadata)

**다운로드 통계:**
```bash
python scripts/ipeds_cli.py metadata stats
```

**다운로드 이력:**
```bash
python scripts/ipeds_cli.py metadata history
```

**등록된 파일 목록:**
```bash
python scripts/ipeds_cli.py metadata files
```

**메타데이터 내보내기:**
```bash
python scripts/ipeds_cli.py metadata export output.json
```

#### 5. 목록 조회 (list)

**서베이 목록:**
```bash
python scripts/ipeds_cli.py list surveys
```

**연도 범위:**
```bash
python scripts/ipeds_cli.py list years
```

### 도움말

각 명령의 상세한 옵션은 `--help`로 확인할 수 있습니다.

```bash
python scripts/ipeds_cli.py --help
python scripts/ipeds_cli.py download --help
python scripts/ipeds_cli.py metadata --help
```

## 설정

설정 파일은 `config/` 디렉토리에 있습니다.

- **`downloader_config.yaml`**: 다운로더 주요 설정
- **`surveys.yaml`**: IPEDS 서베이 정의
- **`logging_config.yaml`**: 로깅 설정

### 주요 설정 항목

#### downloader_config.yaml

```yaml
ipeds:
  base_url: "https://nces.ed.gov/ipeds/datacenter/data/"
  years:
    start: 2013  # 시작 연도
    end: null    # 종료 연도 (null이면 최신 연도까지)

storage:
  raw_dir: "./data/raw"
  extracted_dir: "./data/extracted"
  metadata_dir: "./data/metadata"

download:
  skip_existing: true     # 기존 파일 건너뛰기
  verify_checksum: true   # 체크섬 검증
  auto_extract: false     # 자동 압축 해제
```

## 디렉토리 구조

```
.
├── config/              # 설정 파일
├── data/                # 데이터 저장소
│   ├── raw/            # 원본 ZIP 파일
│   ├── extracted/      # 압축 해제된 파일
│   └── metadata/       # 메타데이터 (JSON)
├── logs/                # 로그 파일
├── scripts/             # CLI 스크립트
│   └── ipeds_cli.py    # 메인 CLI
├── src/modules/         # 소스 코드 모듈
│   ├── client/         # HTTP 클라이언트
│   ├── config/         # 설정 관리
│   ├── downloader/     # 다운로드 관리
│   ├── storage/        # 파일/메타데이터 관리
│   ├── utils/          # 유틸리티
│   └── cli/            # CLI 명령
└── tests/               # 테스트 코드
```

## 개발

### Phase 01: 다운로더 구현 (현재)

- ✅ 프로젝트 구조 설정
- ✅ 핵심 모듈 구현
- ✅ CLI 인터페이스 구현
- ⏳ 테스트 작성 (예정)

### Phase 02: 데이터 변환 (예정)

- 자연어 컬럼명 변환
- 코드값 자연어 변환

### Phase 03: 데이터베이스 구축 (예정)

- 시계열 데이터베이스 스키마 설계
- 데이터 적재

## 문서

프로젝트 문서는 `.claude/` 디렉토리에 있습니다.

- **`global_purpose.md`**: 프로젝트 전체 목적
- **`phase01_spec_downloader.md`**: Phase 01 명세서
- **`phase01_impl_plan.md`**: Phase 01 구현 계획
- **`coding_standards.md`**: 코딩 규칙
- **`naming_conventions.md`**: 네이밍 규칙

## 라이선스

이 프로젝트는 교육 및 연구 목적으로 작성되었습니다.

## 참고

- IPEDS 데이터센터: https://nces.ed.gov/ipeds/datacenter/
- IPEDS 데이터 사용 가이드: https://nces.ed.gov/ipeds/use-the-data
