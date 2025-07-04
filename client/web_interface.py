#!/usr/bin/env python3
"""
ZAYONA License Management Client Web Interface
Web-based interface for license management
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
import threading
import webbrowser
import time

# Add agent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent'))

from agent.config import config
from agent.utils.hardware_fingerprint import hardware_fingerprint
from agent.utils.api_client import api_client
from agent.utils.license_saver import license_saver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'zayona-license-web-interface-secret-key'
CORS(app)

# Global variables
api_base_url = config.API_BASE_URL
license_saver_instance = license_saver
hardware_fingerprint_instance = hardware_fingerprint

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate_license():
    """Generate license page"""
    if request.method == 'POST':
        try:
            # Get form data
            username = request.form.get('username')
            password = request.form.get('password')
            product_id = request.form.get('product_id')
            customer_name = request.form.get('customer_name')
            email = request.form.get('email')
            
            # Validate required fields
            if not all([username, password, product_id, customer_name, email]):
                flash('All fields are required', 'error')
                return redirect(url_for('generate_license'))
            
            # Generate hardware fingerprint
            hw_fingerprint = hardware_fingerprint_instance.generate_fingerprint()
            
            # Call API to generate license
            response = api_client.generate_license(
                username=username,
                password=password,
                product_id=product_id,
                customer_name=customer_name,
                email=email,
                hardware_fingerprint=hw_fingerprint
            )
            
            if response.get('success'):
                license_data = response['license']
                
                # Save license to file
                if license_saver_instance.save_license(license_data):
                    flash('License generated and saved successfully!', 'success')
                    return redirect(url_for('view_license', license_key=license_data['license_key']))
                else:
                    flash('License generated but failed to save locally', 'warning')
                    return redirect(url_for('view_license', license_key=license_data['license_key']))
            else:
                flash(f'License generation failed: {response.get("message", "Unknown error")}', 'error')
                return redirect(url_for('generate_license'))
                
        except Exception as e:
            logger.error(f"License generation error: {e}")
            flash(f'Error generating license: {str(e)}', 'error')
            return redirect(url_for('generate_license'))
    
    return render_template('generate.html')

@app.route('/verify')
def verify_license():
    """Verify license page"""
    try:
        # Check if license file exists
        if not license_saver_instance.license_exists():
            flash('No license file found', 'error')
            return redirect(url_for('index'))
        
        # Load license from file
        license_data = license_saver_instance.load_license()
        if not license_data:
            flash('Failed to load license file', 'error')
            return redirect(url_for('index'))
        
        license_key = license_data.get('license_key')
        if not license_key:
            flash('Invalid license file - missing license key', 'error')
            return redirect(url_for('index'))
        
        # Generate hardware fingerprint
        hw_fingerprint = hardware_fingerprint_instance.generate_fingerprint()
        
        # Verify license via API
        response = api_client.verify_license(license_key, hw_fingerprint)
        
        if response.get('success'):
            flash('License verification successful!', 'success')
            return redirect(url_for('view_license', license_key=license_key))
        else:
            flash(f'License verification failed: {response.get("message", "Unknown error")}', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"License verification error: {e}")
        flash(f'Error verifying license: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/license/<license_key>')
def view_license(license_key):
    """View license details"""
    try:
        # Try to load from file first
        if license_saver_instance.license_exists():
            license_data = license_saver_instance.load_license()
            if license_data and license_data.get('license_key') == license_key:
                return render_template('license.html', license=license_data)
        
        # If not in file, try to get from API
        response = api_client.get_license_info(license_key)
        if response.get('success'):
            return render_template('license.html', license=response['license_info'])
        else:
            flash('License not found', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"Error viewing license: {e}")
        flash(f'Error viewing license: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/status')
def api_status():
    """Check API connection status"""
    try:
        response = requests.get(f"{api_base_url}/health", timeout=5)
        if response.status_code == 200:
            return jsonify({'status': 'connected', 'data': response.json()})
        else:
            return jsonify({'status': 'error', 'message': f'API returned status {response.status_code}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/hardware-fingerprint')
def get_hardware_fingerprint():
    """Get hardware fingerprint"""
    try:
        fingerprint = hardware_fingerprint_instance.generate_fingerprint()
        return jsonify({'fingerprint': fingerprint})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_templates():
    """Create HTML templates"""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Base template
    base_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}ZAYONA License Management{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .card { border: none; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        .btn-primary { background: linear-gradient(45deg, #667eea, #764ba2); border: none; }
        .navbar-brand { font-weight: bold; }
        .alert { border-radius: 10px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-shield-alt"></i> ZAYONA License Management
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/"><i class="fas fa-home"></i> Home</a>
                <a class="nav-link" href="/generate"><i class="fas fa-plus"></i> Generate License</a>
                <a class="nav-link" href="/verify"><i class="fas fa-check"></i> Verify License</a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>"""
    
    # Index template
    index_template = """{% extends "base.html" %}

{% block title %}Home - ZAYONA License Management{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card">
            <div class="card-body text-center p-5">
                <h1 class="card-title mb-4">
                    <i class="fas fa-shield-alt text-primary"></i>
                    Welcome to ZAYONA License Management
                </h1>
                <p class="card-text lead mb-4">
                    Secure license generation and verification system
                </p>
                
                <div class="row mt-5">
                    <div class="col-md-6">
                        <div class="card h-100">
                            <div class="card-body text-center">
                                <i class="fas fa-plus-circle fa-3x text-success mb-3"></i>
                                <h5 class="card-title">Generate License</h5>
                                <p class="card-text">Create a new license for your software</p>
                                <a href="/generate" class="btn btn-success">
                                    <i class="fas fa-plus"></i> Generate License
                                </a>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card h-100">
                            <div class="card-body text-center">
                                <i class="fas fa-check-circle fa-3x text-info mb-3"></i>
                                <h5 class="card-title">Verify License</h5>
                                <p class="card-text">Verify an existing license</p>
                                <a href="/verify" class="btn btn-info">
                                    <i class="fas fa-check"></i> Verify License
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mt-4">
                    <div id="api-status" class="alert alert-info">
                        <i class="fas fa-spinner fa-spin"></i> Checking API connection...
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
function checkApiStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            const statusDiv = document.getElementById('api-status');
            if (data.status === 'connected') {
                statusDiv.className = 'alert alert-success';
                statusDiv.innerHTML = '<i class="fas fa-check-circle"></i> API Server Connected';
            } else {
                statusDiv.className = 'alert alert-danger';
                statusDiv.innerHTML = '<i class="fas fa-times-circle"></i> API Server Disconnected';
            }
        })
        .catch(error => {
            const statusDiv = document.getElementById('api-status');
            statusDiv.className = 'alert alert-danger';
            statusDiv.innerHTML = '<i class="fas fa-times-circle"></i> API Server Unreachable';
        });
}

// Check status on page load
checkApiStatus();

// Check status every 30 seconds
setInterval(checkApiStatus, 30000);
</script>
{% endblock %}"""
    
    # Generate template
    generate_template = """{% extends "base.html" %}

{% block title %}Generate License - ZAYONA License Management{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h3 class="card-title mb-0">
                    <i class="fas fa-plus-circle text-success"></i> Generate New License
                </h3>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="username" class="form-label">Username *</label>
                            <input type="text" class="form-control" id="username" name="username" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="password" class="form-label">Password *</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="product_id" class="form-label">Product ID *</label>
                            <input type="text" class="form-control" id="product_id" name="product_id" 
                                   placeholder="e.g., ZAYONA-PRO-9988" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="customer_name" class="form-label">Customer Name *</label>
                            <input type="text" class="form-control" id="customer_name" name="customer_name" required>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="email" class="form-label">Email Address *</label>
                        <input type="email" class="form-control" id="email" name="email" required>
                    </div>
                    
                    <div class="d-grid">
                        <button type="submit" class="btn btn-success btn-lg">
                            <i class="fas fa-plus"></i> Generate License
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""
    
    # License template
    license_template = """{% extends "base.html" %}

