
// Считывает последовательность направлений и шагов и выводит координаты конечной точки.

#include <bits/stdc++.h>
using namespace std;

int main() {
	string dir;
	long long steps;
	long long x = 0, y = 0;
	while (cin >> dir >> steps) {
		if (dir == "North") y += steps;
		else if (dir == "South") y -= steps;
		else if (dir == "East") x += steps;
		else if (dir == "West") x -= steps;
	}
	cout << x << " " << y << '\n';
	return 0;
}

