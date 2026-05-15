## Why

`taskflow-mvp` 변경에서 미션·스펙·설계를 완전히 정의했다. 이제 그 스펙을 실제 동작하는 코드로 구현한다. 그린필드 프로젝트이므로 기존 코드 없이 처음부터 전체 애플리케이션을 구축한다.

## What Changes

- **NEW**: `backend/` — FastAPI 앱, SQLAlchemy 모델 4개, Alembic 마이그레이션, JWT/bcrypt 유틸, 라우터 4개 (auth/teams/tasks/messages)
- **NEW**: `frontend/` — Vanilla JS MPA 4페이지 (login/team/kanban/chat) + 공통 모듈 (api.js, auth.js)
- **NEW**: `tests/` — pytest 테스트 5파일 (conftest, auth, teams, tasks, messages)
- **NEW**: `api/index.py` + `vercel.json` — Vercel Serverless Functions 배포 설정
- **NEW**: `.env.example`, `requirements.txt`, `alembic.ini` — 프로젝트 설정 파일
- **NEW**: Swagger UI(/docs) 활성화 — 18개 API 브라우저 테스트 가능

## Capabilities

### New Capabilities

- `project-setup`: 디렉토리 구조, requirements.txt, .env, Alembic, .gitignore — 프로젝트 기반 설정
- `backend-core`: FastAPI main.py, database.py, config.py, dependencies.py, schemas.py, exceptions.py — 공통 인프라
- `backend-api`: 4개 라우터 파일 (auth/teams/tasks/messages) — 18개 엔드포인트 구현체
- `frontend-pages`: 4개 HTML + JS 페이지, api.js/auth.js 공통 모듈, Tailwind CDN
- `test-suite`: conftest.py + 4개 테스트 파일, 인메모리 SQLite 픽스처
- `deployment`: api/index.py (Vercel ASGI handler), vercel.json (rewrites 규칙)

### Modified Capabilities

## Impact

- **신규 파일**: backend/(15+), frontend/(10+), tests/(5), api/(1), 설정파일(5)
- **의존성**: fastapi, uvicorn[standard], sqlalchemy, alembic, python-jose[cryptography], passlib[bcrypt], psycopg2-binary, python-dotenv, httpx, pytest, pytest-asyncio, mangum
- **로컬 실행**: `pip install -r requirements.txt && alembic upgrade head && uvicorn backend.main:app --reload`
- **테스트**: `pytest tests/ -v` (외부 서버·DB 불필요, 인메모리 SQLite)
- **배포**: Vercel CLI or GitHub main push → 자동 배포
