#!/bin/bash

# MQTT Noise Map UI - Quick Start Script
# This script automates the setup process for the React app

set -e  # Exit on any error

echo "🎵 MQTT Noise Map Dashboard - Quick Start Setup"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Node.js is installed
check_nodejs() {
    print_status "Checking Node.js installation..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js found: $NODE_VERSION"
        
        # Check if Node version is >= 16
        NODE_MAJOR_VERSION=$(echo $NODE_VERSION | cut -d'.' -f1 | sed 's/v//')
        if [ "$NODE_MAJOR_VERSION" -ge 16 ]; then
            print_success "Node.js version is compatible (>= v16)"
        else
            print_error "Node.js version is too old. Please install Node.js v16 or newer."
            exit 1
        fi
    else
        print_error "Node.js not found. Please install Node.js from https://nodejs.org/"
        exit 1
    fi
}

# Check if npm is installed
check_npm() {
    print_status "Checking npm installation..."
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_success "npm found: $NPM_VERSION"
    else
        print_error "npm not found. Please install npm."
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    print_status "Installing project dependencies..."
    
    if [ -f "package.json" ]; then
        print_status "Found package.json, installing dependencies..."
        npm install
        print_success "Dependencies installed successfully!"
    else
        print_error "package.json not found in current directory."
        print_error "Please ensure you're in the mqtt-noise-map-ui project directory."
        exit 1
    fi
}

# Setup environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ -f ".env.example" ]; then
        if [ ! -f ".env.local" ]; then
            cp .env.example .env.local
            print_success "Created .env.local from .env.example"
            print_warning "Please edit .env.local to configure your MQTT broker settings"
            print_status "Example: REACT_APP_MQTT_BROKER_URL=ws://192.168.1.100:9001"
        else
            print_warning ".env.local already exists, skipping creation"
        fi
    else
        print_warning ".env.example not found, skipping environment setup"
    fi
}

# Check project structure
check_project_structure() {
    print_status "Verifying project structure..."
    
    REQUIRED_DIRS=("src" "src/components" "src/mqtt" "public")
    REQUIRED_FILES=("src/App.js" "src/App.css" "src/index.js" "src/components/NoiseMap.js" "src/mqtt/mqttService.js" "public/index.html")
    
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [ ! -d "$dir" ]; then
            print_error "Required directory missing: $dir"
            exit 1
        fi
    done
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Required file missing: $file"
            exit 1
        fi
    done
    
    print_success "Project structure verified!"
}

# Start development server
start_dev_server() {
    print_status "Starting development server..."
    print_status "The app will be available at http://localhost:3000"
    print_status "Press Ctrl+C to stop the server"
    
    # Give user a chance to cancel
    echo ""
    read -p "Press Enter to continue or Ctrl+C to exit..."
    
    npm start
}

# Show post-installation instructions
show_instructions() {
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Edit .env.local to configure your MQTT broker URL"
    echo "2. Ensure your MQTT broker supports WebSockets on port 9001"
    echo "3. Start the development server with: npm start"
    echo ""
    echo "🔗 Useful Commands:"
    echo "   npm start          - Start development server"
    echo "   npm run build      - Build for production"  
    echo "   npm test           - Run tests"
    echo ""
    echo "📖 For more information, see README.md"
    echo ""
}

# Main execution
main() {
    # Parse command line arguments
    START_SERVER=false
    SKIP_DEPS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --start|-s)
                START_SERVER=true
                shift
                ;;
            --skip-deps)
                SKIP_DEPS=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --start, -s     Start development server after setup"
                echo "  --skip-deps     Skip dependency installation"
                echo "  --help, -h      Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Run setup steps
    check_nodejs
    check_npm
    check_project_structure
    
    if [ "$SKIP_DEPS" = false ]; then
        install_dependencies
    else
        print_warning "Skipping dependency installation"
    fi
    
    setup_environment
    
    if [ "$START_SERVER" = true ]; then
        start_dev_server
    else
        show_instructions
    fi
}

# Error handling
trap 'print_error "Setup failed. Please check the error messages above."' ERR

# Run main function
main "$@"