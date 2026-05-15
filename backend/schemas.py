from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from .models import TaskStatus


# ── Auth ──────────────────────────────────────────
class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError("비밀번호는 8자 이상이어야 합니다")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    team_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    token: str
    user: UserOut


# ── Team ──────────────────────────────────────────
class TeamCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_length(cls, v):
        if not (1 <= len(v) <= 30):
            raise ValueError("팀 이름은 1-30자여야 합니다")
        return v


class TeamJoin(BaseModel):
    invite_code: str


class TeamOut(BaseModel):
    id: int
    name: str
    invite_code: str
    owner_id: Optional[int]
    member_count: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MemberOut(BaseModel):
    id: int
    email: str
    is_owner: bool
    joined_at: datetime

    model_config = {"from_attributes": True}


# ── Task ──────────────────────────────────────────
class TaskCreate(BaseModel):
    title: str
    assignee_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def title_length(cls, v):
        if not (1 <= len(v) <= 100):
            raise ValueError("제목은 1-100자여야 합니다")
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    assignee_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def title_length(cls, v):
        if v is not None and not (1 <= len(v) <= 100):
            raise ValueError("제목은 1-100자여야 합니다")
        return v


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskOut(BaseModel):
    id: int
    team_id: int
    title: str
    status: TaskStatus
    creator_id: Optional[int]
    assignee_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Message ───────────────────────────────────────
class MessageCreate(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def content_length(cls, v):
        if not v or not v.strip():
            raise ValueError("메시지를 입력하세요")
        if len(v) > 1000:
            raise ValueError(f"메시지는 1000자 이내로 입력하세요 (현재 {len(v)}자)")
        return v


class MessageOut(BaseModel):
    id: int
    team_id: int
    user_id: int
    user_email: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
