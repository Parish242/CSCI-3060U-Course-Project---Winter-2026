# Tests for the Disable transaction.
# Input order - standard: N/A (not allowed)
#             - admin:    account_holder, account_number

from transactions import disable, transfer, withdrawal
from utils import AccountsList


# isLoggedInAsAdmin: standard user cannot disable accounts
def test_disable_requires_admin(standard_session, capsys):
    result = disable(standard_session)
    assert result is None
    assert "ERROR: Privileged transaction. Admin access required." in capsys.readouterr().out


# validAccountNameAndNumber: admin successfully disables an active account
# The account status should change from 'A' (active) to 'D' (disabled)
# Transaction code 07 confirms the operation was logged
def test_valid_disable_account(admin_session, mock_input):
    mock_input("Jane Smith", "2")
    result = disable(admin_session)

    assert result is not None
    assert result["code"] == "07"

    account = next(a for a in AccountsList.accounts if a["accountNumber"] == 2)
    assert account["status"] == "D"


# invalidAccountName: account holder does not exist
# The system should reject the transaction
def test_invalid_disable_name(admin_session, mock_input, capsys):
    mock_input("Fake Person", "1")
    result = disable(admin_session)

    assert result is None
    assert "ERROR: Account not found" in capsys.readouterr().out


# invalidAccountNumber: account number does not match holder
# The system should reject the transaction
def test_invalid_disable_account_number(admin_session, mock_input, capsys):
    mock_input("John Doe", "999")
    result = disable(admin_session)

    assert result is None
    assert "ERROR: Account not found" in capsys.readouterr().out


# savesDisableInfo: successful disable should be recorded in the transaction log
# Transaction code 07 confirms the operation was logged
def test_disable_transaction_logged(admin_session, mock_input):
    mock_input("John Doe", "1")
    disable(admin_session)

    assert len(admin_session.log.transactions) == 1
    assert admin_session.log.transactions[0]["code"] == "07"
