// Программа выводит приветствие в формате: Hello, <name>!
// Чтение полного имени (включая пробелы) и вывод без использования оператора +

#include <bits/stdc++.h>
using namespace std;

int main() {
    string name;
    if (!std::getline(cin, name)) return 0;
    cout << "Hello, " << name << "!" << '\n';
    return 0;
}
