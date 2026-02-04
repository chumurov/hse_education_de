#include <iostream>

int main() {
 
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(NULL);

    int n;
    if (!(std::cin >> n)) return 0;

    int prev;
    std::cin >> prev; 
    
    
    int unique_count = 1; 

    
    for (int i = 1; i < n; ++i) {
        int current;
        std::cin >> current;

        
        if (current != prev) {
            unique_count++;
            prev = current; 
        }
        
    }

    std::cout << unique_count << std::endl;

    return 0;
}
