# Tests for the Delete transaction.
# Input order - standard: N/A (not allowed)
#             - admin:    account_holder, account_number

from transactions import delete, transfer
from utils import AccountsList


# isLoggedInAsAdmin: standard user is rejected from performing delete
def test_delete_requires_admin(standard_session, capsys):
    result = delete(standard_session)
    assert result is None
    assert "ERROR: Privileged transaction. Admin access required." in capsys.readouterr().out


# validAccountNameAndNumber: admin deletes an existing account successfully
# The account should be removed from the system and transaction code 06 returned
def test_valid_delete_account(admin_session, mock_input):
    mock_input("Bob Johnson", "3")
    result = delete(admin_session)

    assert result is not None
    assert result["code"] == "06"
    assert not any(a["accountNumber"] == 3 for a in AccountsList.accounts)


# invalidAccountName: account holder name does not exist
# The system should reject the transaction
def test_invalid_delete_name(admin_session, mock_input, capsys):
    mock_input("Fake Person", "1")
    result = delete(admin_session)

    assert result is None
    assert "ERROR: Account not found" in capsys.readouterr().out


# invalidAccountNumber: account number does not match the given holder
# The system should reject the transaction
def test_invalid_delete_account_number(admin_session, mock_input, capsys):
    mock_input("John Doe", "999")
    result = delete(admin_session)

    assert result is None
    assert "ERROR: Account not found" in capsys.readouterr().out


# savesDeleteInfo: successful delete should be recorded in the transaction log
# Transaction code 06 confirms the operation was logged
def test_delete_transaction_logged(admin_session, mock_input):
    mock_input("Charlie Brown", "5")
    delete(admin_session)

    assert len(admin_session.log.transactions) == 1
    assert admin_session.log.transactions[0]["code"] == "06"


# transferToDeletedAccount: attempting to transfer to a deleted account
# should result in an error
def test_transfer_to_deleted_account_rejected(admin_session, mock_input, capsys):
    mock_input("Bob Johnson", "3")
    delete(admin_session)

    mock_input("John Doe", "1", "3", "50.00")
    result = transfer(admin_session)

    assert result is None
    assert "ERROR" in capsys.readouterr().out
