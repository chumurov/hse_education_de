package main

import "fmt"

func main() {
	var n int
	if _, err := fmt.Scan(&n); err != nil {
		fmt.Println("Ошибка ввода")
		return
	}
	if n <= 0 {
		fmt.Println("Ошибка: N должно быть положительным")
		return
	}
	var sum int64
	for i := 1; i <= n; i++ {
		sum += int64(i)
	}
	fmt.Printf("Сумма: %d\nСреднее: %g\n", sum, float64(sum)/float64(n))
}
