from fastapi import FastAPI, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.config import settings
from app.database import Base, engine, get_db, SessionLocal
from app.api import auth, users, messages, tasks, debts
from app.websocket.handlers import handle_websocket_connection
from app.models import User
from app.auth.password import get_password_hash

# Create database tables
Base.metadata.create_all(bind=engine)


def create_default_users():
    """Create default users (Can and Yusuf) on startup if they don't exist"""
    db = SessionLocal()
    try:
        can = db.query(User).filter(User.username == "can").first()
        yusuf = db.query(User).filter(User.username == "yusuf").first()
        
        users_created = []
        
        if not can:
            can = User(
                username="can",
                email="can@example.com",
                hashed_password=get_password_hash("123456")
            )
            db.add(can)
            users_created.append("Can")
        
        if not yusuf:
            yusuf = User(
                username="yusuf",
                email="yusuf@example.com",
                hashed_password=get_password_hash("123456")
            )
            db.add(yusuf)
            users_created.append("Yusuf")
        
        if users_created:
            db.commit()
            print(f"\n✅ Otomatik kullanıcılar oluşturuldu: {', '.join(users_created)}")
            print("📱 Giriş bilgileri: username='can/yusuf', password='123456'\n")
    
    except Exception as e:
        print(f"⚠️  Kullanıcı oluşturma hatası: {e}")
        db.rollback()
    finally:
        db.close()


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered messaging and debt tracking system",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    create_default_users()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(messages.router)
app.include_router(tasks.router)
app.include_router(debts.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Destekli Borç Takip API'ye Hoş Geldiniz!",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "websocket": "/ws/{token}"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.APP_VERSION}


@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time messaging"""
    await handle_websocket_connection(websocket, token, db)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
