package main

import "fmt"

func main() {
	var n int
	if _, err := fmt.Scan(&n); err != nil {
		fmt.Println("Ошибка ввода")
		return
	}
	printTable(n)
}

func printTable(n int) {
	for i := 1; i <= 10; i++ {
		fmt.Printf("%d * %d = %d\n", n, i, n*i)
	}
}
