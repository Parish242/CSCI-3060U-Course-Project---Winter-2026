"""
backend/main.py

TBD - DO FULL FILE COMMENT
"""
import sys
import os

from lists import AccountsList, TransactionsList
import transactions as transactions_backend

# Reads command line arguments for the transaction and account files
def parse_arguments():
    args = sys.argv[1:]
    transactions_file = args[0] if len(args) >= 1 else os.path.join("..", "merged_transactions.txt")
    current_file = args[1] if len(args) >= 2 else os.path.join("..", "current_accounts.txt")
    master_file = args[2] if len(args) >= 3 else os.path.join("..", "master_accounts.txt")
    return transactions_file, current_file, master_file

# Sets up the accounts and transactionns
def main():
    transactions_file, current_file, master_file = parse_arguments()
    accounts_list = AccountsList(current_file=current_file, master_file=master_file)
    accounts_list.read_old_bank_accounts()
    accounts_list.read_old_master_accounts()
    records = TransactionsList(transactions_file)
    records.read_merged_transaction_file()

    for record in records.get_iterator():
        code = record.get('code', '').zfill(2)
        account_name = record.get('accountName', '').strip()
        account_number = record.get('accountNumber', '').zfill(5)
        amount = float(record.get('money', 0.0))
        misc = record.get('misc', '')

        # Transaction types - TBD***********
        if code == '01':
            pass  # TODO: implement withdrawal
        elif code == '02':
            pass  # TODO: implement transfer
        elif code == '03':
            pass  # TODO: implement paybill
        elif code == '04':
            pass  # TODO: implement deposit
        elif code == '05':
            pass  # TODO: implement create account
        elif code == '06':
            pass  # TODO: implement delete account
        elif code == '07':
            pass  # TODO: implement disable account
        elif code == '08':
            pass  # TODO: implement change plan
        elif code == '09':
            pass  # TODO: implement login
        elif code == '10':
            pass  # TODO: implement logout
        else:
            pass  # TODO: handle unknown code

    # TODO: - Write updated accounts back after *******************
    # accounts_list.write_new_current_accounts()
    # accounts_list.write_new_master_accounts()

if __name__ == "__main__":
    main()
