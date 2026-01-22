// Дана строка, состоящая из слов, разделённых пробелами (нет повторяющихся пробелов).
// Определить количество слов.

#include <bits/stdc++.h>
using namespace std;

int main() {
    string s;
    if (!getline(cin, s)) return 0;
    size_t l = s.find_first_not_of(' ');
    if (l == string::npos) { 
        cout << 0 << '\n';
        return 0;
    }
    size_t r = s.find_last_not_of(' ');
    int cnt = 1;
    for (size_t i = l; i <= r; ++i) if (s[i] == ' ') ++cnt;
    cout << cnt << '\n';
    return 0;
}
