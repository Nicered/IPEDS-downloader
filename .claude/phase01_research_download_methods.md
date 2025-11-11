# Phase 01 Research: IPEDS 다운로드 방법 조사

## 조사 일자
2025-11-11

## 조사 목적
IPEDS 웹사이트에서 실제 데이터를 다운로드하는 방법을 연구하여, Phase 01 다운로더 구현에 활용할 수 있는 구체적인 방법론을 확립합니다.

## 핵심 발견사항

### 1. IPEDS 데이터 접근 방법

#### 1.1 공식 제공 방식
IPEDS는 REST API를 제공하지 않으며, 다음 세 가지 방법으로 데이터를 제공합니다:

1. **Complete Data Files** (추천)
   - 서베이별, 연도별 전체 데이터 다운로드
   - ZIP 압축된 CSV 파일 형식
   - 데이터 사전 포함

2. **Custom Data Files**
   - 특정 변수와 기관 선택 다운로드
   - 사용자 정의 데이터셋 생성

3. **Access Databases**
   - Microsoft Access 형식 (2004-05년 이후)
   - 연도별 전체 서베이 데이터

**본 프로젝트는 Complete Data Files 방식을 사용합니다.**

#### 1.2 제3자 API (선택사항)
- **Urban Institute Education Data Portal**
  - API 기본 URL: `https://educationdata.urban.org/api/v1/`
  - JSON 형식으로 데이터 제공
  - 비공식 API이지만 프로그래밍 방식 접근 가능

## 2. 다운로드 URL 패턴

### 2.1 기본 URL 구조

```
기본 디렉토리: http://nces.ed.gov/ipeds/datacenter/

데이터 파일: http://nces.ed.gov/ipeds/datacenter/data/{FILENAME}.zip
사전 파일: http://nces.ed.gov/ipeds/datacenter/data/{FILENAME}_Dict.zip
```

### 2.2 파일명 규칙

**형식**: `{서베이코드}{연도}[_서브코드].zip`

**예시:**
- `HD2022.zip` - 2022년 Directory Information
- `IC2022.zip` - 2022년 Institutional Characteristics
- `EF2022A.zip` - 2022년 Fall Enrollment Part A
- `EF2022B.zip` - 2022년 Fall Enrollment Part B
- `SAL2022_IS.zip` - 2022년 Salaries - Instructional Staff

### 2.3 주요 서베이 코드

| 코드 | 전체 이름 | 설명 |
|------|-----------|------|
| HD | Directory Information | 기관 디렉토리 정보 |
| IC | Institutional Characteristics | 기관 특성 |
| EF | Fall Enrollment | 가을학기 등록 |
| EFFY | Enrollment by Year | 연도별 등록 |
| C | Completions | 학위 수여 |
| F | Finance | 재정 |
| SAL | Salaries | 급여 |
| GR | Graduation Rates | 졸업률 |
| ADM | Admissions | 입학 |
| SFA | Student Financial Aid | 학자금 지원 |
| AL | Academic Libraries | 학술 도서관 |
| S | Staff | 교직원 |

### 2.4 연도 표기법

**4자리 연도 사용**: 2022, 2021, 2020 등
- 일부 서베이는 학년도 표기: 2022-23 → 2022

## 3. 기존 구현 사례 분석

### 3.1 Urban Institute IPEDS Scraper
**GitHub**: https://github.com/UrbanInstitute/ipeds-scraper

#### 접근 방식
- **Selenium + Firefox WebDriver** 사용
- 동적 웹페이지 자동화
- HTML 파싱을 위한 BeautifulSoup4 활용

#### 주요 스크립트
1. `scraper.py` - 사용 가능한 모든 데이터셋 목록 수집
   - 웹페이지 드롭다운 메뉴 조작
   - 테이블에서 메타데이터 추출
   - `ipedsfiles.json` 생성

2. `makeDictionary.py` - 데이터 사전 다운로드 및 통합
   - Excel/HTML 형식 사전 파일 처리
   - 통합 CSV 생성

3. `downloadData.py` - 실제 데이터 파일 다운로드
   - 연도 범위 지정 가능
   - ZIP 자동 압축 해제
   - 수정본(revised) 처리

4. `getColumnNames.py` - 컬럼명 추출 및 JSON 저장

#### 장점
- 포괄적인 메타데이터 수집
- 자동화된 데이터 사전 통합
- 여러 연도 데이터 일괄 처리

#### 단점
- Selenium 의존성 (WebDriver 필요)
- 웹페이지 구조 변경 시 취약
- 설정 복잡도 높음

### 3.2 다른 구현 사례

#### cjseaman/Get-IPEDS-Data
- 간단한 Python 스크립트
- 최신 데이터 다운로드 중점
- Selenium 기반

#### dww142/IPEDS-data-depot
- 포괄적인 데이터 파이프라인
- 다운로드 + ETL + 데이터베이스 적재
- Wide-table → Tall-table 변환
- SQL Server 연동

