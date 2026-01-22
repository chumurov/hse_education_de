use std::time::Instant;
use std::iter;
use std::collections::VecDeque;
use std::cmp::Ordering;
// Обрати внимание: сигнатура изменена на &mut [char].
// Это делает функцию более универсальной (работает и с Vec, и с массивами).

pub fn move_zeroes(nums: &mut Vec<i32>) {

    let mut write_idx = 0; 
    for read_idx in 0..nums.len() {
   
        
        if nums[read_idx] != 0 {
            nums[write_idx] = nums[read_idx];
            write_idx += 1;
            
        }
    

    }
    nums[write_idx..].fill(0);



    }


pub fn remove_duplicates3(nums: &mut Vec<i32>) -> i32 {
    if nums.is_empty() {
        return 0;
    }
    
    let mut write_idx = 1;  // Позиция для записи следующего уникального
    
    for read_idx in 1..nums.len() {
        // Проверяем, отличается ли текущий от предыдущего уникального
        if nums[read_idx] != nums[write_idx - 1] {
            nums[write_idx] = nums[read_idx];  // Копируем (i32 — Copy)
            write_idx += 1;
        }
    }
    
    write_idx as i32  // Количество уникальных элементов
}


    pub fn merge(nums1: &mut Vec<i32>, m: i32, nums2: &mut Vec<i32>, n: i32) {
        let tail_len = (nums1.len() as i32 - m) as usize;
        let mut tail = Vec::with_capacity(tail_len);
        for i in m as usize..nums1.len() {
            tail.push(nums1[i]);
        }
        let mut tail_idx = 0;
        let mut num2_idx = 0; 
        let mut stack = Vec::<i32>::with_capacity(nums1.len());
        let mut stack_idx = 0;
        for read_idx in 0..m as usize {
            if nums1[read_idx] > nums2[num2_idx]  {
                let cash = nums1[read_idx];
                nums1[read_idx] = nums2[num2_idx];
                stack.push(cash);
                num2_idx += 1;
                
            } 
        }

        for read_idx in (m as usize)..nums1.len()  {
     match (nums2.get(num2_idx), stack.get(stack_idx), tail.get(tail_idx)) {
    (Some(&n2), Some(&s), _) if n2 < s => {
        nums1[read_idx] = n2; num2_idx += 1;
    }
    (_, Some(&s), _) => {
        nums1[read_idx] = s; stack_idx += 1;
    }
    (_, _, Some(&t)) => {
        nums1[read_idx] = t; tail_idx += 1;
    }
    _ => {}
}
            
        }
       
    }


pub fn remove_element(nums: &mut Vec<i32>, val: i32) -> i32 {
    let n = nums.len();
    let mut write_idx = 0;  // Позиция для записи следующего уникального
    let mut stack = VecDeque::<usize>::new();
    let mut ct = 0;

    for read_idx in 0..n {
        // Проверяем, отличается ли текущий от предыдущего уникального
        if nums[read_idx] == val {
            stack.push_back(read_idx);
            ct += 1;
      
            
           
        } else {
            if stack.len() > 0 {
                
                let q:usize = stack.pop_front().expect("REASON");
                //println!("{} {}", q, read_idx);
                nums[q] = nums[read_idx ];
                stack.push_back(read_idx);

            }
        }
    }
    //println!("stack: {:?}", stack);
    let res:i32 = (n - ct).try_into().unwrap();
    res
}


pub fn two_sum(numbers: Vec<i32>, target: i32) -> Vec<i32> {
        let mut left = 0;
        let mut right = (numbers.len() - 1) as i32;
        while left < right {
            let sum = numbers[left as usize] + numbers[right as usize];
            match sum.cmp(&target) {
                Ordering::Greater => right -= 1,
                Ordering::Less    => left += 1,
                Ordering::Equal   => return vec![left+1, right+1],
            }
        }
        vec![] 
    }
    

fn main() {
    
    let numbers =  vec![1,2,3,4];  //[2,4]
    let target = 6;
    
    let start = Instant::now();

    let res = two_sum(numbers, target); 
    
    let duration = start.elapsed();
    
    println!("Time: {:?}", duration);
    println!("result: {:?}", res);

    
}
