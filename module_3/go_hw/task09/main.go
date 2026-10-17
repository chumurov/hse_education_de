package main

import (
	"fmt"
	"io"
)

func main() {
	// Денежные суммы вводятся целыми числами в рублях.
	var balance int64
	fmt.Println("Введите начальный баланс:")
	if _, err := fmt.Scan(&balance); err != nil {
		fmt.Println("Ошибка ввода")
		return
	}
	if balance < 0 {
		fmt.Println("Ошибка: баланс не может быть отрицательным")
		return
	}
	fmt.Println("Действия: 1 — баланс, 2 — пополнить, 3 — снять, 0 — выход")
	for {
		fmt.Println("Введите действие:")
		var action int
		if _, err := fmt.Scan(&action); err != nil {
			if err != io.EOF {
				fmt.Println("Ошибка ввода")
			}
			return
		}
		switch action {
		case 0:
			fmt.Println("Работа завершена")
			return
		case 1:
			fmt.Printf("Баланс: %d\n", balance)
		case 2, 3:
			fmt.Println("Введите сумму:")
			var amount int64
			if _, err := fmt.Scan(&amount); err != nil {
				fmt.Println("Ошибка ввода")
				return
			}
			if amount <= 0 {
				fmt.Println("Ошибка: сумма должна быть положительной")
				continue
			}
			if action == 2 {
				const maxInt64 = 1<<63 - 1
				if amount > maxInt64-balance {
					fmt.Println("Ошибка: слишком большая сумма")
					continue
				}
				balance += amount
			} else {
				if amount > balance {
					fmt.Println("Ошибка: недостаточно средств")
					continue
				}
				balance -= amount
			}
			fmt.Printf("Баланс: %d\n", balance)
		default:
			fmt.Println("Ошибка: неизвестное действие")
		}
	}
}
