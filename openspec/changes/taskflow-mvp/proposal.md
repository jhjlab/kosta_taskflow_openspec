## Why

소규모 팀(3-5인)이 업무 진행 상황을 칸반 보드와 실시간 채팅으로 한 화면에서 추적할 수 있는 MVP가 없다. 기존 도구들은 과도하게 복잡하거나 채팅과 칸반이 분리되어 있어 컨텍스트 전환 비용이 크다.

## What Changes

- **NEW**: 이메일/비밀번호 기반 회원가입·로그인, JWT(24h) 인증 시스템
- **NEW**: 팀 생성 + 초대코드(AAAA-9999 형식) 발급 + 코드로 합류하는 팀 관리 시스템 (1인 1팀)
- **NEW**: TODO/DOING/DONE 3컬럼 칸반 보드 — 카드 추가·드래그 상태 변경·assignee 지정·삭제
- **NEW**: 팀 단위 채팅 — 5초 폴링(since= 증분), 메시지 1000자 제한, 본인 메시지 삭제
- **NEW**: FastAPI Swagger UI(/docs) — 전체 API 18개 브라우저에서 직접 테스트 가능
- **NEW**: pytest 기반 백엔드 테스트 코드 — 인증·팀·칸반·채팅 핵심 플로우 커버
- **NEW**: Vercel(FE+BE Serverless) + Neon(PostgreSQL) 운영 배포, 로컬은 SQLite

## Capabilities

### New Capabilities

- `user-auth`: 회원가입(POST /auth/signup), 로그인(POST /auth/login), 내 정보(GET /auth/me), 로그아웃(POST /auth/logout). JWT 24h, bcrypt 해시, stateless logout
- `team-management`: 팀 생성(POST /teams), 초대코드 합류(POST /teams/join), 팀 정보(GET /teams/{id}), 멤버 목록(GET /teams/{id}/members), 팀 나가기(DELETE /teams/{id}/leave). 1인 1팀, users.team_id로 관리
- `kanban-board`: 태스크 목록(GET /teams/{id}/tasks), 생성(POST), 단일 조회(GET /tasks/{id}), 수정(PUT /tasks/{id}), 상태 변경(PATCH /tasks/{id}/status), 삭제(DELETE). assignee_id nullable, creator/owner 삭제 권한
- `team-chat`: 메시지 목록(GET /teams/{id}/messages?since=), 전송(POST), 삭제(DELETE /messages/{id}). 5초 폴링, 1000자 제한, 본인만 삭제
- `api-docs-and-tests`: FastAPI 내장 Swagger UI(/docs, /redoc) 활성화 + pytest 테스트 스위트 (인증·팀·칸반·채팅 핵심 시나리오)
- `frontend-ui`: Vanilla JS + Tailwind CDN MPA — login.html, team.html, kanban.html, chat.html. 반응형(768px breakpoint), HTML5 drag&drop, 5초 setInterval 폴링
- `deployment-config`: 로컬(uvicorn + SQLite), 운영(Vercel Serverless Functions + Neon PostgreSQL). DATABASE_URL 환경변수 전환

### Modified Capabilities

## Impact

- **신규 프로젝트**: 기존 코드 없음, 그린필드
- **백엔드**: FastAPI, SQLAlchemy, pydantic, python-jose, bcrypt, pytest, httpx (테스트용)
- **프론트엔드**: Vanilla JS ES6+, Tailwind CDN, HTML5 Drag & Drop API, Fetch API
- **DB**: SQLite(로컬) / PostgreSQL Neon(운영) — 4테이블: users, teams, tasks, messages
- **API**: 18개 엔드포인트 (Auth 4 + Team 5 + Task 6 + Chat 3)
- **보안**: JWT Bearer 인증, bcrypt 비밀번호 해시, CORS 도메인 제한, 비멤버 403
- **배포**: Vercel (FE 정적 + BE Serverless), GitHub main push 자동 배포
