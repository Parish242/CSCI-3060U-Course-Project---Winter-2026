from enum import Enum
from datetime import datetime

class SessionType(Enum):
    STANDARD = 1
    ADMIN = 2

class TransactionLog:
    def __init__(self):
        self.transactions: list[dict] = []

    def addTransaction(self, transaction: dict):
        self.transactions.append(transaction)

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
    
class AccountsList:
    accounts: tuple = ()

    @classmethod
    def getAccounts(cls):
        return AccountsList.accounts
    
    @classmethod
    def fetchAccounts(cls):
        # This should be recieved from the backend.
        # For now, a placeholder should be written for testing purposes.
        pass