"""
backend/lists.py

Account and transaction record containers for the Banking System Back End.

AccountsList loads account records from the current and master account files,
tracks all in-memory changes made by transaction handlers, and writes updated
records back out at the end of each Back End run.

TransactionsList loads the merged transaction file produced by the Front End
and exposes the records as an iterator for the main processing loop.

Current bank accounts file format (one record per line):
    NNNNN AAAAAAAAAAAAAAAAAAAA S PPPPPPPP
    NNNNN – 5-digit account number
    AAAAAAAAAAAAAAAAAAAA – account holder name (up to 20 chars)
    S     – status: A (active) or D (disabled)
    PPPPPPPP – balance (8 chars, 2 decimal places)
    (no payment-plan field in current accounts)

Master bank accounts file format adds a trailing two-character payment plan:
    NNNNN AAAAAAAAAAAAAAAAAAAA S PPPPPPPP TT

Merged transaction file format (one record per line):
    CC AAAAAAAAAAAAAAAAAAAA NNNNN PPPPPPPP MM
    CC    – 2-digit transaction code
    AAAAA… – account holder name (up to 20 chars)
    NNNNN – 5-digit account number
    PPPPP… – money amount (8 chars)
    MM    – miscellaneous field (2 chars, e.g. first 2 digits of FROM account)
"""

import os
from typing import List, Dict, Optional


