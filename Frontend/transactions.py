"""
Transaction function implementations for the Banking System Front End.
Contains all banking transaction operations such as login, logout, withdrawal, transfer, paybill, deposit, and admin functions.
"""

from utils import SessionType, AccountsList

def login(session) -> dict:
    """
    Start a Front End session by logging in as standard or admin user.

    Args:
        session: Current Session object

    Returns:
        dict: Transaction details for logging
    """
    # Check if already logged in
    if session.permissions is not None:
        print("ERROR: Already logged in. Please logout first.")
        return None

    print("\nLogin Transaction")
    print("-" * 40)

    # Ask for session type
    while True:
        session_type = input("Enter session type (standard/admin): ").strip().lower()

        if session_type == "standard":
            session.permissions = SessionType.STANDARD

            # Ask for account holder name
            account_name = input("Enter account holder name: ").strip()

            if not validate_account_name(account_name):
                session.permissions = None
                return None

            session.accountName = account_name

            # Set transaction limits for standard mode
            session.transactionLimits['withdrawal'] = 500.00
            session.transactionLimits['transfer'] = 1000.00
            session.transactionLimits['paybill'] = 2000.00

            print(f"Logged in as STANDARD user: {account_name}")
            break

        elif session_type == "admin":
            session.permissions = SessionType.ADMIN
            session.accountName = "ADMIN"

            # No transaction limits in admin mode
            session.transactionLimits['withdrawal'] = float('inf')
            session.transactionLimits['transfer'] = float('inf')
            session.transactionLimits['paybill'] = float('inf')

            print("Logged in as ADMIN user")
            break

        else:
            print("ERROR: Invalid session type. Please enter 'standard' or 'admin'")

    # Load accounts file
    print("Loading bank accounts...")
    session.accounts = AccountsList()
    session.accounts.fetchAccounts()
    print("Bank accounts loaded successfully")

    return {
        'code': '10',
        'accountName': session.accountName,
        'accountNumber': '00000',
        'money': '00000.00',
        'misc': '00'
    }

def logout(session) -> dict:
    """
    End a Front End session and write transaction file.

    For this prototype, account changes (balances, status, plans) are not written to current_accounts.txt. 
    Only the transaction log is kept.

    Args:
        session: Current Session object

    Returns:
        dict: Transaction details for logging
    """
    if not require_login(session):
        return None

    print("\nLogout Transaction")
    print("-" * 40)

    # Add end of session transaction to log
    session.log.addTransaction({
        'code': '00',
        'accountName': 'END_OF_SESSION',
        'accountNumber': '00000',
        'money': '00000.00',
        'misc': '00'
    })

    # Write transaction file
    print("Writing transaction log...")
    success = session.log.writeTransactionFile()

    if success:
        print("Transaction log written successfully")
        print(f"Logged out user: {session.accountName}")
    else:
        print("ERROR: Failed to write transaction log")

    # Reset session
    session.permissions = None
    session.accountName = ""
    session.transactionLimits = {
        'withdrawal': 0.0,
        'transfer': 0.0,
        'paybill': 0.0
    }

    return None

def withdrawal(session) -> dict:
    """
    Withdraw money from a bank account.

    Args:
        session: Current Session object

    Returns:
        dict: Transaction details for logging
    """
    if not require_login(session):
        return None

    print_transaction_header("Withdrawal", pending=False)

    account_holder = get_account_holder(session)
    account_number = get_account_number()
    amount = get_amount("Enter withdrawal amount")

    if amount > session.transactionLimits['withdrawal']:
        print("ERROR: Exceeds session withdrawal limit")
        return None

    for acc in session.accounts.getAccounts():
        if acc['accountNumber'] == account_number and acc['accountName'] == account_holder:
            if acc['balance'] - amount < 0:
                print("ERROR: Insufficient funds")
                return None
            acc['balance'] -= amount
            break
    else:
        print("ERROR: Account not found")
        return None

    return log_transaction(session, '01', account_holder, account_number, amount)


def transfer(session) -> dict:
    """
    Transfer money between two bank accounts.

    Args:
        session: Current Session object

    Returns:
        dict: Transaction details for logging
    """
    if not require_login(session):
        return None

    print_transaction_header("Transfer", pending=False)

    account_holder = get_account_holder(session)
    from_acc_num = get_account_number("Enter account number to transfer FROM")
    to_acc_num = get_account_number("Enter account number to transfer TO")
    amount = get_amount("Enter transfer amount")

    if amount > session.transactionLimits['transfer']:
        print("ERROR: Exceeds session transfer limit")
        return None

    from_account = None
    to_account = None
    for acc in session.accounts.getAccounts():
        if acc['accountNumber'] == from_acc_num and acc['accountName'] == account_holder:
            from_account = acc
        if acc['accountNumber'] == to_acc_num:
            to_account = acc

    if not from_account:
        print("ERROR: Source account not found or not owned by account holder")
        return None
    if not to_account:
        print("ERROR: Destination account not found")
        return None
    if from_account['balance'] - amount < 0:
        print("ERROR: Insufficient funds in source account")
        return None

    from_account['balance'] -= amount
    to_account['balance'] += amount

    # Log transaction, using source account in misc
    return log_transaction(session, '02', account_holder, to_acc_num, amount, f'{from_acc_num:05d}')


