from enum import Enum
from datetime import datetime
import os

"""
Simple enum to denote a session type. 
"""
class SessionType(Enum):
    STANDARD = 1
    ADMIN = 2

"""
Manages tracking, logging, and exporting transactions.
"""
class TransactionLog:
    def __init__(self):
        self.transactions: list[dict] = []

    """
    Logs new transaction dictionaries creating from transaction methods.

    Args:
        transaction: new transaction dictionary.
    """
    def addTransaction(self, transaction: dict):
        self.transactions.append(transaction)

    """
    Parses transactions into transaction file format.
    Attempts to write new transaction file.

    Returns:
        bool: If the transaction file was successfully written to.
    """
    def writeTransactionFile(self):
        fileContents = ""
        timeStamp = datetime.now().strftime("%m-%d-%Y %H-%M-%S")

        # Parse transactions to construct file text.
        for i in self.transactions:
            fileContents += f"{i['code']:>02} {i['accountName']:>20} {i['accountNumber']:>05} {i['money']:>08} {i['misc']:>02}\n"

        # Write to file
        try:
            with open(f"{timeStamp}.txt", "w") as file:
                file.write(fileContents)
        except:
            print("Error writing file.")
            return False
        finally:
            file.close()

        return True

"""
Manages storing, sending, and importing bank accounts list.
Written similar to a singleton.
"""
class AccountsList:
    accounts: list[dict] = []

    """
    Simple getter for accounts.
    """
    @classmethod
    def getAccounts(cls):
        return AccountsList.accounts
    
    """
    Parses accounts file and updates accounts to
    store newly created account dictionaries.
    """
    @classmethod
    def fetchAccounts(cls):
        # This should be recieved from the backend.
        cls.accounts = []
        file_path = os.path.join(os.path.dirname(__file__), "..", "current_accounts.txt")
        if not os.path.exists(file_path):
            print("Warning: current_accounts.txt not found")
            return

        with open(file_path, "r") as f:
            for line in f:
                if line.startswith("00000 END_OF_FILE"):
                    continue
                acc_number = int(line[0:5])
                acc_name = line[6:26].rstrip()
                acc_status = line[27]
                acc_balance = float(line[29:37])
                cls.accounts.append({
                    'accountNumber': acc_number,
                    'accountName': acc_name,
                    'status': acc_status,
                    'balance': acc_balance
                })
