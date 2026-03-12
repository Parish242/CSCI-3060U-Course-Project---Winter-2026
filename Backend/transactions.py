"""
backend/transactions.py

Transaction handler functions for the Banking System Back End.

Each function applies a single transaction dict to an AccountsList, enforcing
the business constraints defined in the project spec. Constraint violations are
reported to the terminal as ERROR messages. Returns True if the transaction was
applied successfully, False if it was skipped due to a constraint violation.

Transaction codes handled:
    01 – withdrawal      04 – deposit       07 – disable
    02 – transfer        05 – create        08 – changeplan
    03 – paybill         06 – delete        00 – end_of_session

Transaction fee rates (debited from the account after each money transaction):
    SP (student plan)     – $0.05 per transaction
    NP (non-student plan) – $0.10 per transaction

Note on transfer (code 02):
    The Front End stores the TO account number in the 'accountNumber' field and
    the FROM account holder's name in the 'accountName' field. The 'misc' field
    holds only the first two characters of the FROM account number (a known
    limitation of the current Front End prototype). The FROM account is therefore
    identified by name; if the holder owns multiple accounts the first active one
    is used (best-effort behaviour for this first version).
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Imported for type-checking only to avoid a circular import at runtime.
    from lists import AccountsList


# Per-transaction fee amounts indexed by payment plan code.
TRANSACTION_FEE: dict[str, float] = {
    "SP": 0.05,
    "NP": 0.10,
}


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _charge_fee(account: dict) -> bool:
    """
    Deduct the per-transaction fee from account['balance'] based on the
    account's payment plan, and increment its transaction counter.

    Args:
        account: The account dict to charge.

    Returns:
        True if the fee was applied, False if the balance would go negative.
    """
    fee = TRANSACTION_FEE.get(account.get("plan", "SP"), 0.05)
    if round(account["balance"] - fee, 2) < 0:
        print(
            f"ERROR: Transaction fee of ${fee:.2f} would cause a negative balance "
            f"on account {account['accountNumber']} – fee not applied."
        )
        return False
    account["balance"] = round(account["balance"] - fee, 2)
    account["transactionCount"] = account.get("transactionCount", 0) + 1
    return True


# ---------------------------------------------------------------------------
# Transaction handlers
# ---------------------------------------------------------------------------

def withdrawal(transaction: dict, accounts: AccountsList) -> bool:
    """
    Apply a withdrawal transaction (code 01).

    Deducts 'money' from the account identified by 'accountNumber', then
    charges the per-transaction fee.

    Constraint: the account balance must remain >= $0.00 after both
    the withdrawal and the fee.

    Args:
        transaction: Transaction dict (code, accountName, accountNumber,
                     money, misc).
        accounts:    AccountsList to modify.

    Returns:
        True on success, False if a constraint was violated.
    """
    account = accounts.get_account_by_id(transaction["accountNumber"])
    if account is None:
        print(f"ERROR: Withdrawal failed – account {transaction['accountNumber']} not found.")
        return False
    if account["status"] == "D":
        print(f"ERROR: Withdrawal failed – account {transaction['accountNumber']} is disabled.")
        return False

    amount = transaction["money"]
    fee    = TRANSACTION_FEE.get(account.get("plan", "SP"), 0.05)
    if round(account["balance"] - amount - fee, 2) < 0:
        print(
            f"ERROR: Withdrawal of ${amount:.2f} on account {transaction['accountNumber']} "
            f"would cause a negative balance – transaction skipped."
        )
        return False

    account["balance"] = round(account["balance"] - amount, 2)
    _charge_fee(account)
    return True


def transfer(transaction: dict, accounts: AccountsList) -> bool:
    """
    Apply a transfer transaction (code 02).

    Credits 'money' to the TO account (stored in 'accountNumber') and debits
    the same amount from the FROM account. The FROM account is identified by
    the 'accountName' field (the account holder's name), since the Front End
    only stores the first two characters of the FROM account number in 'misc'.
    If the holder owns more than one active account, the first one found is used.
    The per-transaction fee is charged to the FROM account.

    Constraint: the FROM account balance must remain >= $0.00 after the
    deduction and the fee.

    Args:
        transaction: Transaction dict.
        accounts:    AccountsList to modify.

    Returns:
        True on success, False if a constraint was violated.
    """
    to_account = accounts.get_account_by_id(transaction["accountNumber"])
    if to_account is None:
        print(f"ERROR: Transfer failed – TO account {transaction['accountNumber']} not found.")
        return False
    if to_account["status"] == "D":
        print(f"ERROR: Transfer failed – TO account {transaction['accountNumber']} is disabled.")
        return False

    # Locate the FROM account by the account holder's name (best-effort, see module note).
    name_key     = transaction["accountName"].strip()
    from_account = None
    for acc in accounts.current_accounts:
        if acc["accountName"].strip() == name_key and acc["status"] == "A":
            from_account = acc
            break

    if from_account is None:
        print(
            f"ERROR: Transfer failed – no active account found for holder "
            f"'{name_key}' to transfer from."
        )
        return False

    amount = transaction["money"]
    fee    = TRANSACTION_FEE.get(from_account.get("plan", "SP"), 0.05)
    if round(from_account["balance"] - amount - fee, 2) < 0:
        print(
            f"ERROR: Transfer of ${amount:.2f} from account "
            f"{from_account['accountNumber']} would cause a negative balance "
            f"– transaction skipped."
        )
        return False

    from_account["balance"] = round(from_account["balance"] - amount, 2)
    to_account["balance"]   = round(to_account["balance"]   + amount, 2)
    _charge_fee(from_account)
    return True


def paybill(transaction: dict, accounts: AccountsList) -> bool:
    """
    Apply a paybill transaction (code 03).

    Deducts 'money' from the account identified by 'accountNumber' as payment
    to the company whose code is in 'misc' (EC, CQ, or FI), then charges the
    per-transaction fee.

    Constraint: the account balance must remain >= $0.00 after both the
    payment and the fee.

    Args:
        transaction: Transaction dict ('misc' holds the company code).
        accounts:    AccountsList to modify.

    Returns:
        True on success, False if a constraint was violated.
    """
    account = accounts.get_account_by_id(transaction["accountNumber"])
    if account is None:
        print(f"ERROR: Paybill failed – account {transaction['accountNumber']} not found.")
        return False
    if account["status"] == "D":
        print(f"ERROR: Paybill failed – account {transaction['accountNumber']} is disabled.")
        return False

    amount = transaction["money"]
    fee    = TRANSACTION_FEE.get(account.get("plan", "SP"), 0.05)
    if round(account["balance"] - amount - fee, 2) < 0:
        print(
            f"ERROR: Paybill of ${amount:.2f} on account {transaction['accountNumber']} "
            f"would cause a negative balance – transaction skipped."
        )
        return False

    account["balance"] = round(account["balance"] - amount, 2)
    _charge_fee(account)
    return True


def deposit(transaction: dict, accounts: AccountsList) -> bool:
    """
    Apply a deposit transaction (code 04).

    Credits 'money' to the account identified by 'accountNumber'. Funds
    deposited during a Front End session are not available to the user within
    that session, but are fully available once applied here by the Back End.
    The per-transaction fee is then charged.

    Constraint: the balance after crediting the deposit and deducting the fee
    must remain >= $0.00 (guards against a fee on a zero-balance new deposit).

    Args:
        transaction: Transaction dict.
        accounts:    AccountsList to modify.

    Returns:
        True on success, False if a constraint was violated.
    """
    account = accounts.get_account_by_id(transaction["accountNumber"])
    if account is None:
        print(f"ERROR: Deposit failed – account {transaction['accountNumber']} not found.")
        return False
    if account["status"] == "D":
        print(f"ERROR: Deposit failed – account {transaction['accountNumber']} is disabled.")
        return False

    amount = transaction["money"]
    fee    = TRANSACTION_FEE.get(account.get("plan", "SP"), 0.05)
    if round(account["balance"] + amount - fee, 2) < 0:
        print(
            f"ERROR: Deposit fee of ${fee:.2f} on account {transaction['accountNumber']} "
            f"would cause a negative balance – transaction skipped."
        )
        return False

    account["balance"] = round(account["balance"] + amount, 2)
    _charge_fee(account)
    return True


def create(transaction: dict, accounts: AccountsList) -> bool:
    """
    Apply a create transaction (code 05).

    Adds a brand-new account to accounts.accounts with the account number,
    holder name, and initial balance specified in the transaction. The account
    starts active (A) with the student payment plan (SP) and a zero transaction
    count. The new list is kept in ascending account-number order.

    Constraint: the new account number must not already exist in the system.

    Args:
        transaction: Transaction dict ('accountNumber'=new number,
                     'accountName'=holder name, 'money'=initial balance).
        accounts:    AccountsList to modify.

    Returns:
        True on success, False if a constraint was violated.
    """
    new_num = str(transaction["accountNumber"]).zfill(5)
    if accounts.get_account_by_id(new_num) is not None:
        print(f"ERROR: Create failed – account number {new_num} already exists.")
        return False

    accounts.current_accounts.append({
        "accountNumber":    new_num,
        "accountName":      transaction["accountName"].strip(),
        "status":           "A",
        "balance":          round(transaction["money"], 2),
        "plan":             "SP",   # all new accounts start on the student plan
        "transactionCount": 0,
    })
    # Maintain ascending order by account number as required by the spec.
    accounts.current_accounts.sort(key=lambda a: a["accountNumber"])
    return True


def delete(transaction: dict, accounts: AccountsList) -> bool:
    """
    Apply a delete transaction (code 06).

    Removes the account identified by 'accountNumber' from accounts.accounts.
    No further transactions will be accepted on a deleted account because it
    will no longer appear in the accounts list.

    Args:
        transaction: Transaction dict.
        accounts:    AccountsList to modify.

    Returns:
        True on success, False if the account was not found.
    """
    account = accounts.get_account_by_id(transaction["accountNumber"])
    if account is None:
        print(f"ERROR: Delete failed – account {transaction['accountNumber']} not found.")
        return False

    accounts.current_accounts.remove(account)
    return True


def disable(transaction: dict, accounts: AccountsList) -> bool:
    """
    Apply a disable transaction (code 07).

    Sets the account status from active (A) to disabled (D). Disabled accounts
    will be rejected by subsequent money-transaction handlers.

    Args:
        transaction: Transaction dict.
        accounts:    AccountsList to modify.

    Returns:
        True on success, False if the account was not found.
    """
    account = accounts.get_account_by_id(transaction["accountNumber"])
    if account is None:
        print(f"ERROR: Disable failed – account {transaction['accountNumber']} not found.")
        return False

    account["status"] = "D"
    return True


def changeplan(transaction: dict, accounts: AccountsList) -> bool:
    """
    Apply a changeplan transaction (code 08).

    Changes the account's payment plan from student (SP) to non-student (NP).
    Per the spec, changeplan is a one-way operation in the Front End
    (SP → NP only), so the Back End sets the plan to NP unconditionally.

    Args:
        transaction: Transaction dict.
        accounts:    AccountsList to modify.

    Returns:
        True on success, False if the account was not found.
    """
    account = accounts.get_account_by_id(transaction["accountNumber"])
    if account is None:
        print(f"ERROR: Changeplan failed – account {transaction['accountNumber']} not found.")
        return False

    account["plan"] = "NP"
    return True


def end_of_session(transaction: dict, accounts: AccountsList) -> bool:
    """
    Handle an end-of-session record (code 00).

    This record marks the boundary between sessions in the merged transaction
    file. No account changes are needed; the Back End simply acknowledges it
    and continues processing.

    Args:
        transaction: Transaction dict (ignored).
        accounts:    AccountsList (not modified).

    Returns:
        Always True.
    """
    return True
