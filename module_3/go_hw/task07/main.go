package main

import "fmt"

func main() {
	var n int
	if _, err := fmt.Scan(&n); err != nil {
		fmt.Println("Ошибка ввода")
		return
	}
	if n < 1 {
		fmt.Println("Ошибка: N должно быть положительным")
		return
	}
	var sum int64
	for i := 1; i <= n; i++ {
		if i%2 == 0 && i%3 == 0 {
			sum += int64(i)
		}
	}
	fmt.Printf("Сумма: %d\n", sum)
}
