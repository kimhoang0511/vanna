#!/bin/bash

# Quick deployment script cho Railway
# Tự động commit và push code

set -e

echo "=================================="
echo "🚀 Quick Deploy to Railway"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if there are changes to commit
if [[ -z $(git status -s) ]]; then
    print_info "No changes to commit"
else
    print_info "Changes detected. Committing..."
    
    # Show status
    git status -s
    echo ""
    
    # Add all changes
    git add .
    
    # Commit with message
    COMMIT_MSG="Deploy Flask VannaFlaskApp to Railway - $(date '+%Y-%m-%d %H:%M:%S')"
    git commit -m "$COMMIT_MSG"
    
    print_success "Changes committed"
fi

echo ""

# Push to remote
print_info "Pushing to remote repository..."
git push origin vanna_dev

print_success "Code pushed successfully!"

echo ""
echo "=================================="
echo "📋 Next Steps:"
echo "=================================="
echo ""
echo "1. Go to https://railway.app"
echo ""
echo "2. Create New Project → Deploy from GitHub"
echo "   - Select repository: kimhoang0511/vanna"
echo "   - Select branch: vanna_dev"
echo ""
echo "3. Add Environment Variables:"
echo "   - OPENAI_API_KEY=sk-proj-xxx"
echo "   - HUGGINGFACE_API_KEY=hf_xxx"
echo "   - DB_HOST=your-db-host.railway.app"
echo "   - DB_PORT=5432"
echo "   - DB_NAME=railway"
echo "   - DB_USER=postgres"
echo "   - DB_PASSWORD=xxx"
echo "   - DEBUG=False"
echo "   - ALLOW_LLM_TO_SEE_DATA=True"
echo ""
echo "4. Deploy will start automatically!"
echo ""
echo "5. Access your app at:"
echo "   https://your-app-name.up.railway.app"
echo ""
echo "=================================="
print_success "Ready for deployment!"
echo "=================================="
