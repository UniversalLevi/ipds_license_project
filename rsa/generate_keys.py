#!/usr/bin/env python3
"""
RSA Key Generation Script
Generates private and public keys for license signing and verification
"""

import os
import sys
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

def generate_rsa_keys(key_size=2048):
    """Generate RSA key pair"""
    print("🔐 Generating RSA key pair...")
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    
    # Get public key
    public_key = private_key.public_key()
    
    return private_key, public_key

def save_private_key(private_key, filename="private_key.pem"):
    """Save private key to PEM file"""
    print(f"💾 Saving private key to {filename}...")
    
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    with open(filename, 'wb') as f:
        f.write(pem)
    
    print(f"✅ Private key saved to {filename}")
    print("⚠️  WARNING: Keep this file secure and never share it!")

def save_public_key(public_key, filename="public_key.pem"):
    """Save public key to PEM file"""
    print(f"💾 Saving public key to {filename}...")
    
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    with open(filename, 'wb') as f:
        f.write(pem)
    
    print(f"✅ Public key saved to {filename}")

def main():
    """Main function"""
    print("=" * 50)
    print("🔐 RSA KEY GENERATOR FOR LICENSE SYSTEM")
    print("=" * 50)
    
    try:
        # Create rsa directory if it doesn't exist
        os.makedirs('rsa', exist_ok=True)
        
        # Change to rsa directory
        os.chdir('rsa')
        
        # Generate keys
        private_key, public_key = generate_rsa_keys()
        
        # Save keys
        save_private_key(private_key, "private_key.pem")
        save_public_key(public_key, "public_key.pem")
        
        print("\n" + "=" * 50)
        print("🎉 RSA KEYS GENERATED SUCCESSFULLY!")
        print("=" * 50)
        print("📁 Files created:")
        print("   - private_key.pem (KEEP SECURE!)")
        print("   - public_key.pem (can be shared)")
        print("\n⚠️  IMPORTANT:")
        print("   - Never commit private_key.pem to version control")
        print("   - Keep private_key.pem secure on the server only")
        print("   - public_key.pem can be distributed with the agent")
        
    except Exception as e:
        print(f"❌ Error generating keys: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 