1. Запуск
Для полного развертывания (создание папок, запуск базы и импорт данных) выполните одну команду из папки проекта:


chmod +x docker-import-all.sh
./docker-import-all.sh


2. Подключение к базе
После запуска база данных будет доступна на порту 27018
Реквизиты для подключения:

Хост: localhost
Порт: 27018
База данных: university_grades
Пользователь: university_app
Пароль: app_password123
Auth DB: university_grades


проверка

sudo docker exec university_mongodb mongosh -u university_app -p app_password123 --authenticationDatabase university_grades university_grades --eval "db.studentssudo docker exec university_mongodb mongosh -u university_app -p app_password123 --authenticationDatabase university_grades university_grades --eval "db.students.countDocuments()"

mongodb://university_app:app_password123@localhost:27018/university_grades?authSource=university_grades