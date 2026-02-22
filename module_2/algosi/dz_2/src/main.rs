
// Формат вывода
// Необходимо вывести слово YES, если существует пара соседних элементов с одинаковыми знаками. 
// В противном случае следует вывести слово NO.

//сравнение соседних элементов массива на одинаковый знак
fn check_adjacent_signs(arr: &[i32]) -> &'static str {
    for i in 0..arr.len() - 1 {
        if (arr[i] > 0 && arr[i + 1] > 0) || (arr[i] < 0 && arr[i + 1] < 0) {
            return "YES";
        }
    }
    "NO"
}

//перестановка местами соседних элементов массива 1 с 2, 3 с 4 и т.д.
fn swap_adjacent_elements(arr: &mut [i32]) {
    for i in (0..arr.len() - 1).step_by(2) {
        arr.swap(i, i + 1);
    }

}

//количество уникальных элементов в неубывающем массиве 
fn count_unique_elements(arr: &[i32]) -> usize {
    if arr.is_empty() {
        return 0;
    }
    let mut count = 1;
    for i in 1..arr.len() {
        if arr[i] != arr[i - 1] {
            count += 1;
        }
    }
    count
}

// Дано число n и заполните его по следующему правилу:
// создайте квадратный массив размером n x n;

// числа на диагонали, идущей из правого верхнего в левый нижний угол, равны 1;
// числа, стоящие выше этой диагонали, равны 0;
// числа, стоящие ниже этой диагонали, равны 2.
fn create_special_matrix(n: usize) -> Vec<Vec<i32>> {
    let mut matrix = vec![vec![0; n]; n];
    for i in 0..n {
        for j in 0..n {
            if j < n - i - 1 {
                matrix[i][j] = 0;
            } else if j == n - i - 1 {
                matrix[i][j] = 1;
            } else {
                matrix[i][j] = 2;
            }
        }
    }
    matrix

}

// Проверьте, является ли двумерный массив симметричным относительно главной диагонали. 
// Главная диагональ — та, которая идёт из левого верхнего угла двумерного массива в правый нижний.
fn is_symmetric(matrix: &[Vec<i32>]) -> bool {
    let n = matrix.len();
    for i in 0..n {
        for j in 0..n {
            if matrix[i][j] != matrix[j][i] {
                return false;
            }
        }
    }
    true
}
// В метании молота состязается 
// n спортcменов. Каждый из них сделал 
// m бросков. Побеждает спортсмен, у которого максимален наилучший бросок. 
// Если таких несколько, то из них побеждает тот, у которого наилучшая сумма результатов по всем попыткам. 
// Если и таких несколько, победителем считается спортсмен с минимальным номером. 
// Определите номер победителя соревнований.
fn find_winner(throws: &Vec<Vec<i32>>) -> usize {
    let n = throws.len();
    let m = throws[0].len();
    let mut best_throw = vec![0; n];
    let mut total_score = vec![0; n];
    for i in 0..n { 
        for j in 0..m {
            if throws[i][j] > best_throw[i] {
                best_throw[i] = throws[i][j];
            }
            total_score[i] += throws[i][j];
        }
    }
    let mut winner = 0;
    for i in 1..n {
        if best_throw[i] > best_throw[winner] ||
           (best_throw[i] == best_throw[winner] && total_score[i] > total_score[winner]) {
            winner = i; 
    
           }

    }
    winner
}

fn palindrome_check(s: &str) -> bool {
    let chars: Vec<char> = s.chars().collect();
    let len = chars.len();
    for i in 0..len / 2 {
        if chars[i] != chars[len - 1 - i] {
            return false;
        }
    }
    true
}


fn max_change_last(s: &mut Vec<i32>) {
    let max_idx = s
    .iter()
    .enumerate()
    .max_by_key(|(_, v)| *v)
    .map(|(i, _)| i)
    .unwrap();

    let last = s.len() -   1;

    s.swap(max_idx, last);
    
    


    


}


fn main() {
    
  

// 1 5 2 4 3

    let mut lst = vec![1, 5, 2, 4, 3];
    max_change_last(&mut lst);
    println!("{:?}", lst);

    
}

