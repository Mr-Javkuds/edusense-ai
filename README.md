# 🎓 Edu Sense - Smart Attendance System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.6.0-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15.x-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Sistem Absensi Cerdas Berbasis AI Face Recognition untuk Perguruan Tinggi**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📖 Overview

**Edu Sense** adalah sistem absensi modern yang memanfaatkan teknologi **AI Face Recognition** untuk mengotomasi proses pencatatan kehadiran mahasiswa. Sistem ini menganalisis video kuliah untuk mendeteksi dan mengenali wajah mahasiswa secara real-time, menghilangkan kebutuhan absensi manual dan mencegah kecurangan.

### 🎯 Problem Statement

- ❌ Absensi manual memakan waktu 5-10 menit per kelas
- ❌ Titip absen dan manipulasi data kehadiran
- ❌ Sulit melacak pola kehadiran mahasiswa
- ❌ Proses administrasi yang rumit dan berulang
- ❌ Tidak ada bukti visual kehadiran mahasiswa

### ✅ Solution

Edu Sense menggunakan **InsightFace** (state-of-the-art face recognition) untuk:
- ✅ Deteksi otomatis kehadiran dari video rekaman kuliah
- ✅ Verifikasi kehadiran dengan akurasi tinggi (>95%)
- ✅ Dashboard real-time untuk monitoring kehadiran
- ✅ Sistem pelaporan untuk sengketa kehadiran
- ✅ Analisis emosi dan engagement mahasiswa

---

## ✨ Features

### 👥 Multi-Role System

#### 🎓 Mahasiswa
- 📊 **Dashboard Personal** - Lihat jadwal dan status kehadiran
- 📅 **Jadwal Kuliah** - Daftar mata kuliah per minggu dengan class badge
- ✅ **History Kehadiran** - Riwayat lengkap dengan status (Hadir/Alpha)
- 🚨 **Lapor Kehadiran** - Sistem dispute untuk kehadiran yang salah
- 👤 **Profil** - Informasi akun dan class assignment

#### 👨‍🏫 Dosen
- 📹 **Upload Video** - Upload rekaman kuliah untuk diproses AI
- ⚡ **Real-time Processing** - Monitor status processing video
- 📊 **Dashboard Absensi** - Lihat kehadiran mahasiswa per sesi
- 📝 **Validasi Manual** - Koreksi hasil deteksi AI jika diperlukan
- 📈 **Laporan** - Export data kehadiran ke Excel

#### 🏫 Kaprodi (Admin)
- 👥 **Manajemen User** - CRUD mahasiswa, dosen, dan admin
- 🏛️ **Manajemen Kelas** - Buat dan kelola mata kuliah
- 👨‍🎓 **Student Class** - Kelola kelas mahasiswa (A11.4109, dll)
- 📚 **Enrollment** - Assign mahasiswa ke mata kuliah
- 🗓️ **Set Jadwal** - Atur jadwal kuliah dengan detail lengkap
- 📊 **Dashboard Analytics** - Overview seluruh sistem
- 🚀 **Bulk Face Registration** - Upload ZIP berisi 100+ foto mahasiswa sekaligus

### 🤖 AI-Powered Features

- **Face Detection** - Deteksi wajah dalam video dengan MTCNN
- **Face Recognition** - Identifikasi mahasiswa dengan InsightFace ArcFace
- **Bulk Face Processing** - Process ratusan foto mahasiswa dari ZIP file
- **Emotion Analysis** - Analisis emosi dominan (happy, sad, neutral, dll)
- **Attendance Tracking** - Hitung jumlah kemunculan per mahasiswa
- **Auto-Alpha System** - Otomatis tandai alpha jika tidak terdeteksi
- **Dispute Resolution** - Mahasiswa bisa melaporkan jika ada kesalahan
- **Smart Validation** - Validasi otomatis jumlah wajah (must be exactly 1)

### 🔐 Security & Authentication

- JWT Token-based authentication
- Role-based access control (RBAC)
- Password hashing dengan bcrypt
- Secure file upload validation
- Rate limiting untuk API endpoints

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** 0.6.0 - Modern Python web framework
- **SQLAlchemy** - ORM untuk database operations
- **asyncpg** - Async PostgreSQL driver
- **Pydantic** - Data validation
- **python-jose** - JWT token handling
- **passlib** - Password hashing

### AI/ML
- **InsightFace** - State-of-the-art face recognition
- **MTCNN** - Face detection
- **OpenCV** - Video processing
- **NumPy** - Numerical computing
- **pgvector** - Vector similarity search

### Database
- **PostgreSQL** 15.x - Primary database
- **Supabase** - Cloud PostgreSQL hosting
- **pgvector Extension** - Vector embeddings storage

