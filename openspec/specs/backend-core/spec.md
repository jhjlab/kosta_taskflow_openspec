## ADDED Requirements

### Requirement: FastAPI 앱 구성
backend/main.py가 FastAPI 앱을 생성하고, CORS 미들웨어, StaticFiles, 라우터를 등록해야 한다.
Swagger UI title="TaskFlow API", version="1.0.0". /docs, /redoc 활성화.

#### Scenario: 앱 시작
- **WHEN** `uvicorn backend.main:app --reload --port 8000` 실행
- **THEN** http://localhost:8000/docs 접근 시 Swagger UI 렌더링, 18개 API 전부 표시

#### Scenario: CORS 설정
- **WHEN** 프론트엔드(localhost:3000)에서 API 호출
- **THEN** CORS 허용 응답 (Access-Control-Allow-Origin 헤더 포함)

### Requirement: SQLAlchemy 모델 4개
backend/models.py에 User, Team, Task, Message ORM 모델이 정의되어야 한다.
스토리보드 v2 결정 반영: users.team_id(nullable), tasks.assignee_id(nullable), tasks.created_at.

#### Scenario: 모델 관계 검증
- **WHEN** User 생성 후 team_id 업데이트
- **THEN** users.team_id = teams.id FK 정상 동작, team_id=NULL 허용

#### Scenario: Task assignee_id nullable
- **WHEN** Task 생성 시 assignee_id 미설정
- **THEN** tasks.assignee_id = NULL로 저장

### Requirement: 에러 응답 표준 핸들러
모든 HTTPException이 `{ "error": { "code": "SCREAMING_SNAKE", "message": "한국어" } }` 형태로 반환되어야 한다.

#### Scenario: 404 에러
- **WHEN** 없는 리소스에 GET 요청
- **THEN** HTTP 404, { "error": { "code": "NOT_FOUND", "message": "해당 항목을 찾을 수 없습니다" } }

#### Scenario: 422 Validation 에러 (Pydantic)
- **WHEN** 잘못된 요청 body로 POST 요청
- **THEN** HTTP 422가 아닌 HTTP 400, { "error": { "code": "VALIDATION_ERROR", "message": "..." } }

### Requirement: JWT 유틸리티
backend/utils/jwt.py가 토큰 생성(create_token)과 검증(verify_token)을 제공해야 한다.
만료 24h, 알고리즘 HS256.

#### Scenario: 토큰 생성 및 검증
- **WHEN** create_token({"sub": "42"}) 호출 후 verify_token 실행
- **THEN** payload에서 sub="42" 추출 성공

#### Scenario: 만료 토큰 검증
- **WHEN** 만료된 토큰으로 verify_token 호출
- **THEN** JWTError 발생 → HTTPException 401 TOKEN_EXPIRED