# TODO
def paybill(session) -> dict:
    """
    Pay a bill from a bank account.

    Args:
        session: Current Session object

    Returns:
        dict: Transaction details for logging
    """
    if not require_login(session):
        return None

    print_transaction_header("Paybill")

    account_holder = get_account_holder(session)
    account_number = get_account_number()
    company = get_company_code()
    amount = get_amount("Enter payment amount")

    if amount > session.transactionLimits['paybill']:
        print("ERROR: Exceeds session paybill limit")
        return None

    for acc in session.accounts.getAccounts():
        if acc['accountNumber'] == account_number and acc['accountName'] == account_holder:
            if acc['balance'] - amount < 0:
                print("ERROR: Insufficient funds")
                return None
            acc['balance'] -= amount
            break
    else:
        print("ERROR: Account not found")
        return None

    return log_transaction(session, '03', account_holder, account_number, amount, company)

# TODO
def deposit(session) -> dict:
    # immediately increments the value for the sake of testing/being a prototype
    """
    Deposit money into a bank account.

    Args:
        session: Current Session object

    Returns:
        dict: Transaction details for logging
    """
    if not require_login(session):
        return None

    print_transaction_header("Deposit")

    account_holder = get_account_holder(session)
    account_number = get_account_number()
    amount = get_amount("Enter deposit amount")

    for acc in session.accounts.getAccounts():
        if acc['accountNumber'] == account_number and acc['accountName'] == account_holder:
            acc['balance'] += amount  # funds added but note: not available until next session
            break
    else:
        print("ERROR: Account not found")
        return None

    return log_transaction(session, '04', account_holder, account_number, amount)

# TODO
def create(session) -> dict:
    """
    Create a new bank account with an initial balance (ADMIN ONLY).

    Args:
        session: Current Session object

    Returns:
        dict: Transaction details for logging
    """
    if not require_admin(session):
        return None

    print_transaction_header("Create Account")

    account_holder = input("Enter account holder name: ").strip()
    if not validate_account_name(account_holder):
        return None

    initial_balance = get_amount("Enter initial balance")
    if not validate_balance(initial_balance):
        return None

    # Generate new unique account number
    max_acc = max((acc['accountNumber'] for acc in session.accounts.getAccounts()), default=0)
    new_acc_num = max_acc + 1

    session.accounts.accounts.append({
        'accountNumber': new_acc_num,
        'accountName': account_holder,
        'status': 'A',
        'balance': initial_balance,
        'plan': 'SP'  
        # default set to student plan, doesn't store in our accounts.txt file
})

    return log_transaction(session, '05', account_holder, new_acc_num, initial_balance)

# TODO
def delete(session) -> dict:
    """
    Delete an existing bank account (ADMIN ONLY).

    Args:
        session: Current Session object

    Returns:
        dict: Transaction details for logging
    """
    if not require_admin(session):
        return None

    print_transaction_header("Delete Account")

    account_holder = input("Enter account holder name: ").strip()
    account_number = get_account_number()

    for acc in session.accounts.getAccounts():
        if acc['accountNumber'] == account_number and acc['accountName'] == account_holder:
            session.accounts.accounts.remove(acc)
            break
    else:
        print("ERROR: Account not found")
        return None

    return log_transaction(session, '06', account_holder, account_number, 0)

# TODO
def disable(session) -> dict:
    """
    Disable a bank account (ADMIN ONLY).

    Args:
        session: Current Session object

    Returns:
        dict: Transaction details for logging
    """
    if not require_admin(session):
        return None

    print_transaction_header("Disable Account")

    account_holder = input("Enter account holder name: ").strip()
    account_number = get_account_number()

    for acc in session.accounts.getAccounts():
        if acc['accountNumber'] == account_number and acc['accountName'] == account_holder:
            acc['status'] = 'D'
            break
    else:
        print("ERROR: Account not found")
        return None

    return log_transaction(session, '07', account_holder, account_number, 0)

