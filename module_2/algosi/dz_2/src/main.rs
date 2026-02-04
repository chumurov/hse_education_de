
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



fn main() {
    
  

    //0 1 2
    //1 5 3
    //2 3 4
    let matrix = vec![
        vec![0, 1, 2],
        vec![1, 5, 3],
        vec![2, 3, 4],
    ];
    let symmetric = is_symmetric(&matrix);
    println!("{:?}", symmetric);

    
}

