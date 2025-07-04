"""
Configuration settings for the License API Server
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Database settings
    DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+pymysql://root:password@localhost/zayona')
    DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
    DATABASE_PORT = int(os.getenv('DATABASE_PORT', 3306))
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'zayona')
    DATABASE_USER = os.getenv('DATABASE_USER', 'root')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'password')
    
    # RSA Key paths
    PRIVATE_KEY_PATH = os.getenv('PRIVATE_KEY_PATH', '../rsa/private_key.pem')
    PUBLIC_KEY_PATH = os.getenv('PUBLIC_KEY_PATH', '../rsa/public_key.pem')
    
    # Security settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # Rate limiting
    MAX_VERIFICATIONS_PER_DAY = int(os.getenv('MAX_VERIFICATIONS_PER_DAY', 10))
    OFFLINE_GRACE_PERIOD_HOURS = int(os.getenv('OFFLINE_GRACE_PERIOD_HOURS', 48))
    VERIFICATION_INTERVAL_HOURS = int(os.getenv('VERIFICATION_INTERVAL_HOURS', 24))
    
    # License settings
    LICENSE_KEY_PREFIX = os.getenv('LICENSE_KEY_PREFIX', 'OSPL')
    COMPANY_ABBREVIATION = os.getenv('COMPANY_ABBREVIATION', 'OSPL')
    
    # Server settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8000))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'license_api.log')
    
    # Hardware fingerprinting
    HARDWARE_FINGERPRINT_REQUIRED = os.getenv('HARDWARE_FINGERPRINT_REQUIRED', 'true').lower() == 'true'
    AUTO_REVOKE_ON_SHARING = os.getenv('AUTO_REVOKE_ON_SHARING', 'true').lower() == 'true'
    
    # API settings
    API_PREFIX = "/api/v1"
    TITLE = "ZAYONA License Management API"
    DESCRIPTION = "Secure license verification and management system"
    VERSION = "1.0.0"

# Create config instance
config = Config() 