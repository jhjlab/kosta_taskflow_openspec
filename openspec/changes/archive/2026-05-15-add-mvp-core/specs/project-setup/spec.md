## ADDED Requirements

### Requirement: requirements.txt 의존성 정의
프로젝트는 requirements.txt에 모든 Python 의존성을 고정 버전으로 명시해야 한다.

#### Scenario: 의존성 설치
- **WHEN** `pip install -r requirements.txt` 실행
- **THEN** fastapi, uvicorn[standard], sqlalchemy, alembic, python-jose[cryptography], passlib[bcrypt], psycopg2-binary, python-dotenv, httpx, pytest, pytest-asyncio, mangum 설치 완료

### Requirement: 환경변수 설정
.env.example 파일이 있어야 하고, .env는 .gitignore에 포함되어야 한다.
필수 변수: DATABASE_URL, JWT_SECRET_KEY, JWT_ALGORITHM=HS256, CORS_ORIGINS.

#### Scenario: 로컬 환경변수 로드
- **WHEN** .env 파일에 DATABASE_URL=sqlite:///./taskflow.db 설정 후 uvicorn 실행
- **THEN** 앱이 SQLite에 연결하여 정상 동작

### Requirement: Alembic 마이그레이션 초기화
Alembic으로 DB 스키마를 관리한다. `alembic upgrade head`로 4개 테이블 + 인덱스 생성.

#### Scenario: 초기 마이그레이션 실행
- **WHEN** `alembic upgrade head` 실행
- **THEN** users/teams/tasks/messages 테이블 + 인덱스 생성, alembic_version 테이블 생성
