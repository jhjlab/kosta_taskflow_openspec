from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..dependencies import get_db, get_current_user
from ..models import User
from ..schemas import UserCreate, UserLogin, TokenOut, UserOut
from ..utils.jwt import create_access_token
from ..utils.password import hash_password, verify_password

router = APIRouter()


@router.post("/signup", response_model=TokenOut, status_code=201, summary="회원가입")
def signup(body: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(409, {"code": "EMAIL_TAKEN", "message": "이미 가입된 이메일입니다"})
    user = User(email=body.email, password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id)})
    return {"token": token, "user": user}


@router.post("/login", response_model=TokenOut, summary="로그인")
def login(body: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, {"code": "INVALID_CREDENTIALS", "message": "이메일 또는 비밀번호가 일치하지 않습니다"})
    token = create_access_token({"sub": str(user.id)})
    return {"token": token, "user": user}


@router.get("/me", response_model=UserOut, summary="내 정보 조회")
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout", summary="로그아웃")
def logout():
    return {}
