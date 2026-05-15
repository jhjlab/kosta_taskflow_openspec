## Context

`taskflow-mvp` 변경에서 정의된 스펙을 기반으로 실제 코드를 구현한다.
- 백엔드: FastAPI + SQLAlchemy 2.x + Alembic + python-jose + passlib
- 프론트엔드: Vanilla JS ES6+ + Tailwind CDN, MPA (4 HTML 파일)
- 테스트: pytest + httpx.AsyncClient (인메모리 SQLite)
- 배포: Vercel Serverless (Mangum) + Neon PostgreSQL

## 디렉토리 구조

```
D:\taskflow-openspec\
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱, CORS, StaticFiles, 라우터 등록
│   ├── config.py            # pydantic-settings, 환경변수
│   ├── database.py          # SQLAlchemy 엔진, SessionLocal, Base
│   ├── models.py            # ORM 모델 4개 (User, Team, Task, Message)
│   ├── schemas.py           # Pydantic 요청/응답 스키마
│   ├── dependencies.py      # get_db, get_current_user (JWT 검증)
│   ├── exceptions.py        # HTTPException → { error: { code, message } }
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── jwt.py           # create_token, verify_token
│   │   ├── password.py      # hash_password, verify_password
│   │   └── invite_code.py   # generate_invite_code (^[A-Z]{4}-[0-9]{4}$)
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # /auth/* 4개 엔드포인트
│       ├── teams.py         # /teams/* 5개 엔드포인트
│       ├── tasks.py         # /tasks/*, /teams/{id}/tasks 6개 엔드포인트
│       └── messages.py      # /teams/{id}/messages, /messages/{id} 3개 엔드포인트
├── frontend/
│   ├── login.html
│   ├── team.html
│   ├── kanban.html
│   ├── chat.html
│   └── js/
│       ├── api.js           # fetch wrapper, JWT 헤더 자동 첨부, 401 처리
│       ├── auth.js          # localStorage 토큰 관리
│       ├── login.js
│       ├── team.js
│       ├── kanban.js        # drag&drop, 상태변경, 필터
│       └── chat.js          # 폴링, since=, 1000자 카운터
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # TestClient, 인메모리 SQLite, 픽스처
│   ├── test_auth.py
│   ├── test_teams.py
│   ├── test_tasks.py
│   └── test_messages.py
├── migrations/              # Alembic
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial.py
├── api/
│   └── index.py             # Vercel Serverless: from mangum import Mangum
├── .env.example
├── .env                     # gitignore
├── .gitignore
├── alembic.ini
├── requirements.txt
└── vercel.json
```

## 핵심 구현 패턴

### 에러 응답 표준화
```python
# backend/exceptions.py
from fastapi import Request
from fastapi.responses import JSONResponse

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.detail.get("code"), "message": exc.detail.get("message")}}
    )
```

모든 HTTPException은 `detail={"code": "SNAKE_CASE", "message": "한국어"}` 형태로 발생.

### JWT 의존성
```python
# backend/dependencies.py
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = verify_token(token)  # 만료/유효 검증
    user = db.get(User, payload["sub"])
    if not user:
        raise HTTPException(401, {"code": "TOKEN_EXPIRED", "message": "인증이 만료되었습니다"})
    return user
```

### 팀 멤버십 검증
```python
def require_team_member(team_id: int, current_user: User = Depends(get_current_user)):
    if current_user.team_id != team_id:
        raise HTTPException(403, {"code": "FORBIDDEN", "message": "이 팀의 멤버가 아닙니다"})
    return current_user
```

### 채팅 폴링 since= 파라미터
```python
@router.get("/teams/{team_id}/messages")
async def get_messages(
    team_id: int,
    since: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Message).filter(Message.team_id == team_id)
    if since:
        query = query.filter(Message.created_at > since)
    else:
        query = query.order_by(Message.created_at.desc()).limit(50)
        # 반환 시 오름차순으로 reverse
    return query.order_by(Message.created_at.asc()).all()
```

### Frontend api.js 패턴
```javascript
// frontend/js/api.js
const API_BASE = '/api';

async function request(method, path, body = null) {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE}${path}`, {
        method,
        headers: {
            'Content-Type': 'application/json',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: body ? JSON.stringify(body) : null
    });
    if (res.status === 401) {
        localStorage.removeItem('token');
        location.href = '/login.html';
        return;
    }
    return res.json();
}
```

### pytest conftest 패턴
```python
# tests/conftest.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from backend.database import Base
from backend.main import app
from backend.dependencies import get_db

SQLALCHEMY_TEST_URL = "sqlite://"  # 인메모리

@pytest.fixture
def db():
    engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)

@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### Vercel api/index.py
```python
from mangum import Mangum
from backend.main import app

handler = Mangum(app, lifespan="off")
```

### vercel.json
```json
{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "/api/index" },
    { "source": "/docs", "destination": "/api/index" },
    { "source": "/redoc", "destination": "/api/index" },
    { "source": "/openapi.json", "destination": "/api/index" }
  ]
}
```

## Risks

- **Alembic + SQLite**: `render_as_batch=True` 옵션 필요 (ALTER TABLE 미지원)
- **Vercel Python cold start**: 첫 요청 지연 2-3초, Free tier 허용
- **Mangum lifespan**: SQLAlchemy 연결 이벤트와 충돌 가능 → `lifespan="off"` 설정
- **pytest 인메모리 DB**: `sqlite://` (파일 없음)로 각 테스트마다 독립 DB 보장
