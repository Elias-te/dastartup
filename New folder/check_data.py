import sqlite3
import os

# Path to your database
db_path = os.path.join('instance', 'das_leads.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # SQL query to see your leads
    cursor.execute("SELECT * FROM lead")
    rows = cursor.fetchall()
    
    if rows:
        print(f"✅ Success! Found {len(rows)} leads in DAS database:")
        for row in rows:
            print(f"ID: {row[0]} | Name: {row[1]} | Service: {row[4]}")
    else:
        print("📁 Database exists, but it is currently EMPTY.")
    
    conn.close()
else:
    print("❌ Database file not found!")