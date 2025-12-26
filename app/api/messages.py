from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import User, Message
from app.schemas import MessageResponse
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/messages", tags=["Messages"])


@router.get("/", response_model=List[MessageResponse])
async def get_messages(
    other_user_id: Optional[int] = Query(None, description="Filter messages with specific user"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get message history"""
    query = db.query(Message)
    
    if other_user_id:
        # Get messages between current user and specific user
        query = query.filter(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == other_user_id)) |
            ((Message.sender_id == other_user_id) & (Message.receiver_id == current_user.id))
        )
    else:
        # Get all messages for current user
        query = query.filter(
            (Message.sender_id == current_user.id) | (Message.receiver_id == current_user.id)
        )
    
    messages = query.order_by(Message.created_at.desc()).offset(offset).limit(limit).all()
    return messages


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific message"""
    message = db.query(Message).filter(Message.id == message_id).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check if current user is involved in this message
    if message.sender_id != current_user.id and message.receiver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this message"
        )
    
    return message

