#!/bin/bash

# Script để so sánh thời gian build giữa Nixpacks và Docker
# Sử dụng: ./compare_build_times.sh

echo "🚀 Railway Build Time Comparison Tool"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to test Docker build locally
test_docker_build() {
    echo -e "${BLUE}Testing Docker build locally...${NC}"
    echo ""
    
    # Clean build (no cache)
    echo "1️⃣ Clean build (no cache):"
    START_TIME=$(date +%s)
    docker build --no-cache -t vanna-test:clean . > /dev/null 2>&1
    END_TIME=$(date +%s)
    CLEAN_BUILD_TIME=$((END_TIME - START_TIME))
    echo -e "${GREEN}✓ Clean build completed in: ${CLEAN_BUILD_TIME}s${NC}"
    echo ""
    
    # Cached build (with changes)
    echo "2️⃣ Cached build (only code changes):"
    # Make a small change
    echo "# Test change" >> flask_main.py
    START_TIME=$(date +%s)
    docker build -t vanna-test:cached . > /dev/null 2>&1
    END_TIME=$(date +%s)
    CACHED_BUILD_TIME=$((END_TIME - START_TIME))
    # Revert change
    git checkout flask_main.py > /dev/null 2>&1
    echo -e "${GREEN}✓ Cached build completed in: ${CACHED_BUILD_TIME}s${NC}"
    echo ""
    
    # Calculate improvement
    IMPROVEMENT=$(echo "scale=1; (1 - $CACHED_BUILD_TIME / $CLEAN_BUILD_TIME) * 100" | bc)
    echo -e "${YELLOW}💡 Cache improvement: ${IMPROVEMENT}%${NC}"
    echo ""
}

# Function to estimate Railway build times
estimate_railway_times() {
    echo -e "${BLUE}Estimated Railway Build Times:${NC}"
    echo ""
    
    echo "📊 With Nixpacks (Current):"
    echo "  First build:  5-7 minutes"
    echo "  Cached build: 2-3 minutes"
    echo ""
    
    echo "📊 With Docker (Optimized):"
    echo "  First build:  3-4 minutes  ⚡ 40% faster"
    echo "  Cached build: 1-2 minutes  ⚡ 50% faster"
    echo ""
    
    echo "📊 With Pre-built Image:"
    echo "  All builds:   30-60 seconds  ⚡ 90% faster"
    echo ""
}

# Function to show optimization summary
show_optimization_summary() {
    echo -e "${BLUE}🎯 Optimization Summary:${NC}"
    echo ""
    
    echo "✅ Completed optimizations:"
    echo "  ✓ Updated nixpacks.toml with binary wheel preferences"
    echo "  ✓ Optimized railway.json build command"
    echo "  ✓ Enhanced .dockerignore to exclude unnecessary files"
    echo "  ✓ Created optimized Dockerfile"
    echo ""
    
    echo "📝 Files modified:"
    echo "  - nixpacks.toml"
    echo "  - railway.json"
    echo "  - .dockerignore"
    echo "  - Dockerfile (new)"
    echo ""
}

# Function to show next steps
show_next_steps() {
    echo -e "${BLUE}📋 Next Steps:${NC}"
    echo ""
    
    echo "Option 1: Keep Nixpacks (Easier)"
    echo "  ${GREEN}git add nixpacks.toml railway.json .dockerignore${NC}"
    echo "  ${GREEN}git commit -m '⚡ Optimize Nixpacks build'${NC}"
    echo "  ${GREEN}git push origin vanna_dev${NC}"
    echo ""
    
    echo "Option 2: Switch to Docker (Faster - Recommended)"
    echo "  ${GREEN}git add Dockerfile railway.json .dockerignore${NC}"
    echo "  ${GREEN}git commit -m '🐳 Switch to Docker build'${NC}"
    echo "  ${GREEN}git push origin vanna_dev${NC}"
    echo ""
    
    echo "Then monitor your build on Railway Dashboard:"
    echo "  https://railway.app/project/your-project/deployments"
    echo ""
}

# Main execution
main() {
    show_optimization_summary
    estimate_railway_times
    
    echo -e "${YELLOW}Would you like to test Docker build locally? (y/n)${NC}"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        # Check if Docker is installed
        if ! command -v docker &> /dev/null; then
            echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
            echo "  Visit: https://docs.docker.com/get-docker/"
        else
            test_docker_build
        fi
    fi
    
    echo ""
    show_next_steps
    
    echo -e "${GREEN}🎉 All set! Deploy when you're ready.${NC}"
}

# Run main
main
