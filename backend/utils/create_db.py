import pymysql
import os
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config

def create_database():
    uri = Config.SQLALCHEMY_DATABASE_URI
    # simple parsing
    # mysql+pymysql://root:password@host:port/dbname?params
    if not uri.startswith('mysql+pymysql://'):
        print("Not a MySQL URI")
        return

    try:
        auth_part = uri.split('://')[1]
        user_pass, host_db = auth_part.split('@')
        
        # Handle password with special characters if needed, but simple split for now
        # Assuming username does not contain ':'
        if ':' in user_pass:
            user = user_pass.split(':')[0]
            password = user_pass[len(user)+1:]
        else:
            user = user_pass
            password = ''

        host_port, db_params = host_db.split('/')
        if ':' in host_port:
            host, port = host_port.split(':')
            port = int(port)
        else:
            host = host_port
            port = 3306
        
        db_name = db_params.split('?')[0]
        
        print(f"Connecting to {host}:{port} as {user} to create DB '{db_name}'...")
        
        conn = pymysql.connect(host=host, user=user, password=password, port=port)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print(f"Database '{db_name}' created or already exists.")
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")
        print("Please ensure your Config.SQLALCHEMY_DATABASE_URI is correct.")

if __name__ == '__main__':
    create_database()
