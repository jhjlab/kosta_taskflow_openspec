## ADDED Requirements

### Requirement: Auth 라우터 (backend/routers/auth.py)
4개 엔드포인트가 /auth 접두어로 등록되어야 한다.
POST /auth/signup, POST /auth/login, GET /auth/me, POST /auth/logout.

#### Scenario: 라우터 등록 확인
- **WHEN** GET /openapi.json 호출
- **THEN** /auth/signup, /auth/login, /auth/me, /auth/logout 경로가 포함됨

#### Scenario: signup response_model
- **WHEN** POST /auth/signup 성공
- **THEN** HTTP 201, { token: str, user: { id, email, team_id } } 반환

### Requirement: Teams 라우터 (backend/routers/teams.py)
5개 엔드포인트: POST /teams, POST /teams/join, GET /teams/{id}, GET /teams/{id}/members, DELETE /teams/{id}/leave.

#### Scenario: invite_code 자동 생성
- **WHEN** POST /teams { name: "Test" } 요청
- **THEN** 응답에 invite_code 포함, 정규식 ^[A-Z]{4}-[0-9]{4}$ 만족

#### Scenario: 멤버 목록 is_owner 포함
- **WHEN** GET /teams/{id}/members 요청
- **THEN** 배열 내 각 객체에 is_owner: bool 필드 포함

### Requirement: Tasks 라우터 (backend/routers/tasks.py)
6개 엔드포인트: GET /teams/{id}/tasks, POST /teams/{id}/tasks, GET /tasks/{id}, PUT /tasks/{id}, PATCH /tasks/{id}/status, DELETE /tasks/{id}.

#### Scenario: PATCH status 분리
- **WHEN** PATCH /tasks/{id}/status { status: "DOING" } 요청
- **THEN** HTTP 200, 상태만 변경됨 (제목 등 다른 필드 미변경)

#### Scenario: 삭제 권한 매트릭스
- **WHEN** creator가 아닌 일반 멤버가 DELETE /tasks/{id} 요청
- **THEN** HTTP 403 FORBIDDEN (단, team owner는 허용)

### Requirement: Messages 라우터 (backend/routers/messages.py)
3개 엔드포인트: GET /teams/{id}/messages, POST /teams/{id}/messages, DELETE /messages/{id}.

#### Scenario: since= 파라미터 동작
- **WHEN** GET /teams/{id}/messages?since=2026-05-13T14:27:00Z 요청
- **THEN** 해당 시각 이후 메시지만 반환 (오름차순), 없으면 빈 배열 []

#### Scenario: 메시지 응답에 user_email 포함
- **WHEN** GET /teams/{id}/messages 요청
- **THEN** 각 메시지에 user_id, user_email 필드 포함 (JOIN 또는 관계 로딩)
