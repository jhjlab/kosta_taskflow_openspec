## 1. 프로젝트 초기 설정

- [ ] 1.1 디렉토리 구조 생성 (backend/, frontend/, tests/, api/)
- [ ] 1.2 Python 가상환경 생성 및 requirements.txt 작성 (fastapi, uvicorn, sqlalchemy, alembic, python-jose[cryptography], passlib[bcrypt], psycopg2-binary, python-dotenv, httpx, pytest, pytest-asyncio)
- [ ] 1.3 .env 파일 생성 (DATABASE_URL, JWT_SECRET_KEY, JWT_ALGORITHM, CORS_ORIGINS)
- [ ] 1.4 .gitignore 설정 (.env, __pycache__, *.db, .venv)
- [ ] 1.5 Alembic 초기화 및 alembic.ini 설정 (DATABASE_URL 환경변수 연동)

## 2. DB 모델 및 마이그레이션

- [ ] 2.1 SQLAlchemy Base 및 DB 연결 설정 (backend/database.py — SQLite/PostgreSQL 양쪽 지원)
- [ ] 2.2 users 모델 정의 (id, email UNIQUE, password_hash, team_id FK NULL, created_at)
- [ ] 2.3 teams 모델 정의 (id, name, invite_code UNIQUE, owner_id FK, created_at)
- [ ] 2.4 tasks 모델 정의 (id, team_id FK, title, status, creator_id FK, assignee_id FK NULL, created_at)
- [ ] 2.5 messages 모델 정의 (id, team_id FK, user_id FK, content, created_at)
- [ ] 2.6 Alembic 초기 마이그레이션 생성 및 `alembic upgrade head` 실행 확인
- [ ] 2.7 DB 인덱스 추가 (tasks.team_id+created_at, messages.team_id+created_at, teams.invite_code)

## 3. FastAPI 앱 기본 설정

- [ ] 3.1 backend/main.py — FastAPI 앱 생성, Swagger UI title/description 설정, CORS 미들웨어 설정
- [ ] 3.2 backend/config.py — 환경변수 로드 (pydantic Settings)
- [ ] 3.3 backend/dependencies.py — JWT 검증 의존성(get_current_user), DB 세션 의존성
- [ ] 3.4 backend/schemas.py — Pydantic 요청/응답 스키마 (UserCreate, UserLogin, TeamCreate, TaskCreate, MessageCreate 등)
- [ ] 3.5 backend/exceptions.py — 공통 에러 응답 핸들러 ({ error: { code, message } } 형태)
- [ ] 3.6 FastAPI 앱에 전역 exception handler 등록 (HTTPException → 표준 에러 포맷)

## 4. 인증 API 구현

- [ ] 4.1 POST /auth/signup — 이메일 중복 체크, bcrypt 해시, JWT 발급 (HTTP 201)
- [ ] 4.2 POST /auth/login — 자격증명 검증, JWT 발급 (이메일 존재 여부 노출 금지)
- [ ] 4.3 GET /auth/me — JWT 검증, 현재 사용자 정보 반환
- [ ] 4.4 POST /auth/logout — stateless, HTTP 200 빈 응답
- [ ] 4.5 JWT 생성·검증 유틸리티 (backend/utils/jwt.py — 만료 24h, HS256)

## 5. 팀 API 구현

- [ ] 5.1 POST /teams — 팀 생성 + invite_code 자동 생성(^[A-Z]{4}-[0-9]{4}$) + users.team_id 업데이트
- [ ] 5.2 POST /teams/join — invite_code 형식 검증 + 존재 확인 + users.team_id 업데이트
- [ ] 5.3 GET /teams/{id} — 팀 정보 조회 (멤버십 검증, 비멤버 403)
- [ ] 5.4 GET /teams/{id}/members — 멤버 목록 (is_owner 포함, 비멤버 403)
- [ ] 5.5 DELETE /teams/{id}/leave — 팀 나가기 (users.team_id = NULL)
- [ ] 5.6 팀 멤버십 검증 미들웨어/의존성 (require_team_member)

## 6. 칸반 API 구현

