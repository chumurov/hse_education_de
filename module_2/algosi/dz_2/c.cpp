#include <iostream>

int main() {
    
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(NULL);

    int n;
    if (!(std::cin >> n)) return 0;

    int prev;
    std::cin >> prev; 

    bool found = false;
    for (int i = 1; i < n; ++i) {
        int current;
        std::cin >> current;


        if ((prev > 0 && current > 0) || (prev < 0 && current < 0)) {
            found = true;
        }
        
        prev = current; 
    }

    if (found) {
        std::cout << "YES" << std::endl;
    } else {
        std::cout << "NO" << std::endl;
    }

    return 0;
}
