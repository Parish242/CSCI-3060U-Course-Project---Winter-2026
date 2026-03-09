"""
backend/lists.py

TBD - File comment again
"""

import os
from typing import List, Dict, Optional

class AccountsList:
# Container for accounts
    def __init__(self, current_file: Optional[str] = None, master_file: Optional[str] = None):
        base_dir = os.path.join(os.path.dirname(__file__), "..")
        self.current_file = current_file or os.path.join(base_dir, "current_accounts.txt")
        self.master_file  = master_file  or os.path.join(base_dir, "master_accounts.txt")
        self.current_accounts: List[Dict] = []
        self.master_accounts:  List[Dict] = []

    def read_old_bank_accounts(self, file_path: Optional[str] = None):
        path = file_path or self.current_file
        self.current_accounts = []
        if not os.path.exists(path):
            print("Warning: current accounts file not found:", path)
            return
        with open(path, "r") as fh:
            for line in fh:
                parts = line.strip().split()
                if len(parts) >= 4:
                    acc_num = parts[0]
                    name = " ".join(parts[1:-3])
                    status = parts[-3]
                    balance = float(parts[-2])
                    plan = parts[-1] if len(parts) >= 5 else "NP"
                    self.current_accounts.append({
                        'accountNumber': str(acc_num).zfill(5),
                        'accountName': name,
                        'status': status,
                        'balance': balance,
                        'plan': plan
                    })
                # TODO: handle broken lines with errors and check that I did this right

def read_old_master_accounts(self, file_path: Optional[str] = None):
    path = file_path or self.master_file
    self.master_accounts = []

    with open(path, "r") as f:
        for line in f:
            if line.strip() == "":
                continue

            account = {
                "accountNumber": line[0:5].strip(),
                "accountName": line[6:26].strip(),
                "status": line[27:28].strip(),
                "balance": float(line[29:39].strip()),
                "plan": line[40:42].strip()
            }

            self.master_accounts.append(account)


def write_new_current_accounts(self, file_path: Optional[str] = None):
    path = file_path or self.current_file

    with open(path, "w") as f:
        for acc in self.current_accounts:
            line = (
                f"{acc['accountNumber'].zfill(5)} "
                f"{acc['accountName']:<20} "
                f"{acc['status']} "
                f"{acc['balance']:010.2f} "
                f"{acc['plan']}\n"
            )
            f.write(line)


def write_new_master_accounts(self, file_path: Optional[str] = None):
    path = file_path or self.master_file

    with open(path, "w") as f:
        for acc in self.master_accounts:
            line = (
                f"{acc['accountNumber'].zfill(5)} "
                f"{acc['accountName']:<20} "
                f"{acc['status']} "
                f"{acc['balance']:010.2f} "
                f"{acc['plan']}\n"
            )
            f.write(line)

    def get_account_by_id(self, account_id: str) -> Optional[Dict]:
        key = str(account_id).zfill(5)
        for a in self.current_accounts:
            if a['accountNumber'] == key:
                return a
        return None


class TransactionsList:
# Reads merged transaction file into a list
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.transactions: List[Dict] = []

    def read_merged_transaction_file(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(self.file_path)
        with open(self.file_path, "r") as fh:
            for line in fh:
                if not line.strip() or line.startswith("00000 END_OF_FILE"):
                    continue
                parts = line.strip().split()
                if len(parts) >= 4:
                    self.transactions.append({
                        'code': parts[0],
                        'accountName': " ".join(parts[1:-3]),
                        'accountNumber': str(parts[-3]).zfill(5),
                        'money': float(parts[-2]),
                        'misc': parts[-1] if len(parts) >= 5 else ""
                    })
                # TODO: handle broken lines with errors and check that I did this right

    def get_iterator(self):
        return iter(self.transactions)
