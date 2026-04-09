#!/bin/bash

# For errors
set -euo pipefail

# Set the repo root to be where the script is being run for the sake of pathing
repo_root="$(cd "$(dirname "$0")" && pwd)" 

FRONTEND_PATH="$repo_root/Frontend/main.py"
BACKEND_PATH="$repo_root/Backend/main.py"
MERGE_PATH="$repo_root/Backend/merge_transactions.py"

# Creates files and folders to store the data
DAY_DIR="${1:-$repo_root/runs/day01}"  
CURRENT_INPUT="${2:-$repo_root/current_accounts.txt}"
MASTER_INPUT="${3:-$repo_root/master_accounts.txt}"

# Pathing for those folders and setting them as absoulte paths
mkdir -p "$DAY_DIR"
DAY_DIR_ABS="$(cd "$DAY_DIR" && pwd)"

# All the files for the simulated days
WORK_CURRENT="$DAY_DIR_ABS/current_accounts.txt"
WORK_MASTER="$DAY_DIR_ABS/master_accounts.txt"
MERGED_FILE="$DAY_DIR_ABS/merged_transactions.txt"

# Copy the prior days data
cp "$CURRENT_INPUT" "$WORK_CURRENT"
cp "$MASTER_INPUT" "$WORK_MASTER"

TRANSACTION_TYPES=("login" "logout" "withdrawal" "transfer" "paybill" "deposit" "create" "delete" "disable" "changeplan")
USERS=("John Doe" "Jane Smith" "Bob Johnson" "Alice Williams" "Charlie Brown")

# Changed the number of loops to make more consistant
num_sessions=$(( RANDOM % 4 + 3 ))  

for ((i=0; i<num_sessions; i++)); do
    user_index=$(( RANDOM % 5 ))
    user_account="$(( user_index + 1 ))"

    (
        echo "login"
        echo "standard"
        echo "${USERS[$user_index]}"

        num_transactions=$(( RANDOM % 7 + 3 ))  

        # Changed it to J rather than I so we don't re-use
        for ((j=0; j<num_transactions; j++)); do  
        
            case $(( RANDOM % 4 )) in
                0)
                    echo "withdrawal"
                    echo "$user_account"
                    echo "$(( RANDOM % 500 + 1 ))"
                    ;;
                1)
                    from_acc="$user_account"
                    to_acc="$(( RANDOM % 5 + 1 ))"
                    while [ "$to_acc" -eq "$from_acc" ]; do
                        to_acc="$(( RANDOM % 5 + 1 ))"
                    done

                    echo "transfer"
                    echo "$from_acc"
                    echo "$to_acc"
                    echo "$(( RANDOM % 500 + 1 ))"
                    ;;
                2)
                    COMPANY_CODES=("EC" "CQ" "FI")
                    echo "paybill"
                    echo "$user_account"
                    echo "${COMPANY_CODES[$(( RANDOM % 3 ))]}"
                    echo "$(( RANDOM % 1000 + 1 ))"
                    ;;
                *)
                    echo "deposit"
                    echo "$user_account"
                    echo "$(( RANDOM % 1000 + 1 ))"
                    ;;
            esac
        done

        echo "logout"
    ) | (cd "$DAY_DIR_ABS" && python "$FRONTEND_PATH" "$WORK_CURRENT")  
# Changed to save each output as a file in a folder
done

# Merge and pass the files
python "$MERGE_PATH" "$DAY_DIR_ABS" "$MERGED_FILE"  
python "$BACKEND_PATH" "$MERGED_FILE" "$WORK_CURRENT" "$WORK_MASTER"  
