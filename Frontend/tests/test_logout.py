# Tests for the Logout transaction.
# Input order - standard: N/A (not allowed)
#             - admin:    account_holder, account_number

from transactions import login, withdrawal, transfer, paybill, deposit, create, delete, disable, changeplan, logout
from utils import SessionType, AccountsList


# savesLogoutInfo: successful logout should be recorded in the transaction log
# Transaction code 00 confirms the operation was logged
def test_logout_transaction_logged(monkeypatch, admin_session, mock_input):
    mock_input("John Doe", "1")
    monkeypatch.setattr(
           "utils.TransactionLog.writeTransactionFile",
           lambda self: True
       )
    logout(admin_session)

    assert len(admin_session.log.transactions) == 1
    assert admin_session.log.transactions[0]["code"] == "00"


# validLogout: successful logout occurs after login
def test_valid_logout_transaction(monkeypatch, admin_session, mock_input, capsys):
    mock_input("John Doe", "1")
    monkeypatch.setattr(
           "utils.TransactionLog.writeTransactionFile",
           lambda self: True
       )
    result = logout(admin_session)
    assert result is None
    assert "ERROR: Privileged transaction. Admin access required." not in capsys.readouterr().out


# invalidLogout: attempt to logout without having logged in
def test_invalid_logout_transaction(monkeypatch, new_session, capsys):
    monkeypatch.setattr(
           "utils.TransactionLog.writeTransactionFile",
           lambda self: True
       )
    result = logout(new_session)
    assert result is None
    assert "ERROR: Not logged in. Please login first." in capsys.readouterr().out


# validTransactionAfterLogout: attempt login transaction after logout
def test_login_after_logout(monkeypatch, standard_session):
    monkeypatch.setattr(
           "utils.TransactionLog.writeTransactionFile",
           lambda self: True
       )
    result = logout(standard_session)
    assert result is None
    assert standard_session.log.transactions[0]["code"] == "00"

    it = iter(["standard", "Charlie Brown"])
    monkeypatch.setattr("builtins.input", lambda _: next(it))
    monkeypatch.setattr(AccountsList, "fetchAccounts", classmethod(lambda cls: None))

    result = login(standard_session)
    assert result is not None
    assert standard_session.permissions == SessionType.STANDARD
    assert standard_session.accountName == "Charlie Brown"


# consecutiveUser: confirm information from session logout is not carried over to new session login
def test_new_session_info_after_logout(monkeypatch, standard_session):
    monkeypatch.setattr(
           "utils.TransactionLog.writeTransactionFile",
           lambda self: True
       )
    account_balance_initial = next(a for a in AccountsList.accounts if a["accountNumber"] == 1)["balance"]
    result = logout(standard_session)
    assert result is None
    assert standard_session.log.transactions[0]["code"] == "00"

    it = iter(["standard", "Charlie Brown"])
    monkeypatch.setattr("builtins.input", lambda _: next(it))
    monkeypatch.setattr(AccountsList, "fetchAccounts", classmethod(lambda cls: None))

    result = login(standard_session)
    assert result is not None
    assert standard_session.permissions == SessionType.STANDARD
    assert standard_session.accountName == "Charlie Brown"

    account_balance_final = next(a for a in AccountsList.accounts if a["accountNumber"] == 5)["balance"]
    assert account_balance_initial != account_balance_final


# invalidTransactionAfterLogout: confirm every transaction other than login is rejected and met with an error
def test_withdrawal_after_logout_(monkeypatch, standard_session, capsys):
    monkeypatch.setattr(
           "utils.TransactionLog.writeTransactionFile",
           lambda self: True
       )
    logout(standard_session)
    assert standard_session.log.transactions[0]["code"] == "00"
    assert withdrawal(standard_session) is None
    assert "ERROR: Not logged in. Please login first."  in capsys.readouterr().out

def test_transfer_after_logout_(monkeypatch, standard_session, capsys):
    monkeypatch.setattr(
           "utils.TransactionLog.writeTransactionFile",
           lambda self: True
       )
    logout(standard_session)
    assert standard_session.log.transactions[0]["code"] == "00"
    assert transfer(standard_session) is None
    assert "ERROR: Not logged in. Please login first."  in capsys.readouterr().out

def test_paybill_after_logout_(monkeypatch, standard_session, capsys):
    monkeypatch.setattr(
           "utils.TransactionLog.writeTransactionFile",
           lambda self: True
       )
    logout(standard_session)
    assert standard_session.log.transactions[0]["code"] == "00"
    assert paybill(standard_session) is None
    assert "ERROR: Not logged in. Please login first."  in capsys.readouterr().out

def test_deposit_after_logout_(monkeypatch, standard_session, capsys):
    monkeypatch.setattr(
           "utils.TransactionLog.writeTransactionFile",
           lambda self: True
       )
    logout(standard_session)
    assert standard_session.log.transactions[0]["code"] == "00"
    assert deposit(standard_session) is None
    assert "ERROR: Not logged in. Please login first."  in capsys.readouterr().out

def test_create_after_logout_(monkeypatch, standard_session, capsys):
    monkeypatch.setattr(
           "utils.TransactionLog.writeTransactionFile",
           lambda self: True
       )
    logout(standard_session)
    assert standard_session.log.transactions[0]["code"] == "00"
    assert create(standard_session) is None
    assert "ERROR: Not logged in. Please login first."  in capsys.readouterr().out

def test_delete_after_logout_(monkeypatch, standard_session, capsys):
    monkeypatch.setattr(
           "utils.TransactionLog.writeTransactionFile",
           lambda self: True
       )
    logout(standard_session)
    assert standard_session.log.transactions[0]["code"] == "00"
    assert delete(standard_session) is None
    assert "ERROR: Not logged in. Please login first."  in capsys.readouterr().out

def test_disable_after_logout_(monkeypatch, standard_session, capsys):
    monkeypatch.setattr(
           "utils.TransactionLog.writeTransactionFile",
           lambda self: True
       )
    logout(standard_session)
    assert standard_session.log.transactions[0]["code"] == "00"
    assert disable(standard_session) is None
    assert "ERROR: Not logged in. Please login first."  in capsys.readouterr().out

def test_changePlan_after_logout_(monkeypatch, standard_session, capsys):
    monkeypatch.setattr(
           "utils.TransactionLog.writeTransactionFile",
           lambda self: True
       )
    logout(standard_session)
    assert standard_session.log.transactions[0]["code"] == "00"
    assert changeplan(standard_session) is None
    assert "ERROR: Not logged in. Please login first."  in capsys.readouterr().out