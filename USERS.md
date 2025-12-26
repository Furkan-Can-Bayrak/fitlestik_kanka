# 👥 Kullanıcı Yönetimi

## 🎯 Otomatik Kullanıcılar

Uygulama ilk başlatıldığında **otomatik olarak 2 test kullanıcısı oluşturulur:**

### Can
- **Username:** `can`
- **Email:** `can@example.com`
- **Password:** `123456`
- **ID:** 1

### Yusuf
- **Username:** `yusuf`
- **Email:** `yusuf@example.com`
- **Password:** `123456`
- **ID:** 2

## 🚀 Kullanım

### 1. Otomatik Oluşturma (Önerilen)

Uygulamayı başlattığınızda kullanıcılar otomatik oluşturulur:

```bash
python main.py
```

Console'da göreceksiniz:
```
✅ Otomatik kullanıcılar oluşturuldu: Can, Yusuf
📱 Giriş bilgileri: username='can/yusuf', password='123456'
```

### 2. Manuel Seed (İsteğe Bağlı)

Sadece kullanıcıları oluşturmak isterseniz:

```bash
python seed_db.py
```

Çıktı:
```
🌱 Veritabanı seed başlatılıyor...

✅ can kullanıcısı oluşturuldu
✅ yusuf kullanıcısı oluşturuldu

==================================================
✨ Seed başarıyla tamamlandı!

📱 Test için giriş bilgileri:
   • Can:   username='can',   password='123456'
   • Yusuf: username='yusuf', password='123456'

🎮 test_client.html dosyasını açarak başlayabilirsiniz!
==================================================
```

## 🔐 Güvenlik

### Şifre Hashing
- Şifreler **bcrypt** ile hashlenir
- Düz metin şifreler asla veritabanında saklanmaz
- Hash örneği: `$2b$12$KIXxH8rjd0qF3z...`

### JWT Authentication
- Login sonrası **JWT token** verilir
- Token geçerlilik süresi: **30 dakika**
- Her istekte token doğrulanır

## 📝 Yeni Kullanıcı Ekleme

### API ile (Swagger UI)

1. http://localhost:8000/docs adresine git
2. **POST /api/auth/register** endpoint'ini aç
3. Bilgileri gir:

```json
{
  "username": "ahmet",
  "email": "ahmet@example.com",
  "password": "123456"
}
```

### cURL ile

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "ahmet",
    "email": "ahmet@example.com",
    "password": "123456"
  }'
```

### Python ile (seed_db.py'ye ekle)

`seed_db.py` dosyasındaki `users_to_create` listesine ekle:

```python
{
    "username": "ahmet",
    "email": "ahmet@example.com",
    "password": "123456"
}
```

## 🎮 Test Senaryosu

### İki Tarayıcı/Sekme İle Test

**Sekme 1 (Can):**
1. `test_client.html` dosyasını aç
2. Username: `can`
3. Password: `123456`
4. "Giriş Yap" butonuna tıkla
5. Alıcı olarak "Yusuf" seç
6. Mesaj yaz: "Mop alınacak"

**Sekme 2 (Yusuf):**
1. `test_client.html` dosyasını aç
2. Username: `yusuf`
3. Password: `123456`
4. "Giriş Yap" butonuna tıkla
5. Can'ın mesajını gör
6. Cevap yaz: "Mop aldım 300tl"

**Sonuç:**
- ✅ Görev otomatik oluşturuldu
- ✅ Görev otomatik tamamlandı
- ✅ Borç hesaplandı (150-150 TL)
- ✅ Her iki kullanıcıya bildirim gitti

## 🗄️ Veritabanı Yapısı

```sql
-- Users tablosu
SELECT * FROM users;

┌────┬──────────┬──────────────────┬────────────────────────────────┬─────────────────────┐
│ id │ username │ email            │ hashed_password                │ created_at          │
├────┼──────────┼──────────────────┼────────────────────────────────┼─────────────────────┤
│ 1  │ can      │ can@example.com  │ $2b$12$KIXxH8rjd0qF3z...      │ 2024-12-26 20:30:00 │
│ 2  │ yusuf    │ yusuf@...        │ $2b$12$9fGtR2xM8kL7p...      │ 2024-12-26 20:30:00 │
└────┴──────────┴──────────────────┴────────────────────────────────┴─────────────────────┘
```

## ❓ Sık Sorulan Sorular

### Kullanıcılar zaten varsa ne olur?
Sistem kontrol eder ve sadece yoksa oluşturur. Console'da:
```
⏭️  can zaten mevcut
⏭️  yusuf zaten mevcut
```

### Şifreleri nasıl değiştirebilirim?
`seed_db.py` dosyasında `password` değerini değiştir ve tekrar çalıştır.

### Tüm kullanıcıları nasıl silerim?
```sql
-- PostgreSQL'de
TRUNCATE TABLE users CASCADE;
```

Sonra uygulamayı yeniden başlat, otomatik oluşturulacaklar.

### Farklı kullanıcı eklemek istiyorum?
`seed_db.py` dosyasındaki `users_to_create` listesine ekle:

```python
users_to_create = [
    {"username": "can", "email": "can@example.com", "password": "123456"},
    {"username": "yusuf", "email": "yusuf@example.com", "password": "123456"},
    {"username": "ahmet", "email": "ahmet@example.com", "password": "123456"},  # Yeni!
]
```

## 🎯 Production Notları

**⚠️ UYARI:** Bu otomatik kullanıcı oluşturma sistemi **sadece development/test** için tasarlanmıştır!

**Production'da yapılması gerekenler:**
1. `main.py`'deki `create_default_users()` fonksiyonunu kaldır veya devre dışı bırak
2. Güçlü şifreler kullan
3. Email doğrulama ekle
4. Rate limiting ekle
5. CAPTCHA ekle (bot koruması)

## 📚 İlgili Dosyalar

- `seed_db.py` - Kullanıcı oluşturma scripti
- `main.py` - Otomatik kullanıcı oluşturma (startup event)
- `app/api/auth.py` - Register/Login endpoint'leri
- `app/models.py` - User model tanımı
- `app/auth/password.py` - Şifre hashing
- `app/auth/jwt.py` - JWT token yönetimi

---

**🎉 Hemen test etmeye başlayabilirsiniz!**

```bash
python main.py
# Sonra test_client.html dosyasını aç!
```

