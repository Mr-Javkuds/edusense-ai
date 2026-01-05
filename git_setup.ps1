# Script untuk inisialisasi Git Repository dan Push ke GitHub
# PowerShell Version

Write-Host "🚀 EduSense AI - Git Setup & Push Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Initialize Git (jika belum)
if (-not (Test-Path ".git")) {
    Write-Host "📝 Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✅ Git initialized" -ForegroundColor Green
} else {
    Write-Host "✅ Git already initialized" -ForegroundColor Green
}

# 2. Add all files
Write-Host ""
Write-Host "📦 Adding files to Git..." -ForegroundColor Yellow
git add .

# 3. Show status
Write-Host ""
Write-Host "📊 Git Status:" -ForegroundColor Yellow
git status

# 4. Commit
Write-Host ""
Write-Host "💾 Creating commit..." -ForegroundColor Yellow
git commit -m "Initial commit: EduSense AI Face Recognition System"

# 5. Instructions untuk GitHub
Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Buat repository baru di GitHub" -ForegroundColor White
Write-Host "2. Jalankan perintah berikut:" -ForegroundColor White
Write-Host ""
Write-Host "   git remote add origin <YOUR_GITHUB_REPO_URL>" -ForegroundColor Yellow
Write-Host "   git branch -M main" -ForegroundColor Yellow
Write-Host "   git push -u origin main" -ForegroundColor Yellow
Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
