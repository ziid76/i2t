# 네이버 OCR 테이블 인식 웹 애플리케이션

Django 기반의 네이버 OCR API를 사용한 테이블 인식 웹 애플리케이션입니다.

## 주요 기능

1. **이미지 업로드**: JPG 파일을 웹 인터페이스를 통해 업로드
2. **S3 저장**: 업로드된 이미지를 AWS S3에 자동 저장
3. **OCR 처리**: 네이버 OCR API를 통한 테이블 데이터 추출
4. **결과 시각화**: 
   - 왼쪽: 원본 이미지 + 바운딩 박스 표시
   - 오른쪽: 인식된 테이블 데이터 표시

## 설치 및 실행

### 1. 환경 설정

`.env` 파일을 수정하여 AWS 및 네이버 OCR API 설정을 입력하세요:

```bash
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=ap-northeast-2
NAVER_OCR_API_URL=https://gxx9jkyalr.apigw.ntruss.com/custom/v1/45084/126322645cd06458ae58d8755741bc835005c36d93b372a18efc73b9c3f5d48f/general
NAVER_OCR_SECRET=ZGFvS1hCVUxrU0ZEaktXU2RvSFRIdWtET2prTXRBT2s=
```

### 2. 가상환경 및 패키지 설치

```bash
# 가상환경 생성 (이미 생성됨)
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 3. 데이터베이스 마이그레이션

```bash
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
```

### 4. 슈퍼유저 생성 (선택사항)

```bash
source venv/bin/activate
python manage.py createsuperuser
```

### 5. 서버 실행

#### Linux/Mac:
```bash
# 실행 스크립트 사용
./run_server.sh

# 또는 직접 실행
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

#### Windows:
```batch
# 배치 파일 사용
run_server_windows.bat

# 또는 PowerShell 사용
run_server_windows.ps1

# 또는 직접 실행
venv\Scripts\activate.bat
python manage.py runserver 0.0.0.0:8000
```

**PowerShell 사용 시 주의사항:**
PowerShell에서 스크립트 실행이 차단되는 경우, 다음 명령어를 관리자 권한으로 실행하세요:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 사용 방법

1. 웹 브라우저에서 `http://localhost:8000` 접속
2. JPG 파일을 드래그 앤 드롭하거나 파일 선택을 통해 업로드
3. "OCR 처리 시작" 버튼 클릭
4. 처리 완료 후 결과 페이지에서 확인:
   - 왼쪽: 원본 이미지와 바운딩 박스
   - 오른쪽: 인식된 테이블 데이터

## 프로젝트 구조

```
naverOCR/
├── naverOCR_project/          # Django 프로젝트 설정
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── ocr_app/                   # OCR 앱
│   ├── models.py              # 데이터 모델
│   ├── views.py               # 뷰 로직
│   ├── forms.py               # 폼 정의
│   ├── utils.py               # 유틸리티 함수
│   ├── admin.py               # 관리자 설정
│   ├── urls.py                # URL 패턴
│   └── templates/             # 템플릿 파일
├── data/                      # 업로드 이미지 저장 디렉토리
├── media/                     # Django 미디어 파일
├── venv/                      # Python 가상환경
├── requirements.txt           # Python 패키지 목록
├── .env                       # 환경변수 설정
└── README.md                  # 프로젝트 설명서
```

## API 엔드포인트

- `/`: 메인 페이지 (이미지 업로드)
- `/result/<id>/`: OCR 결과 페이지
- `/api/results/`: 최근 처리 결과 목록 (JSON)
- `/admin/`: Django 관리자 페이지

## 주요 기술 스택

- **Backend**: Django 4.2.7
- **Frontend**: Bootstrap 5, JavaScript
- **Cloud**: AWS S3
- **OCR**: 네이버 Clova OCR API
- **Database**: SQLite (기본)

## 주의사항

1. AWS S3 버킷이 공개 읽기 권한으로 설정되어야 합니다.
2. 네이버 OCR API 키와 엔드포인트가 올바르게 설정되어야 합니다.
3. 업로드 파일 크기는 10MB로 제한됩니다.
4. JPG, JPEG, PNG 파일만 지원됩니다.

## 문제 해결

### S3 업로드 실패
- AWS 자격 증명이 올바른지 확인
- S3 버킷 권한 설정 확인

### OCR API 호출 실패
- 네이버 OCR API 키 확인
- API 엔드포인트 URL 확인
- 이미지 URL이 공개적으로 접근 가능한지 확인

### 바운딩 박스가 표시되지 않음
- OCR 결과에 테이블 데이터가 포함되어 있는지 확인
- 브라우저 개발자 도구에서 JavaScript 오류 확인
