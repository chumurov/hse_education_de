// Напечатать таблицу сумм: на пересечении i-й строки и j-го столбца — i+j.
// В начальной строке и столбце — номера 1..n. Разделитель — символ табуляции.

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n;
    if (!(cin >> n)) return 0;
    // первая (заголовочная) строка: пустое поле, затем 1..n
    cout << '\t';
    for (int j = 1; j <= n; ++j) {
        if (j > 1) cout << '\t';
        cout << j;
    }
    cout << '\n';

    for (int i = 1; i <= n; ++i) {
        cout << i << '\t';
        for (int j = 1; j <= n; ++j) {
            if (j > 1) cout << '\t';
            cout << (i + j);
        }
        cout << '\n';
    }
    return 0;
}
