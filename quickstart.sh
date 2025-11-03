#!/bin/bash

# VidGear Docker Streamer - Quick Start Script
# This script helps you get started quickly with VidGear Docker Streamer

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Docker
    if command -v docker &> /dev/null; then
        print_success "Docker is installed ($(docker --version))"
    else
        print_error "Docker is not installed"
        echo "Please install Docker from: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check Docker Compose
    if docker compose version &> /dev/null; then
        print_success "Docker Compose is available ($(docker compose version))"
    else
        print_warning "Docker Compose not found, falling back to standalone docker commands"
    fi
    
    # Check Docker daemon
    if docker ps &> /dev/null; then
        print_success "Docker daemon is running"
    else
        print_error "Docker daemon is not running"
        echo "Please start Docker first"
        exit 1
    fi
    
    echo ""
}

# Setup environment
setup_environment() {
    print_header "Setting Up Environment"
    
    # Create .env file
    if [ ! -f .env ]; then
        cp .env.example .env
        print_success "Created .env file from .env.example"
        print_info "You can edit .env to customize settings"
    else
        print_warning ".env file already exists, skipping..."
    fi
    
    # Create output directory
    mkdir -p output
    print_success "Created output directory"
    
    echo ""
}

# Build Docker image
build_image() {
    print_header "Building Docker Image"
    print_info "This may take a few minutes on first run..."
    
    if docker compose version &> /dev/null; then
        docker compose build
    else
        docker build -t vidgear-streamer .
    fi
    
    print_success "Docker image built successfully"
    echo ""
}

# Run example
run_example() {
    print_header "Running Example"
    
    read -p "Enter video URL (or press Enter for default): " url
    
    if [ -z "$url" ]; then
        url="https://youtu.be/xvFZjo5PgG0"
        print_info "Using default video URL"
    fi
    
    # Update .env with user's URL
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|^VIDEO_URL=.*|VIDEO_URL=$url|" .env
    else
        sed -i "s|^VIDEO_URL=.*|VIDEO_URL=$url|" .env
    fi
    
    read -p "Process full video or limit frames? (full/limit): " limit_choice
    
    if [ "$limit_choice" = "limit" ]; then
        read -p "Enter frame limit (e.g., 300 for ~10 seconds): " frames
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|^FRAME_LIMIT=.*|FRAME_LIMIT=$frames|" .env
        else
            sed -i "s|^FRAME_LIMIT=.*|FRAME_LIMIT=$frames|" .env
        fi
        print_info "Will process $frames frames"
    else
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|^FRAME_LIMIT=.*|FRAME_LIMIT=0|" .env
        else
            sed -i "s|^FRAME_LIMIT=.*|FRAME_LIMIT=0|" .env
        fi
        print_info "Will process entire video"
    fi
    
    print_info "Starting video processing..."
    echo ""
    
    if docker compose version &> /dev/null; then
        docker compose up
    else
        docker run --rm \
            -v "$(pwd)/output:/app/output" \
            --env-file .env \
            vidgear-streamer
    fi
    
    echo ""
    print_success "Processing complete!"
    print_info "Output file: output/vidgear_output.mp4"
}

# Main menu
show_menu() {
    print_header "VidGear Docker Streamer - Quick Start"
    echo "1. Full setup and run (recommended for first time)"
    echo "2. Build Docker image only"
    echo "3. Run with existing image"
    echo "4. View logs"
    echo "5. Clean up"
    echo "6. Exit"
    echo ""
    read -p "Select an option (1-6): " choice
    
    case $choice in
        1)
            check_prerequisites
            setup_environment
            build_image
            run_example
            ;;
        2)
            check_prerequisites
            build_image
            ;;
        3)
            check_prerequisites
            if [ ! -f .env ]; then
                setup_environment
            fi
            run_example
            ;;
        4)
            if docker compose version &> /dev/null; then
                docker compose logs -f
            else
                docker logs -f vidgear-streamer
            fi
            ;;
        5)
            print_header "Cleaning Up"
            docker compose down 2>/dev/null || true
            rm -rf output/*.mp4 output/*.aac 2>/dev/null || true
            print_success "Cleanup complete"
            ;;
        6)
            print_info "Goodbye!"
            exit 0
            ;;
        *)
            print_error "Invalid option"
            show_menu
            ;;
    esac
}

# Print welcome message
clear
echo -e "${GREEN}"
cat << "EOF"
╦  ╦┬┌┬┐╔═╗┌─┐┌─┐┬─┐  ╔╦╗┌─┐┌─┐┬┌─┌─┐┬─┐
║  ║││ ││ ╦├┤ ├─┤├┬┘   ║║│ ││  ├┴┐├┤ ├┬┘
╚═╝╩┴└─┘╚═╝└─┘┴ ┴┴└─  ═╩╝└─┘└─┘┴ ┴└─┘┴└─
       ╔═╗┌┬┐┬─┐┌─┐┌─┐┌┬┐┌─┐┬─┐
       ╚═╗ │ ├┬┘├┤ ├─┤│││├┤ ├┬┘
       ╚═╝ ┴ ┴└─└─┘┴ ┴┴ ┴└─┘┴└─
EOF
echo -e "${NC}"

# Run main menu
show_menu

# Ask if user wants to do something else
echo ""
read -p "Do you want to perform another action? (y/n): " another

if [ "$another" = "y" ] || [ "$another" = "Y" ]; then
    show_menu
else
    print_info "Goodbye!"
fi
