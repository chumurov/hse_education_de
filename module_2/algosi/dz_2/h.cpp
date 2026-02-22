#include <iostream>
#include <limits>

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int n, m;
    if (!(std::cin >> n >> m)) return 0;

    int best_idx = 0;
    long long best_max = std::numeric_limits<long long>::min();
    long long best_sum = std::numeric_limits<long long>::min();

    for (int i = 0; i < n; ++i) {
        long long mx = std::numeric_limits<long long>::min();
        long long sum = 0;

        for (int j = 0; j < m; ++j) {
            long long x;
            std::cin >> x;
            sum += x;
            if (x > mx) mx = x;
        }

        // Сравнение по правилам:
        // 1) максимальный лучший бросок
        // 2) при равенстве — максимальная сумма
        // 3) при равенстве — минимальный номер (то есть текущий не заменяет)
        if (mx > best_max || (mx == best_max && sum > best_sum)) {
            best_max = mx;
            best_sum = sum;
            best_idx = i;
        }
    }

    std::cout << best_idx;
    return 0;
}
