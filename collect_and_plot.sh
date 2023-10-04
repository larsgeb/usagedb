#!/bin/bash

# Execute data collection script
/usr/bin/python3 /var/usagedb/data_collection.py

# Uncomment the following lines if you would like to generate plots periodically
# Generate usage plots for 10 minutes
#/usr/bin/python3 /var/usagedb/data_plotting.py --duration 10 --output /var/usagedb/plots/usage_plot_1_10_minutes.png

# Generate usage plots for 1 hour
#/usr/bin/python3 /var/usagedb/data_plotting.py --duration 60 --output /var/usagedb/plots/usage_plot_2_1_hour.png

# Generate usage plots for 6 hours
#/usr/bin/python3 /var/usagedb/data_plotting.py --duration 360 --output /var/usagedb/plots/usage_plot_3_6_hours.png
