from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import User, Task, TaskStatus
from app.schemas import TaskResponse, TaskUpdate
from app.auth.dependencies import get_current_user
from datetime import datetime

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    status_filter: Optional[TaskStatus] = Query(None, description="Filter by status"),
    assigned_to: Optional[int] = Query(None, description="Filter by assignee"),
    created_by: Optional[int] = Query(None, description="Filter by creator"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get tasks (filtered)"""
    query = db.query(Task).filter(
        (Task.created_by == current_user.id) | (Task.assigned_to == current_user.id)
    )
    
    if status_filter:
        query = query.filter(Task.status == status_filter)
    
    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)
    
    if created_by:
        query = query.filter(Task.created_by == created_by)
    
    tasks = query.order_by(Task.created_at.desc()).all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if current user is involved in this task
    if task.created_by != current_user.id and task.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this task"
        )
    
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a task (manual update)"""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if current user is involved in this task
    if task.created_by != current_user.id and task.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )
    
    # Update fields
    if task_update.status is not None:
        task.status = task_update.status
        if task_update.status == TaskStatus.COMPLETED and not task.completed_at:
            task.completed_at = datetime.utcnow()
    
    if task_update.completed_at is not None:
        task.completed_at = task_update.completed_at
    
    db.commit()
    db.refresh(task)
    
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Only creator can delete
    if task.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )
    
    db.delete(task)
    db.commit()
    
    return None

