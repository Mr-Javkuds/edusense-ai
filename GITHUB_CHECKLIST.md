# 📋 GitHub Upload Checklist

## ✅ Pre-Upload Checklist

### 1. Environment & Security
- [x] ✅ File `.env` dibuat dengan kredensial asli
- [x] ✅ File `.env.example` dibuat sebagai template
- [x] ✅ `.gitignore` mencakup `.env` dan file sensitif
- [x] ✅ SECRET_KEY dan DATABASE credentials di `.env`
- [x] ✅ `auth_utils.py` menggunakan environment variables
- [x] ✅ `database.py` menggunakan environment variables
- [x] ✅ `python-dotenv` ditambahkan ke `requirements.txt`

### 2. File Organization
- [x] ✅ File temporary dipindah ke folder `helpers/`
- [x] ✅ File test scripts dipindah ke folder `helpers/`
- [x] ✅ File migration scripts dipindah ke folder `helpers/`
- [x] ✅ Root directory bersih dan rapi

### 3. Documentation
- [x] ✅ README.md ada dan informatif
- [x] ✅ SETUP_GUIDE.md dibuat dengan petunjuk instalasi
- [x] ✅ .gitattributes untuk line ending consistency

### 4. Git Configuration
- [x] ✅ .gitignore mencakup semua file yang tidak perlu
- [x] ✅ Script git_setup.ps1 untuk Windows
- [x] ✅ Script git_setup.sh untuk Linux/Mac

## 🚀 Upload Steps

### Step 1: Verifikasi File Sensitif
```bash
# Pastikan file ini TIDAK akan di-commit:
.env
*.db
logs/
temp_videos/
hasil_crop/
__pycache__/
```

### Step 2: Initialize Git Repository
```bash
# Windows PowerShell
.\git_setup.ps1

# Linux/Mac
chmod +x git_setup.sh
./git_setup.sh
```

### Step 3: Buat Repository di GitHub
1. Login ke GitHub
2. Klik "New Repository"
3. Nama repository: `edusense-ai` (atau nama lain)
4. Description: "Smart Attendance System with AI Face Recognition"
5. Pilih: **Public** atau **Private**
6. **JANGAN** centang "Initialize with README" (sudah ada)
7. Klik "Create Repository"

### Step 4: Connect & Push
```bash
# Ganti <YOUR_GITHUB_USERNAME> dan <REPO_NAME>
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<REPO_NAME>.git
git branch -M main
git push -u origin main
```

### Step 5: Verifikasi Upload
1. Refresh halaman GitHub repository
2. Pastikan file `.env` TIDAK ada di repository
3. Pastikan file `.env.example` ada di repository
4. Pastikan README.md terbaca dengan baik

## ⚠️ IMPORTANT WARNINGS

### ❌ JANGAN UPLOAD:
- `.env` - File dengan kredensial asli
- `*.db` - Database files
- `logs/` - Log files
- `__pycache__/` - Python cache
- `temp_videos/` - Video temporary
- `hasil_crop/` - Hasil cropping
- `*.csv` dengan data sensitif

### ✅ HARUS ADA:
- `.env.example` - Template environment
- `.gitignore` - Git ignore configuration
- `requirements.txt` - Dependencies
- `README.md` - Documentation
- `SETUP_GUIDE.md` - Installation guide

## 🔒 Security Reminders

1. **SECRET_KEY**: Generate baru untuk production
   ```python
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Database Credentials**: Jangan hardcode di code

3. **API Keys**: Simpan di `.env`, jangan commit

4. **Sensitive Data**: Review sebelum commit

## 📝 Post-Upload Tasks

### Update Repository Settings
1. Add description dan tags
2. Add topics: `python`, `fastapi`, `face-recognition`, `ai`, `attendance`
3. Add README badges
4. Setup GitHub Actions (optional)

### Setup Collaborators (Optional)
1. Settings → Collaborators
2. Invite team members
3. Set permission levels

### Enable GitHub Pages (Optional)
Untuk hosting documentation static

## ✅ Final Checklist

Sebelum push ke GitHub, pastikan:

- [ ] File `.env` sudah ada di `.gitignore`
- [ ] Credentials database tidak hardcode
- [ ] SECRET_KEY tidak hardcode
- [ ] README.md lengkap dan jelas
- [ ] requirements.txt up to date
- [ ] Folder temporary tidak di-commit
- [ ] Test git status sebelum push

## 🎉 Done!

Setelah upload berhasil:
1. Share repository link dengan tim
2. Setup CI/CD (optional)
3. Monitor issues & pull requests
4. Keep updating documentation

---

**Last Updated**: January 5, 2026
**Version**: 1.0.0
