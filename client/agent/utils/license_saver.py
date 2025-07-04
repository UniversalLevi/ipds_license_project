"""
License file management utilities
"""

import os
import json
import shutil
import logging
from typing import Dict, Any, Optional
from agent.config import config

logger = logging.getLogger(__name__)

class LicenseSaver:
    """Handle license file operations"""
    
    def __init__(self, license_path: str = None, backup_path: str = None):
        """Initialize license saver"""
        self.license_path = license_path or config.LICENSE_FILE_PATH
        self.backup_path = backup_path or config.LICENSE_BACKUP_PATH
    
    def save_license(self, license_data: Dict[str, Any]) -> bool:
        """Save license data to file"""
        try:
            # Create directory if it doesn't exist
            license_dir = os.path.dirname(self.license_path)
            if license_dir and not os.path.exists(license_dir):
                os.makedirs(license_dir, mode=0o755)
            
            # Create backup of existing license if it exists
            if os.path.exists(self.license_path):
                self._create_backup()
            
            # Save new license
            with open(self.license_path, 'w') as f:
                json.dump(license_data, f, indent=2, ensure_ascii=False)
            
            # Set appropriate permissions (readable by owner only)
            os.chmod(self.license_path, 0o600)
            
            logger.info(f"License saved successfully to: {self.license_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save license: {e}")
            return False
    
    def load_license(self) -> Optional[Dict[str, Any]]:
        """Load license data from file"""
        try:
            if not os.path.exists(self.license_path):
                logger.warning(f"License file not found: {self.license_path}")
                return None
            
            with open(self.license_path, 'r') as f:
                license_data = json.load(f)
            
            logger.info(f"License loaded successfully from: {self.license_path}")
            return license_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in license file: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to load license: {e}")
            return None
    
    def license_exists(self) -> bool:
        """Check if license file exists"""
        return os.path.exists(self.license_path)
    
    def get_license_path(self) -> str:
        """Get the license file path"""
        return self.license_path
    
    def _create_backup(self) -> bool:
        """Create backup of existing license file"""
        try:
            shutil.copy2(self.license_path, self.backup_path)
            logger.info(f"License backup created: {self.backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create license backup: {e}")
            return False
    
    def restore_backup(self) -> bool:
        """Restore license from backup"""
        try:
            if not os.path.exists(self.backup_path):
                logger.warning(f"Backup file not found: {self.backup_path}")
                return False
            
            shutil.copy2(self.backup_path, self.license_path)
            logger.info(f"License restored from backup: {self.backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore license from backup: {e}")
            return False
    
    def delete_license(self) -> bool:
        """Delete license file"""
        try:
            if os.path.exists(self.license_path):
                os.remove(self.license_path)
                logger.info(f"License file deleted: {self.license_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete license file: {e}")
            return False
    
    def get_license_info(self) -> Dict[str, Any]:
        """Get basic information about the license file"""
        info = {
            'exists': False,
            'path': self.license_path,
            'size': 0,
            'modified': None
        }
        
        if os.path.exists(self.license_path):
            info['exists'] = True
            info['size'] = os.path.getsize(self.license_path)
            info['modified'] = os.path.getmtime(self.license_path)
        
        return info
    
    def validate_license_file(self) -> bool:
        """Validate that license file contains valid JSON"""
        try:
            license_data = self.load_license()
            if license_data is None:
                return False
            
            # Check for required fields
            required_fields = [
                'customer_name', 'username', 'product_name', 'product_id',
                'license_key', 'status', 'start_date', 'expiry_date', 'signature'
            ]
            
            for field in required_fields:
                if field not in license_data:
                    logger.error(f"Missing required field in license: {field}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"License validation failed: {e}")
            return False

# Global instance
license_saver = LicenseSaver() 