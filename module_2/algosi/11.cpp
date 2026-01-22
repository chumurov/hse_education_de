// Калькулятор на основе switch. Условный оператор if не используется.

#include <bits/stdc++.h>
using namespace std;

int main() {
    int code;
    double a, b;
    cin >> code >> a >> b;
    double res = 0.0;
    switch (code) {
        case 0:
            res = a + b;
            break;
        case 1:
            res = a - b;
            break;
        case 2:
            res = a * b;
            break;
        case 3:
            res = a / b;
            break;
        case 4:
            res = pow(a, b);
            break;
        case 5:
            res = pow(a, 1.0 / b);
            break;
        default:
            cout << -1 << '\n';
            return 0;
    }
    cout << res << '\n';
    return 0;
}
