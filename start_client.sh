#!/bin/bash

echo "🔐 ZAYONA License Management Client (CLI Only)"
echo "==================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "run_client.py" ]; then
    echo "❌ run_client.py not found. Please run this script from the client directory."
    exit 1
fi

echo "🚀 Starting ZAYONA Client (CLI Only)..."
echo "📋 This will:"
echo "   - Check dependencies (install manually if needed)"
echo "   - Run the CLI tool for license management"
echo ""
echo "💡 Make sure to:"
echo "   1. Install dependencies: pip install -r agent/requirements.txt"
echo "   2. Configure .env file with correct API server URL and settings"
echo ""

# Make the script executable
chmod +x run_client.py

# Run the client CLI
python3 run_client.py 