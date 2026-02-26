# Tests for the Transfer transaction.
# Input order - standard: from_account_number, to_account_number, amount
#             - admin:    account_holder, from_account_number, to_account_number, amount

from transactions import transfer
from utils import AccountsList

# validSenderAccount: account owned by the logged-in user is accepted as sender
def test_valid_sender_account_accepted(standard_session, mock_input):
    mock_input("1", "2", "100.00")  # account 1 belongs to John Doe
    result = transfer(standard_session)
    assert result is not None
    assert result["code"] == "02"


# invalidSenderAccount: account not owned by the logged-in user is rejected
def test_invalid_sender_account_rejected(standard_session, mock_input, capsys):
    mock_input("2", "1", "100.00")  # account 2 belongs to Jane Smith
    result = transfer(standard_session)
    assert result is None
    assert "ERROR: Source account not found or not owned by account holder" in capsys.readouterr().out


# validRecieverAccount: existing account is accepted as destination
def test_valid_receiver_account_accepted(standard_session, mock_input):
    mock_input("1", "2", "100.00")  # send from acc 1 to acc 2
    transfer(standard_session)
    receiver = next(a for a in AccountsList.accounts if a["accountNumber"] == 2)
    assert receiver["balance"] == 2600.00  # 2500 + 100


# invalidRecieverAccount: non-existent account number is rejected
def test_invalid_receiver_account_rejected(standard_session, mock_input, capsys):
    mock_input("1", "999", "100.00")  # account 999 does not exist
    result = transfer(standard_session)
    assert result is None
    assert "ERROR: Destination account not found" in capsys.readouterr().out


# duplicateSenderReciever: same account for sender and receiver
# Current implementation allows it; net balance change is zero.
def test_same_account_sender_and_receiver(standard_session, mock_input):
    original_balance = AccountsList.accounts[0]["balance"]
    mock_input("1", "1", "100.00")  # from and to are both account 1
    assert transfer(standard_session) is not None
    assert AccountsList.accounts[0]["balance"] == original_balance  # net change is zero


# zeroDollarTransfer: $0.00 is rejected
# (supply a valid amount afterward so the re-prompt loop can exit)
def test_zero_transfer_rejected(standard_session, mock_input, capsys):
    mock_input("1", "2", "0", "100.00")
    transfer(standard_session)
    assert "ERROR: Amount must be greater than $0.00" in capsys.readouterr().out


# negativeDollarTransfer: negative amount is rejected
def test_negative_transfer_rejected(standard_session, mock_input, capsys):
    mock_input("1", "2", "-50", "100.00")
    transfer(standard_session)
    assert "ERROR: Amount must be greater than $0.00" in capsys.readouterr().out


# aboveLimitTransfer: amount above $1,000 session limit is rejected for standard users
def test_above_limit_transfer_rejected(standard_session, mock_input, capsys):
    mock_input("1", "2", "1500.00")
    result = transfer(standard_session)
    assert result is None
    assert "ERROR: Exceeds session transfer limit" in capsys.readouterr().out

def test_exactly_at_limit_transfer_accepted(standard_session, mock_input):
    mock_input("1", "2", "1000.00")  # $1,000 is exactly the limit
    assert transfer(standard_session) is not None


# aboveLimitTransferAdmin: the same amount is allowed when admin is logged in
def test_admin_can_transfer_above_standard_limit(admin_session, mock_input):
    # Charlie Brown (account 5, $5,000) is used so the balance covers the amount
    mock_input("Charlie Brown", "5", "2", "1500.00")
    assert transfer(admin_session) is not None

def test_admin_transfer_limit_is_infinite(admin_session):
    assert admin_session.transactionLimits["transfer"] == float("inf")


# overdrawTransfer: amount exceeding the sender's balance is rejected
def test_overdraw_transfer_rejected(standard_session, mock_input, capsys):
    AccountsList.accounts[0]["balance"] = 50.00
    mock_input("1", "2", "100.00")  # $100 > $50 balance
    result = transfer(standard_session)
    assert result is None
    assert "ERROR: Insufficient funds in source account" in capsys.readouterr().out

def test_overdraw_transfer_leaves_balance_unchanged(standard_session, mock_input):
    AccountsList.accounts[0]["balance"] = 50.00
    mock_input("1", "2", "100.00")
    transfer(standard_session)
    assert AccountsList.accounts[0]["balance"] == 50.00  # unchanged after rejection
