## ADDED Requirements

### Requirement: 로컬 개발 환경
로컬에서 `uvicorn app.main:app --reload --port 8000`으로 FastAPI를 실행.
DB는 `DATABASE_URL=sqlite:///./taskflow.db`. 정적 파일(frontend/)은 FastAPI StaticFiles로 서빙.
`.env` 파일로 환경변수 관리, `.gitignore`에 포함.

#### Scenario: 로컬 서버 시작
- **WHEN** `uvicorn app.main:app --reload --port 8000` 실행
- **THEN** http://localhost:8000/docs 에서 Swagger UI 접근 가능, http://localhost:8000 에서 프론트엔드 접근 가능

#### Scenario: SQLite DB 초기화
- **WHEN** `alembic upgrade head` 실행
- **THEN** taskflow.db 파일 생성, 4개 테이블(users/teams/tasks/messages) + 인덱스 생성

### Requirement: Vercel 운영 배포 구성
`api/index.py`에 FastAPI ASGI 핸들러, `public/`에 정적 HTML/JS/CSS.
`vercel.json`의 rewrites로 `/api/*` → Serverless Function, `/docs`, `/redoc`, `/openapi.json` → Serverless Function, 나머지 → 정적 파일.

#### Scenario: GitHub main push 시 자동 배포
- **WHEN** git push origin main
- **THEN** Vercel 자동 빌드·배포, https://taskflow.vercel.app 에서 접근 가능

#### Scenario: Vercel 환경변수 설정
- **WHEN** Vercel 대시보드에서 DATABASE_URL, JWT_SECRET_KEY 환경변수 설정
- **THEN** Serverless Function이 Neon PostgreSQL에 연결

### Requirement: DATABASE_URL 환경변수 전환
`DATABASE_URL` 하나로 SQLite(로컬) ↔ PostgreSQL Neon(운영) 전환. SQLAlchemy 엔진 생성 시 URL 파싱.

#### Scenario: 로컬 SQLite 연결
- **WHEN** DATABASE_URL=sqlite:///./taskflow.db
- **THEN** SQLite 파일 DB 사용, check_same_thread=False 옵션 적용

#### Scenario: Neon PostgreSQL 연결
- **WHEN** DATABASE_URL=postgresql+psycopg2://...neon.tech/taskflow?sslmode=require
- **THEN** Neon DB 연결, connection pool 설정(pool_size=5, max_overflow=10)
