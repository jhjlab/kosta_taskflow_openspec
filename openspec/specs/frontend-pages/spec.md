## ADDED Requirements

### Requirement: 공통 JS 모듈 (api.js, auth.js)
api.js는 모든 fetch 요청을 래핑하고, JWT 헤더 자동 첨부, 401 → redirect를 처리해야 한다.
auth.js는 localStorage 토큰 저장·조회·삭제를 제공해야 한다.

#### Scenario: JWT 헤더 자동 첨부
- **WHEN** api.js의 request() 함수로 API 호출 (localStorage에 token 있음)
- **THEN** Authorization: Bearer {token} 헤더가 자동으로 포함됨

#### Scenario: 401 응답 시 redirect
- **WHEN** API 응답이 HTTP 401
- **THEN** localStorage token 삭제 → /login.html redirect

### Requirement: login.html — 로그인/회원가입
단일 HTML 파일에 로그인·회원가입 탭 전환. 에러는 인라인 표시. 처리 중 버튼 비활성화.
가입 성공 또는 로그인 성공 시 team_id null → /team.html, team_id 있음 → /kanban.html.

#### Scenario: 회원가입 성공 후 리다이렉트
- **WHEN** 회원가입 성공 (team_id=null)
- **THEN** /team.html로 redirect

#### Scenario: 로그인 성공 후 리다이렉트 (팀 있음)
- **WHEN** 로그인 성공 (team_id != null)
- **THEN** /kanban.html로 redirect

### Requirement: team.html — 팀 선택/생성
팀 만들기 폼과 초대코드 합류 폼. 팀 생성 후 invite_code 표시 + 클립보드 복사 버튼.
팀이 이미 있는 경우 /kanban.html로 자동 redirect.

#### Scenario: 팀 생성 후 초대코드 표시
- **WHEN** 팀 생성 성공
- **THEN** 생성된 invite_code를 큰 텍스트로 표시, "복사" 버튼으로 클립보드 복사 가능

### Requirement: kanban.html — 칸반 보드
3컬럼(TODO/DOING/DONE), 카드 CRUD, HTML5 drag&drop, 필터(전체/@me/미할당).
페이지 진입 시 GET /teams/{id}/tasks 호출. 카드 drop 시 PATCH /tasks/{id}/status 호출.

#### Scenario: 드래그 drop 시 즉각 반영
- **WHEN** 카드를 DOING 컬럼에 drop
- **THEN** 카드가 즉시 DOING 컬럼으로 이동 (낙관적 업데이트), PATCH 호출 후 확정

### Requirement: chat.html — 채팅
말풍선 UI (본인=오른쪽, 타인=왼쪽). 5초 setInterval 폴링. 입력창 1000자 카운터.
화면 이탈 시 clearInterval로 폴링 중지.

#### Scenario: 1000자 카운터 적색 표시
- **WHEN** 1000자 초과 입력
- **THEN** 카운터 텍스트가 적색으로 변경, 전송 버튼 비활성화
