"""
API client for communicating with the license server
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from agent.config import config

logger = logging.getLogger(__name__)

class LicenseAPIClient:
    """Client for communicating with the license API server"""
    
    def __init__(self, base_url: str = None, timeout: int = None):
        """Initialize API client"""
        self.base_url = base_url or config.API_BASE_URL
        self.timeout = timeout or config.API_TIMEOUT
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ZAYONA-License-Agent/1.0.0'
        })
    
    def set_base_url(self, url: str):
        """Set the base URL for API requests"""
        self.base_url = url
        logger.info(f"API base URL set to: {url}")
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Check if request was successful
            response.raise_for_status()
            
            # Parse JSON response
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"API request timeout: {url}")
            raise Exception("API request timed out")
        except requests.exceptions.ConnectionError:
            logger.error(f"API connection error: {url}")
            raise Exception("Could not connect to license server")
        except requests.exceptions.HTTPError as e:
            logger.error(f"API HTTP error: {e.response.status_code} - {e.response.text}")
            try:
                error_data = e.response.json()
                raise Exception(error_data.get('detail', f"HTTP {e.response.status_code}"))
            except:
                raise Exception(f"HTTP {e.response.status_code}: {e.response.text}")
        except Exception as e:
            logger.error(f"API request failed: {e}")
            raise Exception(f"API request failed: {e}")
    
    def generate_license(self, 
                        username: str,
                        password: str,
                        product_id: str,
                        customer_name: str,
                        email: str,
                        hardware_fingerprint: str = None) -> Dict[str, Any]:
        """Generate a new license"""
        data = {
            'username': username,
            'password': password,
            'product_id': product_id,
            'customer_name': customer_name,
            'email': email
        }
        
        if hardware_fingerprint:
            data['hardware_fingerprint'] = hardware_fingerprint
        
        logger.info(f"Generating license for user: {username}, product: {product_id}")
        
        response = self._make_request('POST', '/api/v1/generate-license', data)
        
        logger.info(f"License generated successfully for user: {username}")
        return response
    
    def verify_license(self, license_key: str, hardware_fingerprint: str) -> Dict[str, Any]:
        """Verify an existing license"""
        data = {
            'license_key': license_key,
            'hardware_fingerprint': hardware_fingerprint
        }
        
        logger.info(f"Verifying license: {license_key}")
        
        response = self._make_request('POST', '/api/v1/verify-license', data)
        
        logger.info(f"License verification successful: {license_key}")
        return response
    
    def get_license_info(self, license_key: str) -> Dict[str, Any]:
        """Get license information"""
        logger.info(f"Getting license info: {license_key}")
        
        response = self._make_request('GET', f'/api/v1/licenses/{license_key}')
        
        logger.info(f"License info retrieved: {license_key}")
        return response
    
    def health_check(self) -> Dict[str, Any]:
        """Check API server health"""
        logger.info("Checking API server health")
        
        response = self._make_request('GET', '/health')
        
        logger.info("API server health check successful")
        return response
    
    def test_connection(self) -> bool:
        """Test connection to API server"""
        try:
            self.health_check()
            return True
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False

# Global instance
api_client = LicenseAPIClient() 