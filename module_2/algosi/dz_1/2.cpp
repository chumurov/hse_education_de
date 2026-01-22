
// Проверить корректность двойного неравенства A < B < C
// Ввод: три целых числа A, B, C (в диапазоне [-1000, 1000])
// Вывод: 1, если A < B < C, иначе 0

#include <bits/stdc++.h>
using namespace std;

int main() {
	int A, B, C;
	if (!(cin >> A >> B >> C)) return 0;
	cout << ( (A < B && B < C) ? 1 : 0 ) << '\n';
	return 0;
}

