from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..dependencies import get_db, get_current_user
from ..models import User, Message
from ..schemas import MessageCreate, MessageOut

router = APIRouter()


def _to_message_out(msg: Message) -> MessageOut:
    return MessageOut(
        id=msg.id,
        team_id=msg.team_id,
        user_id=msg.user_id,
        user_email=msg.user.email,
        content=msg.content,
        created_at=msg.created_at,
    )


@router.get("/teams/{team_id}/messages", response_model=List[MessageOut], summary="채팅 메시지 목록 (폴링)")
def list_messages(
    team_id: int,
    since: Optional[datetime] = Query(None, description="ISO 시각 이후 메시지만 반환"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.team_id != team_id:
        raise HTTPException(403, {"code": "FORBIDDEN", "message": "권한이 없습니다"})
    q = db.query(Message).filter(Message.team_id == team_id)
    if since:
        q = q.filter(Message.created_at > since)
        messages = q.order_by(Message.created_at.asc()).all()
    else:
        messages = (
            q.order_by(Message.created_at.desc()).limit(50).all()[::-1]
        )
    return [_to_message_out(m) for m in messages]


@router.post("/teams/{team_id}/messages", response_model=MessageOut, status_code=201, summary="메시지 전송")
def send_message(
    team_id: int,
    body: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.team_id != team_id:
        raise HTTPException(403, {"code": "FORBIDDEN", "message": "권한이 없습니다"})
    if len(body.content) > 1000:
        raise HTTPException(
            400,
            {"code": "TOO_LONG", "message": "메시지는 1000자 이내로 입력하세요",
             "limit": 1000, "actual": len(body.content)},
        )
    msg = Message(team_id=team_id, user_id=current_user.id, content=body.content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return _to_message_out(msg)


@router.delete("/messages/{message_id}", status_code=204, summary="메시지 삭제 (본인만)")
def delete_message(message_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    msg = db.get(Message, message_id)
    if not msg:
        raise HTTPException(404, {"code": "NOT_FOUND", "message": "해당 항목을 찾을 수 없습니다"})
    if msg.user_id != current_user.id:
        raise HTTPException(403, {"code": "NOT_OWNER", "message": "본인의 메시지만 삭제할 수 있습니다"})
    db.delete(msg)
    db.commit()