#### scipeds (Python 패키지)
- IPEDS 데이터 분석용 패키지
- 전처리 및 표준화 기능
- 데이터베이스 쿼리 도구 제공

## 4. 추천 구현 방안

### 4.1 방법 1: 직접 URL 다운로드 (추천)

**장점:**
- 구현 간단 (requests 라이브러리만 필요)
- 빠른 실행 속도
- 외부 의존성 최소화
- 안정적 (URL 패턴 변경 가능성 낮음)

**단점:**
- 사용 가능한 파일 목록을 미리 알아야 함
- 새로운 서베이 추가 시 수동 업데이트 필요

**구현 방법:**
```python
import requests

def download_ipeds_file(survey_code, year, output_dir):
    """
    IPEDS 데이터 파일 다운로드

    Args:
        survey_code: 서베이 코드 (예: 'HD', 'IC', 'EF')
        year: 연도 (예: 2022)
        output_dir: 저장 경로
    """
    base_url = "http://nces.ed.gov/ipeds/datacenter/data/"

    # 데이터 파일
    data_filename = f"{survey_code}{year}.zip"
    data_url = base_url + data_filename

    # 사전 파일
    dict_filename = f"{survey_code}{year}_Dict.zip"
    dict_url = base_url + dict_filename

    # 다운로드 로직
    # ...
```

### 4.2 방법 2: 웹 스크래핑 (고급)

**장점:**
- 자동으로 사용 가능한 파일 목록 탐색
- 새로운 데이터 자동 감지

**단점:**
- Selenium 설치 필요
- WebDriver 관리 필요
- 웹페이지 구조 변경 시 수정 필요
- 실행 속도 느림

**적용 시나리오:**
- 파일 목록을 모르는 경우
- 정기적으로 자동 업데이트가 필요한 경우

### 4.3 방법 3: 하이브리드 접근 (최적)

**전략:**
1. **초기 설정**: 웹 스크래핑으로 파일 목록 수집
   - `ipedsfiles.json` 생성
   - 사용 가능한 모든 서베이/연도 파악

2. **정기 다운로드**: 직접 URL 다운로드
   - JSON 파일 기반 다운로드
   - 빠르고 안정적

3. **갱신**: 주기적으로 목록 재수집
   - 분기별 또는 연간 갱신

## 5. 데이터 파일 구조

### 5.1 ZIP 파일 내용

각 ZIP 파일은 다음을 포함합니다:

**데이터 파일 (`{코드}{연도}.zip`):**
- `{코드}{연도}.csv` - 실제 데이터
- `{코드}{연도}_rv.csv` - 수정본 (있는 경우)

**사전 파일 (`{코드}{연도}_Dict.zip`):**
- `{코드}{연도}.xlsx` - 데이터 사전 (Excel)
- 또는 `{코드}{연도}_dict.html` - 데이터 사전 (HTML, 2009년 이전)

### 5.2 CSV 파일 형식

