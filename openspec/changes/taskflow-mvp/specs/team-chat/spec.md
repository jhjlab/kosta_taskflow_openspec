## ADDED Requirements

### Requirement: 메시지 목록 조회 (폴링)
팀 멤버는 팀 채팅 메시지를 조회할 수 있다. since= 파라미터로 증분 폴링 지원.
since 없으면 최근 50개, since 있으면 해당 시각 이후 메시지만 반환.

#### Scenario: 초기 조회 (since 없음)
- **WHEN** GET /teams/{id}/messages (팀 멤버)
- **THEN** HTTP 200, 최근 50개 메시지 배열 (created_at 오름차순), [{ id, user_id, user_email, content, created_at }]

#### Scenario: 증분 폴링 (since 있음)
- **WHEN** GET /teams/{id}/messages?since=2026-05-13T14:27:00Z (팀 멤버)
- **THEN** HTTP 200, 해당 시각 이후 새 메시지만 반환 (빈 배열이면 [] 반환)

#### Scenario: 비멤버 접근
- **WHEN** GET /teams/{id}/messages (다른 팀 소속 사용자)
- **THEN** HTTP 403, { error: { code: "FORBIDDEN", message: "권한이 없습니다" } }

### Requirement: 메시지 전송
팀 멤버는 팀 채팅에 메시지를 전송할 수 있다. 내용은 1-1000자, 클라이언트와 서버 양쪽에서 검증.

#### Scenario: 정상 전송
- **WHEN** POST /teams/{id}/messages { content: "안녕하세요" } (팀 멤버)
- **THEN** HTTP 201, { id, team_id, user_id, user_email, content, created_at }

#### Scenario: 1000자 초과
- **WHEN** POST /teams/{id}/messages { content: "a" * 1001 }
- **THEN** HTTP 400, { error: { code: "TOO_LONG", message: "메시지는 1000자 이내로 입력하세요", limit: 1000, actual: 1001 } }

#### Scenario: 빈 메시지
- **WHEN** POST /teams/{id}/messages { content: "" }
- **THEN** HTTP 400, { error: { code: "VALIDATION_ERROR", message: "메시지를 입력하세요" } }

#### Scenario: 비멤버 전송 시도
- **WHEN** POST /teams/{id}/messages { content: "test" } (다른 팀 소속 사용자)
- **THEN** HTTP 403, { error: { code: "FORBIDDEN", message: "권한이 없습니다" } }

### Requirement: 메시지 삭제
본인이 작성한 메시지만 삭제할 수 있다. team owner도 타인 메시지 삭제 불가.

#### Scenario: 본인 메시지 삭제
- **WHEN** DELETE /messages/{id} (user_id = current_user_id)
- **THEN** HTTP 204

#### Scenario: 타인 메시지 삭제 시도
- **WHEN** DELETE /messages/{id} (user_id != current_user_id, owner여도)
- **THEN** HTTP 403, { error: { code: "NOT_OWNER", message: "본인의 메시지만 삭제할 수 있습니다" } }

#### Scenario: 존재하지 않는 메시지 삭제
- **WHEN** DELETE /messages/{id} (없는 id)
- **THEN** HTTP 404, { error: { code: "NOT_FOUND", message: "해당 항목을 찾을 수 없습니다" } }
