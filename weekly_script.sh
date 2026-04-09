#!/bin/bash
set -euo pipefail  

# Set the repo root to be where the script is being run for the sake of pathing
repo_root="$(cd "$(dirname "$0")" && pwd)" 

# Continue from the previous files if any
CURRENT_FILE="$repo_root/current_accounts.txt"  
MASTER_FILE="$repo_root/master_accounts.txt"  

# New folders to store the days
mkdir -p "$repo_root/runs"  

for day in 1 2 3 4 5 6 7; do
    # Folder for each day
    DAY_DIR="$repo_root/runs/day$(printf '%02d' "$day")"

    # Call the daily script with the info for the day number, current accounts and master accounts files
    "$repo_root/daily_script.sh" "$DAY_DIR" "$CURRENT_FILE" "$MASTER_FILE"  
    
    # Update the files
    CURRENT_FILE="$DAY_DIR/current_accounts.txt"  
    MASTER_FILE="$DAY_DIR/master_accounts.txt"  
done
