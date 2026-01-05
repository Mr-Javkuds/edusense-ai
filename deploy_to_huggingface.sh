#!/bin/bash

# ============================================
# Deploy EduSense to Hugging Face Spaces
# Run this script to automate deployment
# ============================================

set -e  # Exit on error

echo "🚀 Starting EduSense deployment to Hugging Face..."

# Check if huggingface-cli is installed
if ! command -v huggingface-cli &> /dev/null; then
    echo "❌ huggingface-cli not found. Installing..."
    pip install huggingface_hub
fi

# Prompt for Hugging Face username
read -p "Enter your Hugging Face username: " HF_USERNAME

# Prompt for space name
read -p "Enter space name (default: edusense-attendance): " SPACE_NAME
SPACE_NAME=${SPACE_NAME:-edusense-attendance}

SPACE_URL="https://huggingface.co/spaces/${HF_USERNAME}/${SPACE_NAME}"

echo ""
echo "📦 Preparing files for deployment..."

# Create temporary deployment directory
DEPLOY_DIR="./deploy_hf"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR

# Copy essential files
echo "  ✓ Copying Python files..."
cp main.py $DEPLOY_DIR/
cp models.py $DEPLOY_DIR/
cp database.py $DEPLOY_DIR/
cp auth_utils.py $DEPLOY_DIR/

echo "  ✓ Copying HTML templates..."
cp dashboard_*.html $DEPLOY_DIR/ 2>/dev/null || echo "    (No dashboard files found)"
cp login.html $DEPLOY_DIR/ 2>/dev/null || echo "    (No login.html found)"
cp register.html $DEPLOY_DIR/ 2>/dev/null || echo "    (No register.html found)"

echo "  ✓ Copying static files..."
cp -r static $DEPLOY_DIR/ 2>/dev/null || echo "    (No static folder found)"

echo "  ✓ Copying configuration files..."
cp Dockerfile $DEPLOY_DIR/
cp requirements.txt $DEPLOY_DIR/
cp README_HF.md $DEPLOY_DIR/README.md

# Create .gitignore
cat > $DEPLOY_DIR/.gitignore << 'EOF'
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
*.mp4
*.avi
EOF

echo "  ✓ Created .gitignore"

# Check if space already exists
echo ""
echo "🔍 Checking if space exists..."

if huggingface-cli repo info "${HF_USERNAME}/${SPACE_NAME}" --repo-type space &> /dev/null; then
    echo "  ℹ️  Space already exists: ${SPACE_URL}"
    read -p "Do you want to update it? (y/n): " UPDATE
    if [ "$UPDATE" != "y" ]; then
        echo "❌ Deployment cancelled"
        exit 0
    fi
else
    echo "  ℹ️  Space does not exist. Creating new space..."
    huggingface-cli repo create "${SPACE_NAME}" \
        --type space \
        --space_sdk docker \
        --private false
    echo "  ✓ Space created: ${SPACE_URL}"
fi

# Clone or pull space repository
echo ""
echo "📥 Setting up git repository..."
cd $DEPLOY_DIR

if [ -d ".git" ]; then
    echo "  ✓ Git repository exists, pulling latest..."
    git pull
else
    echo "  ✓ Cloning space repository..."
    git clone https://huggingface.co/spaces/${HF_USERNAME}/${SPACE_NAME} .
fi

# Configure git
git config user.name "${HF_USERNAME}"
git config user.email "${HF_USERNAME}@users.noreply.huggingface.co"

# Add and commit files
echo ""
echo "📝 Committing changes..."
git add .
git commit -m "Deploy EduSense v$(date +%Y%m%d-%H%M%S)" || echo "  ℹ️  No changes to commit"

# Push to Hugging Face
echo ""
echo "🚢 Pushing to Hugging Face..."
git push

cd ..

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🎉 Your space is available at:"
echo "   ${SPACE_URL}"
echo ""
echo "⚠️  IMPORTANT: Set environment variables in Space Settings:"
echo "   1. Go to: ${SPACE_URL}/settings"
echo "   2. Add Repository secrets:"
echo "      - DATABASE_URL=your_postgresql_url"
echo "      - JWT_SECRET_KEY=your_secret_key"
echo "      - JWT_ALGORITHM=HS256"
echo "      - JWT_EXPIRATION=1440"
echo ""
echo "📊 Monitor build progress:"
echo "   ${SPACE_URL}"
echo ""
echo "🧹 Cleaning up temporary files..."
rm -rf $DEPLOY_DIR
echo "   ✓ Cleanup complete"
echo ""
echo "✨ Done!"
