"""
Database seed script - Create default users for testing
Run: python seed_db.py
"""
from app.database import SessionLocal
from app.models import User
from app.auth.password import get_password_hash


def seed_database():
    """Create default users (Can and Yusuf) if they don't exist"""
    db = SessionLocal()
    
    users_to_create = [
        {
            "username": "can",
            "email": "can@example.com",
            "password": "123456"
        },
        {
            "username": "yusuf",
            "email": "yusuf@example.com",
            "password": "123456"
        }
    ]
    
    print("🌱 Veritabanı seed başlatılıyor...\n")
    
    created_count = 0
    
    try:
        for user_data in users_to_create:
            existing = db.query(User).filter(User.username == user_data["username"]).first()
            
            if not existing:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=get_password_hash(user_data["password"])
                )
                db.add(user)
                print(f"✅ {user_data['username']} kullanıcısı oluşturuldu")
                created_count += 1
            else:
                print(f"⏭️  {user_data['username']} zaten mevcut")
        
        db.commit()
        
        print("\n" + "="*50)
        if created_count > 0:
            print("✨ Seed başarıyla tamamlandı!")
        else:
            print("✨ Tüm kullanıcılar zaten mevcut!")
        
        print("\n📱 Test için giriş bilgileri:")
        print("   • Can:   username='can',   password='123456'")
        print("   • Yusuf: username='yusuf', password='123456'")
        print("\n🎮 test_client.html dosyasını açarak başlayabilirsiniz!")
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

