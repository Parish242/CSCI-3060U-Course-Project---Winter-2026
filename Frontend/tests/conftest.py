"""
Shared pytest fixtures and configuration for the Banking System Front End tests.

To run tests, ensure pytest package is installed and execute `pytest` in terminal in the source directory. This will automatically discover and run all test files matching the pattern `test_*.py` in the `tests/` directory.

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