### Frontend
- **Vanilla JavaScript** - No framework overhead
- **TailwindCSS** 3.x - Utility-first CSS
- **Axios** - HTTP client
- **SweetAlert2** - Beautiful alerts
- **Font Awesome** 6.4.0 - Icons

### DevOps
- **Docker** - Containerization
- **Uvicorn** - ASGI server
- **Hugging Face Spaces** - Deployment platform

---

## 🚀 Installation

### Prerequisites

- Python 3.10+
- PostgreSQL 15.x
- Cloudflare WARP (untuk koneksi ke Supabase jika ISP memblokir)
- Git

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/edu-sense.git
cd edu-sense
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Database

```bash
# Edit database.py dengan connection string Anda
DATABASE_URL = "postgresql+asyncpg://user:password@host:5432/database"
```

### 5. Run Migrations

```bash
cd helpers
python reset_and_seeder_db.py  # Create tables dan seed data
python optimize_database.py     # Buat indexes untuk performa
```

### 6. Create Admin User

```bash
python create_admin.py
# Username: admin
# Password: admin123
```

### 7. Run Application

```bash
cd ..
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Aplikasi akan berjalan di: `http://127.0.0.1:8000`

---

## 📝 Configuration

### Environment Variables

Buat file `.env` di root directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@host:5432/postgres

# JWT Secret
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# InsightFace
INSIGHTFACE_HOME=/code/cache

# Application
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### Database Configuration

File `database.py`:
```python
DATABASE_URL = "postgresql+asyncpg://postgres:password@host:5432/postgres"
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)
```

### Cloudflare WARP (Required untuk Supabase)

Jika ISP Anda memblokir koneksi langsung ke Supabase:

1. Install Cloudflare WARP
2. Aktifkan WARP sebelum menjalankan aplikasi
3. Gunakan port **5432** (direct connection), bukan **6543** (pooler)

---

## 💻 Usage

### Login

1. Buka `http://127.0.0.1:8000/login.html`
2. Login dengan kredensial:
   - **Mahasiswa**: NIM sebagai username
   - **Dosen**: NPP sebagai username
   - **Kaprodi**: `admin` / `admin123`

### Workflow: Dosen

1. **Login** sebagai dosen
2. **Pilih Jadwal** dari dropdown
3. **Upload Video** rekaman kuliah (.mp4, .avi, .mov)
4. **Tunggu Processing** (progress bar real-time)
5. **Review Hasil** absensi otomatis
6. **Validasi Manual** jika diperlukan
7. **Export Excel** untuk dokumentasi

### Workflow: Mahasiswa

1. **Login** dengan NIM
2. **Lihat Jadwal** kuliah hari ini dan minggu ini
3. **Cek Kehadiran** status hadir/alpha
4. **Lapor** jika ada kesalahan deteksi
5. **Lihat History** riwayat kehadiran lengkap

### Workflow: Kaprodi

1. **Manajemen User** - Tambah mahasiswa/dosen
2. **Buat Kelas** - Tambah mata kuliah baru
3. **Buat Student Class** - Buat kelas (A11.4109, dll)
4. **Enrollment** - Assign mahasiswa ke mata kuliah
5. **Set Jadwal** - Atur jadwal kuliah
6. **Monitor** - Lihat statistik keseluruhan

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────┐
│   Client Side   │
│  (Browser/JS)   │
└────────┬────────┘
         │ HTTP/REST API
         │
┌────────▼────────┐
│   FastAPI App   │
│   (main.py)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼─────┐
│ Auth  │ │  Face  │
│Module │ │   AI   │
└───┬───┘ └──┬─────┘
    │        │
┌───▼────────▼───┐
│   PostgreSQL   │
│   + pgvector   │
└────────────────┘
```

### Database Schema

```
users (Akun & Autentikasi)
├── user_id (PK)
├── username (UNIQUE)
├── password (hashed)
├── full_name
├── role
└── is_active

mahasiswa (Data Biometrik)
├── nim (PK)
├── user_id (FK → users)
└── embedding_data (vector[512])

student_class (Kelas Mahasiswa)
├── class_id (PK)
├── class_name (UNIQUE)
└── created_at

kelas (Mata Kuliah)
├── kelas_id (PK)
├── nama_matkul
└── kode_ruang

kelas_enrollment (Pendaftaran)
├── enrollment_id (PK)
├── nim (FK → mahasiswa)
├── student_class_id (FK → student_class)
└── enrolled_at

jadwal (Sesi Kuliah)
├── jadwal_id (PK)
├── dosen_username (FK → users)
├── kelas_id (FK → kelas)
├── student_class_id (FK → student_class)
├── hari
├── jam_mulai
└── jam_selesai

