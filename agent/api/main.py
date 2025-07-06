#!/usr/bin/env python3
"""
License Management API Server
FastAPI server for license verification and management
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pymysql
import bcrypt

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.config import config
from api.utils.crypto_utils import license_crypto
from api.utils.license_generator import license_generator
from api.utils.hardware_fingerprint import hardware_fingerprint

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

# Initialize FastAPI app
app = FastAPI(
    title=config.TITLE,
    description=config.DESCRIPTION,
    version=config.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db_connection():
    """Get database connection"""
    try:
        connection = pymysql.connect(
            host=config.DATABASE_HOST,
            port=config.DATABASE_PORT,
            user=config.DATABASE_USER,
            password=config.DATABASE_PASSWORD,
            database=config.DATABASE_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# Rate limiting - DISABLED FOR TESTING
# def check_rate_limit(license_id: int, db_connection) -> bool:
#     """Check if license has exceeded daily verification limit"""
#     try:
#         with db_connection.cursor() as cursor:
#             # Get current license info
#             cursor.execute(
#                 "SELECT verification_count_today, last_verification_reset, daily_verification_limit FROM licenses WHERE id = %s",
#                 (license_id,)
#             )
#             license_info = cursor.fetchone()
#             
#             if not license_info:
#                 return False
#             
#             # Check if it's a new day
#             today = datetime.now().date()
#             last_reset = license_info['last_verification_reset']
#             
#             if last_reset is None or last_reset.date() < today:
#                 # Reset counter for new day
#                 cursor.execute(
#                     "UPDATE licenses SET verification_count_today = 0, last_verification_reset = %s WHERE id = %s",
#                     (today, license_id)
#                 )
#                 db_connection.commit()
#                 return True
#             
#             # Check if limit exceeded
#             if license_info['verification_count_today'] >= license_info['daily_verification_limit']:
#                 return False
#             
#             # Increment counter
#             cursor.execute(
#                 "UPDATE licenses SET verification_count_today = verification_count_today + 1 WHERE id = %s",
#                 (license_id,)
#             )
#             db_connection.commit()
#             return True
#             
#     except Exception as e:
#         logger.error(f"Rate limit check failed: {e}")
#         return False

# Log license activity
def log_license_activity(license_id: int, status: str, source_ip: str, user_agent: str, 
                        hardware_fingerprint: str = None, verification_type: str = "ONLINE", 
                        error_message: str = None, db_connection = None):
    """Log license verification activity"""
    if db_connection is None:
        db_connection = get_db_connection()
    
    try:
        with db_connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO license_logs 
                   (license_id, status, source_ip, user_agent, hardware_fingerprint, verification_type, error_message)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (license_id, status, source_ip, user_agent, hardware_fingerprint, verification_type, error_message)
            )
            db_connection.commit()
    except Exception as e:
        logger.error(f"Failed to log license activity: {e}")

# Authentication
def verify_user_credentials(username: str, password: str, db_connection) -> Optional[Dict]:
    """Verify user credentials"""
    try:
        with db_connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, username, password_hash, email FROM users WHERE username = %s AND is_active = TRUE",
                (username,)
            )
            user = cursor.fetchone()
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return user
            return None
            
    except Exception as e:
        logger.error(f"User verification failed: {e}")
        return None

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ZAYONA License Management API",
        "version": config.VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db = get_db_connection()
        with db.cursor() as cursor:
            cursor.execute("SELECT 1")
        db.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy")

@app.post("/api/v1/generate-license")
async def generate_license(request: Request):
    """Generate a new license for a user"""
    try:
        # Get request data
        data = await request.json()
        
        # Validate required fields
        required_fields = ['username', 'password', 'product_id', 'customer_name', 'email']
        for field in required_fields:
            if field not in data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Get client IP and user agent
        client_ip = request.client.host
        user_agent = request.headers.get('user-agent', 'Unknown')
        
        # Connect to database
        db = get_db_connection()
        
        try:
            # Verify user credentials
            user = verify_user_credentials(data['username'], data['password'], db)
            if not user:
                log_license_activity(0, "REJECTED", client_ip, user_agent, error_message="Invalid credentials")
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Get product information
            with db.cursor() as cursor:
                cursor.execute(
                    "SELECT id, name, product_code FROM products WHERE product_code = %s",
                    (data['product_id'],)
                )
                product = cursor.fetchone()
                
                if not product:
                    log_license_activity(0, "REJECTED", client_ip, user_agent, error_message="Invalid product")
                    raise HTTPException(status_code=400, detail="Invalid product")
            
            # Check if user already has a license for this product
            with db.cursor() as cursor:
                cursor.execute(
                    "SELECT id FROM licenses WHERE user_id = %s AND product_id = %s AND is_revoked = FALSE",
                    (user['id'], product['id'])
                )
                existing_license = cursor.fetchone()
                
                if existing_license:
                    log_license_activity(existing_license['id'], "REJECTED", client_ip, user_agent, error_message="License already exists")
                    raise HTTPException(status_code=400, detail="License already exists for this user and product")
            
            # Get existing license keys for uniqueness check
            with db.cursor() as cursor:
                cursor.execute("SELECT license_key FROM licenses")
                existing_keys = [row['license_key'] for row in cursor.fetchall()]
            
            # Generate unique license key
            license_key = license_generator.generate_unique_license_key(
                product['product_code'], 
                user['username'], 
                existing_keys
            )
            
            # Get hardware fingerprint from request or generate one
            hw_fingerprint = data.get('hardware_fingerprint')
            if not hw_fingerprint:
                # Generate a mock fingerprint for testing
                hw_fingerprint = hardware_fingerprint.generate_fingerprint()
            
            # Create license data
            license_data = license_generator.format_license_json(
                customer_name=data['customer_name'],
                username=user['username'],
                product_name=product['name'],
                product_id=product['product_code'],
                license_key=license_key,
                email=data['email']
            )
            
            # Sign the license
            signature = license_crypto.sign_license(license_data)
            license_data['signature'] = signature
            
            # Save license to database
            with db.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO licenses 
                       (user_id, product_id, license_key, valid_till, hardware_fingerprint, max_installations, current_installations)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (
                        user['id'],
                        product['id'],
                        license_key,
                        license_data['expiry_date'],
                        hw_fingerprint,
                        1,  # max_installations
                        1   # current_installations
                    )
                )
                license_id = cursor.lastrowid
                db.commit()
            
            # Log successful license generation
            log_license_activity(license_id, "VALID", client_ip, user_agent, hw_fingerprint, "ONLINE")
            
            return {
                "success": True,
                "message": "License generated successfully",
                "license": license_data,
                "license_id": license_id
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"License generation failed: {e}")
        raise HTTPException(status_code=500, detail="License generation failed")

@app.post("/api/v1/verify-license")
async def verify_license(request: Request):
    """Verify an existing license"""
    try:
        # Get request data
        data = await request.json()
        
        # Validate required fields
        required_fields = ['license_key', 'hardware_fingerprint']
        for field in required_fields:
            if field not in data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Get client IP and user agent
        client_ip = request.client.host
        user_agent = request.headers.get('user-agent', 'Unknown')
        
        # Connect to database
        db = get_db_connection()
        
        try:
            # Get license information
            with db.cursor() as cursor:
                cursor.execute(
                    """SELECT l.*, u.username, p.name as product_name, p.product_code 
                       FROM licenses l 
                       JOIN users u ON l.user_id = u.id 
                       JOIN products p ON l.product_id = p.id 
                       WHERE l.license_key = %s""",
                    (data['license_key'],)
                )
                license_info = cursor.fetchone()
                
                if not license_info:
                    log_license_activity(0, "REJECTED", client_ip, user_agent, error_message="License not found")
                    raise HTTPException(status_code=404, detail="License not found")
            
            # Check if license is revoked
            if license_info['is_revoked']:
                log_license_activity(license_info['id'], "REVOKED", client_ip, user_agent, data['hardware_fingerprint'])
                raise HTTPException(status_code=403, detail="License has been revoked")
            
            # Check if license is expired
            if datetime.now() > license_info['valid_till']:
                log_license_activity(license_info['id'], "EXPIRED", client_ip, user_agent, data['hardware_fingerprint'])
                raise HTTPException(status_code=403, detail="License has expired")
            
            # Check rate limiting - DISABLED FOR TESTING
            # if not check_rate_limit(license_info['id'], db):
            #     log_license_activity(license_info['id'], "RATE_LIMITED", client_ip, user_agent, data['hardware_fingerprint'])
            #     raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            # Check hardware fingerprint
            stored_fingerprint = license_info['hardware_fingerprint']
            current_fingerprint = data['hardware_fingerprint']
            
            if stored_fingerprint != current_fingerprint:
                log_license_activity(license_info['id'], "SHARING_DETECTED", client_ip, user_agent, current_fingerprint)
                raise HTTPException(status_code=403, detail="Hardware fingerprint mismatch - potential license sharing")
            
            # Log successful verification
            log_license_activity(license_info['id'], "VALID", client_ip, user_agent, current_fingerprint, "ONLINE")
            
            return {
                "success": True,
                "message": "License verification successful",
                "license_info": {
                    "license_key": license_info['license_key'],
                    "username": license_info['username'],
                    "product_name": license_info['product_name'],
                    "product_code": license_info['product_code'],
                    "valid_till": license_info['valid_till'].isoformat(),
                    "status": "Active"
                }
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"License verification failed: {e}")
        raise HTTPException(status_code=500, detail="License verification failed")

@app.get("/api/v1/licenses/{license_key}")
async def get_license_info(license_key: str, request: Request):
    """Get license information"""
    try:
        # Get client IP and user agent
        client_ip = request.client.host
        user_agent = request.headers.get('user-agent', 'Unknown')
        
        # Connect to database
        db = get_db_connection()
        
        try:
            # Get license information
            with db.cursor() as cursor:
                cursor.execute(
                    """SELECT l.*, u.username, u.name as customer_name, p.name as product_name, p.product_code 
                       FROM licenses l 
                       JOIN users u ON l.user_id = u.id 
                       JOIN products p ON l.product_id = p.id 
                       WHERE l.license_key = %s""",
                    (license_key,)
                )
                license_info = cursor.fetchone()
                
                if not license_info:
                    raise HTTPException(status_code=404, detail="License not found")
            
            # Don't return sensitive information like hardware fingerprint
            safe_license_info = {
                "license_key": license_info['license_key'],
                "customer_name": license_info['customer_name'],
                "username": license_info['username'],
                "product_name": license_info['product_name'],
                "product_code": license_info['product_code'],
                "valid_till": license_info['valid_till'].isoformat(),
                "issued_at": license_info['issued_at'].isoformat(),
                "is_revoked": license_info['is_revoked'],
                "status": "Active" if not license_info['is_revoked'] and datetime.now() <= license_info['valid_till'] else "Inactive"
            }
            
            return {
                "success": True,
                "license": safe_license_info
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get license info failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get license information")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    ) 