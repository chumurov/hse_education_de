// Вася изучает C++. Нужно определить среднее арифметическое двух вещественных чисел.

#include <bits/stdc++.h>
using namespace std;

int main() {
    double a, b;
    if (!(cin >> a >> b)) return 0;
    double ans = (a + b) / 2.0;
    cout << fixed << setprecision(6) << ans << '\n';
    return 0;
}
