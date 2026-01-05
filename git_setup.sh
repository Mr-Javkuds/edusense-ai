#!/bin/bash
# Script untuk inisialisasi Git Repository dan Push ke GitHub

echo "🚀 EduSense AI - Git Setup & Push Script"
echo "========================================"
echo ""

# 1. Initialize Git (jika belum)
if [ ! -d ".git" ]; then
    echo "📝 Initializing Git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "✅ Git already initialized"
fi

# 2. Add all files
echo ""
echo "📦 Adding files to Git..."
git add .

# 3. Show status
echo ""
echo "📊 Git Status:"
git status

# 4. Commit
echo ""
echo "💾 Creating commit..."
git commit -m "Initial commit: EduSense AI Face Recognition System"

# 5. Instructions untuk GitHub
echo ""
echo "🎯 Next Steps:"
echo "1. Buat repository baru di GitHub"
echo "2. Jalankan perintah berikut:"
echo ""
echo "   git remote add origin <YOUR_GITHUB_REPO_URL>"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "✅ Setup complete!"
