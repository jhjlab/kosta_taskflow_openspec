## ADDED Requirements

### Requirement: Vercel Serverless 핸들러 (api/index.py)
api/index.py는 Mangum을 사용해 FastAPI ASGI 앱을 Vercel Serverless Function으로 노출해야 한다.

#### Scenario: Vercel 배포 후 API 호출
- **WHEN** Vercel 배포 후 https://taskflow.vercel.app/api/auth/me 호출
- **THEN** Serverless Function이 FastAPI 앱으로 요청을 라우팅하여 정상 응답

### Requirement: vercel.json rewrites 규칙
vercel.json이 /api/*, /docs, /redoc, /openapi.json 요청을 Serverless Function으로, 나머지를 정적 파일로 라우팅해야 한다.

#### Scenario: /docs Serverless 라우팅
- **WHEN** GET https://taskflow.vercel.app/docs
- **THEN** FastAPI Swagger UI 응답 (Serverless Function 처리)

#### Scenario: 정적 HTML 서빙
- **WHEN** GET https://taskflow.vercel.app/login.html
- **THEN** 정적 파일 반환 (Serverless 미경유)

### Requirement: 로컬 실행 가이드
README 또는 .env.example에 로컬 실행 명령어가 명시되어야 한다.

#### Scenario: 로컬 최초 실행
- **WHEN** pip install -r requirements.txt && alembic upgrade head && uvicorn backend.main:app --reload
- **THEN** http://localhost:8000 에서 앱 동작, /docs 에서 Swagger UI 접근 가능
