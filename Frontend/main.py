"""
CSCI 3060U Banking System - Front End
Main program for handling banking transactions through console interface.
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
