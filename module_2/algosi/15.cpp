
// Читает целое число и выводит две строки в формате:
// The next number for the number <n> is <n+1>.
// The previous number for the number <n> is <n-1>.

#include <bits/stdc++.h>
using namespace std;

int main() {
	int n;
	if (!(cin >> n)) return 0;
	cout << "The next number for the number " << n << " is " << (n + 1) << "." << '\n';
	cout << "The previous number for the number " << n << " is " << (n - 1) << "." << '\n';
	return 0;
}

