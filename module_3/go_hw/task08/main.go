package main

import "fmt"

func main() {
	var n int
	if _, err := fmt.Scan(&n); err != nil {
		fmt.Println("Ошибка ввода")
		return
	}
	if isPrime(n) {
		fmt.Println("Простое число")
	} else {
		fmt.Println("Не является простым числом")
	}
}

func isPrime(n int) bool {
	if n < 2 {
		return false
	}
	for divisor := 2; divisor <= n/divisor; divisor++ {
		if n%divisor == 0 {
			return false
		}
	}
	return true
}
