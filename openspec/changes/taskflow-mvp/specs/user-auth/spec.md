## ADDED Requirements

### Requirement: 회원가입
시스템은 이메일과 비밀번호를 받아 계정을 생성하고 JWT를 즉시 발급해야 한다.
이메일은 UNIQUE, 비밀번호는 bcrypt 해시 저장. 이메일 인증 없이 즉시 활성화.
응답: HTTP 201 + `{ token, user: { id, email, team_id } }`.
실패: 이메일 형식 오류 → 400 VALIDATION_ERROR, 중복 이메일 → 409 EMAIL_TAKEN, 비밀번호 8자 미만 → 400 VALIDATION_ERROR.

#### Scenario: 정상 회원가입
- **WHEN** POST /auth/signup { email: "user@example.com", password: "pass1234" }
- **THEN** HTTP 201, 응답에 JWT token 포함, users 테이블에 INSERT, password_hash는 bcrypt 해시값

#### Scenario: 중복 이메일 가입 시도
- **WHEN** POST /auth/signup { email: "taken@example.com", password: "pass1234" } (이미 존재하는 이메일)
- **THEN** HTTP 409, { error: { code: "EMAIL_TAKEN", message: "이미 가입된 이메일입니다" } }

#### Scenario: 비밀번호 8자 미만
- **WHEN** POST /auth/signup { email: "user@example.com", password: "short" }
- **THEN** HTTP 400, { error: { code: "VALIDATION_ERROR", message: "비밀번호는 8자 이상이어야 합니다" } }

#### Scenario: 잘못된 이메일 형식
- **WHEN** POST /auth/signup { email: "not-an-email", password: "pass1234" }
- **THEN** HTTP 400, { error: { code: "VALIDATION_ERROR", message: "올바른 이메일 형식이 아닙니다" } }

### Requirement: 로그인
시스템은 이메일과 비밀번호를 검증하고 JWT(만료 24h)를 발급해야 한다.
이메일 존재 여부를 응답에서 구별하지 않는다(보안). 응답에 user.team_id 포함(팀 소속 여부 분기용).

#### Scenario: 정상 로그인
- **WHEN** POST /auth/login { email: "user@example.com", password: "pass1234" }
- **THEN** HTTP 200, { token: "eyJ...", user: { id, email, team_id } }, JWT exp = 현재 + 24h

#### Scenario: 잘못된 자격증명
- **WHEN** POST /auth/login { email: "user@example.com", password: "wrongpass" }
- **THEN** HTTP 401, { error: { code: "INVALID_CREDENTIALS", message: "이메일 또는 비밀번호가 일치하지 않습니다" } }

#### Scenario: 존재하지 않는 이메일
- **WHEN** POST /auth/login { email: "notexist@example.com", password: "anypass" }
- **THEN** HTTP 401, { error: { code: "INVALID_CREDENTIALS", message: "이메일 또는 비밀번호가 일치하지 않습니다" } } (이메일 존재 여부 노출 X)

### Requirement: 내 정보 조회
시스템은 유효한 JWT를 가진 사용자의 정보를 반환해야 한다.

#### Scenario: 정상 조회
- **WHEN** GET /auth/me (Authorization: Bearer {valid_jwt})
- **THEN** HTTP 200, { id, email, team_id, created_at }

#### Scenario: JWT 없이 요청
- **WHEN** GET /auth/me (Authorization 헤더 없음)
- **THEN** HTTP 401, { error: { code: "TOKEN_EXPIRED", message: "인증이 만료되었습니다" } }

#### Scenario: 만료된 JWT
- **WHEN** GET /auth/me (만료된 JWT)
- **THEN** HTTP 401, { error: { code: "TOKEN_EXPIRED", message: "인증이 만료되었습니다" } }

### Requirement: 로그아웃 (Stateless)
서버는 JWT 블랙리스트 없이 HTTP 200만 반환한다. 클라이언트가 localStorage에서 토큰을 삭제하는 방식으로 처리.

#### Scenario: 로그아웃 요청
- **WHEN** POST /auth/logout (Authorization: Bearer {jwt})
- **THEN** HTTP 200, {} (빈 응답)

#### Scenario: 토큰 없이 로그아웃
- **WHEN** POST /auth/logout (Authorization 헤더 없음)
- **THEN** HTTP 200, {} (토큰 검증 안 함, 항상 200)
