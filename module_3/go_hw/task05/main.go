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
	var value float64
	if _, err := fmt.Scan(&value); err != nil {
		fmt.Println("Ошибка ввода")
		return
	}
	minimum, maximum := value, value
	for i := 1; i < n; i++ {
		if _, err := fmt.Scan(&value); err != nil {
			fmt.Println("Ошибка ввода")
			return
		}
		if value < minimum {
			minimum = value
		}
		if value > maximum {
			maximum = value
		}
	}
	fmt.Printf("Максимум: %g\nМинимум: %g\n", maximum, minimum)
}
