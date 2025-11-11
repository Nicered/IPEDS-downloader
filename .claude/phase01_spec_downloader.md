# Phase 01: IPEDS 다운로더 구현 명세서

## 개요

Phase 01은 IPEDS(Integrated Postsecondary Education Data System) 웹사이트에서 필요한 모든 데이터를 자동으로 다운로드하는 시스템을 구축하는 단계입니다.

## 목표

- IPEDS 데이터센터에서 제공하는 모든 데이터셋 자동 다운로드
- 연도별, 데이터셋별 체계적 파일 관리
- 중단/재개 가능한 안정적인 다운로드 프로세스
- 다운로드 메타데이터 수집 및 관리

## IPEDS 데이터 구조 이해

### IPEDS 웹사이트
- **기본 URL**: `https://nces.ed.gov/ipeds/datacenter/data/`
- **데이터 형식**: ZIP 파일 (내부에 CSV 및 데이터 사전 포함)
- **제공 방식**: 연도별, 서베이별 파일 제공

### 데이터셋 종류
IPEDS는 다양한 서베이 데이터를 제공합니다:
- **IC**: Institutional Characteristics (기관 특성)
- **HD**: Directory Information (기관 디렉토리)
- **EF**: Enrollment (등록)
- **SAL**: Salaries (급여)
- **F**: Finance (재정)
- **GR**: Graduation Rates (졸업률)
- **ADM**: Admissions (입학)
- **SFA**: Student Financial Aid (학자금 지원)
- 기타 다수의 서베이 데이터

### 연도 범위
- **시작 연도**: 1980년대 (데이터 가용성에 따라 조정)
- **종료 연도**: 최신 연도 (자동 감지)
- **학년도 표기**: 예) 2022-23, 2021-22

## 다운로더 요구사항

### 1. 다운로드 대상 정의

#### 1.1 데이터 범위
```yaml
대상:
  - 모든 IPEDS 데이터셋
  - 최소 10년치 데이터 (설정 가능)
  - 데이터 사전 파일 포함
  - 설명 문서 포함 (가능한 경우)
```

#### 1.2 우선순위
```
1순위: 핵심 데이터셋 (HD, IC, EF, F)
2순위: 학생 관련 데이터 (ADM, SFA, GR)
3순위: 기타 데이터셋
```

### 2. 다운로드 방법론

#### 2.1 기술 스택
- **HTTP 클라이언트**: requests 라이브러리
- **웹 파싱**: BeautifulSoup4 (필요시)
- **비동기 다운로드**: aiohttp (선택사항)
- **재시도 로직**: tenacity 또는 자체 구현

#### 2.2 다운로드 프로세스
```python
1. IPEDS 데이터 목록 페이지 접근
2. 사용 가능한 데이터셋 목록 파싱
3. 각 데이터셋의 다운로드 URL 추출
4. 파일 다운로드 및 저장
5. 다운로드 메타데이터 기록
6. 파일 무결성 검증
```

#### 2.3 URL 패턴 분석
```
일반적인 IPEDS 데이터 파일 URL 패턴:
https://nces.ed.gov/ipeds/datacenter/data/[DatasetCode][Year].zip

예시:
- HD2022.zip (2022년 Directory Information)
- IC2022.zip (2022년 Institutional Characteristics)
- EF2022A.zip (2022년 Enrollment - Part A)
```

### 3. 파일 저장 구조

#### 3.1 디렉토리 구조
```
data/
├── raw/                          # 원본 다운로드 파일
│   ├── 2022/
│   │   ├── HD2022.zip
│   │   ├── IC2022.zip
│   │   └── EF2022.zip
│   ├── 2021/
│   │   └── ...
│   └── metadata/
│       ├── download_log.json    # 다운로드 이력
│       └── file_registry.json   # 파일 목록 및 상태
├── extracted/                    # 압축 해제된 파일
│   ├── 2022/
│   │   ├── HD2022/
│   │   │   ├── hd2022.csv
│   │   │   └── hd2022_dict.csv
│   │   └── ...
│   └── ...
└── processed/                    # 처리된 데이터 (Phase 02+)
```

#### 3.2 파일명 규칙
- **원본 파일**: IPEDS에서 제공하는 파일명 그대로 유지
- **메타데이터**: snake_case 사용
- **로그 파일**: `download_YYYYMMDD_HHMMSS.log`

### 4. 다운로드 관리

#### 4.1 진행상황 추적
```python
다운로드 상태:
- PENDING: 다운로드 대기
- IN_PROGRESS: 다운로드 중
- COMPLETED: 다운로드 완료
- FAILED: 다운로드 실패
- SKIPPED: 이미 존재하여 건너뜀
```

#### 4.2 다운로드 로그
```json
{
  "file_name": "HD2022.zip",
  "url": "https://nces.ed.gov/ipeds/...",
  "download_date": "2025-11-11T10:30:00",
  "file_size": 12345678,
  "status": "COMPLETED",
  "checksum": "sha256:abc123...",
  "retry_count": 0,
  "error_message": null
}
```

#### 4.3 재시도 로직
- **최대 재시도 횟수**: 3회
- **재시도 간격**: 지수 백오프 (2초, 4초, 8초)
- **재시도 대상**: HTTP 오류, 네트워크 오류, 타임아웃
- **재시도 제외**: 404 Not Found

### 5. 에러 처리

#### 5.1 예상 에러 시나리오
```python
에러 유형:
1. 네트워크 오류 (ConnectionError, Timeout)
   → 재시도

2. HTTP 오류
   - 404: 파일 없음 → 로그 기록 후 건너뜀
   - 403/401: 접근 거부 → 중단 및 알림
   - 500+: 서버 오류 → 재시도

3. 디스크 공간 부족
   → 중단 및 알림

4. 파일 손상
   → 재다운로드

5. 압축 해제 실패
   → 재다운로드 또는 건너뜀
```

