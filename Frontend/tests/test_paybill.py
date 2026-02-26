# Tests for the Paybill transaction.
# Input order - standard: account_number, company_code, amount
#             - admin:    account_holder, account_number, company_code, amount

from transactions import paybill
from utils import AccountsList

# validAccountHolder: account owned by the logged-in user is accepted
def test_valid_account_holder_accepted(standard_session, mock_input):
    mock_input("1", "EC", "50.00")  # account 1 belongs to John Doe
    result = paybill(standard_session)
    assert result is not None
    assert result["code"] == "03"


# invalidAccountHolder: account belonging to a different user is rejected
def test_wrong_account_holder_rejected(standard_session, mock_input, capsys):
    mock_input("2", "EC", "50.00")  # account 2 belongs to Jane Smith
    result = paybill(standard_session)
    assert result is None
    assert "ERROR: Account not found" in capsys.readouterr().out


# validAccountNumber: correct account number is accepted
def test_valid_account_number_accepted(standard_session, mock_input):
    mock_input("1", "EC", "50.00")
    result = paybill(standard_session)
    assert result is not None
    assert result["accountNumber"] == "00001"


# invalidAccountNumber: non-existent account number is rejected
def test_invalid_account_number_rejected(standard_session, mock_input, capsys):
    mock_input("999", "EC", "50.00")  # account 999 does not exist
    result = paybill(standard_session)
    assert result is None
    assert "ERROR: Account not found" in capsys.readouterr().out


# validPaymentCompany: each valid company code is accepted
def test_company_code_EC_accepted(standard_session, mock_input):
    mock_input("1", "EC", "50.00")
    result = paybill(standard_session)
    assert result is not None
    assert result["misc"].strip() == "EC"

def test_company_code_CQ_accepted(standard_session, mock_input):
    mock_input("1", "CQ", "50.00")
    result = paybill(standard_session)
    assert result is not None
    assert result["misc"].strip() == "CQ"

def test_company_code_FI_accepted(standard_session, mock_input):
    mock_input("1", "FI", "50.00")
    result = paybill(standard_session)
    assert result is not None
    assert result["misc"].strip() == "FI"


# invalidPaymentCompany: invalid company code is rejected
# (supply a valid code afterward so the re-prompt loop can exit)
def test_invalid_company_code_rejected(standard_session, mock_input, capsys):
    mock_input("1", "HYDRO", "EC", "50.00")  # HYDRO invalid; EC valid
    paybill(standard_session)
    assert "ERROR: Invalid company code" in capsys.readouterr().out

def test_lowercase_company_code_accepted(standard_session, mock_input):
    mock_input("1", "ec", "50.00")  # should be normalised to uppercase
    assert paybill(standard_session) is not None


# validBillPayment: valid payment is accepted and balance is decremented
def test_valid_payment_decrements_balance(standard_session, mock_input):
    mock_input("1", "EC", "100.00")
    assert paybill(standard_session) is not None
    assert AccountsList.accounts[0]["balance"] == 900.00  # 1000 - 100


# overpayment: amount exceeding the account balance is rejected
def test_overpayment_rejected(standard_session, mock_input, capsys):
    AccountsList.accounts[0]["balance"] = 50.00
    mock_input("1", "EC", "100.00")  # $100 > $50 balance
    result = paybill(standard_session)
    assert result is None
    assert "ERROR: Insufficient funds" in capsys.readouterr().out


# zeroDollarPayment: $0.00 is rejected
def test_zero_payment_rejected(standard_session, mock_input, capsys):
    mock_input("1", "EC", "0", "50.00")
    paybill(standard_session)
    assert "ERROR: Amount must be greater than $0.00" in capsys.readouterr().out


# negativeDollarPayment: negative amount is rejected
def test_negative_payment_rejected(standard_session, mock_input, capsys):
    mock_input("1", "EC", "-20", "50.00")
    paybill(standard_session)
    assert "ERROR: Amount must be greater than $0.00" in capsys.readouterr().out


# aboveMaxPayment: amount above $2,000 session limit is rejected
def test_above_limit_payment_rejected(standard_session, mock_input, capsys):
    mock_input("1", "EC", "2500.00")
    result = paybill(standard_session)
    assert result is None
    assert "ERROR: Exceeds session paybill limit" in capsys.readouterr().out

def test_exactly_at_limit_payment_accepted(standard_session, mock_input):
    AccountsList.accounts[0]["balance"] = 3000.00  # ensure enough funds
    mock_input("1", "EC", "2000.00")  # $2,000 is exactly the limit
    assert paybill(standard_session) is not None


# isLoggedInAsAdmin: admin is prompted for account holder name
def test_admin_prompted_for_account_holder(admin_session, mock_input):
    mock_input("John Doe", "1", "EC", "100.00")  # admin supplies holder name first
    assert paybill(admin_session) is not None

def test_standard_user_not_prompted_for_account_holder(standard_session, mock_input):
    mock_input("1", "EC", "100.00")  # standard uses session name, no holder prompt
    assert paybill(standard_session) is not None


# balanceAboveMinimum: balance stays >= $0 after a valid payment
def test_exact_balance_payment_leaves_zero(standard_session, mock_input):
    AccountsList.accounts[0]["balance"] = 100.00
    mock_input("1", "EC", "100.00")  # pay exactly the full balance
    assert paybill(standard_session) is not None
    assert AccountsList.accounts[0]["balance"] == 0.00

def test_payment_below_zero_rejected(standard_session, mock_input, capsys):
    AccountsList.accounts[0]["balance"] = 50.00
    mock_input("1", "EC", "75.00")  # would leave -$25
    result = paybill(standard_session)
    assert result is None
    assert "ERROR: Insufficient funds" in capsys.readouterr().out


# savesWithdrawalInfo: successful paybill is saved to the transaction log
def test_successful_paybill_logged(standard_session, mock_input):
    mock_input("1", "EC", "100.00")
    paybill(standard_session)
    assert len(standard_session.log.transactions) == 1
    logged = standard_session.log.transactions[0]
    assert logged["code"] == "03"
    assert logged["accountNumber"] == "00001"
    assert logged["money"] == "00100.00"
    assert logged["misc"].strip() == "EC"

def test_failed_paybill_not_logged(standard_session, mock_input):
    mock_input("1", "EC", "3000.00")  # over limit - will be rejected
    paybill(standard_session)
    assert len(standard_session.log.transactions) == 0
