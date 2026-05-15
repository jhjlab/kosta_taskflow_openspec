## ADDED Requirements

### Requirement: 팀 생성
인증된 사용자가 팀을 생성하면 invite_code(대문자 4자 + '-' + 숫자 4자, ^[A-Z]{4}-[0-9]{4}$)가 자동 생성되고, owner_id가 현재 사용자로 설정되며, users.team_id가 업데이트된다.

#### Scenario: 정상 팀 생성
- **WHEN** POST /teams { name: "Frontiers" } (인증된 사용자, team_id=NULL)
- **THEN** HTTP 201, { id, name, invite_code: "FRNT-2026", owner_id, created_at }, users.team_id = teams.id로 업데이트

#### Scenario: 이미 팀에 소속된 사용자가 팀 생성 시도
- **WHEN** POST /teams { name: "NewTeam" } (team_id가 이미 있는 사용자)
- **THEN** HTTP 409, { error: { code: "ALREADY_IN_TEAM", message: "이미 팀에 소속되어 있습니다" } }

#### Scenario: 팀 이름 길이 초과
- **WHEN** POST /teams { name: "a" * 31 }
- **THEN** HTTP 400, { error: { code: "VALIDATION_ERROR", message: "팀 이름은 1-30자여야 합니다" } }

### Requirement: 초대코드로 팀 합류
사용자가 invite_code를 입력하면 형식 검증 → 존재 확인 → users.team_id 업데이트 순서로 처리.
응답에 팀 정보(member_count 포함) 반환.

#### Scenario: 정상 합류
- **WHEN** POST /teams/join { invite_code: "FRNT-2026" } (team_id=NULL 사용자)
- **THEN** HTTP 200, { team: { id, name, member_count }, redirect: "/teams/{id}" }, users.team_id 업데이트

#### Scenario: 형식 오류
- **WHEN** POST /teams/join { invite_code: "abcd1234" } (소문자, 하이픈 없음)
- **THEN** HTTP 400, { error: { code: "VALIDATION_ERROR", message: "초대코드 형식이 올바르지 않습니다 (예: ABCD-1234)" } }

#### Scenario: 존재하지 않는 초대코드
- **WHEN** POST /teams/join { invite_code: "XXXX-9999" }
- **THEN** HTTP 404, { error: { code: "NOT_FOUND", message: "해당 초대코드를 찾을 수 없습니다" } }

#### Scenario: 이미 팀 소속 사용자
- **WHEN** POST /teams/join { invite_code: "FRNT-2026" } (team_id != NULL 사용자)
- **THEN** HTTP 409, { error: { code: "ALREADY_IN_TEAM", message: "이미 다른 팀에 소속되어 있습니다" } }

### Requirement: 팀 정보 조회
팀 멤버만 팀 정보를 조회할 수 있다. 비멤버는 403.

#### Scenario: 정상 조회
- **WHEN** GET /teams/{id} (해당 팀 멤버)
- **THEN** HTTP 200, { id, name, invite_code, owner_id, member_count, created_at }

#### Scenario: 비멤버 접근
- **WHEN** GET /teams/{id} (다른 팀 소속 사용자)
- **THEN** HTTP 403, { error: { code: "FORBIDDEN", message: "이 팀의 멤버가 아닙니다" } }

### Requirement: 팀 멤버 목록 조회
팀 멤버만 멤버 목록을 조회할 수 있다. owner 여부(is_owner) 포함.

#### Scenario: 정상 조회
- **WHEN** GET /teams/{id}/members (해당 팀 멤버)
- **THEN** HTTP 200, [{ id, email, is_owner: bool, joined_at }] (joined_at = users.created_at)

#### Scenario: 비멤버 접근
- **WHEN** GET /teams/{id}/members (다른 팀 소속 사용자)
- **THEN** HTTP 403, { error: { code: "FORBIDDEN", message: "권한이 없습니다" } }

### Requirement: 팀 나가기
사용자가 팀을 나가면 users.team_id를 NULL로 업데이트. owner가 나가면 팀은 유지되고 owner_id는 NULL로(또는 다음 멤버로 — MVP에서는 NULL 허용).

#### Scenario: 멤버가 팀 나가기
- **WHEN** DELETE /teams/{id}/leave (해당 팀 멤버)
- **THEN** HTTP 200, {}, users.team_id = NULL로 업데이트

#### Scenario: 비멤버 나가기 시도
- **WHEN** DELETE /teams/{id}/leave (다른 팀 소속 사용자)
- **THEN** HTTP 403, { error: { code: "FORBIDDEN", message: "이 팀의 멤버가 아닙니다" } }
