"""
Shared pytest fixtures and configuration for the Banking System Back End tests.

To run tests, ensure pytest package is installed and execute `pytest` in terminal in the source directory. This will automatically discover and run all test files matching the pattern `test_*.py` in the `tests/` directory.

"""

import sys
import os
import pytest

# Add the Backend directory to sys.path so tests can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lists import AccountsList

# Sample accounts used across all test modules
SAMPLE_ACCOUNTS = [
    {"accountNumber": '00001', "accountName": "John Doe",       "status": "A", "balance": 1000.00, "plan": "NP"},
    {"accountNumber": '00002', "accountName": "Jane Smith",     "status": "A", "balance": 2500.00, "plan": "NP"},
    {"accountNumber": '00003', "accountName": "Bob Johnson",    "status": "A", "balance":  750.00, "plan": "NP"},
    {"accountNumber": '00004', "accountName": "Alice Williams", "status": "D", "balance":  100.00, "plan": "NP"},
    {"accountNumber": '00005', "accountName": "Charlie Brown",  "status": "A", "balance": 5000.00, "plan": "SP"},
]

@pytest.fixture
def accounts_list():
    """
    Reset the AccountsList to a fresh copy of
    SAMPLE_ACCOUNTS before every test, and clear it afterward.
    Since this wasn't written as a singleton, this must be
    passed in as an argument (unlike in the frontend tests).
    """
    list = AccountsList()
    list.current_accounts = [dict(acc) for acc in SAMPLE_ACCOUNTS]
    yield list
    AccountsList.current_accounts = []
