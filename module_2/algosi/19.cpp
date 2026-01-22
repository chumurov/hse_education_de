#include <iostream>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int N;
    cin >> N;

    long long sum = 0;
    long long mn = 1000000000LL;   // 1e9
    long long mx = -1000000000LL;  // -1e9

    for (int i = 0; i < N; ++i) {
        long long x;
        cin >> x;
        sum += x;
        if (x < mn) mn = x;
        if (x > mx) mx = x;
    }

    cout << sum << ' ' << mn << ' ' << mx << '\n';
    return 0;
}