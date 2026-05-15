## ADDED Requirements

### Requirement: MPA 4개 HTML 페이지 구성
프론트엔드는 login.html, team.html, kanban.html, chat.html 4개 파일로 구성된다.
공통 모듈: `js/api.js`(fetch wrapper + JWT 자동 첨부 + 401 redirect), `js/auth.js`(localStorage 관리).
Tailwind CSS CDN으로 스타일링. 페이지 진입 시 JWT 유효성 검사 후 미인증 시 login.html로 redirect.

#### Scenario: 미인증 사용자가 kanban.html 직접 접근
- **WHEN** localStorage에 token 없는 상태에서 /kanban.html 접근
- **THEN** /login.html로 redirect

#### Scenario: JWT 만료 후 API 호출
- **WHEN** 만료된 JWT로 API 호출 → 서버 401 응답
- **THEN** localStorage token 삭제 + /login.html redirect + 토스트 "인증이 만료되었습니다"

### Requirement: 칸반 드래그 & 드롭
HTML5 native Drag & Drop API로 태스크 카드를 컬럼 간 이동. drop 시 PATCH /tasks/{id}/status 호출.
모바일(768px 미만)에서는 길게 누르기 → 상태 변경 드롭다운 메뉴로 대체.

#### Scenario: PC 드래그 상태 변경
- **WHEN** TODO 컬럼의 카드를 DOING 컬럼에 drop
- **THEN** PATCH /tasks/{id}/status { status: "DOING" } 호출, 카드가 DOING 컬럼으로 이동 (화면 즉시 반영)

#### Scenario: 모바일 상태 변경
- **WHEN** 모바일에서 태스크 카드 길게 누르기
- **THEN** 상태 변경 드롭다운(TODO/DOING/DONE) 표시, 선택 시 PATCH 호출

### Requirement: 채팅 5초 폴링
채팅 화면 진입 시 GET /teams/{id}/messages 첫 호출 후, 5초마다 since= 파라미터로 증분 폴링.
채팅 화면 이탈 시 폴링 중지(clearInterval).

#### Scenario: 새 메시지 수신
- **WHEN** 채팅 화면 열린 상태에서 5초 경과, 서버에 새 메시지 있음
- **THEN** 새 메시지가 화면 하단에 추가, 자동 스크롤

#### Scenario: 네트워크 끊김 후 재연결
- **WHEN** 폴링 중 네트워크 오류 발생 → 재연결 성공
- **THEN** since= 파라미터로 누락 메시지 일괄 수신, 연결 복구 토스트 표시

### Requirement: 반응형 UI
Tailwind CSS breakpoint(md:768px) 기준으로 PC/모바일 레이아웃 분기.
모바일에서 칸반은 1컬럼 스와이프, 채팅은 풀스크린, 네비게이션은 햄버거 메뉴.

#### Scenario: 모바일 칸반 컬럼 스와이프
- **WHEN** 768px 미만 화면에서 칸반 접근
- **THEN** 1컬럼씩 표시, TODO/DOING/DONE 탭 또는 좌우 스와이프로 전환

#### Scenario: 데스크탑 칸반 3컬럼
- **WHEN** 768px 이상 화면에서 칸반 접근
- **THEN** TODO/DOING/DONE 3컬럼 나란히 표시
