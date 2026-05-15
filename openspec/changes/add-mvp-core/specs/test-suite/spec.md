## ADDED Requirements

### Requirement: conftest.py — 테스트 픽스처
tests/conftest.py는 인메모리 SQLite DB 픽스처와 TestClient 픽스처를 제공해야 한다.
각 테스트 함수마다 독립된 DB (테이블 생성 → 테스트 → 테이블 삭제).

#### Scenario: 테스트 격리
- **WHEN** 두 테스트가 순서대로 실행
- **THEN** 첫 번째 테스트에서 생성된 데이터가 두 번째 테스트에 영향을 주지 않음

#### Scenario: 인증된 클라이언트 픽스처
- **WHEN** authed_client 픽스처 사용
- **THEN** 이미 회원가입+로그인된 사용자의 JWT가 헤더에 포함된 TestClient 반환

### Requirement: test_auth.py — 인증 테스트
signup 3케이스(정상/중복/약한비번), login 2케이스(정상/잘못된자격증명), me 2케이스(정상/만료토큰), logout 1케이스.

#### Scenario: 전체 인증 테스트 실행
- **WHEN** `pytest tests/test_auth.py -v` 실행
- **THEN** 8개 이상 테스트 모두 PASSED

### Requirement: test_teams.py — 팀 테스트
팀 생성, 초대코드 합류(정상/잘못된코드/이미소속), 멤버 목록, 팀 나가기.

#### Scenario: 전체 팀 테스트 실행
- **WHEN** `pytest tests/test_teams.py -v` 실행
- **THEN** 6개 이상 테스트 모두 PASSED

### Requirement: test_tasks.py — 칸반 테스트
태스크 CRUD, PATCH 상태변경, 삭제 권한 매트릭스(creator/owner/타인), 필터(me/unassigned).

#### Scenario: 전체 칸반 테스트 실행
- **WHEN** `pytest tests/test_tasks.py -v` 실행
- **THEN** 8개 이상 테스트 모두 PASSED

### Requirement: test_messages.py — 채팅 테스트
메시지 전송, since= 폴링, 삭제(본인/타인), 1000자 초과 검증.

#### Scenario: 전체 채팅 테스트 실행
- **WHEN** `pytest tests/test_messages.py -v` 실행
- **THEN** 6개 이상 테스트 모두 PASSED

### Requirement: 전체 테스트 스위트 실행
`pytest tests/ -v`로 외부 의존성 없이 전체 테스트가 실행되어야 한다.

#### Scenario: 전체 테스트 실행
- **WHEN** `pytest tests/ -v` 실행 (서버·DB 없이)
- **THEN** 모든 테스트 PASSED, 0 failed
