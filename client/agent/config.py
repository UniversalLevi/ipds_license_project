"""
Configuration for the License Agent CLI
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AgentConfig:
    """Agent configuration settings"""
    
    # API Server settings
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', 30))
    
    # License file settings
    LICENSE_FILE_PATH = os.getenv('LICENSE_FILE_PATH', '/etc/octopyder/license.json')
    LICENSE_BACKUP_PATH = os.getenv('LICENSE_BACKUP_PATH', '/etc/octopyder/license.json.backup')
    
    # Public key settings
    PUBLIC_KEY_PATH = os.getenv('PUBLIC_KEY_PATH', '../rsa/public_key.pem')
    
    # Hardware fingerprinting
    HARDWARE_FINGERPRINT_ENABLED = os.getenv('HARDWARE_FINGERPRINT_ENABLED', 'true').lower() == 'true'
    
    # User interface
    INTERACTIVE_MODE = os.getenv('INTERACTIVE_MODE', 'true').lower() == 'true'
    COLOR_OUTPUT = os.getenv('COLOR_OUTPUT', 'true').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'agent.log')

# Global config instance
config = AgentConfig() 