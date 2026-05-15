## 1. 프로젝트 초기 설정

- [x] 1.1 루트 디렉토리 구조 생성: backend/, backend/routers/, backend/utils/, frontend/, frontend/js/, tests/, api/, migrations/versions/
- [x] 1.2 requirements.txt 작성 (fastapi, uvicorn[standard], sqlalchemy>=2.0, alembic, python-jose[cryptography], passlib[bcrypt], psycopg2-binary, python-dotenv, httpx, pytest, pytest-asyncio, mangum)
- [x] 1.3 .env.example 작성 (DATABASE_URL, JWT_SECRET_KEY, JWT_ALGORITHM=HS256, CORS_ORIGINS)
- [x] 1.4 .env 파일 생성 (DATABASE_URL=sqlite:///./taskflow.db, JWT_SECRET_KEY=dev-secret-change-in-prod)
- [x] 1.5 .gitignore 작성 (.env, __pycache__, *.db, .venv, *.pyc)
- [x] 1.6 pip install -r requirements.txt 실행 확인

## 2. DB 모델 및 Alembic 설정

- [x] 2.1 backend/database.py — create_engine (DATABASE_URL 환경변수), SessionLocal, Base 정의
- [x] 2.2 backend/models.py — User 모델 (id, email UNIQUE, password_hash, team_id FK NULL, created_at)
- [x] 2.3 backend/models.py — Team 모델 (id, name 1-30자, invite_code UNIQUE, owner_id FK, created_at)
- [x] 2.4 backend/models.py — Task 모델 (id, team_id FK, title 1-100자, status Enum, creator_id FK, assignee_id FK NULL, created_at)
- [x] 2.5 backend/models.py — Message 모델 (id, team_id FK, user_id FK, content 1-1000자, created_at)
- [x] 2.6 alembic.ini 설정 (sqlalchemy.url = env:DATABASE_URL)
- [x] 2.7 migrations/env.py 설정 (Base.metadata import, run_migrations_online)
- [x] 2.8 alembic revision --autogenerate -m "initial" 실행 → versions/001_initial.py 생성 확인
- [x] 2.9 alembic upgrade head 실행 → taskflow.db 생성, 4테이블 + 인덱스 확인

## 3. FastAPI 공통 인프라

- [x] 3.1 backend/config.py — pydantic-settings Settings 클래스 (DATABASE_URL, JWT_SECRET_KEY, JWT_ALGORITHM, CORS_ORIGINS)
- [x] 3.2 backend/utils/jwt.py — create_access_token(data, expires_delta=24h), verify_token(token) → payload dict
- [x] 3.3 backend/utils/password.py — hash_password(plain), verify_password(plain, hashed)
- [x] 3.4 backend/utils/invite_code.py — generate_invite_code() → 정규식 ^[A-Z]{4}-[0-9]{4}$ 형태 랜덤 생성
- [x] 3.5 backend/exceptions.py — AppError 헬퍼, http_exception_handler (→ {error:{code,message}}), validation_exception_handler (422→400)
- [x] 3.6 backend/schemas.py — 요청/응답 Pydantic 모델 전부 정의 (UserCreate, UserOut, TokenOut, TeamCreate, TeamOut, TaskCreate, TaskOut, TaskStatusUpdate, MessageCreate, MessageOut, ErrorOut)
- [x] 3.7 backend/dependencies.py — get_db (SessionLocal yield), get_current_user (JWT 검증), require_team_member (team_id 비교)
- [x] 3.8 backend/main.py — FastAPI(title="TaskFlow API"), CORSMiddleware, exception_handler 등록, StaticFiles("/", "frontend"), 라우터 4개 include

## 4. Auth 라우터

- [x] 4.1 backend/routers/auth.py — POST /auth/signup: 이메일 중복체크 → bcrypt 해시 → users INSERT → JWT 발급 → HTTP 201
- [x] 4.2 backend/routers/auth.py — POST /auth/login: 이메일 조회 → bcrypt 검증 → JWT 발급 → HTTP 200 (이메일 존재 여부 노출 금지)
- [x] 4.3 backend/routers/auth.py — GET /auth/me: get_current_user 의존성 → user 반환
- [x] 4.4 backend/routers/auth.py — POST /auth/logout: HTTP 200 {} (토큰 검증 없음)

## 5. Teams 라우터

- [x] 5.1 backend/routers/teams.py — POST /teams: team 생성 + invite_code 생성 + users.team_id 업데이트 → HTTP 201
- [x] 5.2 backend/routers/teams.py — POST /teams/join: 형식 검증 → invite_code 조회 → 중복 체크 → users.team_id 업데이트 → HTTP 200
- [x] 5.3 backend/routers/teams.py — GET /teams/{id}: require_team_member 검증 → team + member_count 반환
- [x] 5.4 backend/routers/teams.py — GET /teams/{id}/members: require_team_member 검증 → [{ id, email, is_owner, joined_at }]
- [x] 5.5 backend/routers/teams.py — DELETE /teams/{id}/leave: require_team_member → users.team_id = NULL

## 6. Tasks 라우터

- [x] 6.1 backend/routers/tasks.py — GET /teams/{id}/tasks: filter 쿼리파라미터(all/me/unassigned), created_at desc
- [x] 6.2 backend/routers/tasks.py — POST /teams/{id}/tasks: title/assignee_id 검증 → INSERT → HTTP 201
- [x] 6.3 backend/routers/tasks.py — GET /tasks/{id}: 팀 멤버십 검증 → task 반환
- [x] 6.4 backend/routers/tasks.py — PUT /tasks/{id}: title/assignee_id 수정 → 반환
- [x] 6.5 backend/routers/tasks.py — PATCH /tasks/{id}/status: TODO/DOING/DONE 검증 → status 업데이트 → 반환
- [x] 6.6 backend/routers/tasks.py — DELETE /tasks/{id}: creator 또는 owner 검증 → 204 No Content

## 7. Messages 라우터

- [x] 7.1 backend/routers/messages.py — GET /teams/{id}/messages: since= 파라미터, 없으면 최근 50개, 오름차순 반환, user_email JOIN
- [x] 7.2 backend/routers/messages.py — POST /teams/{id}/messages: 1-1000자 검증 → INSERT → HTTP 201 (user_email 포함)
- [x] 7.3 backend/routers/messages.py — DELETE /messages/{id}: 본인 검증(user_id != current) → 403 NOT_OWNER, 본인이면 204

## 8. 프론트엔드 공통 모듈

- [x] 8.1 frontend/js/auth.js — saveToken(token), getToken(), removeToken(), isLoggedIn(), getCurrentUser()
- [x] 8.2 frontend/js/api.js — request(method, path, body), get/post/put/patch/del 헬퍼, 401 intercept → removeToken + redirect, 에러 토스트

## 9. 프론트엔드 페이지

- [x] 9.1 frontend/login.html + js/login.js — 로그인/회원가입 탭, 인라인 에러, 처리중 버튼, team_id 분기 redirect
- [x] 9.2 frontend/team.html + js/team.js — 팀 만들기/초대코드 합류 폼, invite_code 표시+복사, 미가입 강제 진입 로직
- [x] 9.3 frontend/kanban.html + js/kanban.js — 3컬럼 카드 렌더링, 인라인 추가, HTML5 drag&drop + PATCH, 필터 버튼(전체/@me/미할당), 모달(상세/수정/삭제)
- [x] 9.4 frontend/chat.html + js/chat.js — 말풍선 렌더링, setInterval(5000) 폴링, since= 증분, 1000자 카운터+적색, 호버 삭제 아이콘
- [x] 9.5 공통 레이아웃 — 헤더(팀명/탭/이메일/로그아웃), 반응형(768px), 모바일 햄버거 메뉴
- [x] 9.6 공통 UI 컴포넌트 — showToast(msg, type), showConfirm(msg) → Promise, showLoading/hideLoading

## 10. 배포 설정

- [x] 10.1 api/index.py — from mangum import Mangum; from backend.main import app; handler = Mangum(app, lifespan="off")
- [x] 10.2 vercel.json — rewrites: /api/* → /api/index, /docs → /api/index, /redoc → /api/index, /openapi.json → /api/index
- [x] 10.3 FastAPI StaticFiles에서 frontend/ 정적 서빙 설정 확인 (로컬 http://localhost:8000/ → login.html)

## 11. pytest 테스트 작성

- [x] 11.1 tests/conftest.py — 인메모리 SQLite 엔진(StaticPool), Base.metadata.create_all, get_db override, client 픽스처, authed_client 픽스처
- [x] 11.2 tests/test_auth.py — signup 정상/중복이메일/비밀번호약함, login 정상/잘못된자격증명, me 정상/토큰없음, logout
- [x] 11.3 tests/test_teams.py — 팀생성 정상/이미소속, 합류 정상/잘못된코드/미존재/이미소속, 멤버목록, 팀나가기
- [x] 11.4 tests/test_tasks.py — 태스크 생성/조회/수정/삭제(creator권한/owner권한/타인403), 상태변경, 필터(@me/미할당)
- [x] 11.5 tests/test_messages.py — 전송 정상/1000자초과/비멤버, 폴링(since=있음/없음), 삭제 본인/타인403

## 12. 최종 검증

- [x] 12.1 pytest tests/ -v 전체 실행 → 35/35 PASSED
- [x] 12.2 uvicorn backend.main:app --reload 후 http://localhost:8000/docs 에서 18개 API 모두 확인
- [x] 12.3 로컬 전체 플로우 수동 테스트 — 회원가입 → 팀생성 → 초대코드 복사 → 다른 계정 합류 → 칸반 드래그 → 채팅 폴링
- [ ] 12.4 모바일(768px 이하) 반응형 UI 확인
