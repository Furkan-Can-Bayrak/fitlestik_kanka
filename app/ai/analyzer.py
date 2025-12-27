from sqlalchemy.orm import Session
from app.ai.gemini import GeminiClient
from app.models import Message, Task, Expense, Debt, User, TaskStatus, DebtStatus
from datetime import datetime
from typing import Dict, Any, Optional


class MessageAnalyzer:
    """Handles message analysis and automatic task/expense creation"""
    
    def __init__(self, db: Session):
        self.db = db
        self.gemini = GeminiClient()
    
    def analyze_and_process(
        self, 
        message: Message, 
        sender: User, 
        receiver: User
    ) -> Dict[str, Any]:
        """
        Analyze a message and create tasks/expenses/payments if needed
        
        Returns:
            dict: Processing result with created tasks, expenses, debts, and payments
        """
        print(f"[AI ANALYZER] Starting analysis for: '{message.content}'")
        
        # Analyze message with Gemini
        analysis = self.gemini.analyze_message(
            message.content,
            sender.username,
            receiver.username
        )
        print(f"[AI ANALYZER] Gemini returned: {analysis}")
        
        # Store analysis result
        message.ai_analysis = analysis
        self.db.commit()
        
        result = {
            "analysis": analysis,
            "task": None,
            "expense": None,
            "debt": None,
            "payment": None
        }
        
        # Process based on analysis type
        if analysis["type"] == "task" and analysis["item"]:
            result["task"] = self._create_task(message, sender, receiver, analysis["item"])
        
        elif analysis["type"] == "expense" and analysis["item"] and analysis["amount"]:
            result.update(
                self._process_expense(
                    message, 
                    sender, 
                    receiver, 
                    analysis["item"], 
                    analysis["amount"]
                )
            )
        
        elif analysis["type"] == "payment":
            result["payment"] = self._process_payment(
                message, 
                sender, 
                receiver, 
                analysis.get("amount")
            )
        
        return result
    
    def _create_task(
        self, 
        message: Message, 
        creator: User, 
        assignee: User, 
        item_name: str
    ) -> Task:
        """Create a new task"""
        task = Task(
            created_by=creator.id,
            assigned_to=assignee.id,
            item_name=item_name,
            status=TaskStatus.PENDING,
            related_message_id=message.id
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def _process_expense(
        self, 
        message: Message, 
        payer: User, 
        other_user: User, 
        item_name: str, 
        amount: float
    ) -> Dict[str, Any]:
        """
        Process an expense: complete task, create expense, calculate debt
        
        Returns:
            dict: Created expense, task, and debt information
        """
        result = {
            "task": None,
            "expense": None,
            "debt": None
        }
        
        # Find related pending task for this item
        task = self.db.query(Task).filter(
            Task.item_name.ilike(f"%{item_name}%"),
            Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
            ((Task.created_by == payer.id) | (Task.assigned_to == payer.id))
        ).first()
        
        # If no exact match, create a new task
        if not task:
            task = Task(
                created_by=payer.id,
                assigned_to=other_user.id,
                item_name=item_name,
                status=TaskStatus.COMPLETED,
                related_message_id=message.id,
                completed_at=datetime.utcnow()
            )
            self.db.add(task)
            self.db.flush()
        else:
            # Complete the existing task
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
        
        result["task"] = task
        
        # Create expense
        expense = Expense(
            task_id=task.id,
            paid_by=payer.id,
            amount=amount
        )
        self.db.add(expense)
        self.db.flush()
        result["expense"] = expense
        
        # Calculate and create debt
        # Split the expense equally between two users
        split_amount = amount / 2
        
        # The other user owes the payer their share
        debt = Debt(
            debtor_id=other_user.id,
            creditor_id=payer.id,
            amount=split_amount,
            status=DebtStatus.ACTIVE
        )
        self.db.add(debt)
        
        self.db.commit()
        self.db.refresh(expense)
        self.db.refresh(debt)
        
        result["debt"] = debt
        
        return result
    
    def _process_payment(
        self, 
        message: Message, 
        payer: User,
        receiver: User,
        amount: Optional[float]
    ) -> Dict[str, Any]:
        """
        Process a debt payment
        
        Args:
            message: Original message
            payer: User who is paying the debt
            receiver: User receiving the payment
            amount: Payment amount (None means pay all debts)
        
        Returns:
            dict: Payment information
        """
        print(f"[PAYMENT] Processing payment from {payer.username} to {receiver.username}")
        
        # Find active debts where payer owes to receiver
        active_debts = self.db.query(Debt).filter(
            Debt.debtor_id == payer.id,
            Debt.creditor_id == receiver.id,
            Debt.status == DebtStatus.ACTIVE
        ).order_by(Debt.created_at).all()
        
        if not active_debts:
            print(f"[PAYMENT] No active debts found")
            return {
                "success": False,
                "message": "Aktif borç bulunamadı",
                "paid_amount": 0,
                "remaining_debts": []
            }
        
        total_debt = sum(debt.amount for debt in active_debts)
        print(f"[PAYMENT] Total debt: {total_debt} TL")
        
        # If amount not specified, pay all debts
        if amount is None:
            amount = total_debt
        
        # Payment cannot exceed total debt
        if amount > total_debt:
            amount = total_debt
        
        remaining_amount = amount
        settled_debts = []
        partially_paid_debt = None
        
        # Pay debts starting from oldest
        for debt in active_debts:
            if remaining_amount <= 0:
                break
            
            if remaining_amount >= debt.amount:
                # Fully settle this debt
                debt.status = DebtStatus.SETTLED
                debt.settled_at = datetime.utcnow()
                remaining_amount -= debt.amount
                settled_debts.append(debt)
                print(f"[PAYMENT] Debt {debt.id} fully settled: {debt.amount} TL")
            else:
                # Partially pay this debt
                debt.amount -= remaining_amount
                partially_paid_debt = {
                    "debt_id": debt.id,
                    "paid": remaining_amount,
                    "remaining": debt.amount
                }
                remaining_amount = 0
                print(f"[PAYMENT] Debt {debt.id} partially paid: {partially_paid_debt['paid']} TL, remaining: {partially_paid_debt['remaining']} TL")
        
        self.db.commit()
        
        # Calculate remaining total debt
        remaining_total = sum(
            debt.amount for debt in self.db.query(Debt).filter(
                Debt.debtor_id == payer.id,
                Debt.creditor_id == receiver.id,
                Debt.status == DebtStatus.ACTIVE
            ).all()
        )
        
        result = {
            "success": True,
            "paid_amount": amount,
            "settled_count": len(settled_debts),
            "partially_paid": partially_paid_debt,
            "remaining_total_debt": remaining_total,
            "message": f"{amount} TL ödeme yapıldı"
        }
        
        print(f"[PAYMENT] Payment processed: {result}")
        return result
    
    @staticmethod
    def calculate_net_balance(db: Session, user1_id: int, user2_id: int) -> Dict[str, float]:
        """
        Calculate net balance between two users
        
        Returns:
            dict: Net balance information
        """
        # User1 owes to User2
        user1_owes = db.query(Debt).filter(
            Debt.debtor_id == user1_id,
            Debt.creditor_id == user2_id,
            Debt.status == DebtStatus.ACTIVE
        ).all()
        
        # User2 owes to User1
        user2_owes = db.query(Debt).filter(
            Debt.debtor_id == user2_id,
            Debt.creditor_id == user1_id,
            Debt.status == DebtStatus.ACTIVE
        ).all()
        
        user1_total_owed = sum(debt.amount for debt in user1_owes)
        user2_total_owed = sum(debt.amount for debt in user2_owes)
        
        # Net balance (positive = user1 should receive, negative = user1 should pay)
        net_balance = user2_total_owed - user1_total_owed
        
        return {
            "user1_owes": user1_total_owed,
            "user2_owes": user2_total_owed,
            "net_balance": net_balance
        }
