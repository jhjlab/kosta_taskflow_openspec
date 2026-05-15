from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..dependencies import get_db, get_current_user
from ..models import User, Team, Task, TaskStatus
from ..schemas import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskOut

router = APIRouter()


def _get_member_task(task_id: int, db: Session, current_user: User) -> Task:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(404, {"code": "NOT_FOUND", "message": "해당 항목을 찾을 수 없습니다"})
    if current_user.team_id != task.team_id:
        raise HTTPException(403, {"code": "FORBIDDEN", "message": "권한이 없습니다"})
    return task


@router.get("/teams/{team_id}/tasks", response_model=List[TaskOut], summary="태스크 목록 조회")
def list_tasks(
    team_id: int,
    filter: Optional[str] = Query(None, description="all | me | unassigned"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.team_id != team_id:
        raise HTTPException(403, {"code": "FORBIDDEN", "message": "권한이 없습니다"})
    q = db.query(Task).filter(Task.team_id == team_id)
    if filter == "me":
        q = q.filter(Task.assignee_id == current_user.id)
    elif filter == "unassigned":
        q = q.filter(Task.assignee_id.is_(None))
    return q.order_by(Task.created_at.desc()).all()


@router.post("/teams/{team_id}/tasks", response_model=TaskOut, status_code=201, summary="태스크 생성")
def create_task(
    team_id: int,
    body: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.team_id != team_id:
        raise HTTPException(403, {"code": "FORBIDDEN", "message": "권한이 없습니다"})
    task = Task(
        team_id=team_id,
        title=body.title,
        assignee_id=body.assignee_id,
        creator_id=current_user.id,
        status=TaskStatus.TODO,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/tasks/{task_id}", response_model=TaskOut, summary="태스크 단일 조회")
def get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _get_member_task(task_id, db, current_user)


@router.put("/tasks/{task_id}", response_model=TaskOut, summary="태스크 제목/담당자 수정")
def update_task(
    task_id: int,
    body: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = _get_member_task(task_id, db, current_user)
    if body.title is not None:
        task.title = body.title
    if "assignee_id" in body.model_fields_set:
        task.assignee_id = body.assignee_id
    db.commit()
    db.refresh(task)
    return task


@router.patch("/tasks/{task_id}/status", response_model=TaskOut, summary="태스크 상태 변경")
def update_task_status(
    task_id: int,
    body: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = _get_member_task(task_id, db, current_user)
    task.status = body.status
    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=204, summary="태스크 삭제")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = _get_member_task(task_id, db, current_user)
    team = db.get(Team, task.team_id)
    is_owner = team and team.owner_id == current_user.id
    is_creator = task.creator_id == current_user.id
    if not is_owner and not is_creator:
        raise HTTPException(403, {"code": "FORBIDDEN", "message": "권한이 없습니다"})
    db.delete(task)
    db.commit()
