# Database Setup Guide

## 🗄️ Manual Database Setup

### Step 1: Install MySQL/MariaDB

**On Kali Linux:**
```bash
sudo apt update
sudo apt install mysql-server
# or for MariaDB:
sudo apt install mariadb-server
```

### Step 2: Start MySQL Service
```bash
sudo systemctl start mysql
sudo systemctl enable mysql
```

### Step 3: Secure MySQL Installation
```bash
sudo mysql_secure_installation
```
- Set root password (or leave empty if you want no password)
- Remove anonymous users
- Disallow root login remotely
- Remove test database
- Reload privilege tables

### Step 4: Create Database and User

**Option A: Using MySQL Command Line**
```bash
sudo mysql -u root -p
```

Then run these SQL commands:
```sql
CREATE DATABASE zayona;
CREATE USER 'zayona_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON zayona.* TO 'zayona_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**Option B: Using Root (No Password)**
```bash
sudo mysql
```

Then run:
```sql
CREATE DATABASE zayona;
EXIT;
```

### Step 5: Update .env File

Edit the `.env` file in the agent directory:

**For Option A (with user):**
```
DATABASE_USER=zayona_user
DATABASE_PASSWORD=your_password
```

**For Option B (root, no password):**
```
DATABASE_USER=root
DATABASE_PASSWORD=
```

### Step 6: Import Database Schema

```bash
cd agent
mysql -u root -p zayona < database.sql
# or if using a specific user:
mysql -u zayona_user -p zayona < database.sql
```

### Step 7: Test Database Connection

```bash
cd agent
python3 -c "
import pymysql
try:
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',  # or your user
        password='',  # or your password
        database='zayona'
    )
    print('✅ Database connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

## 🔧 Troubleshooting

### Common Issues:

1. **"Access denied for user 'root'@'localhost'"**
   - Check if MySQL is running: `sudo systemctl status mysql`
   - Verify password in .env file
   - Try connecting manually: `sudo mysql -u root -p`

2. **"Can't connect to MySQL server"**
   - Start MySQL service: `sudo systemctl start mysql`
   - Check if port 3306 is open: `netstat -tlnp | grep 3306`

3. **"Unknown database 'zayona'"**
   - Create the database: `CREATE DATABASE zayona;`
   - Import schema: `mysql -u root -p zayona < database.sql`

4. **Permission denied errors**
   - Check file permissions: `ls -la database.sql`
   - Use sudo if needed: `sudo mysql -u root -p zayona < database.sql`

## 📋 Quick Setup Commands

```bash
# Install MySQL
sudo apt update && sudo apt install mysql-server

# Start and enable MySQL
sudo systemctl start mysql && sudo systemctl enable mysql

# Secure installation
sudo mysql_secure_installation

# Create database (as root)
sudo mysql -e "CREATE DATABASE zayona;"

# Import schema
cd agent && sudo mysql zayona < database.sql

# Test connection
python3 -c "import pymysql; conn = pymysql.connect(host='localhost', user='root', database='zayona'); print('Success!'); conn.close()"
```

## 🔐 Security Notes

1. **Change default passwords** in production
2. **Use dedicated database user** instead of root
3. **Restrict database access** to localhost only
4. **Regular backups** of the database
5. **Monitor database logs** for suspicious activity 