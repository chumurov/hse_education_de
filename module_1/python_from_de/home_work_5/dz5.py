import re
from datetime import datetime


class Account:
    """Базовый класс банковского счёта  Этап 2.
    """
    # Приватный счётчик на уровне класса, начинается с 1000
    _account_counter = 1000

    def __init__(self, account_holder: str, balance: float = 0.0):
        # Валидация начального баланса
        if balance < 0:
            raise ValueError('Начальный баланс не может быть отрицательным.')

        # Валидация имени владельца: "Имя Фамилия" с заглавных букв (кириллица или латиница)
        # Поддерживаем буквы A-Z, a-z и кириллический диапазон (А-Я, а-я, Ёё)
        name_pattern = re.compile(r'^[A-ZА-ЯЁ][a-zа-яё]+ [A-ZА-ЯЁ][a-zа-яё]+$')
        if not isinstance(account_holder, str) or not name_pattern.match(account_holder):
            raise ValueError('Имя владельца должно быть в формате "Имя Фамилия" с заглавных букв.')

        # Присвоение номера счёта по счётчику и инкремент счётчика
        Account._account_counter += 1
        self.account_number = f'ACC-{Account._account_counter:04}'
        self.holder = account_holder

        # Приватный баланс и история операций
        self._balance = float(balance)
        self.operations_history = []

    def __repr__(self) -> str:
        return (f'Account(holder={self.holder!r}, '
                f'balance={self._balance:.2f})')

    def _record_operation(self, op_type: str, amount: float, status: str) -> None:
        "Вспомогательный метод для записи операции в историю"
        self.operations_history.append({
            'type': op_type,
            'amount': float(amount),
            'datetime': datetime.now(),
            'balance': float(self._balance),
            'status': status
        })

    def deposit(self, amount: float) -> None:
        "Пополнение счёта. При отрицательной сумме -- исключение."
        if amount <= 0:
            raise ValueError('Депозит должен быть положительным')

        self._balance += float(amount)
        self._record_operation('deposit', amount, 'success')

    def withdraw(self, amount: float) -> None:
        "Снятие со счёта. При недостатке средств операция фиксируется как 'fail'."
        if amount <= 0:
            raise ValueError('Снятие должно быть положительным')

        if amount <= self._balance:
            self._balance -= float(amount)
            self._record_operation('withdraw', amount, 'success')
        else:
            # Фиксируем неудачную попытку снятия, баланс не меняется
            self._record_operation('withdraw', amount, 'fail')

    def get_balance(self) -> float:
        return float(self._balance)

    def get_history(self):
        # Возвращаем копию истории, чтобы внешние изменения не влияли на внутреннее состояние
        return list(self.operations_history)
    
    def plot_history(self):
        import pandas as pd
        import plotly.express as px
        # Создайте метод `plot_history(self)`, который использует библиотеку Pandas для создания датафрейма из истории операций.
        df = pd.DataFrame(self.operations_history)
        fig = px.line(df, x='datetime', y='balance',  title='История операций')
        # Подписи осей
        fig.update_layout(xaxis_title='Дата и время', yaxis_title='Баланс')

        fig.show()

    def get_top_transactions(self, n: int = 5):
        """Возвращает список из последних n крупных операций.

        Сначала сортируем по абсолютной величине суммы (amount) по убыванию,
        затем по дате (datetime) по убыванию, чтобы при равных суммах
        возвращались более свежие операции.
        """
        if not isinstance(n, int) or n <= 0:
            raise ValueError('n должно быть положительным целым числом')

        # Сортируем копию списка, чтобы не менять внутреннее состояние
        sorted_ops = sorted(
            self.operations_history,
            key=lambda op: (abs(op.get('amount', 0)), op.get('datetime')),
            reverse=True
        )
        return list(sorted_ops[:n])

    @staticmethod
    def _parse_date_str(date_str: str):
        """Пробуем распарсить дату в разных форматах, возвращаем datetime или None."""
        if not date_str:
            return None
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%d/%m/%Y %H:%M',
            '%d/%m/%Y %H:%M:%S',
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except Exception:
                continue
        return None

    @staticmethod
    def _read_transactions_from_file(file_path: str):
        """Читает CSV или JSON файл транзакций и возвращает список словарей."""
        import os
        import csv
        import json

        ext = os.path.splitext(file_path)[1].lower()
        rows = []
        if ext == '.csv':
            with open(file_path, newline='', encoding='utf-8') as fh:
                reader = csv.DictReader(fh)
                for r in reader:
                    # Normalize keys to expected names
                    rows.append(r)
        elif ext == '.json':
            with open(file_path, encoding='utf-8') as fh:
                rows = json.load(fh)
        else:
            raise ValueError('Unsupported file format: ' + ext)
        return rows

    def clean_history(self, transactions: list) -> list:
        """Очищает список транзакций, возвращает список валидных записей в формате операции.

        Правила валидации:
        - operation должно быть допустимым для типа счёта;
        - amount не должен быть отрицательным и должен быть присутствовать (не None, не пустая строк);
        - datetime должен быть парсабельным (поддерживаем несколько форматов);
        - balance (balance_after) должно быть числом.
        Все некорректные записи отбрасываются.
        """
        valid_ops = []
        # допустимые операции в зависимости от типа счёта
        allowed = {'deposit', 'withdraw'}
        if getattr(self, 'account_type', None) == 'savings':
            allowed = {'deposit', 'withdraw', 'interest'}

        for t in transactions:
            try:
                op = t.get('operation') if isinstance(t, dict) else None
                # normalize empty strings to None
                if op == '':
                    op = None
                if op is None:
                    # missing operation — invalid
                    continue
                op = str(op).strip()
                if op not in allowed:
                    continue

                # amount
                amt_raw = t.get('amount') if isinstance(t, dict) else None
                if amt_raw == '' or amt_raw is None:
                    # missing amount — invalid
                    continue
                try:
                    amount = float(amt_raw)
                except Exception:
                    continue
                if amount < 0:
                    continue

                # date
                date_raw = t.get('date') if isinstance(t, dict) else None
                dt = self._parse_date_str(str(date_raw))
                if dt is None:
                    continue

                # balance
                bal_raw = t.get('balance_after') if 'balance_after' in t else t.get('balance')
                if bal_raw == '' or bal_raw is None:
                    continue
                try:
                    balance = float(bal_raw)
                except Exception:
                    continue

                status = t.get('status') if isinstance(t, dict) else None

                valid_ops.append({
                    'type': op,
                    'amount': float(amount),
                    'datetime': dt,
                    'balance': float(balance),
                    'status': status,
                })
            except Exception:
                # на всякий случай пропускаем проблемные записи
                continue

        # Сортируем по дате — от старых к новым
        valid_ops.sort(key=lambda x: x['datetime'])
        return valid_ops

    def load_history(self, file_path: str) -> None:
        """Загружает историю транзакций из файла (CSV или JSON) для этого аккаунта.

        Фильтрация происходит по полю account_number, обязательно в файле должно быть поле 'account_number'.
        Только валидные операции (после clean_history) добавляются в `operations_history`.
        Баланс аккаунта обновляется до последнего `balance` из валидных операций.
        """
        rows = self._read_transactions_from_file(file_path)

        # Отфильтруем по account_number равному этому счёту
        acct_num = getattr(self, 'account_number', None)
        if acct_num is None:
            return

        filtered = [r for r in rows if str(r.get('account_number')) == str(acct_num)]

        cleaned = self.clean_history(filtered)

        # Добавляем в историю (не перезаписываем, просто добавляем в конец)
        for op in cleaned:
            # Приводим к внутреннему формату
            self.operations_history.append({
                'type': op['type'],
                'amount': float(op['amount']),
                'datetime': op['datetime'],
                'balance': float(op['balance']),
                'status': op.get('status')
            })

        # Обновляем баланс до последней записи (если есть)
        if cleaned:
            self._balance = float(cleaned[-1]['balance'])


