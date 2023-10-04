import os
import subprocess
from datetime import datetime
import  os, sys

# Construct the absolute path to config.py
config_path = os.path.join('/var/usagedb')

# Ensure that config_path is in sys.path
sys.path.insert(0, config_path)

# Import configuration variables from config.py
from configuration import durations


# Define the absolute path to your data_plotting.py script
data_plotting_script = "/var/usagedb/data_plotting.py"

# Define the output directory for the plots
output_directory = "/var/usagedb/plots/"

# Define the mapping of human-readable duration names to minutes

# Define a consistent prefix for the filenames
filename_prefix = "usage_plot_"

# Get the current date and time
current_datetime = datetime.now()

# Create a function to generate plots for a given duration
def generate_plots(duration_name, duration_minutes):
    output_filename = f"{filename_prefix}{duration_name}.png"
    output_path = os.path.join(output_directory, output_filename)
    
    # Run the data_plotting.py script with the specified duration and output path
    subprocess.run([
        "/usr/bin/python3",
        data_plotting_script,
        "--database", "/var/usagedb/usage_data.db",
        "--duration", str(duration_minutes),
        "--output", output_path
    ])

    print(f"Generated {output_filename} at {current_datetime}")

# Loop through the list of durations and generate plots
for iduration, (duration_name, duration_minutes) in enumerate(durations.items()):
    generate_plots(f"{iduration+1}_{duration_name}", duration_minutes)
