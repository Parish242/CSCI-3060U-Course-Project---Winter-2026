"""
Shared pytest fixtures and configuration for the Banking System Front End tests.

=== HOW TO WRITE A NEW TEST FILE ===

1. IMPORT PATTERN
   Import directly from the Frontend modules - no package prefix needed:
       from transactions import withdrawal
       from utils import SessionType, AccountsList

2. TEST STRUCTURE
   Write each test as a plain function - no classes needed. Group related tests
   with a short comment header:

       # sectionName: one line describing what is being tested

       def test_something(standard_session, mock_input):
           mock_input("1", "100.00")
           result = withdrawal(standard_session)
           assert result is not None

   Add mock_input as a parameter only when the test needs to supply inputs.
   Tests that expect an immediate error (e.g. not logged in) don't need it.

3. SESSION FIXTURES
   Request one of the three fixtures as a test parameter:
       new_session      – not logged in (use for login tests)
       standard_session – logged in as "John Doe" (account 1), standard limits apply
       admin_session    – logged in as admin, no transaction limits

   Admin-only transactions (create, delete, disable, changeplan) will always
   reject a standard_session with "ERROR: Privileged transaction." - use
   admin_session as the baseline for those test files.

4. MOCKING USER INPUT
   mock_input is a fixture defined in this file — request it as a test parameter
   and call it with the values input() should return, in order:

       def test_something(standard_session, mock_input):
           mock_input("value1", "value2", ...)
           result = withdrawal(standard_session)

   Input order per transaction (STANDARD / ADMIN):
     login        standard: session_type, account_name
                  admin:    session_type
     withdrawal   standard: account_number, amount
                  admin:    account_holder, account_number, amount
     transfer     standard: from_account_number, to_account_number, amount
                  admin:    account_holder, from_account_number, to_account_number, amount
     paybill      standard: account_number, company_code, amount
                  admin:    account_holder, account_number, company_code, amount
     deposit      standard: account_number, amount
                  admin:    account_holder, account_number, amount
     create       admin:    account_holder, initial_balance
     delete       admin:    account_holder, account_number
     disable      admin:    account_holder, account_number
     changeplan   admin:    account_holder, account_number
     logout       (no input required)

5. TESTING RE-PROMPT LOOPS
   Some inputs are validated in a loop (amounts, company codes). To test that an
   invalid value is rejected, supply the bad value first, then a valid one so the
   function can exit cleanly. Assert on the captured output:

       def test_zero_rejected(standard_session, mock_input, capsys):
           mock_input("1", "0", "100.00")  # "0" triggers error, "100.00" exits
           withdrawal(standard_session)
           assert "ERROR: Amount must be greater than $0.00" in capsys.readouterr().out

6. LOGOUT WRITES A FILE
   logout() calls TransactionLog.writeTransactionFile(), which creates a
   timestamped .txt file in the working directory. Patch it out to avoid
   side-effects in tests:

       monkeypatch.setattr(
           "transactions.TransactionLog.writeTransactionFile",
           lambda self: True
       )

7. CHECKING THE TRANSACTION LOG
   After a successful transaction, inspect session.log.transactions:

       assert len(session.log.transactions) == 1
       assert session.log.transactions[0]["code"] == "01"
"""

import sys
import os
import pytest

# Add the Frontend directory to sys.path so tests can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils import SessionType, AccountsList, TransactionLog

# Sample accounts used across all test modules
SAMPLE_ACCOUNTS = [
    {"accountNumber": 1, "accountName": "John Doe",       "status": "A", "balance": 1000.00, "plan": "SP"},
    {"accountNumber": 2, "accountName": "Jane Smith",     "status": "A", "balance": 2500.00, "plan": "SP"},
    {"accountNumber": 3, "accountName": "Bob Johnson",    "status": "A", "balance":  750.00, "plan": "SP"},
    {"accountNumber": 4, "accountName": "Alice Williams", "status": "D", "balance":  100.00, "plan": "SP"},
    {"accountNumber": 5, "accountName": "Charlie Brown",  "status": "A", "balance": 5000.00, "plan": "SP"},
]


@pytest.fixture(autouse=True)
def reset_accounts():
    """
    Reset the AccountsList class-level singleton to a fresh copy of
    SAMPLE_ACCOUNTS before every test, and clear it afterward.
    This prevents state leakage between tests.
    """
    AccountsList.accounts = [dict(acc) for acc in SAMPLE_ACCOUNTS]
    yield
    AccountsList.accounts = []

@pytest.fixture
def mock_input(monkeypatch):
    """Fixture that returns a callable for patching input() with pre-set responses.
    Usage: mock_input("value1", "value2", ...)
    Available to all test files automatically — no import needed.
    """
    def _mock(*values):
        it = iter(values)
        def _get_next_input(everything_breaks_if_this_parameter_isnt_here=None):
            try:
                return next(it)
            except StopIteration:
                raise Exception("No more inputs provided in test.")

        monkeypatch.setattr("builtins.input", _get_next_input)
    return _mock


# Session factory helpers
class _Session:
    """Minimal stand-in for main.Session used in unit tests."""

    def __init__(self):
        self.permissions: SessionType = None
        self.accountName: str = ""
        self.log: TransactionLog = TransactionLog()
        self.accounts: AccountsList = AccountsList()
        self.transactionLimits: dict = {
            "withdrawal": 0.0,
            "transfer": 0.0,
            "paybill": 0.0,
        }

@pytest.fixture
def new_session():
    """A session that has not yet been logged in."""
    return _Session()

@pytest.fixture
def standard_session():
    """A pre-authenticated standard user session as 'John Doe' (account 1)."""
    s = _Session()
    s.permissions = SessionType.STANDARD
    s.accountName = "John Doe"
    s.transactionLimits = {
        "withdrawal": 500.00,
        "transfer": 1000.00,
        "paybill": 2000.00,
    }
    return s

@pytest.fixture
def admin_session():
    """A pre-authenticated admin session."""
    s = _Session()
    s.permissions = SessionType.ADMIN
    s.accountName = "ADMIN"
    s.transactionLimits = {
        "withdrawal": float("inf"),
        "transfer": float("inf"),
        "paybill": float("inf"),
    }
    return s
