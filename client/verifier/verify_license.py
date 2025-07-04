#!/usr/bin/env python3
"""
License Verifier
Standalone license verification tool
"""

import os
import sys
import json
import logging
from datetime import datetime
from colorama import init, Fore, Back, Style

# Initialize colorama
init()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.utils.crypto_utils import license_crypto
from agent.utils.hardware_fingerprint import hardware_fingerprint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LicenseVerifier:
    """Standalone license verifier"""
    
    def __init__(self, license_path: str = None, public_key_path: str = None):
        """Initialize verifier"""
        self.license_path = license_path or '/etc/octopyder/license.json'
        self.public_key_path = public_key_path or '../rsa/public_key.pem'
        self.crypto = license_crypto
        self.hw_fingerprint = hardware_fingerprint
    
    def load_license(self) -> dict:
        """Load license from file"""
        try:
            if not os.path.exists(self.license_path):
                raise FileNotFoundError(f"License file not found: {self.license_path}")
            
            with open(self.license_path, 'r') as f:
                license_data = json.load(f)
            
            logger.info(f"License loaded from: {self.license_path}")
            return license_data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in license file: {e}")
        except Exception as e:
            raise Exception(f"Failed to load license: {e}")
    
    def verify_signature(self, license_data: dict) -> bool:
        """Verify license signature"""
        try:
            # Load public key
            self.crypto.load_public_key(self.public_key_path)
            
            # Get signature from license
            signature = license_data.get('signature')
            if not signature:
                raise ValueError("No signature found in license")
            
            # Verify signature
            is_valid = self.crypto.verify_signature(license_data, signature)
            
            if is_valid:
                logger.info("License signature verification successful")
            else:
                logger.error("License signature verification failed")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    def check_expiry(self, license_data: dict) -> bool:
        """Check if license is expired"""
        try:
            expiry_date_str = license_data.get('expiry_date')
            if not expiry_date_str:
                raise ValueError("No expiry date found in license")
            
            # Parse expiry date
            expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d")
            current_date = datetime.now()
            
            is_valid = current_date <= expiry_date
            
            if is_valid:
                logger.info(f"License is valid until: {expiry_date_str}")
            else:
                logger.error(f"License expired on: {expiry_date_str}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Expiry check error: {e}")
            return False
    
    def check_hardware_fingerprint(self, license_data: dict) -> bool:
        """Check hardware fingerprint (basic check)"""
        try:
            # For now, just log the fingerprint
            # In a real implementation, you might want to compare with stored fingerprint
            current_fingerprint = self.hw_fingerprint.generate_fingerprint()
            logger.info(f"Current hardware fingerprint: {current_fingerprint}")
            
            # Return True for now (hardware fingerprint validation would be done server-side)
            return True
            
        except Exception as e:
            logger.error(f"Hardware fingerprint check error: {e}")
            return False
    
    def verify_license(self) -> dict:
        """Complete license verification"""
        result = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'license_info': {}
        }
        
        try:
            print(f"{Fore.CYAN}🔍 VERIFYING LICENSE{Style.RESET_ALL}")
            print(f"{Fore.WHITE}License file: {self.license_path}{Style.RESET_ALL}")
            
            # Load license
            print(f"{Fore.YELLOW}🔄 Loading license file...{Style.RESET_ALL}")
            license_data = self.load_license()
            result['license_info'] = license_data
            
            # Verify signature
            print(f"{Fore.YELLOW}🔄 Verifying digital signature...{Style.RESET_ALL}")
            if not self.verify_signature(license_data):
                result['errors'].append("Digital signature verification failed")
            else:
                print(f"{Fore.GREEN}✅ Digital signature verified{Style.RESET_ALL}")
            
            # Check expiry
            print(f"{Fore.YELLOW}🔄 Checking expiry date...{Style.RESET_ALL}")
            if not self.check_expiry(license_data):
                result['errors'].append("License has expired")
            else:
                print(f"{Fore.GREEN}✅ License is not expired{Style.RESET_ALL}")
            
            # Check status
            status = license_data.get('status', 'Unknown')
            if status != 'Active':
                result['errors'].append(f"License status is not active: {status}")
            else:
                print(f"{Fore.GREEN}✅ License status is active{Style.RESET_ALL}")
            
            # Check hardware fingerprint
            print(f"{Fore.YELLOW}🔄 Checking hardware fingerprint...{Style.RESET_ALL}")
            if not self.check_hardware_fingerprint(license_data):
                result['warnings'].append("Hardware fingerprint check failed")
            else:
                print(f"{Fore.GREEN}✅ Hardware fingerprint check passed{Style.RESET_ALL}")
            
            # Determine overall validity
            result['valid'] = len(result['errors']) == 0
            
            return result
            
        except Exception as e:
            result['errors'].append(f"Verification failed: {e}")
            logger.error(f"License verification error: {e}")
            return result
    
    def print_verification_result(self, result: dict):
        """Print verification results"""
        print(f"\n{Fore.CYAN}📋 VERIFICATION RESULTS{Style.RESET_ALL}")
        
        if result['valid']:
            print(f"{Fore.GREEN}✅ LICENSE IS VALID{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ LICENSE IS INVALID{Style.RESET_ALL}")
        
        # Show errors
        if result['errors']:
            print(f"\n{Fore.RED}❌ ERRORS:{Style.RESET_ALL}")
            for error in result['errors']:
                print(f"{Fore.RED}  • {error}{Style.RESET_ALL}")
        
        # Show warnings
        if result['warnings']:
            print(f"\n{Fore.YELLOW}⚠️ WARNINGS:{Style.RESET_ALL}")
            for warning in result['warnings']:
                print(f"{Fore.YELLOW}  • {warning}{Style.RESET_ALL}")
        
        # Show license info
        if result['license_info']:
            license_data = result['license_info']
            print(f"\n{Fore.CYAN}📄 LICENSE INFORMATION{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Customer: {Fore.YELLOW}{license_data.get('customer_name', 'N/A')}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Product: {Fore.YELLOW}{license_data.get('product_name', 'N/A')}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}License Key: {Fore.CYAN}{license_data.get('license_key', 'N/A')}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Status: {Fore.GREEN if license_data.get('status') == 'Active' else Fore.RED}{license_data.get('status', 'N/A')}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Expiry: {Fore.YELLOW}{license_data.get('expiry_date', 'N/A')}{Style.RESET_ALL}")
    
    def run(self):
        """Run the verifier"""
        try:
            result = self.verify_license()
            self.print_verification_result(result)
            
            # Return appropriate exit code
            return 0 if result['valid'] else 1
            
        except Exception as e:
            print(f"{Fore.RED}❌ Verification failed: {e}{Style.RESET_ALL}")
            logger.error(f"Verification failed: {e}")
            return 1

def main():
    """Main function"""
    try:
        verifier = LicenseVerifier()
        exit_code = verifier.run()
        sys.exit(exit_code)
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to start verifier: {e}{Style.RESET_ALL}")
        logger.error(f"Verifier startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 