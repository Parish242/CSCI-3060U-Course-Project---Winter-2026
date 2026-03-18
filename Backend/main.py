"""
backend/main.py

Banking System Back End - main entry point.

Reads the old master bank accounts file and a merged bank account transaction
file, applies every transaction to the account records (enforcing business
constraints), then writes out:
  • a new master bank accounts file (balances, plans, and transaction counts updated)
  • a new current bank accounts file (for tomorrow's Front End sessions)

Usage:
    python main.py [merged_transactions] [current_accounts] [master_accounts]

All three file-path arguments are optional; reasonable defaults relative to
the repository root are used when they are not supplied.

Input files:
    merged_transactions  - concatenation of one or more Front End transaction
                           files, ended with an end-of-session (00) record.
    current_accounts     - current bank accounts file written by the previous
                           Back End run (used as a fallback if no master exists).
    master_accounts      - master bank accounts file written by the previous
                           Back End run (authoritative source for balances,
                           plans, and transaction counts).

Output files:
    master_accounts      - updated master file (overwrites the input).
    current_accounts     - updated current accounts file for the Front End.
"""

import sys
import os
from lists import AccountsList, TransactionsList


def parse_arguments() -> tuple[str, str, str]:
    """
    Parse command-line arguments and return the three file paths.

    Returns:
        Tuple of (transactions_file, current_file, master_file).
    """
    args     = sys.argv[1:]
    base_dir = os.path.join(os.path.dirname(__file__), "..")
    transactions_file = args[0] if len(args) >= 1 else os.path.join(base_dir, "merged_transactions.txt")
    current_file      = args[1] if len(args) >= 2 else os.path.join(base_dir, "current_accounts.txt")
    master_file       = args[2] if len(args) >= 3 else os.path.join(base_dir, "master_accounts.txt")
    return transactions_file, current_file, master_file


def main() -> None:
    """
    Main Back End processing loop.

    1. Load account records from the master (and current) accounts files.
    2. Load all transactions from the merged transaction file.
    3. Apply each transaction in order via AccountsList.perform_transaction().
    4. Write the updated accounts to the new master and current account files.
    """
    transactions_file, current_file, master_file = parse_arguments()

    # Load bank accounts from the current and master accounts files.
    accounts_list = AccountsList(current_file=current_file, master_file=master_file)
    accounts_list.read_old_bank_accounts()
    accounts_list.read_old_master_accounts()

    # Load the merged transaction file.
    transaction_records = TransactionsList(transactions_file)
    transaction_records.read_merged_transaction_file()

    # Apply every transaction in order; constraint errors are printed to the terminal.
    for transaction in transaction_records.get_iterator():
        accounts_list.perform_transaction(transaction)

    # Write the updated accounts to both output files.
    accounts_list.write_new_master_accounts()
    accounts_list.write_new_current_accounts()


if __name__ == "__main__":
    main()