class AccountsList:
    """Container for bank accounts loaded from the current and master account files."""

    def __init__(self, current_file: Optional[str] = None, master_file: Optional[str] = None):
        """
        Initialize file paths and empty account lists.

        Args:
            current_file: Path to the current accounts file. Defaults to
                          current_accounts.txt in the repository root.
            master_file:  Path to the master accounts file. Defaults to
                          master_accounts.txt in the repository root.
        """
        base_dir = os.path.join(os.path.dirname(__file__), "..")
        self.current_file = current_file or os.path.join(base_dir, "current_accounts.txt")
        self.master_file  = master_file  or os.path.join(base_dir, "master_accounts.txt")
        self.current_accounts: List[Dict] = []
        self.master_accounts:  List[Dict] = []

    def read_old_bank_accounts(self, file_path: Optional[str] = None):
        """
        Read the current bank accounts file into self.current_accounts.

        Expected record format:
            NNNNN AAAAAAAAAAAAAAAAAAAA S PPPPPPPP

        Parses each non-sentinel line into a dict with keys: accountNumber,
        accountName, status, balance, plan.

        Current accounts lines do not carry payment plan, so plan defaults
        to NP and may later be overridden by master account data.

        Args:
            file_path: Override the default current accounts file path.
        """
        path = file_path or self.current_file
        self.current_accounts = []
        if not os.path.exists(path):
            print("Warning: current accounts file not found:", path)
            return
        with open(path, "r") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if len(line) < 37:
                    continue

                acc_num = line[0:5].strip()
                if acc_num == "00000":  # END_OF_FILE sentinel
                    break

                self.current_accounts.append({
                    "accountNumber": str(acc_num).zfill(5),
                    "accountName": line[6:26].rstrip(),
                    "status": line[27:28].strip(),
                    "balance": float(line[29:37].strip()),
                    "plan": "NP",
                })
                # TODO: handle broken lines with errors and check that I did this right

    def read_old_master_accounts(self, file_path: Optional[str] = None):
        """
        Read the master bank accounts file into self.master_accounts.

        Expected record format:
            NNNNN AAAAAAAAAAAAAAAAAAAA S PPPPPPPP TT

        Uses fixed-position parsing so account names with spaces are handled
        correctly. Stops at the END_OF_FILE (00000) sentinel line.

        Args:
            file_path: Override the default master accounts file path.
        """
        path = file_path or self.master_file
        self.master_accounts = []
        if not os.path.exists(path):
            print("Warning: master accounts file not found:", path)
            return
        with open(path, "r") as f:
            for line in f:
                line = line.rstrip("\n")
                if line.strip() == "":
                    continue
                if line[0:5].strip() == "00000":  # END_OF_FILE sentinel
                    break
                account = {
                    "accountNumber": line[0:5].strip(),
                    "accountName": line[6:26].strip(),
                    "status": line[27:28].strip(),
                    "balance": float(line[29:37].strip()),
                    "plan": line[38:40].strip() if len(line) >= 40 else "NP",
                }
                self.master_accounts.append(account)

        # Master accounts are the authoritative source for Back End processing.
        self.current_accounts = [dict(acc) for acc in self.master_accounts]

    def write_new_current_accounts(self, file_path: Optional[str] = None):
        """
        Write self.current_accounts to the current accounts file.

        Produces one line per account in the format:
            NNNNN AAAAAAAAAAAAAAAAAAAA S PPPPPPPP

        Args:
            file_path: Override the default current accounts file path.
        """
        path = file_path or self.current_file

        with open(path, "w") as f:
            for acc in self.current_accounts:
                line = (
                    f"{acc['accountNumber'].zfill(5)} "
                    f"{acc['accountName']:<20} "
                    f"{acc['status']} "
                    f"{acc['balance']:08.2f}\n"
                )
                f.write(line)
            f.write("00000 END_OF_FILE          A 00000.00\n")

    def write_new_master_accounts(self, file_path: Optional[str] = None):
        """
        Write the updated account list to the master accounts file.

        Produces one line per account in the format:
            NNNNN AAAAAAAAAAAAAAAAAAAA S PPPPPPPP TT

        Args:
            file_path: Override the default master accounts file path.
        """
        path = file_path or self.master_file

        with open(path, "w") as f:
            for acc in self.current_accounts:
                line = (
                    f"{acc['accountNumber'].zfill(5)} "
                    f"{acc['accountName']:<20} "
                    f"{acc['status']} "
                    f"{acc['balance']:08.2f} "
                    f"{acc.get('plan', 'NP')}\n"
                )
                f.write(line)

    def get_account_by_id(self, account_id: str) -> Optional[Dict]:
        """
        Return the account dict from current_accounts with the given number.

        Args:
            account_id: Account number (zero-padded to 5 digits if necessary).

        Returns:
            The matching account dict, or None if no account was found.
        """
        key = str(account_id).zfill(5)
        for a in self.current_accounts:
            if a['accountNumber'] == key:
                return a
        return None

    def perform_transaction(self, transaction):
        """
        Dispatch a transaction dict to the appropriate handler in transactions.py.

        Transaction codes:
            00 – end_of_session    04 – deposit    08 – changeplan
            01 – withdrawal        05 – create
            02 – transfer          06 – delete
            03 – paybill           07 – disable

        Codes 09 and 10 (login/logout) are Front End only and are silently
        ignored. Any other unrecognised code prints an ERROR message.

        Args:
            transaction: Dict with keys: code, accountName, accountNumber,
                         money, misc.
        """
        import transactions as tx
        code = str(transaction.get('code', '')).zfill(2)
        dispatch = {
            '01': tx.withdrawal,
            '02': tx.transfer,
            '03': tx.paybill,
            '04': tx.deposit,
            '05': tx.create,
            '06': tx.delete,
            '07': tx.disable,
            '08': tx.changeplan,
            '00': tx.end_of_session,
        }
        handler = dispatch.get(code)
        if handler:
            handler(transaction, self)
        elif code not in ('09', '10'):  # login/logout have no backend action
            print(f"ERROR: Unknown transaction code '{code}' - skipping.")


class TransactionsList:
    """Reads the merged transaction file produced by the Front End into a list."""

    def __init__(self, file_path: str):
        """
        Initialize with the path to the merged transaction file.

        Args:
            file_path: Path to the merged transaction file.
        """
        self.file_path = file_path
        self.transactions: List[Dict] = []

    def read_merged_transaction_file(self):
        """
        Parse the merged transaction file into self.transactions.

        Each non-sentinel line is split on whitespace and stored as a dict
        with keys: code, accountName, accountNumber, money, misc.

        Raises:
            FileNotFoundError: If the transaction file does not exist.
        """
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
        """Return an iterator over the parsed transaction records."""
        return iter(self.transactions)