#### 5.2 에러 로깅
```python
로그 레벨:
- INFO: 다운로드 시작/완료
- WARNING: 재시도, 건너뜀
- ERROR: 다운로드 실패
- CRITICAL: 시스템 오류로 중단
```

### 6. 성능 및 제약사항

#### 6.1 다운로드 속도 제한
- **요청 간격**: 최소 1초 (서버 부하 방지)
- **동시 다운로드**: 최대 3개 (선택사항)
- **User-Agent**: 적절한 식별자 설정
  ```
  User-Agent: IPEDS-Downloader/1.0 (Educational Research Purpose)
  ```

#### 6.2 디스크 공간
- **예상 필요 공간**: 연도당 약 500MB ~ 2GB
- **10년치 데이터**: 약 5GB ~ 20GB
- **공간 부족 시**: 경고 후 중단

#### 6.3 타임아웃 설정
- **연결 타임아웃**: 10초
- **읽기 타임아웃**: 300초 (5분, 큰 파일 고려)

### 7. 메타데이터 수집

#### 7.1 수집할 메타데이터
```python
파일 메타데이터:
- 파일명
- 데이터셋 코드
- 연도
- 다운로드 URL
- 파일 크기
- 다운로드 일시
- MD5/SHA256 체크섬
- 상태
```

#### 7.2 데이터셋 정보
```python
데이터셋 메타데이터:
- 데이터셋 코드 (HD, IC, EF 등)
- 데이터셋 전체 이름
- 설명
- 포함된 파일 목록 (CSV, 데이터 사전 등)
```

### 8. 구현 기능 목록

#### 8.1 핵심 기능
- [ ] IPEDS 데이터 목록 자동 탐색
- [ ] 데이터 파일 자동 다운로드
- [ ] 다운로드 진행상황 표시
- [ ] 중단 후 재개 기능
- [ ] 에러 처리 및 재시도
- [ ] 다운로드 로그 기록

#### 8.2 부가 기능
- [ ] 특정 연도/데이터셋만 선택 다운로드
- [ ] 중복 다운로드 방지 (기존 파일 체크)
- [ ] 파일 무결성 검증 (체크섬)
- [ ] 압축 파일 자동 해제
- [ ] 다운로드 통계 리포트
- [ ] CLI 인터페이스

#### 8.3 설정 기능
- [ ] 설정 파일 지원 (YAML/JSON)
- [ ] 다운로드 경로 설정
- [ ] 연도 범위 설정
- [ ] 데이터셋 필터링
- [ ] 재시도 설정 (횟수, 간격)

### 9. 스크립트 구조

#### 9.1 주요 모듈
```
scripts/
├── downloader.py              # 메인 다운로더 스크립트
├── ipeds_client.py           # IPEDS API/웹 클라이언트
├── file_manager.py           # 파일 저장 및 관리
├── metadata_manager.py       # 메타데이터 관리
├── config.py                 # 설정 관리
└── utils.py                  # 유틸리티 함수
```

#### 9.2 설정 파일
```
config/
└── downloader_config.yaml
```

설정 예시:
```yaml
download:
  base_url: "https://nces.ed.gov/ipeds/datacenter/data/"
  output_dir: "./data/raw"
  years:
    start: 2013
    end: 2023
  datasets:
    - HD
    - IC
    - EF
    - F
  retry:
    max_attempts: 3
    backoff: [2, 4, 8]
  timeout:
    connect: 10
    read: 300
```

### 10. 테스트 요구사항

#### 10.1 단위 테스트
- URL 생성 로직
- 파일 저장 로직
- 메타데이터 관리
- 에러 처리

#### 10.2 통합 테스트
- 실제 IPEDS 사이트에서 소량 데이터 다운로드
- 중단 후 재개 시나리오
- 에러 시나리오 (네트워크 오류 시뮬레이션)

#### 10.3 테스트 데이터
- 테스트용 소규모 데이터셋 (최근 1-2년)
- Mock IPEDS 서버 (선택사항)

### 11. 성공 기준

#### 11.1 필수 요건
- ✅ 지정된 연도 범위의 모든 데이터셋 다운로드 완료
- ✅ 95% 이상의 다운로드 성공률
- ✅ 모든 다운로드 이력이 로그에 기록됨
- ✅ 중단 후 재개 시 중복 다운로드 없이 이어서 진행

#### 11.2 품질 요건
- ✅ 다운로드 실패 시 적절한 에러 메시지 제공
- ✅ 파일 무결성 검증 통과
- ✅ 메타데이터 정확성 100%

### 12. 다음 단계와의 연계

Phase 01 완료 후 Phase 02에서 사용할 출력물:
- `data/raw/`: 원본 ZIP 파일
- `data/extracted/`: 압축 해제된 CSV 및 데이터 사전
- `data/metadata/file_registry.json`: 다운로드된 파일 목록
- `logs/`: 다운로드 로그

### 13. 참고사항

#### 13.1 IPEDS 데이터 사용 정책
- IPEDS 데이터는 공개 데이터이며 무료로 사용 가능
- 적절한 출처 표기 필요
- 서버에 과도한 부하를 주지 않도록 주의

#### 13.2 유용한 링크
- IPEDS 데이터센터: https://nces.ed.gov/ipeds/datacenter/
- IPEDS 데이터 사용 가이드: https://nces.ed.gov/ipeds/use-the-data

---

**이 명세서는 Phase 01 구현의 기준 문서이며, 구현 중 발견되는 이슈에 따라 업데이트될 수 있습니다.**
