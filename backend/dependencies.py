from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import SessionLocal
from .utils.jwt import verify_token
from .models import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail={"code": "TOKEN_EXPIRED", "message": "인증이 만료되었습니다"},
        )
    payload = verify_token(credentials.credentials)
    user_id = payload.get("sub")
    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(
            status_code=401,
            detail={"code": "TOKEN_EXPIRED", "message": "인증이 만료되었습니다"},
        )
    return user


def require_team_member(team_id: int, current_user: User = Depends(get_current_user)) -> User:
    if current_user.team_id != team_id:
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "이 팀의 멤버가 아닙니다"},
        )
    return current_user
