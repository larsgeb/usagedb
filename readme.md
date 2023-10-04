# Usage Data Web Application

This web application allows you to visualize and analyze system usage data collected from various users on a single machine. It utilizes Python, Flask, SQLite, and Chart.js to display CPU and memory usage data in a user-friendly format.

## Installation

1. Clone the repository to your local machine:

```bash
git clone https://github.com/larsgeb/usage-data-web-app.git
```

Install the required Python packages using pip:
```bash
Copy code
pip install -r requirements.txt
```

## Configuration

The usage data is stored in an SQLite database located by default at `/var/usagedb/usage_data.db`. Make sure this database exists:
```bash
sqlite3 usage_data.db < create_schema.sql
```
You can set up a CRONTAB job to periodically log system usage data to the SQLite database. 
```bash
* * * * * root /var/usagedb/collect_and_plot.sh
```

Customize the configuration.py file:

- `machine_id`: The identifier for your machine (e.g., "swppc").
- `physical_cores`: The number of physical CPU cores on your machine.
- `total_system_memory`: The total system memory in GB on your machine.
- `excluded_users`: A list of users to exclude from data analysis (e.g., ['syslog', 'cups-pk-helper']).
- `local_database_path`: The path to the local SQLite database.

## Usage

Start the Flask application in a tmux shell:
```bash
export FLASK_APP=app.py 
flask run --port 4999 --debug
```

Open a web browser and navigate to http://localhost:4999 to access the usage data dashboard.


## Technologies Used

This usage data dashboard is built using a combination of technologies to collect, process, and display system usage data effectively. The core technologies and libraries used include:

- **Python**: The primary programming language used for developing the web application and data collection scripts.

- **Flask**: A lightweight and powerful web framework for Python used to build the web application.

- **SQLite**: A self-contained, serverless, and zero-configuration database engine used to store and retrieve system usage data.

- **Chart.js**: A popular JavaScript library for creating interactive and visually appealing charts and graphs. It is used to visualize CPU and memory usage data.

- **Pandas**: A Python library for data manipulation and analysis. It is used to process and structure the collected data.

- **CRONTAB**: A time-based job scheduler in Unix-like operating systems used to automate the collection of system usage data at regular intervals.

- **psutil**: A Python cross-platform library that provides an interface for retrieving information on system utilization (CPU, memory, disks, network, sensors) and running processes.

- **subprocess**: A Python module used for spawning new processes, connecting to their input/output/error pipes, and obtaining their return codes.


These technologies work together to provide a user-friendly interface for monitoring and analyzing system resource utilization over time.
