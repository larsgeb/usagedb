# config.py
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

# Machine identifier
machine_id = "swppc"

# System specifications
physical_cores = 18  # Number of physical CPU cores
total_system_memory = 128  # Total system memory in GB

# Define the users to exclude
excluded_users = ['syslog', 'cups-pk-helper']

# Local database path
local_database_path = "/var/usagedb/usage_data.db"


def connect_to_database(database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    return conn, cursor

def retrieve_users_from_database(cursor):
    cursor.execute("SELECT DISTINCT user FROM usage;")
    return [row[0] for row in cursor.fetchall()]


def get_data(database_path, duration_minutes, safety_period=60):
    conn, cursor = connect_to_database(database_path)
    users_with_home_folders = retrieve_users_from_database(cursor)
    conn.close()

    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=duration_minutes + safety_period)

    conn, cursor = connect_to_database(database_path)

    # SQL query for CPU Usage
    cpu_query = """
    SELECT user, timestamp, cpu_percent
    FROM usage
    WHERE timestamp >= ? AND timestamp <= ?
      AND user IN (
        SELECT user
        FROM usage
        WHERE timestamp >= ? AND timestamp <= ?
        GROUP BY user
        HAVING MAX(memory_usage_bytes) > 0 OR MAX(cpu_percent) > 0
      );
    """

    # Execute the CPU query
    cursor.execute(cpu_query, (start_time, end_time, start_time, end_time))
    cpu_data = cursor.fetchall()

    # SQL query for Memory Usage
    mem_query = """
    SELECT user, timestamp, memory_usage_bytes
    FROM usage
    WHERE timestamp >= ? AND timestamp <= ?
      AND user IN (
        SELECT user
        FROM usage
        WHERE timestamp >= ? AND timestamp <= ?
        GROUP BY user
        HAVING MAX(memory_usage_bytes) > 0 OR MAX(cpu_percent) > 0
      );
    """

    # Execute the Memory query
    cursor.execute(mem_query, (start_time, end_time, start_time, end_time))
    mem_data = cursor.fetchall()

    conn.close()

    cpu_per_user = {}
    mem_per_user = {}

    for row in cpu_data:
        user, timestamp, cpu_percent = row
        if user not in cpu_per_user:
            cpu_per_user[user] = {}
        cpu_per_user[user][timestamp] = cpu_percent

    for row in mem_data:
        user, timestamp, memory_percent = row
        if user not in mem_per_user:
            mem_per_user[user] = {}
        mem_per_user[user][timestamp] = memory_percent

    cpu_per_user_df = pd.DataFrame(cpu_per_user)
    cpu_per_user_df.index = pd.to_datetime(cpu_per_user_df.index)
    cpu_per_user_df = cpu_per_user_df.groupby(cpu_per_user_df.index).sum()

    mem_per_user_df = pd.DataFrame(mem_per_user)
    mem_per_user_df.index = pd.to_datetime(mem_per_user_df.index)
    mem_per_user_df = mem_per_user_df.groupby(mem_per_user_df.index).sum()

    return users_with_home_folders, cpu_per_user_df, mem_per_user_df