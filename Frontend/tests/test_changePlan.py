# Tests for the ChangePlan transaction.
# Input order - standard: N/A (not allowed)
#             - admin:    account_holder, account_number

from transactions import changeplan, transfer, withdrawal
from utils import AccountsList


# isLoggedInAsAdmin: standard user cannot change account plans
def test_changePlan_requires_admin(standard_session, capsys):
    result = changeplan(standard_session)
    assert result is None
    assert "ERROR: Privileged transaction. Admin access required." in capsys.readouterr().out


# invalidAccountName: account holder does not exist
# The system should reject the transaction
def test_invalid_changePlan_name(admin_session, mock_input, capsys):
    mock_input("Fake Person", "1")
    result = changeplan(admin_session)

    assert result is None
    assert "ERROR: Account not found" in capsys.readouterr().out


# invalidAccountNumber: account number does not match holder
# The system should reject the transaction
def test_invalid_changePlan_account_number(admin_session, mock_input, capsys):
    mock_input("John Doe", "999")
    result = changeplan(admin_session)

    assert result is None
    assert "ERROR: Account not found" in capsys.readouterr().out


# savesChangePlanInfo: successful changePlan should be recorded in the transaction log
# Transaction code 08 confirms the operation was logged
def test_changePlan_transaction_logged(admin_session, mock_input):
    mock_input("John Doe", "1")
    changeplan(admin_session)

    assert len(admin_session.log.transactions) == 1
    assert admin_session.log.transactions[0]["code"] == "08"

# validAccountNameAndNumber: admin successfully change plan of an account
# The account plan should change from 'SP' (student plan) to 'NP' (non-student plan)
# Transaction code 08 confirms the operation was logged
def test_valid_disable_account(admin_session, mock_input):
    mock_input("Jane Smith", "2")
    result = changeplan(admin_session)

    assert result is not None
    assert result["code"] == "8"

    account = next(a for a in AccountsList.accounts if a["accountNumber"] == 2)
    assert account["plan"] == "NP"