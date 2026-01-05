# 🤗 Deploy EduSense ke Hugging Face Spaces

## 📋 Prerequisites

1. Akun Hugging Face: https://huggingface.co/join
2. Git installed
3. Hugging Face CLI: `pip install huggingface_hub`

---

## 🚀 Setup Langkah-demi-Langkah

### **Step 1: Login ke Hugging Face**

```bash
# Install Hugging Face CLI
pip install huggingface_hub

# Login
huggingface-cli login
# Paste your token from: https://huggingface.co/settings/tokens
```

---

### **Step 2: Buat Hugging Face Space**

1. Buka https://huggingface.co/spaces
2. Klik **"Create new Space"**
3. Isi form:
   - **Space name:** `edusense-attendance`
   - **License:** MIT
   - **Select SDK:** Docker
   - **Hardware:** CPU (free) atau GPU T4 (berbayar)
4. Klik **Create Space**

---

### **Step 3: Clone Repository Space**

```bash
# Clone space repository
git clone https://huggingface.co/spaces/YOUR_USERNAME/edusense-attendance
cd edusense-attendance

# Configure git
git config user.email "your@email.com"
git config user.name "Your Name"
```

---

### **Step 4: Prepare Files untuk Upload**

Copy files penting ke space repository:

```bash
# Di folder EduSense Anda
cp main.py ../edusense-attendance/
cp models.py ../edusense-attendance/
cp database.py ../edusense-attendance/
cp auth_utils.py ../edusense-attendance/
cp requirements.txt ../edusense-attendance/

# Copy static files (optional - jika ingin UI)
cp -r static ../edusense-attendance/
cp dashboard_*.html ../edusense-attendance/
```

---

### **Step 5: Create Dockerfile**

```dockerfile
# File: Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for face recognition
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p temp_videos hasil_crop logs

# Expose port
EXPOSE 7860

# Run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
```

---

### **Step 6: Update requirements.txt untuk HF**

```txt
# File: requirements.txt
fastapi==0.115.5
uvicorn[standard]==0.32.1
sqlalchemy[asyncio]==2.0.36
asyncpg==0.30.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.20
aiofiles==24.1.0
insightface==0.7.3
onnxruntime==1.20.1
opencv-python-headless==4.10.0.84
numpy==1.26.4
Pillow==11.0.0
```

---

### **Step 7: Create README.md untuk Space**

```markdown
---
title: EduSense Attendance
emoji: 📸
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# EduSense - Smart Attendance System

Sistem absensi otomatis menggunakan face recognition dengan InsightFace.

## Features
- 🎥 Video-based attendance
- 👤 Face recognition with InsightFace
- 📊 Real-time dashboard
- 🔐 JWT authentication

## API Endpoints

### Authentication
- `POST /login` - Login
- `POST /register` - Register

### Face Registration
- `POST /mhs/register_face` - Register student face
- `GET /mhs/check_face_status` - Check face registration status

### Attendance
- `POST /dosen/upload_attendance_video` - Upload attendance video
- `GET /dosen/class/{jadwal_id}/attendance` - Get attendance list

## Environment Variables

Create `.env` file:
```
DATABASE_URL=your_postgresql_url
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRATION=1440
```

## Local Development

\`\`\`bash
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
\`\`\`
```

---

### **Step 8: Create .env file untuk Secrets**

⚠️ **PENTING:** Jangan commit `.env` ke git!

Create file: `.env`
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION=1440
```

Untuk Hugging Face, set secrets via UI:
1. Go to Space Settings
2. Variables and Secrets section
3. Add secrets:
   - `DATABASE_URL`
   - `JWT_SECRET_KEY`

---

### **Step 9: Create .gitignore**

```gitignore
# File: .gitignore
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.env
.venv
env/
venv/
temp_videos/
hasil_crop/
logs/
*.log
.DS_Store
```

---

### **Step 10: Push ke Hugging Face**

```bash
cd edusense-attendance

# Add files
git add Dockerfile README.md requirements.txt
git add main.py models.py database.py auth_utils.py
git add .gitignore

# Commit
git commit -m "Initial EduSense deployment"

# Push to Hugging Face
git push

# Monitor build
# Go to: https://huggingface.co/spaces/YOUR_USERNAME/edusense-attendance
```

---

## 🔧 Configuration di Hugging Face Space

### **Set Environment Variables:**

1. Go to Space → Settings
2. Add Repository secrets:
   - `DATABASE_URL`: Your Supabase PostgreSQL URL
   - `JWT_SECRET_KEY`: Your secret key
   - `JWT_ALGORITHM`: HS256
   - `JWT_EXPIRATION`: 1440

### **Upgrade Hardware (Optional):**

Untuk performa lebih baik:
- CPU Basic (Free) → untuk demo
- CPU Upgrade ($0.03/hour) → untuk production kecil
- GPU T4 ($0.60/hour) → untuk face recognition lebih cepat

---

## 📊 Testing Deployment

Setelah build selesai:

```bash
# Test API
curl https://YOUR_USERNAME-edusense-attendance.hf.space/

# Test login
curl -X POST https://YOUR_USERNAME-edusense-attendance.hf.space/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## ⚠️ Known Issues & Solutions

### Issue 1: Build Timeout
**Solution:** Reduce model size atau gunakan pre-built Docker image

### Issue 2: Memory Error
**Solution:** 
- Upgrade ke CPU Upgrade atau GPU
- Reduce batch size di video processing

### Issue 3: Database Connection
**Solution:**
- Verify DATABASE_URL secret is set
- Check Supabase allows connections from Hugging Face IPs

---

## 🎯 Alternative: Deploy as Gradio App

Jika ingin UI yang lebih simple:

```python
# File: app.py
import gradio as gr
import requests

API_URL = "http://localhost:7860"

def login(username, password):
    response = requests.post(f"{API_URL}/login", json={
        "username": username,
        "password": password
    })
    return response.json()

with gr.Blocks() as demo:
    gr.Markdown("# EduSense Attendance System")
    
    with gr.Tab("Login"):
        username = gr.Textbox(label="Username")
        password = gr.Textbox(label="Password", type="password")
        login_btn = gr.Button("Login")
        output = gr.JSON()
        
        login_btn.click(login, [username, password], output)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
```

Update requirements:
```txt
gradio==4.0.0
```

Update Dockerfile SDK:
```yaml
sdk: gradio
sdk_version: 4.0.0
```

---

## 📚 Resources

- Hugging Face Spaces Docs: https://huggingface.co/docs/hub/spaces
- Docker SDK Guide: https://huggingface.co/docs/hub/spaces-sdks-docker
- Gradio SDK Guide: https://huggingface.co/docs/hub/spaces-sdks-gradio

---

## ✅ Checklist Deployment

- [ ] Akun Hugging Face created
- [ ] Space created (Docker SDK)
- [ ] Files copied (main.py, models.py, etc.)
- [ ] Dockerfile created
- [ ] requirements.txt updated
- [ ] README.md created
- [ ] .gitignore configured
- [ ] Environment variables set in Space settings
- [ ] Code pushed to HF
- [ ] Build successful
- [ ] API tested
- [ ] Database connection verified

---

**Need Help?** 
- Hugging Face Discord: https://discord.gg/huggingface
- Hugging Face Forum: https://discuss.huggingface.co/
