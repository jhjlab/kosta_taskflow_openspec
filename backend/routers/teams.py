import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..dependencies import get_db, get_current_user
from ..models import User, Team
from ..schemas import TeamCreate, TeamJoin, TeamOut, MemberOut
from ..utils.invite_code import generate_invite_code

router = APIRouter()

INVITE_CODE_RE = re.compile(r"^[A-Z]{4}-[0-9]{4}$")


@router.post("/teams", response_model=TeamOut, status_code=201, summary="팀 생성")
def create_team(body: TeamCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.team_id:
        raise HTTPException(409, {"code": "ALREADY_IN_TEAM", "message": "이미 팀에 소속되어 있습니다"})
    invite_code = generate_invite_code()
    while db.query(Team).filter(Team.invite_code == invite_code).first():
        invite_code = generate_invite_code()
    team = Team(name=body.name, invite_code=invite_code, owner_id=current_user.id)
    db.add(team)
    db.flush()
    current_user.team_id = team.id
    db.commit()
    db.refresh(team)
    member_count = db.query(User).filter(User.team_id == team.id).count()
    result = TeamOut.model_validate(team)
    result.member_count = member_count
    return result


@router.post("/teams/join", summary="초대코드로 팀 합류")
def join_team(body: TeamJoin, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not INVITE_CODE_RE.match(body.invite_code):
        raise HTTPException(400, {"code": "VALIDATION_ERROR", "message": "초대코드 형식이 올바르지 않습니다 (예: ABCD-1234)"})
    if current_user.team_id:
        raise HTTPException(409, {"code": "ALREADY_IN_TEAM", "message": "이미 다른 팀에 소속되어 있습니다"})
    team = db.query(Team).filter(Team.invite_code == body.invite_code).first()
    if not team:
        raise HTTPException(404, {"code": "NOT_FOUND", "message": "해당 초대코드를 찾을 수 없습니다"})
    current_user.team_id = team.id
    db.commit()
    db.refresh(team)
    member_count = db.query(User).filter(User.team_id == team.id).count()
    return {"team": {"id": team.id, "name": team.name, "member_count": member_count}, "redirect": f"/teams/{team.id}"}


@router.get("/teams/{team_id}", response_model=TeamOut, summary="팀 정보 조회")
def get_team(team_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.team_id != team_id:
        raise HTTPException(403, {"code": "FORBIDDEN", "message": "이 팀의 멤버가 아닙니다"})
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(404, {"code": "NOT_FOUND", "message": "해당 항목을 찾을 수 없습니다"})
    member_count = db.query(User).filter(User.team_id == team_id).count()
    result = TeamOut.model_validate(team)
    result.member_count = member_count
    return result


@router.get("/teams/{team_id}/members", response_model=List[MemberOut], summary="팀 멤버 목록")
def get_members(team_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.team_id != team_id:
        raise HTTPException(403, {"code": "FORBIDDEN", "message": "권한이 없습니다"})
    team = db.get(Team, team_id)
    members = db.query(User).filter(User.team_id == team_id).all()
    return [
        MemberOut(
            id=m.id,
            email=m.email,
            is_owner=(team.owner_id == m.id),
            joined_at=m.created_at,
        )
        for m in members
    ]


@router.delete("/teams/{team_id}/leave", summary="팀 나가기")
def leave_team(team_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.team_id != team_id:
        raise HTTPException(403, {"code": "FORBIDDEN", "message": "이 팀의 멤버가 아닙니다"})
    current_user.team_id = None
    db.commit()
    return {}
