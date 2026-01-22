// Печать блоков таблицы умножения для m в [m1,m2] и n в [n1,n2]

#include <bits/stdc++.h>
using namespace std;

int main() {
    int m1, m2, n1, n2;
    if (!(cin >> m1 >> m2 >> n1 >> n2)) return 0;
    for (int m = m1; m <= m2; ++m) {
        for (int n = n1; n <= n2; ++n) {
            cout << m << " * " << n << " = " << (m * n) << '\n';
        }
        if (m != m2) cout << '\n';
    }
    return 0;
}
