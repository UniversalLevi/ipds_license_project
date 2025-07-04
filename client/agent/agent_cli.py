#!/usr/bin/env python3
"""
ZAYONA License Agent CLI
Interactive command-line tool for license management
"""

import os
import sys
import logging
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.config import config
from agent.utils.hardware_fingerprint import hardware_fingerprint
from agent.utils.api_client import api_client
from agent.utils.license_saver import license_saver

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LicenseAgentCLI:
    """Interactive CLI for license management"""
    
    def __init__(self):
        """Initialize the CLI"""
        self.api_client = api_client
        self.license_saver = license_saver
        self.hardware_fingerprint = hardware_fingerprint
        self.api_url = self.prompt_api_url()
        self.api_client.set_base_url(self.api_url)
        self.api_connection_status = self.test_api_connection(silent=True)
    
    def prompt_api_url(self):
        """Prompt for API URL with default from config"""
        default_url = getattr(config, 'API_BASE_URL', 'http://localhost:8000')
        print(f"\n{Fore.CYAN}API Server URL Configuration{Style.RESET_ALL}")
        print(f"Current default: {Fore.YELLOW}{default_url}{Style.RESET_ALL}")
        url = input(f"Enter API server URL [{default_url}]: ").strip()
        if not url:
            url = default_url
        print(f"{Fore.GREEN}Using API server: {url}{Style.RESET_ALL}")
        return url

    def change_api_url(self):
        """Change the API URL during runtime"""
        print(f"\n{Fore.CYAN}Change API Server URL{Style.RESET_ALL}")
        url = input(f"Enter new API server URL [{self.api_url}]: ").strip()
        if url:
            self.api_url = url
            self.api_client.set_base_url(self.api_url)
            print(f"{Fore.GREEN}API server URL updated to: {self.api_url}{Style.RESET_ALL}")
            self.api_connection_status = self.test_api_connection(silent=True)
        else:
            print(f"{Fore.YELLOW}API server URL unchanged.{Style.RESET_ALL}")

    def print_banner(self):
        """Print application banner"""
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}🔐 ZAYONA LICENSE MANAGEMENT AGENT (CLI){Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.WHITE}Version: 1.0.0")
        print(f"{Fore.WHITE}API Server: {Fore.YELLOW}{self.api_url}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}License Path: {config.LICENSE_FILE_PATH}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        if not self.api_connection_status:
            print(f"{Fore.RED}❌ Warning: Could not connect to API server at {self.api_url}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✅ API server reachable!{Style.RESET_ALL}")

    def print_menu(self):
        """Print main menu"""
        print(f"\n{Fore.YELLOW}📋 MAIN MENU{Style.RESET_ALL}")
        print(f"{Fore.WHITE}1. {Fore.GREEN}Generate New License{Style.RESET_ALL}")
        print(f"{Fore.WHITE}2. {Fore.BLUE}Verify Existing License{Style.RESET_ALL}")
        print(f"{Fore.WHITE}3. {Fore.MAGENTA}Show License Info{Style.RESET_ALL}")
        print(f"{Fore.WHITE}4. {Fore.CYAN}Test API Connection{Style.RESET_ALL}")
        print(f"{Fore.WHITE}5. {Fore.YELLOW}Show Hardware Fingerprint{Style.RESET_ALL}")
        print(f"{Fore.WHITE}6. {Fore.CYAN}Change API Server URL{Style.RESET_ALL}")
        print(f"{Fore.WHITE}7. {Fore.RED}Exit{Style.RESET_ALL}")
    
    def get_user_input(self, prompt: str, required: bool = True) -> str:
        """Get user input with validation"""
        while True:
            value = input(f"{Fore.CYAN}{prompt}: {Style.RESET_ALL}").strip()
            if value or not required:
                return value
            print(f"{Fore.RED}This field is required. Please try again.{Style.RESET_ALL}")
    
    def generate_license(self):
        """Generate a new license"""
        print(f"\n{Fore.GREEN}🔑 LICENSE GENERATION{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Please provide the following information:{Style.RESET_ALL}")
        
        try:
            # Get user input
            username = self.get_user_input("Username")
            password = self.get_user_input("Password")
            product_id = self.get_user_input("Product ID (e.g., ZAYONA-PRO-9988)")
            customer_name = self.get_user_input("Customer Name")
            email = self.get_user_input("Email Address")
            
            print(f"\n{Fore.YELLOW}🔄 Generating hardware fingerprint...{Style.RESET_ALL}")
            try:
                hw_fingerprint = self.hardware_fingerprint.generate_fingerprint()
                print(f"{Fore.GREEN}✅ Hardware fingerprint generated{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️  Warning: Could not get full hardware fingerprint: {e}{Style.RESET_ALL}")
                hw_fingerprint = "UNKNOWN"
            
            print(f"\n{Fore.YELLOW}🔄 Connecting to license server...{Style.RESET_ALL}")
            
            # Generate license via API
            response = self.api_client.generate_license(
                username=username,
                password=password,
                product_id=product_id,
                customer_name=customer_name,
                email=email,
                hardware_fingerprint=hw_fingerprint
            )
            
            if response.get('success'):
                license_data = response['license']
                
                print(f"\n{Fore.GREEN}✅ License generated successfully!{Style.RESET_ALL}")
                print(f"{Fore.WHITE}License Key: {Fore.CYAN}{license_data['license_key']}{Style.RESET_ALL}")
                
                # Save license to file
                print(f"\n{Fore.YELLOW}🔄 Saving license to file...{Style.RESET_ALL}")
                if self.license_saver.save_license(license_data):
                    print(f"{Fore.GREEN}✅ License saved to: {license_data['license_key']}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Failed to save license file{Style.RESET_ALL}")
                
                # Show license details
                self.show_license_details(license_data)
                
            else:
                print(f"{Fore.RED}❌ License generation failed{Style.RESET_ALL}")
                print(f"{Fore.RED}Error: {response.get('message', 'Unknown error')}{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error generating license: {e}{Style.RESET_ALL}")
            logger.error(f"License generation error: {e}")
    
    def verify_license(self):
        """Verify an existing license"""
        print(f"\n{Fore.BLUE}🔍 LICENSE VERIFICATION{Style.RESET_ALL}")
        
        try:
            # Check if license file exists
            if not self.license_saver.license_exists():
                print(f"{Fore.RED}❌ No license file found at: {config.LICENSE_FILE_PATH}{Style.RESET_ALL}")
                return
            
            # Load license from file
            license_data = self.license_saver.load_license()
            if not license_data:
                print(f"{Fore.RED}❌ Failed to load license file{Style.RESET_ALL}")
                return
            
            license_key = license_data.get('license_key')
            if not license_key:
                print(f"{Fore.RED}❌ Invalid license file - missing license key{Style.RESET_ALL}")
                return
            
            print(f"{Fore.YELLOW}🔄 Generating hardware fingerprint...{Style.RESET_ALL}")
            try:
                hw_fingerprint = self.hardware_fingerprint.generate_fingerprint()
                print(f"{Fore.GREEN}✅ Hardware fingerprint generated{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️  Warning: Could not get full hardware fingerprint: {e}{Style.RESET_ALL}")
                hw_fingerprint = "UNKNOWN"
            
            print(f"{Fore.YELLOW}🔄 Verifying license with server...{Style.RESET_ALL}")
            
            # Verify license via API
            response = self.api_client.verify_license(license_key, hw_fingerprint)
            
            if response.get('success'):
                print(f"{Fore.GREEN}✅ License verification successful!{Style.RESET_ALL}")
                license_info = response['license_info']
                print(f"{Fore.WHITE}Status: {Fore.GREEN}{license_info['status']}{Style.RESET_ALL}")
                print(f"{Fore.WHITE}Valid Until: {Fore.CYAN}{license_info['valid_till']}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ License verification failed{Style.RESET_ALL}")
                print(f"{Fore.RED}Error: {response.get('message', 'Unknown error')}{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error verifying license: {e}{Style.RESET_ALL}")
            logger.error(f"License verification error: {e}")
    
    def show_license_info(self):
        """Show license information"""
        print(f"\n{Fore.MAGENTA}📄 LICENSE INFORMATION{Style.RESET_ALL}")
        
        try:
            # Check if license file exists
            if not self.license_saver.license_exists():
                print(f"{Fore.RED}❌ No license file found at: {config.LICENSE_FILE_PATH}{Style.RESET_ALL}")
                return
            
            # Load license from file
            license_data = self.license_saver.load_license()
            if not license_data:
                print(f"{Fore.RED}❌ Failed to load license file{Style.RESET_ALL}")
                return
            
            # Show license details
            self.show_license_details(license_data)
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error showing license info: {e}{Style.RESET_ALL}")
            logger.error(f"Show license info error: {e}")
    
    def show_license_details(self, license_data: dict):
        """Show detailed license information"""
        print(f"\n{Fore.CYAN}📋 LICENSE DETAILS{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Customer Name: {Fore.YELLOW}{license_data.get('customer_name', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Username: {Fore.YELLOW}{license_data.get('username', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Product Name: {Fore.YELLOW}{license_data.get('product_name', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Product ID: {Fore.YELLOW}{license_data.get('product_id', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}License Key: {Fore.CYAN}{license_data.get('license_key', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}License Type: {Fore.YELLOW}{license_data.get('license_type', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Status: {Fore.GREEN}{license_data.get('status', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Start Date: {Fore.YELLOW}{license_data.get('start_date', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Expiry Date: {Fore.YELLOW}{license_data.get('expiry_date', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Email: {Fore.YELLOW}{license_data.get('email', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Last Check: {Fore.YELLOW}{license_data.get('license_server_check', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Timestamp: {Fore.YELLOW}{license_data.get('timestamp', 'N/A')}{Style.RESET_ALL}")
        signature = license_data.get('signature', '')
        if signature:
            print(f"{Fore.WHITE}Signature: {Fore.CYAN}{signature[:20]}...{Style.RESET_ALL}")
    
    def test_api_connection(self, silent=False):
        """Test connection to API server"""
        if not silent:
            print(f"\n{Fore.CYAN}🔗 API CONNECTION TEST{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}🔄 Testing connection to: {self.api_url}{Style.RESET_ALL}")
        try:
            if self.api_client.test_connection():
                if not silent:
                    print(f"{Fore.GREEN}✅ API connection successful!{Style.RESET_ALL}")
                return True
            else:
                if not silent:
                    print(f"{Fore.RED}❌ API connection failed{Style.RESET_ALL}")
                return False
        except Exception as e:
            if not silent:
                print(f"{Fore.RED}❌ API connection test failed: {e}{Style.RESET_ALL}")
            logger.error(f"API connection test error: {e}")
            return False
    
    def show_hardware_fingerprint(self):
        """Show hardware fingerprint"""
        print(f"\n{Fore.YELLOW}🖥️ HARDWARE FINGERPRINT{Style.RESET_ALL}")
        try:
            print(f"{Fore.YELLOW}🔄 Generating hardware fingerprint...{Style.RESET_ALL}")
            try:
                fingerprint = self.hardware_fingerprint.generate_fingerprint()
                print(f"{Fore.GREEN}✅ Hardware fingerprint generated{Style.RESET_ALL}")
                print(f"{Fore.WHITE}Fingerprint: {Fore.CYAN}{fingerprint}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️  Warning: Could not get full hardware fingerprint: {e}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error generating hardware fingerprint: {e}{Style.RESET_ALL}")
            logger.error(f"Hardware fingerprint error: {e}")
    
    def run(self):
        """Run the CLI application"""
        self.print_banner()
        while True:
            try:
                self.print_menu()
                choice = self.get_user_input("Enter your choice (1-7)", required=True)
                if choice == '1':
                    self.generate_license()
                elif choice == '2':
                    self.verify_license()
                elif choice == '3':
                    self.show_license_info()
                elif choice == '4':
                    self.test_api_connection()
                elif choice == '5':
                    self.show_hardware_fingerprint()
                elif choice == '6':
                    self.change_api_url()
                elif choice == '7':
                    print(f"\n{Fore.GREEN}👋 Thank you for using ZAYONA License Agent!{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED}❌ Invalid choice. Please enter a number between 1-7.{Style.RESET_ALL}")
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n\n{Fore.YELLOW}⚠️ Operation cancelled by user{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"\n{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}")
                logger.error(f"Unexpected error in CLI: {e}")

def main():
    """Main function"""
    try:
        cli = LicenseAgentCLI()
        cli.run()
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to start CLI: {e}{Style.RESET_ALL}")
        logger.error(f"CLI startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 