- **인코딩**: UTF-8 또는 Latin-1
- **구분자**: 쉼표 (,)
- **따옴표**: 큰따옴표 (")
- **헤더**: 첫 번째 줄에 컬럼명

### 5.3 데이터 사전 구조

**Excel 형식 (2009년 이후):**
- 시트 1: varlist - 변수 목록
- 시트 2: Frequencies - 변수별 빈도
- 시트 3: ValueLabels - 코드 값 설명

**주요 컬럼:**
- `varname`: 변수명
- `varTitle`: 변수 설명
- `DataType`: 데이터 타입
- `codevalue`: 코드 값
- `valuelabel`: 코드 레이블

## 6. 구현 시 고려사항

### 6.1 연도 범위 결정

```python
# 권장 연도 범위
START_YEAR = 2013  # 데이터 형식 안정화 시점
END_YEAR = 2023    # 최신 연도 (또는 자동 감지)

# 일부 서베이는 더 이른 시점부터 제공
# 필요시 서베이별 다른 시작 연도 설정
```

### 6.2 우선순위 서베이

**1순위 (필수):**
- HD - 기관 디렉토리
- IC - 기관 특성
- EF - 등록 데이터
- EFFY - 연도별 등록

**2순위 (중요):**
- F - 재정
- C - 학위 수여
- GR - 졸업률

**3순위 (선택):**
- SAL, ADM, SFA, AL, S 등

### 6.3 파일 존재 확인

모든 연도/서베이 조합이 존재하는 것은 아닙니다:
- 일부 서베이는 격년 수집
- 서베이 시작/종료 시점 상이
- 404 오류 처리 필요

**확인 방법:**
```python
response = requests.head(url)
if response.status_code == 200:
    # 파일 존재
    file_size = response.headers.get('content-length')
elif response.status_code == 404:
    # 파일 없음 - 건너뜀
    pass
```

### 6.4 데이터 무결성 검증

**체크섬 활용:**
```python
import hashlib

def calculate_checksum(filepath):
    """SHA256 체크섬 계산"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
```

**ZIP 파일 검증:**
```python
import zipfile

def verify_zip(filepath):
    """ZIP 파일 무결성 확인"""
    try:
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            bad_file = zip_ref.testzip()
            return bad_file is None
    except zipfile.BadZipFile:
        return False
```

## 7. 메타데이터 JSON 구조

### 7.1 파일 목록 JSON

```json
{
  "files": [
    {
      "survey_code": "HD",
      "year": 2022,
      "title": "Institutional Characteristics - Directory Information",
      "data_url": "http://nces.ed.gov/ipeds/datacenter/data/HD2022.zip",
      "dict_url": "http://nces.ed.gov/ipeds/datacenter/data/HD2022_Dict.zip",
      "data_filename": "HD2022.zip",
      "dict_filename": "HD2022_Dict.zip"
    }
  ]
}
```

### 7.2 다운로드 로그 JSON

```json
{
  "file_name": "HD2022.zip",
  "survey_code": "HD",
  "year": 2022,
  "url": "http://nces.ed.gov/ipeds/datacenter/data/HD2022.zip",
  "file_size": 12345678,
  "checksum": "sha256:abc123...",
  "download_start": "2025-11-11T10:30:00",
  "download_end": "2025-11-11T10:31:15",
  "status": "COMPLETED",
  "retry_count": 0,
  "error_message": null
}
```

## 8. 주요 과제 및 해결방안

### 8.1 과제: 변수명 연도별 변경

**문제:**
- IPEDS 변수명이 연도마다 변경됨
- 값 정의도 시간에 따라 변화

**해결:**
- Phase 02에서 데이터 사전 기반 매핑 수행
- Phase 01에서는 원본 그대로 저장

### 8.2 과제: 대용량 파일 다운로드

**문제:**
- 일부 파일 크기 수백 MB
- 네트워크 중단 가능성

**해결:**
- 스트리밍 다운로드 사용
- 부분 다운로드 재개 (Range 헤더)
- 타임아웃 설정 충분히 확보

### 8.3 과제: 서버 부하 방지

**문제:**
- 연속적인 요청으로 서버 부하 유발 가능

**해결:**
- 요청 간 1초 간격 유지
- User-Agent 적절히 설정
- 동시 다운로드 제한 (최대 3개)

## 9. 구현 우선순위

### Phase 01-A: 기본 다운로더
1. ✅ 직접 URL 다운로드 구현
2. ✅ 우선순위 서베이 (HD, IC, EF, F) 다운로드
3. ✅ 기본 에러 처리 및 재시도
4. ✅ 다운로드 로그 기록

### Phase 01-B: 고급 기능
1. ⏸️ 전체 서베이 목록 지원
2. ⏸️ ZIP 자동 압축 해제
3. ⏸️ 파일 무결성 검증
4. ⏸️ CLI 인터페이스

### Phase 01-C: 선택 기능
1. ⏸️ 웹 스크래핑 기반 파일 목록 수집
2. ⏸️ 다운로드 통계 및 리포트
3. ⏸️ 증분 업데이트 (신규 파일만)

## 10. 다음 단계

1. **설정 파일 작성**
   - `config/downloader_config.yaml`
   - 다운로드 대상 서베이 및 연도 정의

2. **파일 목록 JSON 생성**
   - 수동 또는 스크래핑으로 `data/metadata/ipeds_files.json` 생성
   - 우선순위 서베이 중심

3. **다운로더 스크립트 구현**
   - `scripts/downloader.py` - 메인 스크립트
   - `scripts/ipeds_client.py` - HTTP 클라이언트
   - `scripts/file_manager.py` - 파일 관리

4. **테스트 실행**
   - 소규모 데이터셋으로 테스트 (최근 1-2년)
   - 에러 시나리오 검증

## 11. 참고 자료

### 공식 문서
- IPEDS 데이터센터: https://nces.ed.gov/ipeds/datacenter/
- IPEDS 사용 가이드: https://nces.ed.gov/ipeds/use-the-data
- Complete Data Files: https://nces.ed.gov/ipeds/help/complete-data-files

### GitHub 프로젝트
- Urban Institute IPEDS Scraper: https://github.com/UrbanInstitute/ipeds-scraper
- IPEDS Data Depot: https://github.com/dww142/IPEDS-data-depot
- scipeds Package: https://github.com/scienceforamerica/scipeds

### 제3자 API
- Urban Institute Education Data API: https://educationdata.urban.org/documentation/

---

**이 연구 문서는 Phase 01 구현의 기술적 근거를 제공하며, 실제 구현 과정에서 발견되는 추가 정보를 반영하여 지속적으로 업데이트됩니다.**
