from flask import Flask, render_template, jsonify, request
import sqlite3
from datetime import datetime, timedelta
import json
import pandas as pd  # Import Pandas library


import configuration

app = Flask(__name__)


@app.route("/data")
def get_data_json():
    minutes = int(request.args.get("minutes", 60))

    cutoff_time = datetime.now() - timedelta(minutes=minutes + 1)

    _, cpu_per_user_df, mem_per_user_df = configuration.get_data(
        configuration.local_database_path, minutes, safety_period=minutes
    )

    # Resample while preserving maxima
    max_points = 361
    if (int(max(minutes / max_points, 1))) > 1:
        print(f"Resampling to: {(int(max(minutes/max_points,1)))} minute intervals")
        cpu_per_user_df = cpu_per_user_df.resample(
            f"{int(max(minutes/max_points,1))}T"
        ).max()
        mem_per_user_df = mem_per_user_df.resample(
            f"{int(max(minutes/max_points,1))}T"
        ).max()

    cpu_per_user_df = cpu_per_user_df[cpu_per_user_df.index >= cutoff_time]
    mem_per_user_df = mem_per_user_df[mem_per_user_df.index >= cutoff_time]

    timestamps = (
        cpu_per_user_df.index.astype(int) // 10**9
    ).tolist()  # Convert nanoseconds to seconds

    total_usage = (cpu_per_user_df.T.sum()).tolist()

    cpu_users = [col for col in cpu_per_user_df.columns]
    mem_users = [col for col in mem_per_user_df.columns]

    assert cpu_users == mem_users

    cpu_data = [cpu_per_user_df[col].tolist() for col in cpu_per_user_df.columns]
    mem_data = [
        (mem_per_user_df[col] / (1024**3)).tolist() for col in mem_per_user_df.columns
    ]

    cpu_data[0] = total_usage

    # Pass the split data to the template
    data = {
        "users_with_home_folders": cpu_users,
        "timestamps": timestamps,
        "cpu_data": cpu_data,
        "mem_data": mem_data,
    }

    return jsonify(data)


# Define a route to render the HTML page
@app.route("/")
def index():
    return render_template(
        "index.html",
        hostname=configuration.machine_id,
        cpu_cores=configuration.physical_cores,
        total_system_memory=configuration.total_system_memory,
    )


if __name__ == "__main__":
    app.run()
