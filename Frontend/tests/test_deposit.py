# Tests for the Deposit transaction.
# Input order - standard: account_number, amount
#             - admin:    account_holder, account_number, amount

from transactions import deposit, withdrawal
from utils import AccountsList

# validDepositAccount: account owned by the logged-in user is accepted
def test_valid_deposit_account(standard_session, mock_input):
    mock_input("1", "20.00")
    assert deposit(standard_session) is not None

# invalidDepositAccount: account belonging to a different user is rejected
def test_invalid_deposit_account(standard_session, mock_input, capsys):
    mock_input("2", "20.00")
    assert deposit(standard_session) is None
    assert "ERROR: Account not found" in capsys.readouterr().out

# zeroDollarDeposit: deposit totalling $0.00 is rejected
def test_zero_dollar_deposit(standard_session, mock_input, capsys):
    mock_input("1", "0.00")
    assert deposit(standard_session) is None
    assert "ERROR: Deposit amount must be greater than 0.00." in capsys.readouterr().out

# negativeDollarDeposit: deposit totalling a negative value is rejected
def test_negative_dollar_deposit(standard_session, mock_input, capsys):
    mock_input("1", "-1.00")
    assert deposit(standard_session) is None
    assert "ERROR: Deposit amount must be greater than 0.00." in capsys.readouterr().out

# savesDepositInfo: successful deposit is saved to the transaction log
def test_saves_deposit_info(standard_session, mock_input):
    mock_input("1", "20.00")
    assert deposit(standard_session) is not None
    logged = standard_session.log.transactions[0]
    assert logged['code'] == '04'
    assert logged['accountNumber'] == '00001'
    assert logged['money'] == '00020.00'

# isLoggedInAsAdmin: admin is prompted for account holder name
def test_is_logged_in_as_admin(admin_session, mock_input):
    mock_input("John Doe", "1", "25.00")
    assert deposit(admin_session) is not None

# depositUnusable: deposited money cannot be used in other transactions within the same session.
def deposit_unusable(standard_session, mock_input, capsys):
    mock_input("1", "20.00")
    assert deposit(standard_session) is not None
    mock_input("1", "1020.00")
    assert withdrawal(standard_session) is None
    assert "ERROR: Insufficient funds" in capsys.readouterr().out