#!/bin/bash

echo "🔐 ZAYONA License Management Agent Server"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "run_server.py" ]; then
    echo "❌ run_server.py not found. Please run this script from the agent directory."
    exit 1
fi

echo "🚀 Starting ZAYONA Agent Server..."
echo "📋 This will:"
echo "   - Check dependencies (install manually if needed)"
echo "   - Check database setup (setup manually if needed)"
echo "   - Generate RSA keys"
echo "   - Start the API server"
echo ""
echo "💡 Make sure to:"
echo "   1. Install dependencies: pip install -r api/requirements.txt"
echo "   2. Setup database: See DATABASE_SETUP.md"
echo "   3. Configure .env file with correct database credentials"
echo ""

# Make the script executable
chmod +x run_server.py

# Run the server
python3 run_server.py 