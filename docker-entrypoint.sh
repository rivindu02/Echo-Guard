#!/bin/bash
# Quick setup and run script for Docker Compose
# React UI only (Server runs on Raspberry Pi)

echo "╔════════════════════════════════════════╗"
echo "║  Echo-Guard Docker Setup Script        ║"
echo "║      React UI Only                     ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose found"
echo ""

# Get Raspberry Pi IP
get_pi_ip() {
    read -p "Enter Raspberry Pi IP address (or hostname): " pi_ip
    if [ -z "$pi_ip" ]; then
        echo "❌ IP address cannot be empty"
        get_pi_ip
    else
        echo "✅ Pi IP set to: $pi_ip"
    fi
}

# Function to display menu
show_menu() {
    echo "═══════════════════════════════════════"
    echo "         DOCKER COMMANDS                "
    echo "═══════════════════════════════════════"
    echo "1. Build React UI"
    echo "2. Start React UI"
    echo "3. Stop React UI"
    echo "4. View logs"
    echo "5. Restart React UI"
    echo "6. Remove container"
    echo "7. View running containers"
    echo "8. Set Pi IP address"
    echo "9. Exit"
    echo "═══════════════════════════════════════"
}

# Initialize with default or from environment
PI_IP="${PI_IP:-192.168.208.242}"

while true; do
    show_menu
    read -p "Select an option (1-9): " choice
    
    case $choice in
        1)
            echo "🔨 Building React UI..."
            docker-compose build noise-map-ui
            echo "✅ Build complete!"
            ;;
        2)
            echo "🚀 Starting React UI..."
            PI_IP=$PI_IP docker-compose up -d
            echo "✅ React UI started!"
            echo ""
            echo "📍 Access point:"
            echo "   React UI: http://localhost:3000"
            echo ""
            echo "⚙️  Configuration:"
            echo "   WebSocket URL: ws://${PI_IP}:9001"
            echo "   Make sure the server is running on Raspberry Pi!"
            echo ""
            sleep 2
            docker-compose ps
            ;;
        3)
            echo "🛑 Stopping React UI..."
            docker-compose down
            echo "✅ React UI stopped!"
            ;;
        4)
            echo "📋 Showing logs (press Ctrl+C to exit)..."
            docker-compose logs -f noise-map-ui
            ;;
        5)
            echo "🔄 Restarting React UI..."
            docker-compose restart noise-map-ui
            echo "✅ React UI restarted!"
            sleep 2
            docker-compose ps
            ;;
        6)
            echo "⚠️  This will remove the React UI container!"
            read -p "Are you sure? (y/n): " confirm
            if [ "$confirm" = "y" ]; then
                docker-compose down
                echo "✅ Container removed!"
            else
                echo "❌ Cancelled"
            fi
            ;;
        7)
            echo "📦 Running containers:"
            docker-compose ps
            ;;
        8)
            get_pi_ip
            export PI_IP=$pi_ip
            echo "💾 Pi IP updated to: $PI_IP"
            ;;
        9)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please try again."
            ;;
    esac
    
    echo ""
done
