## ADDED Requirements

### Requirement: 태스크 목록 조회
팀 멤버는 팀의 태스크 목록을 조회할 수 있다. 필터(all/me/unassigned)와 정렬(created_at desc) 지원.
응답: [{ id, team_id, title, status, creator_id, assignee_id, created_at }]

#### Scenario: 전체 조회
- **WHEN** GET /teams/{id}/tasks (팀 멤버)
- **THEN** HTTP 200, 팀의 모든 태스크 배열, created_at 내림차순

#### Scenario: 내 태스크 필터
- **WHEN** GET /teams/{id}/tasks?filter=me (팀 멤버)
- **THEN** HTTP 200, assignee_id = current_user_id 인 태스크만 반환 (creator_id 아님)

#### Scenario: 미할당 필터
- **WHEN** GET /teams/{id}/tasks?filter=unassigned (팀 멤버)
- **THEN** HTTP 200, assignee_id IS NULL 인 태스크만 반환

#### Scenario: 비멤버 접근
- **WHEN** GET /teams/{id}/tasks (다른 팀 소속 사용자)
- **THEN** HTTP 403, { error: { code: "FORBIDDEN", message: "권한이 없습니다" } }

### Requirement: 태스크 생성
팀 멤버는 태스크를 생성할 수 있다. 기본 status = TODO, assignee_id는 nullable.
title 1-100자 제한.

#### Scenario: 정상 생성
- **WHEN** POST /teams/{id}/tasks { title: "JWT 구현", assignee_id: 42 }
- **THEN** HTTP 201, { id, team_id, title, status: "TODO", creator_id, assignee_id: 42, created_at }

#### Scenario: assignee 없이 생성 (미할당)
- **WHEN** POST /teams/{id}/tasks { title: "리뷰 요청" }
- **THEN** HTTP 201, { ..., assignee_id: null }

#### Scenario: title 100자 초과
- **WHEN** POST /teams/{id}/tasks { title: "a" * 101 }
- **THEN** HTTP 400, { error: { code: "VALIDATION_ERROR", message: "제목은 1-100자여야 합니다" } }

### Requirement: 태스크 단일 조회
팀 멤버는 태스크 ID로 단일 태스크를 조회할 수 있다.

#### Scenario: 정상 조회
- **WHEN** GET /tasks/{id} (해당 팀 멤버)
- **THEN** HTTP 200, { id, team_id, title, status, creator_id, assignee_id, created_at }

#### Scenario: 존재하지 않는 태스크
- **WHEN** GET /tasks/{id} (없는 id)
- **THEN** HTTP 404, { error: { code: "NOT_FOUND", message: "해당 항목을 찾을 수 없습니다" } }

### Requirement: 태스크 제목·assignee 수정
팀 멤버는 태스크 제목과 assignee_id를 수정할 수 있다.

#### Scenario: 제목 수정
- **WHEN** PUT /tasks/{id} { title: "새 제목" } (팀 멤버)
- **THEN** HTTP 200, 수정된 태스크 반환

#### Scenario: assignee 변경
- **WHEN** PUT /tasks/{id} { assignee_id: 99 } (팀 멤버)
- **THEN** HTTP 200, 수정된 태스크 반환

#### Scenario: assignee NULL로 변경 (미할당)
- **WHEN** PUT /tasks/{id} { assignee_id: null } (팀 멤버)
- **THEN** HTTP 200, { ..., assignee_id: null }

### Requirement: 태스크 상태 변경 (드래그)
팀 멤버는 태스크 상태를 TODO/DOING/DONE 중 하나로 변경할 수 있다. 별도 PATCH 엔드포인트.

#### Scenario: 상태 변경
- **WHEN** PATCH /tasks/{id}/status { status: "DOING" } (팀 멤버)
- **THEN** HTTP 200, { ..., status: "DOING" }

#### Scenario: 유효하지 않은 상태값
- **WHEN** PATCH /tasks/{id}/status { status: "INVALID" }
- **THEN** HTTP 400, { error: { code: "VALIDATION_ERROR", message: "status는 TODO/DOING/DONE 중 하나여야 합니다" } }

### Requirement: 태스크 삭제
creator 또는 team owner만 태스크를 삭제할 수 있다.

#### Scenario: creator가 본인 태스크 삭제
- **WHEN** DELETE /tasks/{id} (creator_id = current_user_id)
- **THEN** HTTP 204

#### Scenario: team owner가 타인 태스크 삭제
- **WHEN** DELETE /tasks/{id} (current_user = team.owner_id, 타인 태스크)
- **THEN** HTTP 204

#### Scenario: 일반 멤버가 타인 태스크 삭제 시도
- **WHEN** DELETE /tasks/{id} (creator도 owner도 아닌 멤버)
- **THEN** HTTP 403, { error: { code: "FORBIDDEN", message: "권한이 없습니다" } }
