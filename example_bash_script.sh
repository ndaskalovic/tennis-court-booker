#!/bin/bash
# This script is an example of how to execute the booking script in a conda environment
# Useful for Cron jobs
# Replace the paths with your own
# Move to directory where the script is located
cd /path/to/your/directory/
# Activate conda environment and run the script
eval "$(/path/to/conda shell.bash hook)"
conda activate env-name
/path/to/conda/bin/python /path/to/make_bookings.py
conda deactivate