# Note: This doesn't write to the .txt file this just toggles the variable since we don't have a field for the plan yet
def changeplan(session) -> dict:
    """
    Change transaction payment plan for an account (ADMIN ONLY).

    Args:
        session: Current Session object

    Returns:
        dict: Transaction details for logging
    """
    if not require_admin(session):
        return None

    print_transaction_header("Change Plan")

    account_holder = input("Enter account holder name: ").strip()
    account_number = get_account_number()

    # Find the account
    for acc in session.accounts.getAccounts():
        if acc['accountNumber'] == account_number and acc['accountName'] == account_holder:
            # Toggle plan
            if acc['plan'] == 'SP':
                acc['plan'] = 'NP'
            else:
                acc['plan'] = 'SP'
            break
    else:
        print("ERROR: Account not found")
        return None

    return log_transaction(session, '08', account_holder, account_number, 0)

# All Helper functions below for transaction operations
def require_login(session) -> bool:
    """
    Check if user is logged in.

    Args:
        session: Current Session object

    Returns:
        bool: True if logged in, False otherwise
    """
    if session.permissions is None:
        print("ERROR: Not logged in. Please login first.")
        return False
    return True


def require_admin(session) -> bool:
    """
    Check if user is logged in as admin.

    Args:
        session: Current Session object

    Returns:
        bool: True if logged in as admin, False otherwise
    """
    if not require_login(session):
        return False

    if session.permissions != SessionType.ADMIN:
        print("ERROR: Privileged transaction. Admin access required.")
        return False

    return True


def get_account_holder(session) -> str:
    """
    Get account holder name based on session type.
    For admin sessions, prompts for name. For standard sessions, uses logged-in name.

    Args:
        session: Current Session object

    Returns:
        str: Account holder name
    """
    if session.permissions == SessionType.ADMIN:
        return input("Enter account holder name: ").strip()
    return session.accountName


def get_account_number(prompt: str = "Enter account number") -> int:
    """
    Get and validate account number from user input.

    Args:
        prompt: Custom prompt message

    Returns:
        int: Valid account number
    """
    while True:
        try:
            num_str = input(f"{prompt}: ").strip()
            num = int(num_str)
            if num < 0:
                print("ERROR: Account number cannot be negative")
                continue
            return num
        except ValueError:
            print("ERROR: Invalid account number. Please enter a valid number.")


def get_amount(prompt: str = "Enter amount") -> float:
    """
    Get and validate monetary amount from user input.

    Args:
        prompt: Custom prompt message

    Returns:
        float: Valid positive amount
    """
    while True:
        try:
            amount_str = input(f"{prompt}: ").strip()
            amount = float(amount_str)
            if amount <= 0:
                print("ERROR: Amount must be greater than $0.00")
                continue
            return amount
        except ValueError:
            print("ERROR: Invalid amount. Please enter a valid number.")


def get_company_code() -> str:
    """
    Get and validate company code for paybill transaction.

    Returns:
        str: Valid company code (EC, CQ, or FI)
    """
    valid_companies = {
        'EC': 'The Bright Light Electric Company',
        'CQ': 'Credit Card Company Q',
        'FI': 'Fast Internet, Inc.'
    }

    print("Valid companies:")
    for code, name in valid_companies.items():
        print(f"  {code} - {name}")

    while True:
        company = input("Enter company code (EC/CQ/FI): ").strip().upper()
        if company in valid_companies:
            return company
        print("ERROR: Invalid company code. Please enter EC, CQ, or FI.")


def print_transaction_header(name: str, pending: bool = True) -> None:
    """
    Print standardized transaction header.

    Args:
        name: Transaction name
        pending: Whether to show "TODO: Implementation pending" message
    """
    print(f"\n{name} Transaction")
    print("-" * 40)
    if pending:
        print("TODO: Implementation pending")


def log_transaction(session, code: str, account_name: str, 
                   account_number: int, amount: float, misc: str = '00') -> dict:
    """
    Create and log a transaction with proper formatting.

    Args:
        session: Current Session object
        code: Two-digit transaction code
        account_name: Account holder name
        account_number: Account number
        amount: Transaction amount
        misc: Miscellaneous info (default '00')

    Returns:
        dict: The logged transaction
    """
    transaction = {
        'code': code,
        'accountName': account_name[:20].ljust(20),
        'accountNumber': f'{int(account_number):05d}',
        'money': f'{float(amount):08.2f}',
        'misc': misc[:2].ljust(2)
    }
    session.log.addTransaction(transaction)
    return transaction


def validate_account_name(name: str) -> bool:
    """
    Validate account holder name constraints.

    Args:
        name: Account holder name to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if len(name) == 0:
        print("ERROR: Account holder name cannot be empty")
        return False

    if len(name) > 20:
        print("ERROR: Account holder name cannot exceed 20 characters")
        return False

    return True


def validate_balance(balance: float) -> bool:
    """
    Validate account balance constraints.

    Args:
        balance: Balance amount to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if balance < 0:
        print("ERROR: Account balance cannot be negative")
        return False

    if balance > 99999.99:
        print("ERROR: Account balance cannot exceed $99,999.99")
        return False

    return True
