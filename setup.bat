@echo off
echo ========================================
echo AI Destekli Borc Takip - Kurulum
echo ========================================
echo.

echo [1/5] Virtual environment aktif ediliyor...
call venv\Scripts\activate

echo.
echo [2/5] Bagimliliklari yukleniyor...
pip install -r requirements.txt

echo.
echo [3/5] .env dosyasi kontrol ediliyor...
if not exist .env (
    echo .env dosyasi bulunamadi. Lutfen .env dosyasi olusturun!
    echo Ornek:
    echo DATABASE_URL=postgresql://postgres:postgres@localhost:5432/borc_db
    echo SECRET_KEY=your-secret-key-here
    echo GOOGLE_API_KEY=your-gemini-api-key
    pause
    exit /b 1
)

echo.
echo [4/6] Veritabani migration...
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

echo.
echo [5/6] Varsayilan kullanicilar olusturuluyor...
python seed_db.py

echo.
echo [6/6] Kurulum tamamlandi!
echo.
echo Uygulamayi baslatmak icin: python main.py
echo Test client: test_client.html dosyasini tarayicida acin
echo API Docs: http://localhost:8000/docs
echo.
pause

