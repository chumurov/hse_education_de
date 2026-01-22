
// Имеется N кг сплава. Изготавливают заготовки по K кг, затем из каждой заготовки
// вытачивают детали по M кг. Остатки сплавляют и повторяют цикл, пока можно сделать
// хотя бы одну заготовку. Вычислить максимальное число деталей.

#include <bits/stdc++.h>
using namespace std;

int main() {
	int N, K, M;
	if (!(cin >> N >> K >> M)) return 0;
	if (K < M) { // из заготовки нельзя получить ни одной детали
		cout << 0 << '\n';
		return 0;
	}
	int parts = 0;
	int available = N;
	while (available >= K) {
		int blanks = available / K;
		int parts_per_blank = K / M;
		parts += blanks * parts_per_blank;
		int leftover = available % K + blanks * (K % M);
		available = leftover;
	}
	cout << parts << '\n';
	return 0;
}

