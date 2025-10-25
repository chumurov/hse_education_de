import os
from datetime import datetime
import pytest

from dz5 import SavingsAccount, CheckingAccount, Account

ROOT = os.path.abspath(os.path.dirname(__file__) + '/..')
CSV_PATH = os.path.join(ROOT, 'transactions_dirty.csv')
JSON_PATH = os.path.join(ROOT, 'transactions_dirty.json')


def test_clean_history_filters_bad():
    a = SavingsAccount('Alice Smith', 0)
    # create some good and bad sample rows
    rows = [
        {'account_number': a.account_number, 'operation': 'deposit', 'amount': '100.0', 'date': '2025-10-01 12:00:00', 'balance_after': '100.0', 'status': 'success'},
        {'account_number': a.account_number, 'operation': 'diposit', 'amount': '50.0', 'date': '2025-10-01 12:00:00', 'balance_after': '150.0', 'status': 'success'},
        {'account_number': a.account_number, 'operation': 'withdraw', 'amount': '-20', 'date': '2025-10-01 12:01:00', 'balance_after': '130.0', 'status': 'success'},
        {'account_number': a.account_number, 'operation': 'interest', 'amount': None, 'date': '2025-10-02 12:00:00', 'balance_after': '140.0', 'status': 'success'},
        {'account_number': a.account_number, 'operation': 'deposit', 'amount': 'abc', 'date': '2025-10-02 12:00:00', 'balance_after': '140.0', 'status': 'success'},
        {'account_number': a.account_number, 'operation': 'deposit', 'amount': '50.0', 'date': '01/10/2025 12:00', 'balance_after': '190.0', 'status': 'success'},
    ]

    cleaned = a.clean_history(rows)
    # Expect only the valid deposit 100 and deposit 50 (last one has dd/mm format allowed)
    assert len(cleaned) == 2
    assert all(isinstance(r['datetime'], datetime) for r in cleaned)
    assert all(r['amount'] >= 0 for r in cleaned)
    assert cleaned[0]['type'] == 'deposit'


def test_load_history_csv_savings_updates_balance_and_filters():
    s = SavingsAccount('Bob Brown', 0)
    # Force account_number to one present in the dirty CSV
    s.account_number = 'ACC-100002'
    s.load_history(CSV_PATH)

    assert len(s.operations_history) > 0
    # Проверяем, что все операции допустимые для savings
    allowed = {'deposit', 'withdraw', 'interest'}
    assert all(op['type'] in allowed for op in s.operations_history)
    # Нет отрицательных сумм
    assert all(op['amount'] >= 0 for op in s.operations_history)
    # Даты распарсены
    assert all(isinstance(op['datetime'], datetime) for op in s.operations_history)
    # Баланс аккаунта соответствует последней записи
    assert pytest.approx(s.get_balance(), rel=1e-9) == s.operations_history[-1]['balance']


def test_load_history_json_checking_filters_interest():
    c = CheckingAccount('Carl Jones', 0)
    c.account_number = 'ACC-100001'
    # load from json (file included)
    c.load_history(JSON_PATH)

    assert len(c.operations_history) > 0
    # Checking account should not have 'interest' operations after cleaning
    assert all(op['type'] in {'deposit', 'withdraw'} for op in c.operations_history)
    # balance updated
    assert pytest.approx(c.get_balance(), rel=1e-9) == c.operations_history[-1]['balance']
