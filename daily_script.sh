#!/bin/bash

FRONTEND_PATH="Frontend/main.py"
BACKEND_PATH="Backend/main.py"
MERGE_PATH="Backend/merge_transactions.py"

TRANSACTION_TYPES=("login" "logout" "withdrawal" "transfer" "paybill" "deposit" "create" "delete" "disable" "changeplan")
USERS=("John Doe" "Jane Smith" "Bob Johnson" "Alice Williams" "Charlie Brown")

python $FRONTEND_PATH &

for((i=0; i<=$(( RANDOM % 4 + 3 )); i++));
do
    (
        echo "${TRANSACTION_TYPES[0]}"
        echo "standard"
        echo "${USERS[$(( RANDOM % 5 ))]}"

        for((i=0; i<=$(( RANDOM % 7 + 3 )); i++));
        do
            # Placeholder (this is the part where the transactions should take place)
            echo "withdrawal"
            echo 5
            echo "$(( RANDOM % 50 + 1 ))"
        done

        echo "logout"
    ) | python "$FRONTEND_PATH"

    sleep 1
done

python "$MERGE_PATH"

sleep 1

python "$BACKEND_PATH"