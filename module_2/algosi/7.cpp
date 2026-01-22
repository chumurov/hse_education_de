
// Дано трёхзначное число. Найдите сумму его цифр.

#include <bits/stdc++.h>
using namespace std;

int main() {
	int n;
	if (!(cin >> n)) return 0;
	int sum = 0;
	while (n > 0) {
		sum += n % 10;
		n /= 10;
	}
	cout << sum << '\n';
	return 0;
}

