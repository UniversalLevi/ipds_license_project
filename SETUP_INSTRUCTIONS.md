# ZAYONA License Management System - Setup Instructions

## 🚀 Quick Start Guide

This project has been streamlined with single scripts for both client and agent sides. Follow these instructions to get everything running quickly.

## 📋 Prerequisites

### On Kali Linux (Agent Server):
- Python 3.7+
- MySQL/MariaDB server
- Internet connection for package installation

### On Ubuntu Server (Client):
- Python 3.7+
- Internet connection for package installation

## 🔧 Setup Instructions

### Step 1: Agent Server Setup (Kali Linux)

1. **Navigate to the agent directory:**
   ```bash
   cd agent
   ```

2. **Run the agent server script:**
   ```bash
   python run_server.py
   ```

   This script will automatically:
   - ✅ Install all Python dependencies
   - ✅ Create configuration files
   - ✅ Set up the database
   - ✅ Generate RSA keys
   - ✅ Start the API server

3. **Verify the server is running:**
   - Open browser: `http://YOUR_KALI_IP:8000`
   - API docs: `http://YOUR_KALI_IP:8000/docs`
   - Health check: `http://YOUR_KALI_IP:8000/health`

### Step 2: Client Setup (Ubuntu Server)

1. **Navigate to the client directory:**
   ```bash
   cd client
   ```

2. **Run the client script:**
   ```bash
   python run_client.py
   ```

   This script will automatically:
   - ✅ Install all Python dependencies
   - ✅ Create configuration files
   - ✅ Prompt for agent server URL
   - ✅ Test connection to agent server
   - ✅ Start the web interface

3. **Enter the agent server details:**
   - When prompted, enter the IP address of your Kali Linux machine
   - Format: `192.168.1.100:8000` (replace with your actual IP)

4. **Access the web interface:**
   - Open browser: `http://YOUR_UBUNTU_IP:5000`
   - The interface will automatically open in your default browser

## 🌐 Using the System

### Web Interface Features:

1. **Home Page:**
   - Shows system status
   - Displays API connection status
   - Quick access to all features

2. **Generate License:**
   - Enter customer details
   - Select product information
   - Generate new licenses
   - Automatic hardware fingerprinting

3. **Verify License:**
   - Verify existing licenses
   - Check license status
   - View detailed information

4. **License Details:**
   - Complete license information
   - Customer details
   - Product information
   - System information

## 🔗 Network Configuration

### Firewall Settings:

**On Kali Linux (Agent Server):**
```bash
# Allow port 8000
sudo ufw allow 8000
# Or for iptables:
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
```

**On Ubuntu Server (Client):**
```bash
# Allow port 5000
sudo ufw allow 5000
# Or for iptables:
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
```

### Finding IP Addresses:

**On Kali Linux:**
```bash
ip addr show
# or
hostname -I
```

**On Ubuntu Server:**
```bash
ip addr show
# or
hostname -I
```

## 🛠️ Troubleshooting

### Common Issues:

1. **"Connection refused" error:**
   - Check if agent server is running
   - Verify IP address and port
   - Check firewall settings
   - Ensure both machines are on the same network

2. **"Module not found" errors:**
   - Run the setup scripts again
   - Check Python version (should be 3.7+)
   - Install missing packages manually if needed

3. **Database connection errors:**
   - Ensure MySQL/MariaDB is running
   - Check database credentials in `.env` file
   - Verify database exists

4. **Permission errors:**
   - Run with appropriate permissions
   - Check file ownership
   - Ensure write permissions in directories

### Manual Database Setup (if needed):

```bash
# On Kali Linux
sudo mysql -u root -p
CREATE DATABASE zayona;
CREATE USER 'zayona_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON zayona.* TO 'zayona_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## 📁 File Structure

```
project/
├── agent/
│   ├── run_server.py          # 🚀 Single script to run agent server
│   ├── api/                   # API server code
│   ├── database.sql           # Database schema
│   ├── scripts/               # Database setup scripts
│   └── rsa/                   # RSA key generation
└── client/
    ├── run_client.py          # 🚀 Single script to run client
    ├── web_interface.py       # Web interface
    ├── agent/                 # Client agent code
    └── templates/             # Web templates (auto-generated)
```

## 🔐 Security Notes

1. **Change default passwords** in the `.env` files
2. **Use HTTPS** in production environments
3. **Restrict network access** to trusted IPs
4. **Regular backups** of license data
5. **Monitor logs** for suspicious activity

## 📞 Support

If you encounter any issues:

1. Check the logs in the respective directories
2. Verify network connectivity between machines
3. Ensure all prerequisites are met
4. Check firewall and security settings

## 🎯 Quick Commands

**Start Agent Server:**
```bash
cd agent && python run_server.py
```

**Start Client:**
```bash
cd client && python run_client.py
```

**Check Server Status:**
```bash
curl http://KALI_IP:8000/health
```

**Access Web Interface:**
```bash
# Open in browser
http://UBUNTU_IP:5000
```

---

## ✅ Verification Checklist

- [ ] Agent server running on Kali Linux (port 8000)
- [ ] Client web interface running on Ubuntu (port 5000)
- [ ] Network connectivity between machines
- [ ] Database properly configured
- [ ] RSA keys generated
- [ ] Web interface accessible
- [ ] License generation working
- [ ] License verification working

Once all items are checked, your ZAYONA License Management System is ready for use! 🎉 