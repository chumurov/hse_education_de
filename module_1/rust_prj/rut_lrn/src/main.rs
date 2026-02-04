use std::io;

fn get_name() -> String {
    let mut name = String::new();
    // Запросите и считайте имя пользователя
    io::stdin()
        .read_line(&mut name)
        .expect("Не удалось прочитать строку");
    name
}

fn greet(name: String) {
    // Выведите приветствие
    println!("Hello, {}!", name.trim());

}

fn main() {
    // Вызовите get_name и greet
    let name = get_name();
    greet(name);
}