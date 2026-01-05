---
title: EduSense Attendance System
emoji: 📸
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# 🎓 EduSense - Smart Attendance System

Sistem absensi otomatis menggunakan face recognition dengan InsightFace dan FastAPI.

## ✨ Features

- 🎥 **Video-based Attendance** - Upload video untuk absensi otomatis
- 👤 **Face Recognition** - Menggunakan InsightFace (buffalo_l model)
- 📊 **Real-time Dashboard** - Dashboard untuk Kaprodi, Dosen, dan Mahasiswa
- 🔐 **JWT Authentication** - Secure authentication dengan role-based access
- 📈 **Analytics & Reports** - Laporan absensi dan statistik kehadiran
- ⚡ **Async Processing** - Background video processing untuk performa optimal

## 🚀 Quick Start

### API Base URL
```
https://YOUR_USERNAME-edusense-attendance.hf.space
```

### Authentication

**Login:**
```bash
curl -X POST https://YOUR_USERNAME-edusense-attendance.hf.space/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_dosen",
    "password": "password123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "username": "demo_dosen",
    "full_name": "Demo Dosen",
    "role": "dosen"
  }
}
```

## 📚 API Endpoints

### 🔑 Authentication
- `POST /login` - Login
- `POST /register` - Register new user
- `POST /admin/create_user` - Create user (admin only)

### 👤 Mahasiswa (Student)
- `POST /mhs/register_face` - Register face with photo
- `GET /mhs/check_face_status` - Check face registration status
- `GET /mhs/report` - Get personal attendance report
- `GET /mhs/history` - Get attendance history

### 👨‍🏫 Dosen (Teacher)
- `POST /dosen/upload_attendance_video` - Upload attendance video
- `GET /dosen/class/{jadwal_id}/attendance` - Get class attendance
- `POST /dosen/manual_absen` - Manual check-in
- `POST /dosen/close_class` - Close class session
- `GET /dosen/class_report/{jadwal_id}` - Get class report

### 👨‍💼 Kaprodi (Admin)
- `GET /admin/users` - List all users
- `POST /admin/users` - Create new user
- `PUT /admin/users/{username}` - Update user
- `DELETE /admin/users/{username}` - Delete user
- `GET /admin/stats` - Get system statistics

### 📊 History & Reports
- `GET /history/tasks` - Get video processing history
- `GET /history/tasks/{task_id}` - Get specific task details

## 🔧 Configuration

### Environment Variables

Set these in Space Settings → Repository secrets:

```env
# Database (Required)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# JWT Settings (Required)
JWT_SECRET_KEY=your-super-secret-key-minimum-32-characters
JWT_ALGORITHM=HS256
JWT_EXPIRATION=1440

# Optional Settings
LOG_LEVEL=INFO
MAX_VIDEO_SIZE_MB=100
FACE_DETECTION_THRESHOLD=0.6
```

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │
│  (HTML/JS)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI       │
│   Backend       │
└────────┬────────┘
         │
    ┌────┴────┬──────────────┐
    ▼         ▼              ▼
┌────────┐ ┌─────────┐ ┌──────────┐
│ PostgreSQL │ InsightFace│ Background│
│ + PGVector │ (buffalo_l)│  Workers  │
└────────┘ └─────────┘ └──────────┘
```

## 📊 Tech Stack

- **Backend:** FastAPI 0.115.5
- **Database:** PostgreSQL + PGVector (Supabase)
- **Face Recognition:** InsightFace (buffalo_l)
- **Authentication:** JWT (python-jose)
- **Video Processing:** OpenCV, async workers
- **Frontend:** Vanilla JS + Tailwind CSS

## 💾 Database Schema

**Tables:**
- `users` - User accounts (kaprodi, dosen, mahasiswa)
- `mahasiswa` - Student profiles with face embeddings
- `kelas` - Course/class information
- `jadwal` - Class schedules
- `kelas_enrollment` - Student enrollment in classes
- `log_absensi` - Attendance logs
- `video_tasks` - Video processing tasks
- `student_class` - Student class groups

## 🎯 Use Cases

### 1. Register Student Face
```python
import requests

# Login as mahasiswa
response = requests.post(
    "https://YOUR_SPACE.hf.space/login",
    json={"username": "a114109", "password": "pass"}
)
token = response.json()["access_token"]

# Upload face photo
with open("student_photo.jpg", "rb") as f:
    response = requests.post(
        "https://YOUR_SPACE.hf.space/mhs/register_face",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": f}
    )
print(response.json())
```

### 2. Upload Attendance Video
```python
# Login as dosen
response = requests.post(
    "https://YOUR_SPACE.hf.space/login",
    json={"username": "dosen1", "password": "pass"}
)
token = response.json()["access_token"]

# Upload video
with open("class_video.mp4", "rb") as f:
    response = requests.post(
        "https://YOUR_SPACE.hf.space/dosen/upload_attendance_video",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": f},
        data={"jadwal_id": 1}
    )
print(response.json())
```

## 🐛 Troubleshooting

### Build Errors
- Check Dockerfile syntax
- Verify all dependencies in requirements.txt
- Check Space logs in Settings → Logs

### Database Connection
- Verify DATABASE_URL secret is set correctly
- Check Supabase allows connections from Hugging Face
- Test connection: `SELECT 1;`

### Face Recognition Issues
- Ensure InsightFace model downloads correctly
- Check INSIGHTFACE_HOME environment variable
- Verify image format (JPEG/PNG)

## 📝 License

MIT License - see LICENSE file

## 👥 Contributors

- Your Name - Initial work

## 🔗 Links

- [GitHub Repository](https://github.com/yourusername/edusense)
- [Documentation](https://edusense-docs.example.com)
- [Demo Video](https://youtube.com/watch?v=xxx)

---

**Built with ❤️ using Hugging Face Spaces**
