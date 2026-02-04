#include <iostream>
#include <cstdio>
#include <algorithm>

int main() {
    // Ускоряем ввод
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(NULL);

    int n;
    if (!(std::cin >> n)) return 0;

    long long sum = 0, current;
    // Используем крайние значения для инициализации поиска min/max
    long long mn = 3e18; // Достаточно большое число
    long long mx = -3e18; // Достаточно маленькое число

    for (int i = 0; i < n; ++i) {
        if (!(std::cin >> current)) break;
        sum += current;
        if (current < mn) mn = current;
        if (current > mx) mx = current;
    }

    // Вывод в две строки согласно вашему примеру
    // Первая строка: сумма и среднее
    // Вторая строка: минимум и максимум
    printf("%lld %.4f\n", sum, (double)sum / n);
    printf("%lld %lld\n", mn, mx);

    return 0;
}
