package main

import "fmt"

func main() {
	var n int
	if _, err := fmt.Scan(&n); err != nil {
		fmt.Println("Ошибка ввода")
		return
	}
	if n < 0 {
		fmt.Println("Ошибка: N не может быть отрицательным")
		return
	}
	positive, negative, zero := 0, 0, 0
	for i := 0; i < n; i++ {
		var value float64
		if _, err := fmt.Scan(&value); err != nil {
			fmt.Println("Ошибка ввода")
			return
		}
		if value > 0 {
			positive++
		} else if value < 0 {
			negative++
		} else {
			zero++
		}
	}
	fmt.Printf("Положительных: %d\nОтрицательных: %d\nНулей: %d\n", positive, negative, zero)
}
