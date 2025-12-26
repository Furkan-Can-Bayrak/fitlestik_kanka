from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from app.database import get_db
from app.models import User, Debt, DebtStatus
from app.schemas import DebtResponse, DebtBalance, SettleDebtRequest
from app.auth.dependencies import get_current_user
from app.ai.analyzer import MessageAnalyzer

router = APIRouter(prefix="/api/debts", tags=["Debts"])


@router.get("/balance", response_model=DebtBalance)
async def get_balance(
    other_user_id: Optional[int] = Query(None, description="Calculate balance with specific user"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get debt balance for current user"""
    if other_user_id:
        # Balance with specific user
        balance_data = MessageAnalyzer.calculate_net_balance(db, current_user.id, other_user_id)
        other_user = db.query(User).filter(User.id == other_user_id).first()
        
        if not other_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return DebtBalance(
            user_id=current_user.id,
            username=current_user.username,
            total_owed=balance_data["user1_owes"],
            total_to_collect=balance_data["user2_owes"],
            net_balance=balance_data["net_balance"]
        )
    else:
        # Total balance with all users
        debts_owed = db.query(Debt).filter(
            Debt.debtor_id == current_user.id,
            Debt.status == DebtStatus.ACTIVE
        ).all()
        
        debts_to_collect = db.query(Debt).filter(
            Debt.creditor_id == current_user.id,
            Debt.status == DebtStatus.ACTIVE
        ).all()
        
        total_owed = sum(debt.amount for debt in debts_owed)
        total_to_collect = sum(debt.amount for debt in debts_to_collect)
        net_balance = total_to_collect - total_owed
        
        return DebtBalance(
            user_id=current_user.id,
            username=current_user.username,
            total_owed=total_owed,
            total_to_collect=total_to_collect,
            net_balance=net_balance
        )


@router.get("/history", response_model=List[DebtResponse])
async def get_debt_history(
    status_filter: Optional[DebtStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get debt history"""
    query = db.query(Debt).filter(
        or_(
            Debt.debtor_id == current_user.id,
            Debt.creditor_id == current_user.id
        )
    )
    
    if status_filter:
        query = query.filter(Debt.status == status_filter)
    
    debts = query.order_by(Debt.created_at.desc()).offset(offset).limit(limit).all()
    return debts


@router.post("/settle", response_model=dict)
async def settle_debt(
    settle_request: SettleDebtRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Settle debt manually (mark debts as settled)"""
    creditor_id = settle_request.creditor_id
    amount_to_settle = settle_request.amount
    
    # Get active debts where current user owes to creditor
    debts = db.query(Debt).filter(
        Debt.debtor_id == current_user.id,
        Debt.creditor_id == creditor_id,
        Debt.status == DebtStatus.ACTIVE
    ).order_by(Debt.created_at.asc()).all()
    
    if not debts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active debts found with this creditor"
        )
    
    total_debt = sum(debt.amount for debt in debts)
    
    if amount_to_settle > total_debt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Amount exceeds total debt ({total_debt} TL)"
        )
    
    # Settle debts
    remaining = amount_to_settle
    settled_debts = []
    
    for debt in debts:
        if remaining <= 0:
            break
        
        if debt.amount <= remaining:
            # Fully settle this debt
            debt.status = DebtStatus.SETTLED
            remaining -= debt.amount
            settled_debts.append(debt.id)
        else:
            # Partially settle (split the debt)
            # Create a new settled debt for the paid amount
            settled_debt = Debt(
                debtor_id=debt.debtor_id,
                creditor_id=debt.creditor_id,
                amount=remaining,
                status=DebtStatus.SETTLED,
                created_at=debt.created_at
            )
            db.add(settled_debt)
            
            # Update original debt amount
            debt.amount -= remaining
            settled_debts.append(settled_debt.id)
            remaining = 0
    
    db.commit()
    
    return {
        "message": "Debt settled successfully",
        "settled_amount": amount_to_settle,
        "settled_debt_ids": settled_debts,
        "remaining_debt": total_debt - amount_to_settle
    }

