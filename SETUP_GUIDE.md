# Edu Sense AI - Setup Guide

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd edu_sense
```

### 2. Setup Environment Variables
```bash
# Copy template file
cp .env.example .env

# Edit .env dan isi dengan kredensial Anda
# - SECRET_KEY: Generate dengan python -c "import secrets; print(secrets.token_urlsafe(32))"
# - DATABASE_URL: URL koneksi ke PostgreSQL Supabase Anda
```

### 3. Install Dependencies
```bash
# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 4. Run Application
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Aplikasi akan berjalan di: http://localhost:8000

## 📋 Environment Variables

Buat file `.env` berdasarkan `.env.example` dan isi dengan nilai berikut:

| Variable | Description | Example |
|----------|-------------|---------|
| SECRET_KEY | JWT secret key untuk autentikasi | `your_secret_key_32_chars` |
| DATABASE_URL | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host:5432/db` |
| APP_NAME | Nama aplikasi | `EduSense AI` |
| ENVIRONMENT | Environment mode | `production` / `development` |
| LOG_LEVEL | Level logging | `INFO` / `DEBUG` |

## 🗄️ Database Setup

### Supabase PostgreSQL
1. Buat akun di [Supabase](https://supabase.com)
2. Buat project baru
3. Copy connection string dari Settings → Database
4. Update `DATABASE_URL` di file `.env`

### Struktur Database
Database akan otomatis dibuat saat pertama kali menjalankan aplikasi.

## 📦 Dependencies

Lihat [requirements.txt](requirements.txt) untuk daftar lengkap dependencies.

Main packages:
- **FastAPI**: Web framework
- **InsightFace**: Face recognition engine
- **SQLAlchemy**: Database ORM
- **OpenCV**: Computer vision
- **NumPy & Pandas**: Data processing

## 🔒 Security

- ⚠️ **JANGAN** commit file `.env` ke repository
- ⚠️ **JANGAN** share SECRET_KEY atau database credentials
- ✅ Gunakan `.env.example` sebagai template
- ✅ Generate SECRET_KEY yang kuat untuk production

## 📚 Documentation

Setelah aplikasi berjalan, akses dokumentasi API di:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## ⚙️ Configuration

### JWT Token
- Token expire time: 60 menit (default)
- Algorithm: HS256
- Edit di `auth_utils.py` jika perlu customize

### Database Pool
- Pool size: 5 connections
- Max overflow: 10 connections
- Pool timeout: 30 seconds
- Edit di `database.py` jika perlu customize

## 🐛 Troubleshooting

### Database Connection Error
```
Pastikan:
1. DATABASE_URL format benar
2. Supabase project aktif
3. Network tidak diblok firewall
4. Credentials (username/password) benar
```

### Face Recognition Not Working
```
Pastikan:
1. InsightFace model terdownload
2. OpenCV terinstall dengan benar
3. Folder temp_videos/ ada dan writable
```

## 📞 Support

Untuk pertanyaan atau masalah, silakan buat issue di GitHub repository.

## 📄 License

Copyright © 2025 EduSense Engineering Team. All Rights Reserved.
