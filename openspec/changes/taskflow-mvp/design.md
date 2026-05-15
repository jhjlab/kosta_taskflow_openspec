## Context

그린필드(greenfield) 프로젝트. 소규모 팀 협업 앱 TaskFlow MVP를 처음부터 구축한다.
스토리보드 v2(42슬라이드) 기준 결정 8건을 모두 채택. 로컬 개발 환경은 Python 3.10+이 설치된 Windows.
배포는 Vercel(FE 정적 + BE Python Serverless) + Neon PostgreSQL. DB는 환경변수 `DATABASE_URL` 하나로 SQLite ↔ Neon 전환.

## Goals / Non-Goals

**Goals:**
- 인증·팀·칸반·채팅 5종 기능 완전 동작 (로컬 + 운영)
- FastAPI 자동 Swagger UI(/docs, /redoc) — 18개 API 브라우저 직접 테스트
- pytest 테스트 스위트 — 핵심 플로우(회원가입·로그인·팀·칸반·채팅) 커버
- Vanilla JS MPA + Tailwind CDN — 4개 HTML 페이지, 반응형(768px)
- DATABASE_URL 하나로 로컬 SQLite ↔ 운영 Neon 전환

**Non-Goals:**
- WebSocket 실시간 메시지 (5초 폴링으로 대체)
- 파일 첨부, 전문 검색, 이메일 알림
- JWT refresh token (24h 만료 시 재로그인)
- 테스트 자동화 CI (수동 pytest 실행만)
- 마이크로서비스 분리 (단일 FastAPI 앱)

## Decisions

### 1. 백엔드 프레임워크 — FastAPI
**선택**: FastAPI  
**이유**: Pydantic으로 자동 입력 검증, OpenAPI 스키마 자동 생성 → Swagger UI(/docs) 기본 제공. async 지원으로 폴링 API 부하 처리. pytest-asyncio + httpx AsyncClient로 통합 테스트 작성이 간결.  
**대안**: Flask — Swagger 별도 설치 필요, 타입 안전성 낮음.

### 2. ORM — SQLAlchemy 2.x (Core + ORM) + Alembic
**선택**: SQLAlchemy ORM + Alembic  
**이유**: SQLite ↔ PostgreSQL 양쪽 호환. Alembic으로 스키마 버전 관리. `DATABASE_URL` 환경변수 하나로 엔진 전환.  
**대안**: Tortoise-ORM — async 친화적이나 Alembic 미지원, SQLite 호환성 불안정.

### 3. 인증 — JWT + bcrypt
**선택**: python-jose (JWT), passlib[bcrypt] (비밀번호 해시)  
**이유**: python-jose는 표준 JOSE 스펙 구현체, passlib은 bcrypt 비용 파라미터 조정 가능. stateless JWT로 서버 세션 불필요.  
**결정**: JWT 만료 24h, refresh token 없음, logout은 클라이언트 localStorage 삭제만.

### 4. 프론트엔드 구조 — Vanilla JS MPA + Tailwind CDN
**선택**: MPA (login/team/kanban/chat.html 분리) + Tailwind CDN  
**이유**: 빌드 도구 없이 즉시 실행 가능. 학습 비용 최소화. 각 페이지가 독립적이라 디버깅 용이.  
**결정**: `js/api.js` (공통 fetch wrapper + JWT 자동 첨부 + 401 redirect), `js/auth.js` (localStorage 관리) 공유.

### 5. 칸반 드래그 — HTML5 Native Drag & Drop
**선택**: HTML5 dragstart/dragover/drop API  
**이유**: 외부 라이브러리 없음. Vanilla JS로 구현 가능. drop 시 `PATCH /tasks/{id}/status` 호출.  
**모바일**: `touchstart/touchmove/touchend` 이벤트로 폴백, 또는 길게 누르기 → 상태 변경 메뉴.

### 6. 채팅 폴링 — setInterval + since= 파라미터
**선택**: `setInterval(5000)` + `GET /teams/{id}/messages?since=<ISO>`  
**이유**: WebSocket 범위 외(스토리보드 결정). since= 증분 폴링으로 전체 재조회 없이 새 메시지만 수신. 네트워크 끊김 시 exponential backoff(5→10→20→40→60s).

### 7. 테스트 — pytest + httpx AsyncClient
**선택**: pytest + httpx.AsyncClient(app=app) + pytest-asyncio  
**이유**: FastAPI 앱을 실제 서버 없이 인메모리 SQLite로 통합 테스트. 픽스처로 DB 세션 격리.  
**커버 범위**: 인증(signup/login/me/logout), 팀(create/join/members), 칸반(CRUD/status/권한), 채팅(send/poll/delete).

### 8. Vercel 배포 — Python Serverless + 정적 파일
**선택**: `api/index.py` (ASGI handler) + `public/` (정적 HTML/JS/CSS)  
**이유**: Vercel Python runtime이 ASGI 앱을 Serverless Function으로 실행. `vercel.json`의 rewrites로 `/api/*` → Serverless, 나머지 → 정적 파일.  
**로컬**: `uvicorn app.main:app --reload --port 8000`, 정적 파일은 FastAPI StaticFiles로 서빙.

## Risks / Trade-offs

- **SQLite → PostgreSQL 타입 차이** → Alembic 마이그레이션을 SQLite/PostgreSQL 양쪽에서 검증. `PRAGMA foreign_keys=ON` 필수.
- **5초 폴링 서버 부하** → Vercel Serverless는 요청당 과금. 팀당 5명 × 5초 = 분당 60 req/팀 수준이므로 Free tier 내 허용.
- **HTML5 Drag & Drop 모바일 미지원** → 모바일에서는 길게 누르기 → 상태 변경 드롭다운 메뉴로 대체.
- **JWT localStorage 보안(XSS)** → MVP 범위에서 허용(스토리보드 Assumption). httpOnly cookie는 범위 외.
- **Vercel Python Cold Start** → 첫 요청 2-3초 지연 가능. Free tier에서 감수.
- **pytest 인메모리 DB 격리** → 각 테스트 함수마다 새 DB 픽스처. 트랜잭션 롤백 또는 DB 재생성으로 격리.

## Migration Plan

1. 로컬 개발: `DATABASE_URL=sqlite:///./taskflow.db uvicorn app.main:app --reload`
2. Alembic 초기 마이그레이션 생성: `alembic upgrade head`
3. 테스트 실행: `pytest tests/ -v`
4. Vercel 배포: `vercel --prod` (Vercel CLI) or GitHub push → 자동 배포
5. Neon DB 연결: Vercel 환경변수에 `DATABASE_URL` 설정 (Vercel Marketplace Neon 통합)

## Open Questions

- Neon Pooled connection string 사용 여부 (Serverless 환경에서 connection pool 고갈 방지 필요)
  → `?sslmode=require&pgbouncer=true` 파라미터 추가 예정
- Vercel Python runtime 버전: 3.12 vs 3.11 (Neon psycopg2 호환성 확인 필요)
