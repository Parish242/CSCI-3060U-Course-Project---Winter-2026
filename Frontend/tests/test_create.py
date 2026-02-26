# Tests for the Create transaction.
# Input order - standard: N/A (Privileged Transaction)
#             - admin:    account_holder, starting_amount

"""
Tests not implemented (found to not be applicable to actual build):
- duplicateCreateAccount (Account numbers are automatically generated in code, not inputted).
- invalidAccountHolderName (Transaction adds new names to system, no need to check whether or not they exist).
- enabledTransactions (Updating the accounts list is the responsibility of the backend, this will always fail no matter what).
"""

from transactions import create, deposit
from utils import AccountsList

# standardCreateAccount: Standard session is denied from performing transaction
def test_standard_create_account(standard_session, capsys):
    assert create(standard_session) is None
    assert "ERROR: Privileged transaction. Admin access required." in capsys.readouterr().out

# tooLongAccountHolderName: Name over 20 characters is rejected
def test_too_long_account_holder_name(admin_session, mock_input, capsys):
    mock_input("THISNAMEISWAYTOOLONGOVER20", "100.00")
    assert create(admin_session) is None
    assert "ERROR: Account holder name cannot exceed 20 characters" in capsys.readouterr().out

# aboveLimitAccountBalance: Balance over $99999.99 is rejected
def test_above_limit_account_balance(admin_session, mock_input, capsys):
    mock_input("EVE", "100000.00")
    assert create(admin_session) is None
    assert "ERROR: Account balance cannot exceed $99,999.99" in capsys.readouterr().out

# negativeAccountBalance: Balance under $0.00 is rejected
def test_negative_account_balance(admin_session, mock_input, capsys):
    mock_input("EVE", "-1.00")
    assert create(admin_session) is None
    assert "ERROR: Account balance cannot be negative" in capsys.readouterr().out

# savesCreateInfo: Successful create is saved to the transaction log
def test_saves_create_info(admin_session, mock_input):
    mock_input("EVE", "1.00")
    assert create(admin_session) is not None
    logged = admin_session.log.transactions[0]
    assert logged['code'] == '05'
    assert logged['money'] == '00001.00'

# disabledTransaction: Transaction involving account created in that session is rejected
def disabled_transaction(admin_session, mock_input, capsys):
    mock_input("EVE", "1.00")
    assert create(admin_session) is not None
    mock_input("EVE", "6", "20.00")
    assert deposit(admin_session) is None
    assert "ERROR: Account not found" in capsys.readouterr().out