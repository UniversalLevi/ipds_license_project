"""
Cryptographic utilities for license signing and verification
"""

import json
import hashlib
import base64
from datetime import datetime
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

class LicenseCrypto:
    """License cryptography utilities"""
    
    def __init__(self, private_key_path=None, public_key_path=None):
        """Initialize with key paths"""
        self.private_key_path = private_key_path
        self.public_key_path = public_key_path
        self._private_key = None
        self._public_key = None
    
    def load_private_key(self, key_path=None):
        """Load private key from PEM file"""
        if key_path is None:
            key_path = self.private_key_path
            
        try:
            with open(key_path, 'rb') as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None,
                    backend=default_backend()
                )
            self._private_key = private_key
            return private_key
        except Exception as e:
            raise Exception(f"Failed to load private key: {e}")
    
    def load_public_key(self, key_path=None):
        """Load public key from PEM file"""
        if key_path is None:
            key_path = self.public_key_path
            
        try:
            with open(key_path, 'rb') as key_file:
                public_key = serialization.load_pem_public_key(
                    key_file.read(),
                    backend=default_backend()
                )
            self._public_key = public_key
            return public_key
        except Exception as e:
            raise Exception(f"Failed to load public key: {e}")
    
    def sign_license(self, license_data):
        """Sign license data with private key"""
        if self._private_key is None:
            self.load_private_key()
        
        # Create a copy of license data without signature
        data_to_sign = license_data.copy()
        if 'signature' in data_to_sign:
            del data_to_sign['signature']
        
        # Convert to JSON string and encode
        json_string = json.dumps(data_to_sign, sort_keys=True, separators=(',', ':'))
        data_bytes = json_string.encode('utf-8')
        
        # Create hash of the data
        data_hash = hashlib.sha256(data_bytes).digest()
        
        # Sign the hash
        signature = self._private_key.sign(
            data_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Return base64 encoded signature
        return base64.b64encode(signature).decode('utf-8')
    
    def verify_signature(self, license_data, signature):
        """Verify license signature with public key"""
        if self._public_key is None:
            self.load_public_key()
        
        try:
            # Create a copy of license data without signature
            data_to_verify = license_data.copy()
            if 'signature' in data_to_verify:
                del data_to_verify['signature']
            
            # Convert to JSON string and encode
            json_string = json.dumps(data_to_verify, sort_keys=True, separators=(',', ':'))
            data_bytes = json_string.encode('utf-8')
            
            # Create hash of the data
            data_hash = hashlib.sha256(data_bytes).digest()
            
            # Decode signature
            signature_bytes = base64.b64decode(signature.encode('utf-8'))
            
            # Verify signature
            self._public_key.verify(
                signature_bytes,
                data_hash,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except InvalidSignature:
            return False
        except Exception as e:
            raise Exception(f"Signature verification failed: {e}")
    
    def generate_license_hash(self, license_data):
        """Generate a hash of license data for uniqueness checking"""
        # Create a copy without signature
        data_to_hash = license_data.copy()
        if 'signature' in data_to_hash:
            del data_to_hash['signature']
        
        # Convert to JSON string
        json_string = json.dumps(data_to_hash, sort_keys=True, separators=(',', ':'))
        
        # Generate SHA256 hash
        return hashlib.sha256(json_string.encode('utf-8')).hexdigest()

# Global instance
license_crypto = LicenseCrypto() 