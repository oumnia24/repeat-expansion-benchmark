#!/bin/bash
# Helper function to log job submissions
# Usage: ./log_job.sh <script_name>

SCRIPT=$1
JOB_ID=$(sbatch "$SCRIPT" | awk '{print $4}')
DATE=$(date +"%Y-%m-%d %H:%M:%S")

# Ensure logs directory exists
mkdir -p logs

# Create job log if it doesn't exist
LOG_FILE="logs/job_history.csv"
if [ ! -f "$LOG_FILE" ]; then
    echo "job_id,script,date,description,status" > "$LOG_FILE"
fi

# Add entry
echo "${JOB_ID},${SCRIPT},${DATE},pending" >> "$LOG_FILE"

echo "Submitted job ${JOB_ID} for ${SCRIPT}"