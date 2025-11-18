import sqlite3
import os

DB_PATH = "usage_log.db"

print(f"Checking database at: {os.path.abspath(DB_PATH)}")
print(f"Database exists: {os.path.exists(DB_PATH)}")

if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM usage_log")
        count = cursor.fetchone()[0]
        print(f"Records in usage_log: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM usage_log ORDER BY timestamp DESC LIMIT 5")
            recent_data = cursor.fetchall()
            print("Recent records:")
            for record in recent_data:
                print(f"  {record}")
        else:
            print("No records found")
            
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
    
    conn.close()
else:
    print("Database file not found!")
