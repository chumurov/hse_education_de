// Печатать таблицу умножения для 1..n по модулю m. Заголовки в первой строке и столбце.

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, m;
    if (!(cin >> n >> m)) return 0;
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
            cout << ((i * j) % m);
        }
        cout << '\n';
    }
    return 0;
}
