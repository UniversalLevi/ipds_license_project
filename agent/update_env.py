#!/usr/bin/env python3
"""
Update .env file with correct database password
"""

import os

def update_env_file():
    """Update .env file with correct database password"""
    env_content = """# Database Configuration
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=zayona
DATABASE_USER=root
DATABASE_PASSWORD=8888

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
    with open(env_file, 'w') as f:
        f.write(env_content)
    print("✅ .env file updated with correct database password (8888)")

if __name__ == "__main__":
    update_env_file() 