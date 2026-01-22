// Вычислить длину гипотенузы прямоугольного треугольника с катетами a и b.

#include <bits/stdc++.h>
using namespace std;

int main() {
    double a, b;
    if (!(cin >> a >> b)) return 0;
    double c = sqrt(a * a + b * b);
    cout << fixed << setprecision(6) << c << '\n';
    return 0;
}
