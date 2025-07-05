# Fix Guide for ZAYONA License Management System

## 🔧 Current Issues & Solutions

### Issue 1: Database Connection Error
**Problem:** `Database connection failed: (1045, "Access denied for user 'root'@'localhost' (using password: NO)")`

**Solution:**
1. **On Kali Linux (Agent Server):**
   ```bash
   cd agent
   python3 update_env.py
   ```
   This will create/update the `.env` file with the correct password `8888`.

2. **Restart the agent server:**
   ```bash
   ./start_agent.sh
   ```

### Issue 2: API Connection Error
**Problem:** Client can't connect to agent API

**Solution:**
1. **Test the connection from Ubuntu client:**
   ```bash
   cd client
   python3 test_connection.py
   ```

2. **If connection fails, check:**
   - Agent server is running on Kali
   - Database is accessible
   - Firewall allows port 8000
   - Network connectivity between machines

### Issue 3: Input Validation Issue
**Problem:** "This field is required. Please try again." when pressing Enter

**Solution:**
This is a minor UI issue. Just enter a valid choice (1-7) when prompted.

---

## 🚀 Quick Fix Steps

### Step 1: Fix Database Password (Kali Linux)
```bash
cd agent
python3 update_env.py
```

### Step 2: Restart Agent Server (Kali Linux)
```bash
./start_agent.sh
```

### Step 3: Test Connection (Ubuntu Client)
```bash
cd client
python3 test_connection.py
```

### Step 4: Run Client CLI (Ubuntu Client)
```bash
./start_client.sh
```

---

## 🔍 Verification Steps

### 1. Check Agent Server Status
On Kali Linux, you should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```
**No more database connection errors!**

### 2. Test Health Endpoint
From browser or curl:
```
http://10.10.199.65:8000/health
```
Should return:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "..."
}
```

### 3. Test Client Connection
From Ubuntu client:
```bash
python3 test_connection.py
```
Should show:
```
✅ Root endpoint accessible: 200
✅ Health check: 200
🎉 API connection successful!
```

---

## 🎯 Expected Results

After fixing:

1. **Agent Server (Kali):**
   - No database connection errors
   - Health endpoint returns 200 OK
   - All API endpoints working

2. **Client CLI (Ubuntu):**
   - Can connect to agent API
   - Can generate licenses
   - Can verify licenses
   - Can show license info

3. **Database:**
   - MySQL accessible with password '8888'
   - All tables exist and are accessible
   - Users and products data available

---

## 🛠️ Troubleshooting

### If Database Still Fails:
1. Check MySQL is running: `sudo systemctl status mysql`
2. Test MySQL login: `mysql -u root -p` (enter password: 8888)
3. Verify database exists: `USE zayona; SHOW TABLES;`

### If API Still Unreachable:
1. Check agent server is running
2. Check firewall: `sudo ufw status`
3. Test network: `ping 10.10.199.65`
4. Check port: `telnet 10.10.199.65 8000`

### If Client Still Fails:
1. Check dependencies: `pip install -r agent/requirements.txt`
2. Check .env file exists in client directory
3. Verify API URL is correct

---

## 📞 Support

If you still have issues:
1. Run the test script: `python3 test_connection.py`
2. Check agent server logs for errors
3. Verify database credentials
4. Test network connectivity between machines 