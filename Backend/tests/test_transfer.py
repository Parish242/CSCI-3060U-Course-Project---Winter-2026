from transactions import transfer
from lists import AccountsList
import pytest

def test_W1_account_not_found(accounts_list, capsys):
    transaction = {'code': '02', 'accountName': 'Hugh Mann', 'accountNumber': '99999', 'money': 50, 'misc': ''}
    assert transfer(transaction, accounts_list) is False
    assert f"ERROR: Transfer failed – TO account {transaction['accountNumber']} not found." in capsys.readouterr().out

def test_W2_account_disabled(accounts_list, capsys):
    transaction = {'code': '02', 'accountName': 'Alice Williams', 'accountNumber': '00004', 'money': 50, 'misc': ''}
    assert transfer(transaction, accounts_list) is False
    assert f"ERROR: Transfer failed – TO account {transaction['accountNumber']} is disabled." in capsys.readouterr().out

def test_W3_insufficient_balance(accounts_list, capsys):
    transaction = {'code': '02', 'accountName': 'Bob Johnson', 'accountNumber': '00001', 'money': 750, 'misc': ''}
    assert transfer(transaction, accounts_list) is False
    assert f"ERROR: Transfer of $750.00 from account 00003 would cause a negative balance – transaction skipped." in capsys.readouterr().out

def test_W4_boundary_exact_depletion(accounts_list):
    transaction = {'code': '02', 'accountName': 'Bob Johnson', 'accountNumber': '00001', 'money': 749.90, 'misc': ''}
    assert transfer(transaction, accounts_list) is True
    assert accounts_list.current_accounts[2]["balance"] == 0.00

def test_W5_successful_withdrawal_np(accounts_list):
    transaction = {'code': '02', 'accountName': 'John Doe', 'accountNumber': '00002', 'money': 200, 'misc': ''}
    assert transfer(transaction, accounts_list) is True
    assert accounts_list.current_accounts[0]["balance"] == 799.90

def test_W6_successful_withdrawal_sp(accounts_list):
    transaction = {'code': '02', 'accountName': 'Charlie Brown', 'accountNumber': '00001', 'money': 50, 'misc': ''}
    assert transfer(transaction, accounts_list) is True
    assert accounts_list.current_accounts[4]["balance"] == 4949.95