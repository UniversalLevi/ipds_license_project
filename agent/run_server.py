#!/usr/bin/env python3
"""
ZAYONA License Management Agent Server
Single script to run the complete agent server with all setup
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_command(command, description, cwd=None):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, cwd=cwd, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_dependencies():
    """Check if Python dependencies are available"""
    requirements_file = "api/requirements.txt"
    if not os.path.exists(requirements_file):
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    print("📦 Checking Python dependencies...")
    print("💡 Please install dependencies manually using: pip install -r api/requirements.txt")
    return True

def setup_database():
    """Check database setup"""
    print("🗄️  Database setup check...")
    print("💡 Please setup database manually using the scripts in the scripts/ directory")
    print("💡 Make sure MySQL/MariaDB is running and configured")
    return True

def generate_rsa_keys():
    """Generate RSA keys if they don't exist"""
    private_key_path = "rsa/private_key.pem"
    public_key_path = "rsa/public_key.pem"
    
    if not os.path.exists(private_key_path) or not os.path.exists(public_key_path):
        print("🔑 Generating RSA keys...")
        if os.path.exists("rsa/generate_keys.py"):
            return run_command("python generate_keys.py", "Generating RSA keys", "rsa")
        else:
            print("❌ RSA key generation script not found")
            return False
    else:
        print("✅ RSA keys already exist")
        return True

def create_env_file():
    """Create .env file with default configuration"""
    env_content = """# Database Configuration
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=zayona
DATABASE_USER=root
DATABASE_PASSWORD=

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Security
SECRET_KEY=your-secret-key-change-this-in-production
HARDWARE_FINGERPRINT_REQUIRED=true
AUTO_REVOKE_ON_SHARING=true

# Rate Limiting
MAX_VERIFICATIONS_PER_DAY=10
OFFLINE_GRACE_PERIOD_HOURS=48
VERIFICATION_INTERVAL_HOURS=24

# License Settings
LICENSE_KEY_PREFIX=OSPL
COMPANY_ABBREVIATION=OSPL

# Logging
LOG_LEVEL=INFO
LOG_FILE=license_api.log
"""
    
    env_file = ".env"
    if not os.path.exists(env_file):
        print("📝 Creating .env file with default configuration...")
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")
    
    return True

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting ZAYONA License Management API Server...")
    print("📋 Server will be available at: http://0.0.0.0:8000")
    print("📖 API Documentation: http://0.0.0.0:8000/docs")
    print("🔍 Health Check: http://0.0.0.0:8000/health")
    print("\n" + "="*60)
    print("Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "api.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], cwd=".")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

def main():
    """Main function to setup and run the server"""
    print("🔐 ZAYONA LICENSE MANAGEMENT AGENT SERVER")
    print("="*50)
    
    # Change to agent directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Setup steps
    steps = [
        ("Creating environment file", create_env_file),
        ("Checking Python dependencies", check_python_dependencies),
        ("Checking database setup", setup_database),
        ("Generating RSA keys", generate_rsa_keys),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 Step: {step_name}")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            return False
    
    print("\n✅ All setup steps completed successfully!")
    
    # Start the server
    start_server()

if __name__ == "__main__":
    main() 