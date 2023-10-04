import os
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
from datetime import datetime, timedelta
import sqlite3
import  sys

# Construct the absolute path to config.py
config_path = os.path.join('/var/usagedb')

# Ensure that config_path is in sys.path
sys.path.insert(0, config_path)

# Import configuration variables from config.py
from configuration import physical_cores, total_system_memory, get_data

# Define configuration parameters
smooth_data = False
home_dir = "/home"


def plot_cpu_usage(dataframe, users_with_home_folders, colors, linestyles, markers, smooth_data, history_minutes, smoothing_time_minutes):
    _, (ax, _) = plt.subplots(2, 1, figsize=(13, 10))
    
    if smooth_data:
        dataframe = dataframe.rolling(
            smoothing_time_minutes * 4, win_type="gaussian", center=True
        ).mean(std=smoothing_time_minutes).resample(
            timedelta(minutes=smoothing_time_minutes)
        ).mean()

    xlims = [dataframe.index.min(), dataframe.index.max()]

    # Adjust x-axis limits
    xlims[0] = xlims[1] - timedelta(minutes=history_minutes)
    ax.set_xlim(xlims)

    ax.plot(
        xlims,
        [physical_cores * 100, physical_cores * 100],
        "--k",
        alpha=0.5,
        label="Number of cores",
    )
    ax.plot(
        xlims,
        [physical_cores * 100 * 2, physical_cores * 100 * 2],
        "-k",
        alpha=0.5,
        label="Max hyperthreads",
    )

    ax.fill_between(
        xlims,
        [physical_cores * 100, physical_cores * 100],
        [physical_cores * 100 * 2, physical_cores * 100 * 2],
        color="#CCCCFF",
        alpha=0.1,
        hatch="x",
        label="Throttling",
    )

    legend = ax.legend(ncol=3, loc=2, edgecolor="black")

    for user in users_with_home_folders:
        if user == "root":
            continue
        if user =="swppc-admin":
            continue
        
        if user == "total":
            total_usage = (
                dataframe.T.sum()
            )
            total_usage.plot(
                ax=ax,
                alpha=0.25,
                linewidth=1.5,
                marker=markers[user],
                linestyle=linestyles[user],
                color=colors[user],
                x_compat=True,
                markersize=4,
                label="Total"
            )
            continue

        dataframe[user].plot(
            ax=ax,
            alpha=0.75,
            linewidth=2,
            marker=markers[user],
            linestyle=linestyles[user],
            color=colors[user],
            x_compat=True,
            markersize=4,
        )

    _, _ = ax.get_legend_handles_labels()
    legend = ax.legend(ncol=7, loc=2, bbox_to_anchor=(0.0, -0.35))
    legend.get_frame().set_alpha(None)

    ax.grid("on")
    ax.set_xlabel("Datetime")
    ax.set_ylabel("Core usage (%)")
    ax.set_title("CPU usage per user")
    xfmt = md.DateFormatter("%m-%d\n%H:%M:%S")
    ax.xaxis.set_major_formatter(xfmt)

    

def plot_memory_usage(dataframe, users_with_home_folders, colors, linestyles, markers, smooth_data, history_minutes, smoothing_time_minutes):
    ax = plt.subplot(212)

    if smooth_data:
        dataframe = dataframe.rolling(
            smoothing_time_minutes * 4, win_type="gaussian", center=True
        ).mean(std=smoothing_time_minutes).resample(
            timedelta(minutes=smoothing_time_minutes)
        ).mean()

    xlims = [dataframe.index.min(), dataframe.index.max()]

    # Adjust x-axis limits
    xlims[0] = xlims[1] - timedelta(minutes=history_minutes)
    ax.set_xlim(xlims)

    for user in users_with_home_folders:
        try:
            if user == "root" or user =="swppc-admin":
                continue
            if user == "total":
                alpha=0.25
            else:
                alpha=0.75


            dataframe[user].plot(
                ax=ax,
                alpha=alpha,
                linewidth=2,
                marker=markers[user],
                linestyle=linestyles[user],
                color=colors[user],
                x_compat=True,
                markersize=4,
            )
        except KeyError:
            pass

    ax.grid("on")
    ax.set_xlabel("Datetime")
    ax.set_ylabel("Memory usage")
    ax.set_title("Memory usage per user")
    y_ticks = (1024 ** 3) * 2.0 ** (np.arange(40))
    y_tick_labels = [f"{2 ** ival} GB" for ival, val in enumerate(y_ticks)]
    ax.set_yscale("log")
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_tick_labels)
    ax.set_ylim([1024 ** 3 / (2.0**2), total_system_memory * (1024 ** 3)])
    xfmt = md.DateFormatter("%m-%d\n%H:%M:%S")
    ax.xaxis.set_major_formatter(xfmt)



def main(database_path, duration_minutes, output_filename):
    
    users_with_home_folders, cpu_per_user_df, mem_per_user_df = get_data(database_path, duration_minutes)

    # Create lists of plotting styles based on the number of users
    num_users = len(users_with_home_folders)
    colors = plt.get_cmap("tab20")(np.linspace(0, 1, num_users))
    linestyles = ["-", "--", "-.", ":"] * ((num_users + 3) // 4)  
    markers = ["o", "s", "^", "v", "<", ">", "p", "*", "D", "H", "+", "x"] * ((num_users + 11) // 12) 

    # Create dictionaries for user-specific plotting properties
    _c = {}
    _l = {}
    _m = {}

    for iuser, user in enumerate(users_with_home_folders):
        _c[user] = colors[iuser]
        _l[user] = linestyles[iuser]
        _m[user] = markers[iuser]


    # Determine the smoothing time based on the desired maximum data points
    max_data_points = 100
    num_data_points = duration_minutes

    smoothing_time_minutes = int( duration_minutes / max_data_points)

    smooth_data = False
    if num_data_points > max_data_points:
        smooth_data = True

    plot_cpu_usage(cpu_per_user_df, users_with_home_folders, _c, _l, _m, smooth_data, duration_minutes, smoothing_time_minutes)
    plot_memory_usage(mem_per_user_df, users_with_home_folders, _c, _l, _m, smooth_data, duration_minutes, smoothing_time_minutes)
    plt.tight_layout()
    if output_filename:
        plt.savefig(output_filename, dpi=200)
    else:
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate usage plots for CPU and memory usage per user.")
    parser.add_argument("--database", default='/var/usagedb/usage_data.db', help="Path to the SQLite database.")
    parser.add_argument("--duration", type=int, default=5, help="Custom duration for the plot in minutes.")
    parser.add_argument("--output", help="Output filename for the generated plot.")
    args = parser.parse_args()

    main(args.database, args.duration, args.output)