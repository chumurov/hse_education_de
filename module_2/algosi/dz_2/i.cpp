#include <iostream>
#include <vector>

template <typename It>
void select_max(It begin, It end) {
    if (begin == end) return;

    It max_it = begin;
    for (It it = begin; it != end; ++it) {
        if (*it > *max_it) {
            max_it = it;  
        }
    }
    --end;                
    std::swap(*max_it, *end);
}

int main() {
    int n;
    std::cin >> n;

    std::vector<int> a(n);
    for (int i = 0; i < n; ++i)
        std::cin >> a[i];

    select_max(a.begin(), a.end());

    for (int x : a)
        std::cout << x << ' ';
}
