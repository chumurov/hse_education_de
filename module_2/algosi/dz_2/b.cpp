#include <iostream>

int main() {
    // Ускорение работы стандартных потоков ввода-вывода
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(NULL);

    int n;
    // Считываем количество элементов N
    if (!(std::cin >> n)) return 0;

    int count = 0;
    for (int i = 0; i < n; ++i) {
        int current;
        // Поочередно считываем каждое число массива
        std::cin >> current;
        
        // Проверяем условие: число должно быть строго больше 0
        if (current > 0) {
            count++;
        }
    }

    // Выводим итоговое количество положительных чисел
    std::cout << count << std::endl;

    return 0;
}
