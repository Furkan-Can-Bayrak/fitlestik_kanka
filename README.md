# 🤖 AI Destekli Borç Takip Sistemi

FastAPI, WebSocket, PostgreSQL ve Google Gemini AI ile geliştirilmiş akıllı mesajlaşma ve borç takip uygulaması.

## 🌟 Özellikler

- **AI Destekli Mesaj Analizi**: Her mesaj Google Gemini AI tarafından analiz edilir
- **Otomatik Görev Yönetimi**: "Mop alınacak" gibi mesajlar otomatik olarak görev oluşturur
- **Akıllı Borç Hesaplama**: "Mop aldım 300tl" mesajı otomatik olarak borcu hesaplar ve görevleri tamamlar
- **Gerçek Zamanlı Mesajlaşma**: WebSocket ile anlık iletişim
- **JWT Authentication**: Güvenli kullanıcı yönetimi
- **RESTful API**: Tüm işlemler için API endpoints

## 📋 Gereksinimler

- Python 3.8+
- PostgreSQL 12+
- Google Gemini API Key

## 🚀 Kurulum

### 1. Depoyu Klonlayın veya İndirin

```bash
cd borc
```

### 2. Virtual Environment Oluşturun ve Aktifleştirin

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 4. PostgreSQL Veritabanı Oluşturun

```sql
CREATE DATABASE borc_db;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE borc_db TO postgres;
```

### 5. Ortam Değişkenlerini Ayarlayın

`.env` dosyası oluşturun:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/borc_db
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GOOGLE_API_KEY=your-gemini-api-key-here
```

**Google Gemini API Key almak için:**
1. [Google AI Studio](https://makersuite.google.com/app/apikey)'ya gidin
2. "Create API Key" butonuna tıklayın
3. API anahtarınızı kopyalayın ve `.env` dosyasına ekleyin

### 6. Veritabanı Migration

```bash
# Migration oluştur
alembic revision --autogenerate -m "Initial migration"

# Migration'ı uygula
alembic upgrade head
```

### 7. Uygulamayı Başlatın

```bash
python main.py
```

veya

```bash
uvicorn main:app --reload
```

Uygulama `http://localhost:8000` adresinde çalışacaktır.

**🎉 Otomatik Kullanıcılar:** Uygulama başlatıldığında **Can** ve **Yusuf** kullanıcıları otomatik oluşturulur!
- Can: `username='can'`, `password='123456'`
- Yusuf: `username='yusuf'`, `password='123456'`

## 📚 API Dokümantasyonu

Uygulama çalıştırıldıktan sonra:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎮 Test Client Kullanımı

1. `test_client.html` dosyasını tarayıcıda açın
2. **Kullanıcılar otomatik oluşturulmuştur!** Direkt giriş yapabilirsiniz:
   - **Can:** `username='can'`, `password='123456'`
   - **Yusuf:** `username='yusuf'`, `password='123456'`
3. İki farklı tarayıcı/sekme açın ve her birinde farklı kullanıcı ile giriş yapın
4. Alıcı seçin ve mesajlaşmaya başlayın!

### Manuel Kullanıcı Oluşturma (Opsiyonel)

İsterseniz yeni kullanıcılar da oluşturabilirsiniz:

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ahmet",
    "email": "ahmet@example.com",
    "password": "123456"
  }'
```

## 💬 Örnek Kullanım Senaryosu

### Senaryo 1: Görev Oluşturma

**Yusuf mesaj yazar:** "Marketten mop alınacak"

**Sistem:**
- ✅ AI mesajı analiz eder
- ✅ Otomatik olarak "mop" için görev oluşturur
- ✅ Can'a görev bildirimi gönderir

### Senaryo 2: Harcama ve Borç Hesaplama

**Yusuf mesaj yazar:** "Mop aldım 300tl"

**Sistem:**
- ✅ AI mesajı analiz eder ve harcama olarak işaretler
- ✅ İlgili görevi "tamamlandı" olarak işaretler
- ✅ 300 TL'yi ikiye böler (150 TL her birine)
- ✅ Can'ın Yusuf'a 150 TL borcu olduğunu kaydeder
- ✅ Her iki kullanıcıya borç/alacak bilgisi gönderir

### Senaryo 3: Bakiye Sorgulama

```bash
curl -X GET "http://localhost:8000/api/debts/balance?other_user_id=2" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔌 API Endpoints

