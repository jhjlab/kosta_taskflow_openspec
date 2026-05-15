## ADDED Requirements

### Requirement: Swagger UI 제공
FastAPI 앱은 /docs(Swagger UI)와 /redoc(ReDoc)에서 전체 API를 브라우저에서 직접 테스트할 수 있어야 한다.
모든 엔드포인트에 summary, description, response_model, status_code 가 명시되어야 한다.
JWT Bearer 인증을 Swagger UI에서 입력하고 인증된 API를 테스트할 수 있어야 한다.

#### Scenario: Swagger UI 접근
- **WHEN** GET /docs (브라우저)
- **THEN** HTTP 200, Swagger UI HTML 렌더링, 18개 API 엔드포인트 전부 표시

#### Scenario: Swagger UI에서 JWT 인증 후 API 호출
- **WHEN** /docs에서 Authorize 버튼 클릭 → Bearer 토큰 입력 → GET /auth/me 실행
- **THEN** 인증된 응답(200) 반환

#### Scenario: ReDoc 접근
- **WHEN** GET /redoc (브라우저)
- **THEN** HTTP 200, ReDoc HTML 렌더링

### Requirement: pytest 통합 테스트 스위트
`tests/` 디렉토리에 pytest 테스트가 있어야 하며, 인메모리 SQLite로 실제 DB 없이 실행 가능해야 한다.
각 테스트는 독립적으로 격리된 DB 픽스처를 사용한다.

#### Scenario: 테스트 실행
- **WHEN** `pytest tests/ -v` 실행
- **THEN** 모든 테스트 PASS, 외부 서버나 DB 연결 불필요

#### Scenario: 인증 테스트 커버리지
- **WHEN** `pytest tests/test_auth.py -v` 실행
- **THEN** signup(정상/중복/비밀번호약함), login(정상/잘못된자격증명), me(정상/만료토큰), logout 케이스 모두 PASS

#### Scenario: 팀 테스트 커버리지
- **WHEN** `pytest tests/test_teams.py -v` 실행
- **THEN** 팀 생성, 초대코드 합류(정상/잘못된코드/이미소속), 멤버목록, 팀 나가기 케이스 PASS

#### Scenario: 칸반 테스트 커버리지
- **WHEN** `pytest tests/test_tasks.py -v` 실행
- **THEN** 태스크 CRUD, 상태변경(PATCH), 삭제 권한(creator/owner/타인) 케이스 PASS

#### Scenario: 채팅 테스트 커버리지
- **WHEN** `pytest tests/test_messages.py -v` 실행
- **THEN** 메시지 전송, 폴링(since=), 삭제(본인/타인) 케이스 PASS

### Requirement: 에러 응답 표준 일관성
모든 4xx/5xx 에러 응답은 `{ error: { code: string, message: string } }` 형태여야 한다.

#### Scenario: 모든 에러 응답 형태 검증
- **WHEN** 각 오류 케이스(400/401/403/404/409)에서 API 호출
- **THEN** 응답 body가 항상 { error: { code, message } } 구조

#### Scenario: 500 내부 오류
- **WHEN** 서버 내부 오류 발생
- **THEN** HTTP 500, { error: { code: "INTERNAL_ERROR", message: "서버 오류가 발생했습니다" } }
