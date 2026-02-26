# Tests for the Login transaction.
# Input order - standard login: session_type, account_name
#             - admin login:    session_type

from transactions import login, withdrawal, transfer, paybill, deposit, create, delete, disable, changeplan
from utils import SessionType, AccountsList

def mock_login_input(monkeypatch, *values):
    """Patch input AND skip the fetchAccounts file read (accounts are pre-loaded by the fixture)."""
    it = iter(values)
    monkeypatch.setattr("builtins.input", lambda _: next(it))
    monkeypatch.setattr(AccountsList, "fetchAccounts", classmethod(lambda cls: None))


# validInitialTransaction: login works before any session is active
def test_standard_login_succeeds(new_session, monkeypatch):
    mock_login_input(monkeypatch, "standard", "John Doe")
    result = login(new_session)
    assert result is not None
    assert new_session.permissions == SessionType.STANDARD
    assert new_session.accountName == "John Doe"

def test_admin_login_succeeds(new_session, monkeypatch):
    mock_login_input(monkeypatch, "admin")
    result = login(new_session)
    assert result is not None
    assert new_session.permissions == SessionType.ADMIN


# invalidInitialTransaction: all non-login transactions fail when not logged in
def test_withdrawal_fails_when_not_logged_in(new_session, capsys):
    assert withdrawal(new_session) is None
    assert "ERROR" in capsys.readouterr().out

def test_transfer_fails_when_not_logged_in(new_session, capsys):
    assert transfer(new_session) is None
    assert "ERROR" in capsys.readouterr().out

def test_paybill_fails_when_not_logged_in(new_session, capsys):
    assert paybill(new_session) is None
    assert "ERROR" in capsys.readouterr().out

def test_deposit_fails_when_not_logged_in(new_session, capsys):
    assert deposit(new_session) is None
    assert "ERROR" in capsys.readouterr().out

def test_create_fails_when_not_logged_in(new_session, capsys):
    assert create(new_session) is None
    assert "ERROR" in capsys.readouterr().out

def test_delete_fails_when_not_logged_in(new_session, capsys):
    assert delete(new_session) is None
    assert "ERROR" in capsys.readouterr().out

def test_disable_fails_when_not_logged_in(new_session, capsys):
    assert disable(new_session) is None
    assert "ERROR" in capsys.readouterr().out

def test_changeplan_fails_when_not_logged_in(new_session, capsys):
    assert changeplan(new_session) is None
    assert "ERROR" in capsys.readouterr().out


# concurrentLogin: login while already logged in is rejected
def test_login_fails_when_already_logged_in_as_standard(standard_session, capsys):
    assert login(standard_session) is None
    assert "ERROR: Already logged in" in capsys.readouterr().out

def test_login_fails_when_already_logged_in_as_admin(admin_session, capsys):
    assert login(admin_session) is None
    assert "ERROR: Already logged in" in capsys.readouterr().out

def test_standard_cannot_login_while_admin_active(admin_session, capsys):
    assert login(admin_session) is None
    assert "ERROR: Already logged in" in capsys.readouterr().out

def test_admin_cannot_login_while_standard_active(standard_session, capsys):
    assert login(standard_session) is None
    assert "ERROR: Already logged in" in capsys.readouterr().out


# unprivilegedTransactions: standard user cannot run admin-only transactions
def test_create_rejected_for_standard_user(standard_session, capsys):
    assert create(standard_session) is None
    assert "ERROR: Privileged transaction. Admin access required." in capsys.readouterr().out

def test_delete_rejected_for_standard_user(standard_session, capsys):
    assert delete(standard_session) is None
    assert "ERROR: Privileged transaction. Admin access required." in capsys.readouterr().out

def test_disable_rejected_for_standard_user(standard_session, capsys):
    assert disable(standard_session) is None
    assert "ERROR: Privileged transaction. Admin access required." in capsys.readouterr().out

def test_changeplan_rejected_for_standard_user(standard_session, capsys):
    assert changeplan(standard_session) is None
    assert "ERROR: Privileged transaction. Admin access required." in capsys.readouterr().out

def test_login_rejected_for_standard_session(standard_session, capsys):
    assert login(standard_session) is None
    assert "ERROR: Already logged in" in capsys.readouterr().out


# privilegedTransactions: admin can access admin-only transactions
def test_create_available_to_admin(admin_session, mock_input, capsys):
    mock_input("John Doe", "1", "100.00")
    create(admin_session)
    assert "ERROR: Privileged transaction. Admin access required." not in capsys.readouterr().out

def test_delete_available_to_admin(admin_session, mock_input, capsys):
    mock_input("John Doe", "1", "100.00")
    delete(admin_session)
    assert "ERROR: Privileged transaction. Admin access required." not in capsys.readouterr().out

def test_disable_available_to_admin(admin_session, mock_input, capsys):
    mock_input("John Doe", "1", "100.00")
    disable(admin_session)
    assert "ERROR: Privileged transaction. Admin access required." not in capsys.readouterr().out

def test_changeplan_available_to_admin(admin_session, mock_input, capsys):
    mock_input("John Doe", "1", "100.00")
    changeplan(admin_session)
    assert "ERROR: Privileged transaction. Admin access required." not in capsys.readouterr().out

def test_login_rejected_for_admin_session(admin_session, capsys):
    assert login(admin_session) is None
    assert "ERROR: Already logged in" in capsys.readouterr().out


# validLogin: account name validation
def test_login_succeeds_with_valid_account_name(new_session, monkeypatch):
    mock_login_input(monkeypatch, "standard", "John Doe")
    result = login(new_session)
    assert result is not None
    assert new_session.accountName == "John Doe"
    assert new_session.permissions == SessionType.STANDARD

def test_login_stores_correct_account_name(new_session, monkeypatch):
    mock_login_input(monkeypatch, "standard", "Jane Smith")
    login(new_session)
    assert new_session.accountName == "Jane Smith"

def test_login_fails_with_empty_name(new_session, monkeypatch, capsys):
    mock_login_input(monkeypatch, "standard", "")
    assert login(new_session) is None
    assert "ERROR" in capsys.readouterr().out

def test_login_fails_with_name_over_20_chars(new_session, monkeypatch, capsys):
    mock_login_input(monkeypatch, "standard", "A" * 21)
    assert login(new_session) is None
    assert "ERROR" in capsys.readouterr().out