- [ ] 6.1 GET /teams/{id}/tasks — 목록 조회 (filter=all/me/unassigned, created_at desc 정렬)
- [ ] 6.2 POST /teams/{id}/tasks — 태스크 생성 (title 1-100자, assignee_id nullable, status=TODO)
- [ ] 6.3 GET /tasks/{id} — 단일 태스크 조회 (멤버십 검증)
- [ ] 6.4 PUT /tasks/{id} — 제목·assignee 수정
- [ ] 6.5 PATCH /tasks/{id}/status — 상태 변경 (TODO/DOING/DONE 검증)
- [ ] 6.6 DELETE /tasks/{id} — 삭제 (creator 또는 owner만, 비권한 403)

## 7. 채팅 API 구현

- [ ] 7.1 GET /teams/{id}/messages — 메시지 목록 (since= 파라미터 지원, 기본 50개, 오름차순)
- [ ] 7.2 POST /teams/{id}/messages — 메시지 전송 (1-1000자 검증, user_email 포함 응답)
- [ ] 7.3 DELETE /messages/{id} — 본인 메시지만 삭제 (타인/owner 403)

## 8. 프론트엔드 구현

- [ ] 8.1 frontend/js/api.js — fetch wrapper (JWT 헤더 자동 첨부, 401 catch → localStorage 삭제 + redirect)
- [ ] 8.2 frontend/js/auth.js — localStorage 토큰 관리 (save/get/remove/isLoggedIn)
- [ ] 8.3 frontend/login.html + js/login.js — 로그인/회원가입 탭 전환, 에러 인라인 표시, 처리중 버튼 비활성화
- [ ] 8.4 frontend/team.html + js/team.js — 팀 만들기/초대코드 입력 UI, 초대코드 복사 버튼
- [ ] 8.5 frontend/kanban.html + js/kanban.js — 3컬럼 칸반, 카드 CRUD, HTML5 drag&drop + PATCH 호출, 필터 버튼
- [ ] 8.6 frontend/chat.html + js/chat.js — 말풍선 UI, setInterval 5초 폴링, since= 증분, 1000자 카운터, 메시지 삭제
- [ ] 8.7 반응형 레이아웃 — 768px breakpoint, 모바일 햄버거 메뉴, 모바일 칸반 스와이프
- [ ] 8.8 공통 컴포넌트 — 토스트 알림, 확인 다이얼로그, 로딩 스피너

## 9. FastAPI StaticFiles + Vercel 배포 설정

- [ ] 9.1 FastAPI에 StaticFiles 마운트 (frontend/ → /static, index.html → /)
- [ ] 9.2 api/index.py 생성 — Vercel Python Serverless handler (Mangum 또는 직접 ASGI)
- [ ] 9.3 vercel.json 작성 — rewrites: /api/* → Serverless, /docs → Serverless, 나머지 → /public
- [ ] 9.4 public/ 디렉토리에 프론트엔드 파일 심볼릭링크 또는 복사 설정
- [ ] 9.5 requirements.txt Vercel 호환 확인 (psycopg2-binary 포함)

## 10. pytest 테스트 코드 작성

- [ ] 10.1 tests/conftest.py — 인메모리 SQLite 픽스처, TestClient(app) 설정, DB 초기화/정리
- [ ] 10.2 tests/test_auth.py — signup(정상/중복/약한비번), login(정상/잘못된자격증명), me(정상/만료토큰), logout
- [ ] 10.3 tests/test_teams.py — 팀생성, 합류(정상/잘못된코드/이미소속), 멤버목록, 팀나가기
- [ ] 10.4 tests/test_tasks.py — 태스크 CRUD, 상태변경, 삭제 권한(creator/owner/타인), 필터
- [ ] 10.5 tests/test_messages.py — 메시지 전송, since= 폴링, 삭제(본인/타인), 1000자 초과
- [ ] 10.6 `pytest tests/ -v` 전체 실행 확인 — 모든 테스트 PASS

## 11. 최종 검증

- [ ] 11.1 로컬에서 5종 기능 정상 흐름 수동 테스트 (회원가입→팀생성→칸반→채팅)
- [ ] 11.2 Swagger UI(/docs)에서 18개 API 전부 테스트 확인
- [ ] 11.3 모바일 화면(768px 이하) 반응형 동작 확인
- [ ] 11.4 pytest 전체 실행 최종 확인