{% block title %}License Details - ZAYONA License Management{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-10">
        <div class="card">
            <div class="card-header">
                <h3 class="card-title mb-0">
                    <i class="fas fa-key text-primary"></i> License Details
                </h3>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <h5>Customer Information</h5>
                        <table class="table table-borderless">
                            <tr>
                                <td><strong>Customer Name:</strong></td>
                                <td>{{ license.customer_name or 'N/A' }}</td>
                            </tr>
                            <tr>
                                <td><strong>Username:</strong></td>
                                <td>{{ license.username or 'N/A' }}</td>
                            </tr>
                            <tr>
                                <td><strong>Email:</strong></td>
                                <td>{{ license.email or 'N/A' }}</td>
                            </tr>
                        </table>
                    </div>
                    <div class="col-md-6">
                        <h5>Product Information</h5>
                        <table class="table table-borderless">
                            <tr>
                                <td><strong>Product Name:</strong></td>
                                <td>{{ license.product_name or 'N/A' }}</td>
                            </tr>
                            <tr>
                                <td><strong>Product ID:</strong></td>
                                <td>{{ license.product_id or 'N/A' }}</td>
                            </tr>
                            <tr>
                                <td><strong>License Type:</strong></td>
                                <td><span class="badge bg-primary">{{ license.license_type or 'N/A' }}</span></td>
                            </tr>
                        </table>
                    </div>
                </div>
                
                <hr>
                
                <div class="row">
                    <div class="col-md-6">
                        <h5>License Information</h5>
                        <table class="table table-borderless">
                            <tr>
                                <td><strong>License Key:</strong></td>
                                <td>
                                    <code class="bg-light p-2 rounded">{{ license.license_key or 'N/A' }}</code>
                                </td>
                            </tr>
                            <tr>
                                <td><strong>Status:</strong></td>
                                <td>
                                    {% if license.status == 'ACTIVE' %}
                                        <span class="badge bg-success">Active</span>
                                    {% elif license.status == 'EXPIRED' %}
                                        <span class="badge bg-danger">Expired</span>
                                    {% else %}
                                        <span class="badge bg-warning">{{ license.status or 'Unknown' }}</span>
                                    {% endif %}
                                </td>
                            </tr>
                            <tr>
                                <td><strong>Start Date:</strong></td>
                                <td>{{ license.start_date or 'N/A' }}</td>
                            </tr>
                            <tr>
                                <td><strong>Valid Until:</strong></td>
                                <td>{{ license.valid_till or 'N/A' }}</td>
                            </tr>
                        </table>
                    </div>
                    <div class="col-md-6">
                        <h5>System Information</h5>
                        <table class="table table-borderless">
                            <tr>
                                <td><strong>Hardware Fingerprint:</strong></td>
                                <td>
                                    <small class="text-muted">{{ license.hardware_fingerprint or 'N/A' }}</small>
                                </td>
                            </tr>
                            <tr>
                                <td><strong>Created At:</strong></td>
                                <td>{{ license.created_at or 'N/A' }}</td>
                            </tr>
                            <tr>
                                <td><strong>Last Verified:</strong></td>
                                <td>{{ license.last_verified or 'N/A' }}</td>
                            </tr>
                        </table>
                    </div>
                </div>
                
                <div class="text-center mt-4">
                    <a href="/" class="btn btn-primary">
                        <i class="fas fa-home"></i> Back to Home
                    </a>
                    <a href="/verify" class="btn btn-info">
                        <i class="fas fa-check"></i> Verify License
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""
    
    # Write templates
    templates = {
        'base.html': base_template,
        'index.html': index_template,
        'generate.html': generate_template,
        'license.html': license_template
    }
    
    for filename, content in templates.items():
        filepath = os.path.join(templates_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)

def open_browser():
    """Open browser after a short delay"""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

def main():
    """Main function"""
    print("🌐 ZAYONA LICENSE MANAGEMENT WEB INTERFACE")
    print("="*50)
    
    # Create templates
    print("📝 Creating web templates...")
    create_templates()
    print("✅ Templates created")
    
    # Update API base URL if provided as argument
    if len(sys.argv) > 1:
        global api_base_url
        api_base_url = sys.argv[1]
        print(f"🔗 Using API server: {api_base_url}")
    
    # Start browser in background
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print("🚀 Starting web interface...")
    print("📋 Web interface will be available at: http://localhost:5000")
    print("🔗 Make sure the agent server is running and accessible")
    print("\n" + "="*60)
    print("Press Ctrl+C to stop the web interface")
    print("="*60 + "\n")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Web interface stopped by user")
    except Exception as e:
        print(f"❌ Web interface error: {e}")

if __name__ == "__main__":
    main() 