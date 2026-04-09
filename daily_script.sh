#!/bin/bash

FRONTEND_PATH="Frontend/main.py"
BACKEND_PATH="Backend/main.py"
MERGE_PATH="Backend/merge_transactions.py"

TRANSACTION_TYPES=("login" "logout" "withdrawal" "transfer" "paybill" "deposit" "create" "delete" "disable" "changeplan")
USERS=("John Doe" "Jane Smith" "Bob Johnson" "Alice Williams" "Charlie Brown")

for((i=0; i<=$(( RANDOM % 4 + 3 )); i++));
do
    user_index=$(( RANDOM % 5 ))
    user_account="$(( user_index + 1 ))"

    (
        echo "${TRANSACTION_TYPES[0]}"
        echo "standard"
        echo "${USERS[$user_index]}"

        for((i=0; i<=$(( RANDOM % 7 + 3 )); i++));
        do
            # Placeholder (this is the part where the transactions should take place)
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
    ) | python "$FRONTEND_PATH"

    sleep 1
done

python "$MERGE_PATH"

sleep 1

python "$BACKEND_PATH"