class CheckingAccount(Account):
    """Расчётный счёт — простой тип счёта без дополнительных ограничений."""
    account_type = 'checking'


class SavingsAccount(Account):
    """Сберегательный счёт: начисление процентов и ограничение снятия до 50% баланса."""
    account_type = 'savings'

    def apply_interest(self, rate: float) -> None:
        """Начисляет проценты на текущий остаток.

        rate — годовая ставка или процент в процентах (например, 7 для 7%).
        Метод просто применяет указанный процент к текущему балансу и
        записывает операцию типа 'interest'.
        """
        try:
            rate_val = float(rate)
        except Exception:
            raise ValueError('rate должен быть числом')

        # Рассчитываем как процент от текущего баланса
        interest = self._balance * (rate_val / 100.0)
        # Пополняем счёт на сумму процентов (может быть 0)
        if interest != 0:
            self._balance += interest
            self._record_operation('interest', interest, 'success')

    def withdraw(self, amount: float) -> None:
        """Снятие: нельзя снимать больше 50% от текущего баланса.

        При попытке снять отрицательную сумму — исключение.
        Если превышен порог (50%), операция фиксируется как 'fail' и
        выбрасывается исключение.
        """
        if amount <= 0:
            raise ValueError('Снятие должно быть положительным')

        # Максимально допустимая сумма снятия — 50% от текущего баланса
        max_allowed = 0.5 * self._balance
        if amount > max_allowed:
            # Фиксируем неудачную попытку снятия, баланс не меняется
            self._record_operation('withdraw', amount, 'fail')
            raise ValueError('Нельзя снять больше 50% баланса для сберегательного счёта.')

        # Иначе используем поведение базового класса для проверки остатка и записи операции
        if amount <= self._balance:
            self._balance -= float(amount)
            self._record_operation('withdraw', amount, 'success')
        else:
            self._record_operation('withdraw', amount, 'fail')
