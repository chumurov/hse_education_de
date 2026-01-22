
// По номеру дня недели (1..7) вывести сокращённое название: mon, tue, wed, thu, fri, sat, sun

#include <bits/stdc++.h>
using namespace std;

int main() {
	int d;
	if (!(cin >> d)) return 0;
	unordered_map<int, string> m {
		{1, "mon"}, {2, "tue"}, {3, "wed"}, {4, "thu"},
		{5, "fri"}, {6, "sat"}, {7, "sun"}
	};
	auto it = m.find(d);
	if (it != m.end()) cout << it->second << '\n';
	return 0;
}

