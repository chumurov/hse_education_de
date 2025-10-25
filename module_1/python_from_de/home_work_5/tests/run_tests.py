import os
import sys
from datetime import datetime

# Ensure project root is importable when running this script from tests/
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from dz5 import SavingsAccount, CheckingAccount

CSV_PATH = os.path.join(ROOT, 'transactions_dirty.csv')
JSON_PATH = os.path.join(ROOT, 'transactions_dirty.json')


def test_clean_history_filters_bad():
    a = SavingsAccount('Alice Smith', 0)
    rows = [
        {'account_number': a.account_number, 'operation': 'deposit', 'amount': '100.0', 'date': '2025-10-01 12:00:00', 'balance_after': '100.0', 'status': 'success'},
        {'account_number': a.account_number, 'operation': 'diposit', 'amount': '50.0', 'date': '2025-10-01 12:00:00', 'balance_after': '150.0', 'status': 'success'},
        {'account_number': a.account_number, 'operation': 'withdraw', 'amount': '-20', 'date': '2025-10-01 12:01:00', 'balance_after': '130.0', 'status': 'success'},
        {'account_number': a.account_number, 'operation': 'interest', 'amount': None, 'date': '2025-10-02 12:00:00', 'balance_after': '140.0', 'status': 'success'},
        {'account_number': a.account_number, 'operation': 'deposit', 'amount': 'abc', 'date': '2025-10-02 12:00:00', 'balance_after': '140.0', 'status': 'success'},
        {'account_number': a.account_number, 'operation': 'deposit', 'amount': '50.0', 'date': '01/10/2025 12:00', 'balance_after': '190.0', 'status': 'success'},
    ]

    cleaned = a.clean_history(rows)
    assert len(cleaned) == 2
    assert all(isinstance(r['datetime'], datetime) for r in cleaned)
    assert all(r['amount'] >= 0 for r in cleaned)


def test_load_history_csv_savings_updates_balance_and_filters():
    s = SavingsAccount('Bob Brown', 0)
    s.account_number = 'ACC-100002'
    s.load_history(CSV_PATH)

    assert len(s.operations_history) > 0
    allowed = {'deposit', 'withdraw', 'interest'}
    assert all(op['type'] in allowed for op in s.operations_history)
    assert all(op['amount'] >= 0 for op in s.operations_history)
    assert all(isinstance(op['datetime'], datetime) for op in s.operations_history)
    assert s.get_balance() == s.operations_history[-1]['balance']


def test_load_history_json_checking_filters_interest():
    c = CheckingAccount('Carl Jones', 0)
    c.account_number = 'ACC-100001'
    c.load_history(JSON_PATH)

    assert len(c.operations_history) > 0
    assert all(op['type'] in {'deposit', 'withdraw'} for op in c.operations_history)
    assert c.get_balance() == c.operations_history[-1]['balance']


if __name__ == '__main__':
    print('Running simple tests...')
    test_clean_history_filters_bad()
    print('test_clean_history_filters_bad OK')
    test_load_history_csv_savings_updates_balance_and_filters()
    print('test_load_history_csv_savings_updates_balance_and_filters OK')
    test_load_history_json_checking_filters_interest()
    print('test_load_history_json_checking_filters_interest OK')
    print('All tests passed')
