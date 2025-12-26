from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Message
from app.websocket.manager import manager
from app.ai.analyzer import MessageAnalyzer
from app.auth.jwt import verify_token
import json


async def handle_websocket_connection(websocket: WebSocket, token: str, db: Session):
    """
    Handle WebSocket connection and messages
    
    Args:
        websocket: WebSocket connection
        token: JWT authentication token
        db: Database session
    """
    # Verify token and get user
    token_data = verify_token(token)
    if not token_data or not token_data.username:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if not user:
        await websocket.close(code=1008, reason="User not found")
        return
    
    # Connect user
    await manager.connect(websocket, user.id)
    
    # Send welcome message
    await manager.send_personal_message({
        "type": "system",
        "message": "Connected successfully",
        "user_id": user.id,
        "username": user.username
    }, user.id)
    
    try:
        while True:
            # Receive message from WebSocket
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process the message
            await process_message(message_data, user, db)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id)
    except Exception as e:
        print(f"WebSocket error for user {user.id}: {e}")
        manager.disconnect(websocket, user.id)


async def process_message(message_data: dict, sender: User, db: Session):
    """
    Process a received message
    
    Args:
        message_data: Message data from client
        sender: Sender user object
        db: Database session
    """
    try:
        # Extract message details
        receiver_id = message_data.get("receiver_id")
        content = message_data.get("content")
        
        if not receiver_id or not content:
            await manager.send_personal_message({
                "type": "error",
                "message": "Invalid message format"
            }, sender.id)
            return
        
        # Get receiver
        receiver = db.query(User).filter(User.id == receiver_id).first()
        if not receiver:
            await manager.send_personal_message({
                "type": "error",
                "message": "Receiver not found"
            }, sender.id)
            return
        
        # Save message to database
        new_message = Message(
            sender_id=sender.id,
            receiver_id=receiver.id,
            content=content
        )
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        
        # Analyze message with AI and process
        print(f"[DEBUG] Analyzing message: {content}")
        analyzer = MessageAnalyzer(db)
        analysis_result = analyzer.analyze_and_process(new_message, sender, receiver)
        print(f"[DEBUG] Analysis result: {analysis_result['analysis']}")
        
        # Send message to both sender and receiver
        chat_message = {
            "type": "message",
            "id": new_message.id,
            "sender_id": sender.id,
            "sender_username": sender.username,
            "receiver_id": receiver.id,
            "receiver_username": receiver.username,
            "content": content,
            "created_at": new_message.created_at.isoformat(),
            "ai_analysis": analysis_result["analysis"]
        }
        
        await manager.send_personal_message(chat_message, sender.id)
        if sender.id != receiver.id:
            await manager.send_personal_message(chat_message, receiver.id)
        
        # Send task notification if a task was created
        if analysis_result["analysis"]["type"] == "task" and analysis_result["task"]:
            task_notification = {
                "type": "notification",
                "message": f"New task created: {analysis_result['task'].item_name}",
                "task_id": analysis_result["task"].id if analysis_result["task"] else None
            }
            await manager.send_personal_message(task_notification, sender.id)
            if sender.id != receiver.id:
                await manager.send_personal_message(task_notification, receiver.id)
        
        elif analysis_result["analysis"]["type"] == "expense" and analysis_result["debt"]:
            debt = analysis_result["debt"]
            expense = analysis_result["expense"]
            
            # Notify debtor
            await manager.send_personal_message({
                "type": "notification",
                "message": f"New debt: {debt.amount} TL to {sender.username}",
                "debt_id": debt.id,
                "amount": debt.amount
            }, debt.debtor_id)
            
            # Notify creditor
            await manager.send_personal_message({
                "type": "notification",
                "message": f"New credit: {debt.amount} TL from {receiver.username}",
                "debt_id": debt.id,
                "amount": debt.amount
            }, debt.creditor_id)
    
    except Exception as e:
        print(f"Error processing message: {e}")
        await manager.send_personal_message({
            "type": "error",
            "message": f"Error processing message: {str(e)}"
        }, sender.id)
