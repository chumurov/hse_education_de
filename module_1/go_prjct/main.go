package main

import "fmt"

func twoSum(nums []int, target int) []int {
	numMap := make(map[int]int)
	for i, num := range nums {
		if j, found := numMap[target-num]; found {
			return []int{j, i}
		}
		numMap[num] = i
	}
	return nil

}

func main() {
	//Example usage:
	nums := []int{2, 7, 11, 15}
	target := 26
	result := twoSum(nums, target)
	fmt.Println(result) // Output: [0, 1]
}
