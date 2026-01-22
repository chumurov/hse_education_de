// По массиву B, полученному в результате K-кратного применения операции Confuse,
// требуется восстановить разность max(A)-min(A).
// Наблюдение: операция Confuse сохраняет разницу максимума и минимума, поэтому
// ответ равен max(B) - min(B).

#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int N, K;
    if (!(cin >> N >> K)) return 0;
    long long mn = LLONG_MAX, mx = LLONG_MIN;
    for (int i = 0; i < N; ++i) {
        long long b; cin >> b;
        mn = min(mn, b);
        mx = max(mx, b);
    }
    cout << (mx - mn) << '\n';
    return 0;
}