video_tasks (Upload History)
├── task_db_id (PK)
├── task_id (UUID)
├── dosen_username (FK → users)
├── jadwal_id (FK → jadwal)
├── filename
├── status
└── created_at

log_absensi (Attendance Records)
├── log_id (PK)
├── task_id (FK → video_tasks)
├── nim (FK → mahasiswa)
├── jadwal_id (FK → jadwal)
├── waktu_absen
├── metode (AI_VIDEO/MANUAL_DOSEN/ALPHA_SYSTEM)
├── jumlah_muncul
├── emosi_dominan
├── bukti_foto
├── is_disputed
└── keterangan_report
```

### Face Recognition Pipeline

```
1. Video Upload
   ↓
2. Frame Extraction (1 fps)
   ↓
3. Face Detection (MTCNN)
   ↓
4. Face Alignment
   ↓
5. Generate Embeddings (InsightFace)
   ↓
6. Similarity Search (pgvector)
   ↓
7. Emotion Analysis
   ↓
8. Save to Database
   ↓
9. Generate Report
```

---

## 🔌 API Endpoints

### Authentication

```http
POST /token
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123

Response: { "access_token": "...", "token_type": "bearer" }
```

### Mahasiswa Endpoints

```http
GET /mhs/jadwal
Authorization: Bearer {token}
Response: [{ jadwal_id, hari, jam, matkul, dosen, student_class_name }]

GET /mhs/history
Authorization: Bearer {token}
Response: [{ log_id, waktu_absen, matkul, metode, status }]

POST /mhs/report-dispute
Authorization: Bearer {token}
Body: { log_id, keterangan }
```

### Dosen Endpoints

```http
GET /dosen/jadwal
Authorization: Bearer {token}
Response: [{ jadwal_id, hari, jam, matkul, kelas }]

POST /dosen/upload
Authorization: Bearer {token}
Body: multipart/form-data (video file + jadwal_id)
Response: { task_id, status }

GET /dosen/task-status/{task_id}
Authorization: Bearer {token}
Response: { status, progress, result }

GET /dosen/absensi/{jadwal_id}
Authorization: Bearer {token}
Response: [{ nim, nama, jumlah_muncul, emosi, status }]
```

### Admin Endpoints

```http
GET /admin/users
POST /admin/users
PUT /admin/users/{user_id}
DELETE /admin/users/{user_id}

GET /admin/kelas
POST /admin/kelas
PUT /admin/kelas/{kelas_id}
DELETE /admin/kelas/{kelas_id}

GET /admin/student-class
POST /admin/student-class
DELETE /admin/student-class/{class_id}

GET /admin/jadwal
POST /admin/jadwal
PUT /admin/jadwal/{jadwal_id}
DELETE /admin/jadwal/{jadwal_id}

GET /admin/enrollment
POST /admin/enrollment
DELETE /admin/enrollment/{enrollment_id}
```

---

## 🗄️ Database Optimization

### Indexes Created

Untuk performa optimal, 22 indexes telah dibuat:

```sql
-- Foreign Key Indexes
idx_mahasiswa_user_id
idx_jadwal_dosen_username
idx_jadwal_kelas_id
idx_jadwal_student_class_id
idx_kelas_enrollment_student_class_id
idx_log_absensi_jadwal_id
idx_video_tasks_jadwal_id

-- Composite Indexes
idx_kelas_enrollment_composite (nim, student_class_id)
idx_log_absensi_composite (nim, jadwal_id, waktu_absen)
idx_users_role_active (role, is_active)

-- Partial Indexes
idx_mahasiswa_embedding_not_null (WHERE embedding_data IS NOT NULL)

-- Date/Time Indexes
idx_log_absensi_waktu_absen
idx_video_tasks_created_at
```

**Performance Improvements:**
- Dashboard queries: **60% faster**
- Enrollment checks: **67% faster**
- Attendance queries: **65% faster**
- Face recognition: **76% faster**

See `migrations/PERFORMANCE_ANALYSIS.md` for details.

---

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t edu-sense .
```

### Run Container

```bash
docker run -d \
  --name edu-sense \
  -p 7860:7860 \
  -e DATABASE_URL="postgresql+asyncpg://..." \
  -e SECRET_KEY="your-secret-key" \
  edu-sense
```

### Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "7860:7860"
    environment:
      - DATABASE_URL=postgresql+asyncpg://...
      - SECRET_KEY=your-secret-key
    volumes:
      - ./logs:/code/logs
      - ./temp_videos:/code/temp_videos
      - ./hasil_crop:/code/hasil_crop
    restart: unless-stopped
