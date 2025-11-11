# 코딩 규칙

이 문서는 IPEDS-downloader 프로젝트의 코딩 규칙을 정의합니다. **Claude는 모든 코딩 작업 시 이 규칙을 반드시 준수해야 합니다.**

## 문서 작성 규칙

### 언어
- ✅ **모든 문서는 한글로 작성**합니다.
- ✅ 코드 내 주석도 한글로 작성합니다.
- ✅ README, 기술 문서, 가이드 등 모든 문서화는 한글을 사용합니다.
- ✅ 변수명, 함수명, 클래스명은 영어로 작성합니다 (코드 표준).

### 파일명 규칙
- ✅ **모든 파일명은 영어로 작성**합니다.
- ✅ 소문자와 언더바(_)를 사용하는 snake_case를 사용합니다.
  - 좋은 예: `data_processor.py`, `coding_standards.md`
  - 나쁜 예: `데이터처리.py`, `DataProcessor.py`, `data-processor.py`

## 프로젝트 구조

### 폴더 구조
```
IPEDS-downloader/
├── .claude/       # Claude 설정 및 프로젝트 규칙
├── docs/          # 모든 문서 파일 보관
├── scripts/       # 자잘한 Python 스크립트 및 유틸리티 코드
├── src/           # 메인 소스 코드 (필요시)
└── tests/         # 테스트 코드 (필요시)
```

### 파일 배치 규칙
1. **문서 파일**: 모든 `.md`, `.txt` 등 문서 파일은 `docs/` 폴더에 보관
2. **스크립트 파일**: 자잘한 Python 스크립트나 유틸리티 코드는 `scripts/` 폴더에 보관
3. **메인 코드**: 주요 애플리케이션 코드는 `src/` 폴더에 보관 (프로젝트 규모에 따라)
4. **Claude 규칙**: 프로젝트 코딩/커밋 규칙은 `.claude/` 폴더에 보관

## Python 코딩 스타일

### 기본 원칙
- PEP 8 스타일 가이드를 따릅니다.
- 들여쓰기는 공백 4칸을 사용합니다.
- 최대 줄 길이는 100자를 권장합니다.

### 명명 규칙
- **변수명/함수명**: snake_case
  ```python
  user_name = "홍길동"
  def calculate_total_score():
      pass
  ```
- **클래스명**: PascalCase
  ```python
  class DataProcessor:
      pass
  ```
- **상수**: UPPER_SNAKE_CASE
  ```python
  MAX_RETRY_COUNT = 3
  API_BASE_URL = "https://api.example.com"
  ```

### 주석 규칙
- ✅ **모든 주석은 한글로 작성**합니다.
- ✅ 함수와 클래스에는 docstring을 작성합니다.
  ```python
  def process_data(data):
      """
      데이터를 처리하는 함수

      Args:
          data: 처리할 데이터

      Returns:
          처리된 데이터
      """
      pass
  ```

### Import 순서
1. 표준 라이브러리
2. 서드파티 라이브러리
3. 로컬 모듈

각 그룹 사이에 빈 줄을 추가합니다.

```python
# 표준 라이브러리
import os
import sys
from pathlib import Path

# 서드파티 라이브러리
import pandas as pd
import requests

# 로컬 모듈
from scripts.utils import helper_function
```

## 코드 품질

### 에러 처리
- 예상 가능한 모든 예외를 처리합니다.
- 적절한 에러 메시지를 한글로 제공합니다.
  ```python
  try:
      result = process_data(data)
  except ValueError as e:
      print(f"데이터 처리 중 오류 발생: {e}")
  ```

### 로깅
- 중요한 작업에는 로깅을 추가합니다.
- 로그 메시지는 한글로 작성합니다.
  ```python
  import logging

  logger = logging.getLogger(__name__)
  logger.info("데이터 처리 시작")
  ```

## 버전 관리

- 커밋 규칙은 별도 문서 `.claude/commit-conventions.md`를 참조하세요.
- 브랜치 전략: `main` 브랜치는 항상 안정적인 상태를 유지합니다.

## Claude 작업 시 체크리스트

코드 작성 전 확인사항:
- [ ] 모든 문서/주석이 한글로 작성되었는가?
- [ ] 파일명이 영어 소문자와 언더바(_)로 작성되었는가? (snake_case)
- [ ] 문서 파일은 `docs/` 폴더에 배치되었는가?
- [ ] 스크립트 파일은 `scripts/` 폴더에 배치되었는가?
- [ ] PEP 8 스타일을 준수하는가?
- [ ] 함수/클래스에 한글 docstring이 있는가?
- [ ] 에러 처리가 적절히 되어 있는가?
