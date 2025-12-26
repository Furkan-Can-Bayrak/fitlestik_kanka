# 🚀 Hızlı Başlangıç Kılavuzu

Bu projeyi çalıştırmak için adım adım takip edin.

## ✅ Ön Gereksinimler

1. **Python 3.8+** kurulu olmalı
2. **PostgreSQL 12+** kurulu ve çalışıyor olmalı
3. **Google Gemini API Key** (Ücretsiz: https://makersuite.google.com/app/apikey)

## 📝 Kurulum Adımları

### Adım 1: PostgreSQL Veritabanı Oluştur

PostgreSQL'e bağlan ve şu komutları çalıştır:

```sql
CREATE DATABASE borc_db;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE borc_db TO postgres;
```

Veya farklı kullanıcı adı/şifre kullanıyorsan, `.env` dosyasında düzelteceksin.

### Adım 2: Google Gemini API Key Al

1. https://makersuite.google.com/app/apikey adresine git
2. "Create API Key" butonuna tıkla
3. API anahtarını kopyala

### Adım 3: .env Dosyası Oluştur

Proje dizininde `.env` dosyası oluştur ve şunu yaz:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/borc_db
SECRET_KEY=super-gizli-anahtar-buraya-yaz-123456789
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GOOGLE_API_KEY=BURAYA-GEMINI-API-KEY-YAPISTIR
```

**ÖNEMLİ:** `GOOGLE_API_KEY` kısmına kendi API anahtarını yapıştır!

### Adım 4: Kurulumu Çalıştır (Windows)

```bash
setup.bat
```

veya Manuel:

```bash
# Virtual environment aktif et
venv\Scripts\activate

# Bağımlılıkları yükle (zaten yüklü ama güncel değilse)
pip install -r requirements.txt

# Veritabanı migration
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Adım 5: Uygulamayı Başlat

```bash
run.bat
```

veya

```bash
python main.py
```

Uygulama `http://localhost:8000` adresinde çalışacak!

## 🎮 İlk Kullanım

### 1. Kullanıcılar Otomatik Oluşturuldu! ✨

Uygulama başlatıldığında **Can** ve **Yusuf** kullanıcıları otomatik oluşturuldu!

**Giriş Bilgileri:**
- **Can:** username=`can`, password=`123456`
- **Yusuf:** username=`yusuf`, password=`123456`

Manuel kullanıcı oluşturmak isterseniz http://localhost:8000/docs adresine gidip **POST /api/auth/register** endpoint'ini kullanabilirsiniz.

### 2. Test Client'ı Aç

`test_client.html` dosyasını tarayıcıda aç.

- İki farklı tarayıcı/sekme aç
- Birinde "can", diğerinde "yusuf" ile giriş yap
- Mesajlaşmaya başla!

### 3. Test Mesajları

**Görev oluşturmak için:**
```
Yusuf: "Marketten mop alınacak"
```
→ AI otomatik görev oluşturur

**Harcama eklemek için:**
```
Yusuf: "Mop aldım 300tl"
```
→ AI harcamayı kaydeder, görevi tamamlar, borçları hesaplar

## 🐛 Sorun Giderme

### PostgreSQL bağlanamıyor

- PostgreSQL servisinin çalıştığından emin ol
- `.env` dosyasındaki veritabanı URL'ini kontrol et
- Port numarası doğru mu? (varsayılan: 5432)

### Gemini API hatası

- API anahtarının doğru olduğundan emin ol
- İnternet bağlantını kontrol et
- API quota'nı kontrol et (günlük limit)

### Migration hatası

```bash
# Eski migration'ları sil
rd /s alembic\versions

# Yeniden oluştur
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Port zaten kullanımda

Port 8000 meşgulse, main.py'de portu değiştir:

```python
uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
```

## 📱 Kullanım İpuçları

1. **Test için kısa mesajlar kullan:** "mop alınacak", "süt aldım 50tl"
2. **TL/lira ifadelerini kullan:** AI Türk Lirası tanımlarını anlıyor
3. **Bakiyeyi kontrol et:** Test client'ta sol tarafta bakiye görünür
4. **API'yi keşfet:** http://localhost:8000/docs adresinde tüm endpoint'leri test edebilirsin

## 🎯 Sonraki Adımlar

- ✅ Farklı görevler dene
- ✅ Borç kapatma özelliğini test et (/api/debts/settle)
- ✅ Mesaj geçmişini görüntüle (/api/messages/)
- ✅ Kendi senaryolarını oluştur!

---

**Yardıma mı ihtiyacın var?** README.md dosyasına bak veya issue aç!

