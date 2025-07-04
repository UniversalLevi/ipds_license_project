"""
License key generator and license JSON formatter
"""

import random
import string
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any

class LicenseGenerator:
    """Generate unique license keys and format license JSON"""
    
    def __init__(self, company_abbreviation="OSPL"):
        """Initialize with company abbreviation"""
        self.company_abbreviation = company_abbreviation
    
    def generate_license_key(self, product_code: str, username: str = None) -> str:
        """
        Generate a unique license key
        
        Format: COMPANY-PRODUCT-DATE-TIME-RANDOM
        Example: OSPL-VulnScan-20250626-134123-BYTU5JD
        """
        # Get current date and time
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        time_str = now.strftime("%H%M%S")
        
        # Extract product abbreviation (e.g., "VulnScan" from "ZAYONA-PRO-9988")
        product_parts = product_code.split('-')
        if len(product_parts) >= 2:
            product_abbr = product_parts[1]  # e.g., "PRO"
        else:
            product_abbr = product_code[:8]  # Take first 8 chars if no dash
        
        # Generate random string (5 characters: 3 letters + 2 digits)
        letters = ''.join(random.choices(string.ascii_uppercase, k=3))
        digits = ''.join(random.choices(string.digits, k=2))
        random_part = letters + digits
        
        # Create license key
        license_key = f"{self.company_abbreviation}-{product_abbr}-{date_str}-{time_str}-{random_part}"
        
        return license_key
    
    def generate_unique_license_key(self, product_code: str, username: str = None, existing_keys: list = None) -> str:
        """Generate a unique license key that doesn't exist in the database"""
        max_attempts = 100  # Prevent infinite loop
        
        for attempt in range(max_attempts):
            license_key = self.generate_license_key(product_code, username)
            
            # Check if key already exists
            if existing_keys is None or license_key not in existing_keys:
                return license_key
            
            # If we're here, key exists, try again
            continue
        
        # If we get here, we've tried too many times
        raise Exception("Could not generate unique license key after 100 attempts")
    
    def format_license_json(self, 
                          customer_name: str,
                          username: str,
                          product_name: str,
                          product_id: str,
                          license_key: str,
                          license_type: str = "Subscription – Monthly",
                          email: str = None,
                          start_date: str = None,
                          duration_days: int = 30) -> Dict[str, Any]:
        """
        Format license data as JSON
        
        Returns the license data without signature (signature will be added separately)
        """
        # Set start date to now if not provided
        if start_date is None:
            start_date = datetime.now().strftime("%Y-%m-%d")
        
        # Calculate expiry date
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        expiry_dt = start_dt + timedelta(days=duration_days)
        expiry_date = expiry_dt.strftime("%Y-%m-%d")
        
        # Current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Format license JSON
        license_data = {
            "customer_name": customer_name,
            "username": username,
            "product_name": product_name,
            "product_id": product_id,
            "license_key": license_key,
            "license_type": license_type,
            "status": "Active",
            "start_date": start_date,
            "expiry_date": expiry_date,
            "email": email or f"{username}@example.com",
            "license_server_check": f"Successful (Last checked: {datetime.now().strftime('%Y-%m-%d')})",
            "timestamp": timestamp
            # Note: signature will be added separately
        }
        
        return license_data
    
    def generate_hardware_fingerprint(self, mac_address: str = None, cpu_id: str = None, disk_serial: str = None) -> str:
        """
        Generate hardware fingerprint string
        
        Format: MAC:xx:xx:xx:xx:xx:xx|CPU:xxxxxxxx|DISK:xxxxxxxx
        """
        # Use provided values or generate mock ones for testing
        if mac_address is None:
            mac_address = "00:1B:44:11:3A:B7"
        if cpu_id is None:
            cpu_id = "BFEBFBFF000906EA"
        if disk_serial is None:
            disk_serial = "WD-WCC4E5XK1234"
        
        fingerprint = f"MAC:{mac_address}|CPU:{cpu_id}|DISK:{disk_serial}"
        return fingerprint
    
    def validate_license_key_format(self, license_key: str) -> bool:
        """Validate license key format"""
        try:
            parts = license_key.split('-')
            if len(parts) != 5:
                return False
            
            company, product, date, time, random_part = parts
            
            # Check company abbreviation
            if not company.isalpha():
                return False
            
            # Check product abbreviation
            if not product.isalnum():
                return False
            
            # Check date format (YYYYMMDD)
            if len(date) != 8 or not date.isdigit():
                return False
            
            # Check time format (HHMMSS)
            if len(time) != 6 or not time.isdigit():
                return False
            
            # Check random part (5 characters)
            if len(random_part) != 5:
                return False
            
            return True
            
        except Exception:
            return False
    
    def extract_license_info(self, license_key: str) -> Dict[str, str]:
        """Extract information from license key"""
        if not self.validate_license_key_format(license_key):
            raise ValueError("Invalid license key format")
        
        parts = license_key.split('-')
        company, product, date, time, random_part = parts
        
        # Parse date
        date_obj = datetime.strptime(date, "%Y%m%d")
        
        return {
            "company": company,
            "product": product,
            "date": date_obj.strftime("%Y-%m-%d"),
            "time": f"{time[:2]}:{time[2:4]}:{time[4:6]}",
            "random_part": random_part
        }

# Global instance
license_generator = LicenseGenerator() 