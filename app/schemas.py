from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models import TaskStatus, DebtStatus


# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Message Schemas
class MessageCreate(BaseModel):
    receiver_id: int
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    ai_analysis: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# AI Analysis Schema
class AIAnalysis(BaseModel):
    type: str  # "task", "expense", "normal"
    item: Optional[str] = None
    amount: Optional[float] = None
    confidence: float = Field(..., ge=0.0, le=1.0)


# Task Schemas
class TaskCreate(BaseModel):
    assigned_to: int
    item_name: str
    related_message_id: Optional[int] = None


class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    completed_at: Optional[datetime] = None


class TaskResponse(BaseModel):
    id: int
    created_by: int
    assigned_to: int
    item_name: str
    status: TaskStatus
    related_message_id: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Expense Schemas
class ExpenseCreate(BaseModel):
    task_id: int
    paid_by: int
    amount: float = Field(..., gt=0)


class ExpenseResponse(BaseModel):
    id: int
    task_id: int
    paid_by: int
    amount: float
    created_at: datetime
    
    class Config:
        from_attributes = True


# Debt Schemas
class DebtCreate(BaseModel):
    debtor_id: int
    creditor_id: int
    amount: float


class DebtResponse(BaseModel):
    id: int
    debtor_id: int
    creditor_id: int
    amount: float
    status: DebtStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class DebtBalance(BaseModel):
    user_id: int
    username: str
    total_owed: float  # Total they owe to others
    total_to_collect: float  # Total others owe to them
    net_balance: float  # Positive if they should receive, negative if they owe


class SettleDebtRequest(BaseModel):
    creditor_id: int
    amount: float = Field(..., gt=0)

