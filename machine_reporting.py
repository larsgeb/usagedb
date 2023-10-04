
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import psutil , os, sys

# Construct the absolute path to config.py
config_path = os.path.join('/var/usagedb')

# Ensure that config_path is in sys.path
sys.path.insert(0, config_path)

# Import configuration variables from config.py
from configuration import excluded_users, mongo_uri, machine_id, database_id, certificate_path


# Create a MongoDB client with X.509 authentication
client = MongoClient(mongo_uri, tls=True, tlsCertificateKeyFile=certificate_path, server_api=ServerApi('1'))

# Select the database and collection
db = client[database_id]

# Create a collection for machine information
machine_collection = db['machines']

# Get CPU and memory information
cpu_info = {
    "cpu_count": psutil.cpu_count(logical=False),  # Physical CPU count
    "cpu_threads": psutil.cpu_count(logical=True),  # Logical CPU count (including hyperthreads)
}
virtual_memory = psutil.virtual_memory()
memory_info = {
    "total_memory": virtual_memory.total,  # Total RAM in bytes
}

# Insert hardware information into machine information documents
machine_query = {"machine_id": machine_id}  # Replace with your machine ID
machine_collection.update_one(machine_query, {"$set": {"cpu_info": cpu_info, "memory_info": memory_info}}, upsert=True)
