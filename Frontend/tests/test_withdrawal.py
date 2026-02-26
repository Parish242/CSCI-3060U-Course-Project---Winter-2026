# Tests for the Withdrawal transaction.
# Input order - standard: account_number, amount
#             - admin:    account_holder, account_number, amount

from transactions import withdrawal
from utils import AccountsList

# validAccountHolder: account owned by the logged-in user is accepted
def test_valid_account_holder_accepted(standard_session, mock_input):
    mock_input("1", "100.00")  # account 1 belongs to John Doe
    result = withdrawal(standard_session)
    assert result is not None
    assert result["code"] == "01"


# invalidAccountHolder: account belonging to a different user is rejected

def test_wrong_account_holder_rejected(standard_session, mock_input, capsys):
    mock_input("2", "100.00")  # account 2 belongs to Jane Smith
    result = withdrawal(standard_session)
    assert result is None
    assert "ERROR: Account not found" in capsys.readouterr().out


# isLoggedInAsAdmin: admin is prompted for account holder name
def test_admin_prompted_for_account_holder(admin_session, mock_input):
    mock_input("John Doe", "1", "100.00")  # admin supplies holder name first
    assert withdrawal(admin_session) is not None

def test_standard_user_not_prompted_for_account_holder(standard_session, mock_input):
    mock_input("1", "100.00")  # standard uses session name, no holder prompt
    assert withdrawal(standard_session) is not None


# zeroDollarWithdrawal: $0.00 is rejected
# (supply a valid amount afterward so the re-prompt loop can exit)
def test_zero_withdrawal_rejected(standard_session, mock_input, capsys):
    mock_input("1", "0", "100.00")
    withdrawal(standard_session)
    assert "ERROR: Amount must be greater than $0.00" in capsys.readouterr().out


# negativeDollarWithdrawal: negative amount is rejected
def test_negative_withdrawal_rejected(standard_session, mock_input, capsys):
    mock_input("1", "-50", "100.00")
    withdrawal(standard_session)
    assert "ERROR: Amount must be greater than $0.00" in capsys.readouterr().out


# aboveLimitWithdrawal: amount above $500 session limit is rejected
def test_above_limit_withdrawal_rejected(standard_session, mock_input, capsys):
    mock_input("1", "600.00")
    result = withdrawal(standard_session)
    assert result is None
    assert "ERROR: Exceeds session withdrawal limit" in capsys.readouterr().out

def test_exactly_at_limit_withdrawal_accepted(standard_session, mock_input):
    mock_input("1", "500.00")  # $500 is exactly the limit
    assert withdrawal(standard_session) is not None


# overdrawWithdrawal: amount that would leave balance < $0 is rejected
def test_overdraw_withdrawal_rejected(standard_session, mock_input, capsys):
    AccountsList.accounts[0]["balance"] = 200.00
    mock_input("1", "300.00")  # $300 > $200 balance
    result = withdrawal(standard_session)
    assert result is None
    assert "ERROR: Insufficient funds" in capsys.readouterr().out


# balanceAboveMinimum: balance stays >= $0 after a valid withdrawal
def test_exact_balance_withdrawal_leaves_zero(standard_session, mock_input):
    AccountsList.accounts[0]["balance"] = 200.00
    mock_input("1", "200.00")  # withdraw exactly the full balance
    assert withdrawal(standard_session) is not None
    assert AccountsList.accounts[0]["balance"] == 0.00

def test_overdraw_withdrawal_balance_unchanged(standard_session, mock_input, capsys):
    AccountsList.accounts[0]["balance"] = 100.00
    mock_input("1", "150.00")
    withdrawal(standard_session)
    assert AccountsList.accounts[0]["balance"] == 100.00  # unchanged after rejection


# savesWithdrawalInfo: successful withdrawal is saved to the transaction log
def test_successful_withdrawal_logged(standard_session, mock_input):
    mock_input("1", "250.00")
    withdrawal(standard_session)
    assert len(standard_session.log.transactions) == 1
    logged = standard_session.log.transactions[0]
    assert logged["code"] == "01"
    assert logged["accountNumber"] == "00001"
    assert logged["money"] == "00250.00"

def test_failed_withdrawal_not_logged(standard_session, mock_input):
    mock_input("1", "600.00")  # over limit - will be rejected
    withdrawal(standard_session)
    assert len(standard_session.log.transactions) == 0
