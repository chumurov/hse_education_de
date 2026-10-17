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
	var minimum, maximum int
	even, odd := 0, 0
	for i := 0; i < n; i++ {
		var value int
		if _, err := fmt.Scan(&value); err != nil {
			fmt.Println("Ошибка ввода")
			return
		}
		sum += int64(value)
		if i == 0 || value < minimum {
			minimum = value
		}
		if i == 0 || value > maximum {
			maximum = value
		}
		if value%2 == 0 {
			even++
		} else {
			odd++
		}
	}
	fmt.Printf("Сумма: %d\nСреднее: %g\nМаксимум: %d\nМинимум: %d\nЧётных: %d\nНечётных: %d\n", sum, float64(sum)/float64(n), maximum, minimum, even, odd)
}
