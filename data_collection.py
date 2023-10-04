import psutil
import datetime
import subprocess
import argparse
import sqlite3
import pwd, sys, os
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Construct the absolute path to config.py
config_path = os.path.join('/var/usagedb')

# Ensure that config_path is in sys.path
sys.path.insert(0, config_path)

# Import configuration variables from config.py
from configuration import excluded_users, local_database_path

def get_cpu_usage_for_user(username):
    # Get CPU usage for the specified user
    top_cmd = ["top", "-b", "-n", "1", "-u", username]
    top_result = subprocess.run(top_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if top_result.returncode != 0:
        return f"Error running 'top' command: {top_result.stderr}\n{top_cmd}"

    # Process the 'top' command output to calculate CPU usage
    lines = top_result.stdout.strip().split('\n')

    cpu_usage = 0.0
    for line in lines[7:]:
        fields = line.split()
        if len(fields) >= 9:
            cpu_usage += float(fields[8])

    return cpu_usage

def collect_data(database_path):
    # Get a list of all user accounts on the system with home folders in /home
    user_accounts = [user.pw_name for user in pwd.getpwall() if user.pw_dir.startswith('/home') or user.pw_name == 'root']

    # Filter out the excluded users
    user_accounts = [user for user in user_accounts if user not in excluded_users]

    timestamp = datetime.datetime.now()

    try:
        # Collect system usage data for the entire system
        cpu_percent_total = psutil.cpu_percent()
        memory_usage_bytes_total = psutil.virtual_memory().used

        # Store total system data in the local SQLite database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usage (user, timestamp, cpu_percent, memory_usage_bytes) VALUES (?, ?, ?, ?)",
                       ('total', timestamp, cpu_percent_total, memory_usage_bytes_total))
        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Error collecting total system data: {str(e)}")

    user_total_memory_usage = {}

    for process in psutil.process_iter(['pid', 'username', "memory_full_info", "memory_info"]):
        try:
            process_info = process.info
            username = process_info['username']
            memory_info = process_info['memory_full_info']

            # Calculate USS by summing up private memory mappings
            
            try:
                uss = memory_info.uss
            except AttributeError:
                uss = 0 
                
            if username not in user_total_memory_usage:
                user_total_memory_usage[username] = 0

            user_total_memory_usage[username] += uss
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  # Handle exceptions if a process cannot be accessed

    # Create a list to store all data for insertion into the local SQLite database and MongoDB 
    sqlite_insert_data = []


    for username in user_accounts:
        try:
            cpu_percent = get_cpu_usage_for_user(username)
            try:
                memory_usage_bytes = user_total_memory_usage[username]
            except KeyError:
                memory_usage_bytes = 0.0

            # Append data to the list for insertion into SQLite database
            sqlite_insert_data.append((username, timestamp, cpu_percent, memory_usage_bytes))



        except Exception as e:
            print(f"Error collecting data for user {username}: {str(e)}")

    try:
        # Open a connection to the SQLite database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Use a single executemany operation to insert all data into the SQLite database
        cursor.executemany(
            "INSERT INTO usage (user, timestamp, cpu_percent, memory_usage_bytes) VALUES (?, ?, ?, ?)",
            sqlite_insert_data
        )

        # Commit the transaction and close the connection
        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Error inserting data into SQLite database: {str(e)}")

if __name__ == "__main__":
    collect_data(local_database_path)