### Authentication

- `POST /api/auth/register` - Kullanıcı kaydı
- `POST /api/auth/login` - Giriş yap (JWT token al)
- `GET /api/auth/me` - Mevcut kullanıcı bilgisi

### Users

- `GET /api/users/` - Tüm kullanıcılar
- `GET /api/users/{user_id}` - Kullanıcı detayı

### Messages

- `GET /api/messages/` - Mesaj geçmişi
- `GET /api/messages/{message_id}` - Mesaj detayı

### Tasks

- `GET /api/tasks/` - Görevler (filtrelenebilir)
- `GET /api/tasks/{task_id}` - Görev detayı
- `PUT /api/tasks/{task_id}` - Görev güncelle
- `DELETE /api/tasks/{task_id}` - Görev sil

### Debts

- `GET /api/debts/balance` - Borç bakiyesi
- `GET /api/debts/history` - Borç geçmişi
- `POST /api/debts/settle` - Borç kapat

### WebSocket

- `WS /ws/{token}` - Gerçek zamanlı mesajlaşma

## 🧠 AI Analiz Türleri

Google Gemini AI mesajları 3 kategoriye ayırır:

1. **TASK**: Yapılacak iş/alınacak şey
   - Örnekler: "mop alınacak", "süt almalıyız", "market yapılacak"

2. **EXPENSE**: Yapılan harcama
   - Örnekler: "mop aldım 300tl", "süt aldım 50 lira", "marketiten 500 TL harcadım"

3. **NORMAL**: Normal konuşma
   - Örnekler: "Merhaba", "Nasılsın?", "Teşekkürler"

## 🏗️ Proje Yapısı

```
borc/
├── app/
│   ├── __init__.py
│   ├── config.py          # Ayarlar
│   ├── database.py        # Veritabanı bağlantısı
│   ├── models.py          # SQLAlchemy modelleri
│   ├── schemas.py         # Pydantic şemaları
│   ├── auth/              # Authentication modülü
│   │   ├── jwt.py
│   │   ├── password.py
│   │   └── dependencies.py
│   ├── api/               # REST API endpoints
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── messages.py
│   │   ├── tasks.py
│   │   └── debts.py
│   ├── websocket/         # WebSocket işlemleri
│   │   ├── manager.py
│   │   └── handlers.py
│   └── ai/                # AI analiz modülü
│       ├── gemini.py
│       └── analyzer.py
├── alembic/               # Database migrations
├── main.py                # Ana uygulama
├── test_client.html       # Test client
├── requirements.txt
├── .env
└── README.md
```

## 🔒 Güvenlik Notları

- ⚠️ Production'da `SECRET_KEY`'i mutlaka değiştirin
- ⚠️ CORS ayarlarını production için düzenleyin
- ⚠️ `.env` dosyasını asla git'e eklemeyin
- ⚠️ PostgreSQL şifrelerini güçlü tutun
- ⚠️ HTTPS kullanın (production)

## 📊 Veritabanı Şeması

```
users
├── id (PK)
├── username (UNIQUE)
├── email (UNIQUE)
├── hashed_password
└── created_at

messages
├── id (PK)
├── sender_id (FK -> users)
├── receiver_id (FK -> users)
├── content
├── ai_analysis (JSON)
└── created_at

tasks
├── id (PK)
├── created_by (FK -> users)
├── assigned_to (FK -> users)
├── item_name
├── status (pending/in_progress/completed/cancelled)
├── related_message_id (FK -> messages)
├── created_at
└── completed_at

expenses
├── id (PK)
├── task_id (FK -> tasks)
├── paid_by (FK -> users)
├── amount
└── created_at

debts
├── id (PK)
├── debtor_id (FK -> users)
├── creditor_id (FK -> users)
├── amount
├── status (active/settled)
└── created_at
```

## 🎯 Gelecek Geliştirmeler

- [ ] Grup mesajlaşması desteği
- [ ] Özel borç paylaşım oranları (50-50 yerine 60-40 gibi)
- [ ] Borç hatırlatma bildirimleri
- [ ] Mesaj geçmişi arama
- [ ] Dosya/fotoğraf paylaşımı
- [ ] Mobil uygulama
- [ ] Çoklu dil desteği

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 💡 Destek

Sorularınız için issue açabilir veya iletişime geçebilirsiniz.

---

⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın!
