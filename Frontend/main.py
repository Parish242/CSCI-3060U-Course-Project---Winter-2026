"""
CSCI 3060U Banking System - Front End
======================================
Overview:
    This is the Front End of the Banking System. It accepts user commands
    from the console and processes banking transactions (login, logout,
    withdrawal, deposit, transfer, paybill, create, delete, disable, and
    changeplan). Validated transactions are recorded in a transaction log
    that is written to a file on logout for back-end processing.

Input files:
    - current_accounts.txt: The current bank accounts file, located one
      directory above this file (../current_accounts.txt). It is read at
      login to load all active accounts into memory.
      Format per line: NNNNN NAME(20) STATUS BALANCE(8)
        e.g. 00001ALICE               A01000.00

Output files:
    - <timestamp>.txt: A transaction log file written to the working
      directory on logout. Each line represents one transaction in the
      format: CODE NAME(20) NNNNN AMOUNT(8) MISC
        e.g. 04 ALICE                00001 00020.00 00

How to run:
    From the Frontend/ directory, run:
        python main.py [current_accounts_file]
    If no accounts file argument is provided, the program defaults to
    ../current_accounts.txt. Input can be piped from a file:
        python main.py < input.txt
"""

from utils import SessionType, TransactionLog, AccountsList
from transactions import *

class Session:
    """
    Manages the current banking session including user permissions, 
    account information, transaction logging, and transaction limits.
    """

    def __init__(self):
        """Initialize a new session with default values."""
        self.permissions: SessionType = None
        self.accountName: str = ""
        self.log: TransactionLog = TransactionLog()
        self.accounts: AccountsList = None
        self.transactionLimits: dict = {
            'withdrawal': 0.0,
            'transfer': 0.0,
            'paybill': 0.0
        }

    def performTransaction(self, transactionOutput: str) -> None:
        """
        Main transaction handler that routes user commands to appropriate functions.

        Args:
            transactionOutput: The transaction command entered by the user
        """
        transaction = transactionOutput.strip().lower()

        # Transaction routing table for cleaner dispatch
        transactions = {
            'login': login,
            'logout': logout,
            'withdrawal': withdrawal,
            'transfer': transfer,
            'paybill': paybill,
            'deposit': deposit,
            'create': create,
            'delete': delete,
            'disable': disable,
            'changeplan': changeplan
        }

        # Execute transaction if valid
        if transaction in transactions:
            transactions[transaction](self)
        else:
            print(f"ERROR: Unknown transaction '{transactionOutput}'")

def main():
    """
    Main entry point for the Banking System Front End.
    Initializes session and processes transactions until program termination.
    """
    print("Welcome to the Banking System")
    print("-" * 40)

    # Initialize current session
    current_session: Session = None

    # Main transaction loop
    while True:
        try:
            # Get transaction input
            transaction_input = input("Enter transaction: ").strip()

            if not transaction_input:
                continue

            # Initialize session if first transaction
            if current_session is None:
                current_session = Session()

            # Process the transaction
            current_session.performTransaction(transaction_input)

        except KeyboardInterrupt:
            print("\n\nSystem shutting down...")
            break
        except EOFError:
            print("\nEnd of input stream")
            break
        except Exception as e:
            print(f"ERROR: Unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
