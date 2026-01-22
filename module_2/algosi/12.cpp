
// Вычислить сумму: 1 - 1/2 + 1/3 - 1/4 + ... + (-1)^{n+1}/n
// Алгоритм O(n), реализован без использования if.

#include <bits/stdc++.h>
using namespace std;

int main() {
	long long n;
	if (!(cin >> n)) return 0;
	double sum = 0.0;
	double sign = 1.0;
	for (long long k = 1; k <= n; ++k) {
		sum += sign / static_cast<double>(k);
		sign = -sign;
	}
	// Вывод с разумной точностью
	cout << fixed << setprecision(12) << sum << '\n';
	return 0;
}

