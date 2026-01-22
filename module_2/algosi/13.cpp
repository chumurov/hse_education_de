// По данным натуральным числам n и a вычислите сумму
// sqrt(a) + sqrt(2a) + ... + sqrt(na)

#include <bits/stdc++.h>
using namespace std;

int main() {
    long long n, a;
    if (!(cin >> n >> a)) return 0;
    double sum = 0.0;
    for (long long k = 1; k <= n; ++k) {
        sum += sqrt(static_cast<double>(k) * a);
    }
    cout << fixed << setprecision(12) << sum << '\n';
    return 0;
}
