#!/usr/bin/env python3
"""
Database Setup Script
Initialize the license management database
"""

import os
import sys
import pymysql
from colorama import init, Fore, Style

# Initialize colorama
init()

def setup_database():
    """Setup the database with schema and seed data"""
    print(f"{Fore.CYAN}🗄️ DATABASE SETUP{Style.RESET_ALL}")
    
    # Database configuration
    DB_CONFIG = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'password',  # Change this in production
        'charset': 'utf8mb4'
    }
    
    try:
        # Connect to MySQL server (without database)
        print(f"{Fore.YELLOW}🔄 Connecting to MySQL server...{Style.RESET_ALL}")
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset=DB_CONFIG['charset']
        )
        
        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            print(f"{Fore.YELLOW}🔄 Creating database 'zayona'...{Style.RESET_ALL}")
            cursor.execute("CREATE DATABASE IF NOT EXISTS zayona")
            print(f"{Fore.GREEN}✅ Database 'zayona' created/verified{Style.RESET_ALL}")
            
            # Use the database
            cursor.execute("USE zayona")
            
            # Read and execute schema file
            schema_file = os.path.join(os.path.dirname(__file__), '..', 'database.sql')
            if os.path.exists(schema_file):
                print(f"{Fore.YELLOW}🔄 Loading database schema...{Style.RESET_ALL}")
                with open(schema_file, 'r') as f:
                    schema_sql = f.read()
                
                # Split and execute SQL statements
                statements = schema_sql.split(';')
                for statement in statements:
                    statement = statement.strip()
                    if statement:
                        cursor.execute(statement)
                
                connection.commit()
                print(f"{Fore.GREEN}✅ Database schema loaded successfully{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Schema file not found: {schema_file}{Style.RESET_ALL}")
                return False
            
            # Read and execute seed data file
            seed_file = os.path.join(os.path.dirname(__file__), '..', 'db', 'seed_data.sql')
            if os.path.exists(seed_file):
                print(f"{Fore.YELLOW}🔄 Loading seed data...{Style.RESET_ALL}")
                with open(seed_file, 'r') as f:
                    seed_sql = f.read()
                
                # Split and execute SQL statements
                statements = seed_sql.split(';')
                for statement in statements:
                    statement = statement.strip()
                    if statement and not statement.startswith('--'):
                        try:
                            cursor.execute(statement)
                        except Exception as e:
                            # Ignore errors for duplicate data
                            if "Duplicate entry" not in str(e):
                                print(f"{Fore.YELLOW}⚠️ Warning: {e}{Style.RESET_ALL}")
                
                connection.commit()
                print(f"{Fore.GREEN}✅ Seed data loaded successfully{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ Seed data file not found: {seed_file}{Style.RESET_ALL}")
            
            # Verify setup
            print(f"{Fore.YELLOW}🔄 Verifying database setup...{Style.RESET_ALL}")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            expected_tables = [
                'users', 'products', 'licenses', 'license_logs', 
                'license_verifications', 'security_settings'
            ]
            
            found_tables = [table[0] for table in tables]
            missing_tables = [table for table in expected_tables if table not in found_tables]
            
            if missing_tables:
                print(f"{Fore.RED}❌ Missing tables: {missing_tables}{Style.RESET_ALL}")
                return False
            else:
                print(f"{Fore.GREEN}✅ All expected tables found{Style.RESET_ALL}")
            
            # Show table counts
            print(f"\n{Fore.CYAN}📊 DATABASE SUMMARY{Style.RESET_ALL}")
            for table in expected_tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{Fore.WHITE}{table}: {Fore.YELLOW}{count} records{Style.RESET_ALL}")
        
        connection.close()
        print(f"\n{Fore.GREEN}🎉 Database setup completed successfully!{Style.RESET_ALL}")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Database setup failed: {e}{Style.RESET_ALL}")
        return False

def main():
    """Main function"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}🗄️ ZAYONA LICENSE MANAGEMENT - DATABASE SETUP")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    success = setup_database()
    
    if success:
        print(f"\n{Fore.GREEN}✅ Setup completed successfully!")
        print(f"{Fore.WHITE}You can now start the API server and agent.{Style.RESET_ALL}")
        sys.exit(0)
    else:
        print(f"\n{Fore.RED}❌ Setup failed. Please check the errors above.{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main() 