#include <string>
#include <cstddef>

static bool CheckPalindrome(const std::string& s, std::size_t l, std::size_t r_excl) {
    // проверяет s[l..r_excl) на палиндром, O(1) памяти
    if (r_excl <= l) return true;
    std::size_t i = l, j = r_excl - 1;
    while (i < j) {
        if (s[i] != s[j]) return false;
        ++i;
        --j;
    }
    return true;
}

bool CheckPalindrome(const std::string& s) {
    return CheckPalindrome(s, 0, s.size());
}

std::size_t CountPalindromes(const std::string& s) {
    std::size_t count = 0;
    const std::size_t n = s.size();
    std::size_t i = 0;

    while (i < n) {
        // пропускаем пробелы
        while (i < n && s[i] == ' ') ++i;
        if (i >= n) break;

        // слово = максимальный отрезок латинских букв (по условию только латиница и пробелы)
        std::size_t start = i;
        while (i < n && s[i] != ' ') ++i;
        std::size_t end = i; // [start, end)

        if (CheckPalindrome(s, start, end)) ++count;
    }

    return count;
}