```

---

## 📦 Project Structure

```
edu-sense/
├── main.py                 # FastAPI application entry point
├── models.py               # SQLAlchemy ORM models
├── database.py             # Database configuration
├── auth_utils.py           # JWT authentication utilities
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── README.md               # This file
│
├── static/                 # Static files (if any)
│
├── helpers/                # Utility scripts
│   ├── create_admin.py
│   ├── create_dosen.py
│   ├── create_student.py
│   ├── reset_and_seeder_db.py
│   ├── optimize_database.py
│   ├── video_extractor.py
│   └── fc detection.py
│
├── migrations/             # Database migrations
│   ├── optimize_indexes.sql
│   ├── make_student_class_id_nullable.sql
│   ├── PERFORMANCE_ANALYSIS.md
│   └── README_OPTIMIZATION.md
│
├── logs/                   # Application logs
├── temp_videos/            # Temporary video uploads
├── hasil_crop/             # Face detection results
│   └── reports/            # JSON reports
├── laporan_excel/          # Excel exports
└── a114109/                # Face dataset storage
    ├── NIM1/
    │   ├── face1.jpg
    │   └── face2.jpg
    └── NIM2/
```

---

## 🧪 Testing

### Unit Tests

```bash
pytest tests/
```

### Test Coverage

```bash
pytest --cov=. --cov-report=html
```

### Manual Testing

1. Test face recognition:
```bash
cd helpers
python "fc detection.py" --video test.mp4
```

2. Test database connection:
```bash
python -c "import asyncio; from database import engine; asyncio.run(engine.connect())"
```

---

## 📊 Performance Benchmarks

### Face Recognition
- **Detection Speed**: ~30 frames/second
- **Recognition Accuracy**: >95% (dengan dataset yang baik)
- **Processing Time**: ~1-2 menit per video 10 menit

### Database Queries
- **Dashboard Load**: 6-10ms
- **Attendance Query**: 7-12ms
- **Enrollment Check**: 4-6ms
- **Face Vector Search**: 5-8ms

### System Load
- **CPU Usage**: 40-60% saat processing video
- **Memory**: ~2GB per video processing
- **Storage**: ~50MB per 10 menit video

---

## 🔒 Security Considerations

### Authentication
- ✅ JWT tokens dengan expiry
- ✅ Password hashing (bcrypt)
- ✅ Role-based access control
- ✅ Secure cookie handling

### Data Protection
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ XSS protection (input sanitization)
- ✅ CSRF tokens untuk forms
- ✅ File upload validation

### Privacy
- ⚠️ Face embeddings disimpan sebagai vector (tidak bisa di-reverse)
- ⚠️ Video dihapus setelah processing
- ⚠️ Bukti foto hanya visible untuk dosen/admin

---

## 🐛 Troubleshooting

### Database Connection Error

```
Error: [Errno 11001] getaddrinfo failed
```

**Solution:** Aktifkan Cloudflare WARP dan pastikan menggunakan port 5432 (bukan 6543)

### Face Recognition Tidak Akurat

**Possible Causes:**
- Dataset wajah kurang (min 5 foto per mahasiswa)
- Kualitas video rendah (min 720p recommended)
- Pencahayaan buruk dalam video
- Wajah terlalu kecil/jauh dari kamera

**Solution:** 
1. Tambah foto training di folder `a114109/{NIM}/`
2. Run `video_extractor_embeding.py` untuk regenerate embeddings
3. Pastikan kualitas video 720p+

### Video Processing Stuck

**Solution:**
1. Check logs: `tail -f logs/app.log`
2. Restart server
3. Delete stuck task dari `video_tasks` table
4. Pastikan folder `temp_videos/` writable

### Slow Query Performance

**Solution:**
```bash
cd helpers
python optimize_database.py  # Re-run optimization
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings for functions
- Write unit tests for new features
- Update documentation

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors & Contributors

- **Rama** - Initial development and AI integration
- **Contributors** - See [CONTRIBUTORS.md](CONTRIBUTORS.md)

---

## 🙏 Acknowledgments

- [InsightFace](https://github.com/deepinsight/insightface) - Face recognition
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Supabase](https://supabase.com/) - Database hosting
- [Hugging Face](https://huggingface.co/) - Model hosting
- [TailwindCSS](https://tailwindcss.com/) - UI framework

---

## 📧 Contact & Support

- **Email**: support@edusense.com
- **GitHub Issues**: [Create an issue](https://github.com/yourusername/edu-sense/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/edu-sense/wiki)

---

<div align="center">

**⭐ Star this repo if you find it helpful!**

Made with ❤️ for Indonesian Higher Education

</div>
