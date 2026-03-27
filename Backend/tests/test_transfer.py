from transactions import transfer
from lists import AccountsList
import pytest

def test_T1_TO_account_not_found(accounts_list, capsys):
    transaction = {'code': '01', 'accountName': 'John Doe', 'accountNumber': '99999', 'money': 50, 'misc': ''}
    assert transfer(transaction, accounts_list) is False
    assert f"ERROR: Transfer failed – TO account {transaction['accountNumber']} not found." in capsys.readouterr().out

def test_T2_TO_account_disabled(accounts_list, capsys):
    transaction = {'code': '01', 'accountName': 'John Doe', 'accountNumber': '00004', 'money': 50, 'misc': ''}
    assert transfer(transaction, accounts_list) is False
    assert f"ERROR: Transfer failed – TO account {transaction['accountNumber']} is disabled." in capsys.readouterr().out

def test_T3_FROM_account_name_not_found(accounts_list, capsys):
    transaction = {'code': '01', 'accountName': 'Ghost User', 'accountNumber': '00002', 'money': 50, 'misc': ''}
    assert transfer(transaction, accounts_list) is False
    assert f"ERROR: Transfer failed – no active account found for holder '{transaction['accountName']}' to transfer from." in capsys.readouterr().out

def test_T4_name_matches_are_disabled(accounts_list, capsys):
    transaction = {'code': '01', 'accountName': 'Alice Williams', 'accountNumber': '00002', 'money': 50, 'misc': ''}
    assert transfer(transaction, accounts_list) is False
    assert f"ERROR: Transfer failed – no active account found for holder '{transaction['accountName']}' to transfer from." in capsys.readouterr().out

def test_T5_FROM_insufficient_balance(accounts_list, capsys):
    transaction = {'code': '01', 'accountName': 'Bob Johnson', 'accountNumber': '00002', 'money': 750, 'misc': ''}
    assert transfer(transaction, accounts_list) is False
    assert f"ERROR: Transfer of $750.00 from account 00003 would cause a negative balance – transaction skipped." in capsys.readouterr().out

def test_T6_boundary_exact_from_depletion(accounts_list):
    transaction = {'code': '01', 'accountName': 'Bob Johnson', 'accountNumber': '00002', 'money': 749.90, 'misc': ''}
    assert transfer(transaction, accounts_list) is True

def test_T7_successful_transfer_np(accounts_list):
    transaction = {'code': '01', 'accountName': 'John Doe', 'accountNumber': '00002', 'money': 200, 'misc': ''}
    assert transfer(transaction, accounts_list) is True

def test_T8_loop_coverage_0_runs(empty_accounts_list, capsys):
    transaction = {'code': '01', 'accountName': 'John Doe', 'accountNumber': '00003', 'money': 50, 'misc': ''}
    assert transfer(transaction, empty_accounts_list) is False
    assert f"ERROR: Transfer failed – no active account found for holder '{transaction['accountName']}' to transfer from." in capsys.readouterr().out

def test_T9_loop_coverage_0_runs(accounts_list):
    transaction = {'code': '01', 'accountName': 'John Doe', 'accountNumber': '00003', 'money': 50, 'misc': ''}
    assert transfer(transaction, accounts_list) is True

def test_T10_loop_coverage_0_runs(accounts_list):
    transaction = {'code': '01', 'accountName': 'Jane Smith', 'accountNumber': '00003', 'money': 50, 'misc': ''}
    assert transfer(transaction, accounts_list) is True

def test_T11_loop_coverage_0_runs(accounts_list):
    transaction = {'code': '01', 'accountName': 'Charlie Brown', 'accountNumber': '00003', 'money': 50, 'misc': ''}
    assert transfer(transaction, accounts_list) is True