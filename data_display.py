import sqlite3
import  os, sys

# Construct the absolute path to config.py
config_path = os.path.join('/var/usagedb')

# Ensure that config_path is in sys.path
sys.path.insert(0, config_path)

# Import configuration variables from config.py
from configuration import local_database_path


def format_bytes(bytes):
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 * 1024:
        return f"{bytes / 1024:.2f} KB"
    elif bytes < 1024 * 1024 * 1024:
        return f"{bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{bytes / (1024 * 1024 * 1024):.2f} GB"

def display_data():
    try:
        # Connect to the database
        conn = sqlite3.connect(local_database_path)
        cursor = conn.cursor()

        # Retrieve and display the 5 most recent rows for all users
        cursor.execute("SELECT * FROM usage ORDER BY timestamp DESC LIMIT 35;")
        data = cursor.fetchall()

        for row in data:
            id, user, timestamp, cpu_percent, memory_usage_bytes = row
            memory_usage_readable = format_bytes(memory_usage_bytes)
            
            print(f"User: {user}")
            print(f"Timestamp: {timestamp}")
            print(f"CPU Percent: {cpu_percent}%")
            print(f"Memory Usage: {memory_usage_readable}")
            print("-" * 30)

        conn.close()
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    display_data()
