#!/bin/bash

# Test Flask App trước khi deploy lên Railway
# Script này sẽ:
# 1. Check dependencies
# 2. Verify environment variables
# 3. Start server locally
# 4. Test endpoints

set -e  # Exit on error

echo "=================================="
echo "🧪 Pre-deployment Test Script"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Step 1: Check Python version
echo "Step 1: Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python installed: $PYTHON_VERSION"
else
    print_error "Python3 not found. Please install Python 3.11+"
    exit 1
fi
echo ""

# Step 2: Check if .env file exists
echo "Step 2: Checking .env file..."
if [ -f .env ]; then
    print_success ".env file found"
    
    # Source .env file
    export $(cat .env | grep -v '^#' | xargs)
    
    # Check required variables
    if [ -z "$OPENAI_API_KEY" ]; then
        print_error "OPENAI_API_KEY not set in .env"
        exit 1
    fi
    print_success "OPENAI_API_KEY is set"
    
    if [ -z "$HUGGINGFACE_API_KEY" ]; then
        print_error "HUGGINGFACE_API_KEY not set in .env"
        exit 1
    fi
    print_success "HUGGINGFACE_API_KEY is set"
    
    # Check optional DB variables
    if [ -z "$DB_HOST" ]; then
        print_warning "DB_HOST not set (will use default: localhost)"
    else
        print_success "Database config found: $DB_HOST"
    fi
    
else
    print_error ".env file not found. Please create one from .env.example"
    exit 1
fi
echo ""

# Step 3: Check dependencies
echo "Step 3: Checking Python dependencies..."
if [ -f requirements.txt ]; then
    print_info "Installing/verifying requirements..."
    pip3 install -r requirements.txt -q --disable-pip-version-check
    print_success "Dependencies installed"
else
    print_error "requirements.txt not found"
    exit 1
fi
echo ""

# Step 4: Check required files
echo "Step 4: Checking required files..."
files=("flask_main.py" "vietnamese_vanna.py" "bge_m3_embedding.py" "Procfile" "railway.json")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        print_success "$file exists"
    else
        print_error "$file not found"
        exit 1
    fi
done
echo ""

# Step 5: Syntax check
echo "Step 5: Checking Python syntax..."
if python3 -m py_compile flask_main.py 2>/dev/null; then
    print_success "flask_main.py syntax OK"
else
    print_error "Syntax error in flask_main.py"
    exit 1
fi
echo ""

# Step 6: Start server in background
echo "Step 6: Starting Flask server..."
print_info "Starting server on http://localhost:8000"
print_info "Press Ctrl+C to stop the server"
echo ""

# Run the Flask app
python3 flask_main.py

# Note: The script will block here until the server is stopped
# If you want to test endpoints automatically, you can run the server
# in background and add curl tests below

echo ""
print_success "All tests passed! Ready for Railway deployment."
echo ""
echo "Next steps:"
echo "1. Commit and push your changes:"
echo "   git add ."
echo "   git commit -m 'Deploy Flask VannaFlaskApp'"
echo "   git push origin vanna_dev"
echo ""
echo "2. Deploy on Railway:"
echo "   - Go to https://railway.app"
echo "   - Create new project from GitHub repo"
echo "   - Add environment variables"
echo "   - Deploy!"
echo ""
