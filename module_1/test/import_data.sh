#!/bin/bash


echo "Waiting for MongoDB to start..."
sleep 10


echo "Importing data to MongoDB..."


sudo docker exec university_mongodb mongoimport \
  --db university_grades \
  --collection students \
  --username university_app \
  --password app_password123 \
  --authenticationDatabase university_grades \
  --jsonArray \
  --file /data/json/students.json


sudo docker exec university_mongodb mongoimport \
  --db university_grades \
  --collection lecturers \
  --username university_app \
  --password app_password123 \
  --authenticationDatabase university_grades \
  --jsonArray \
  --file /data/json/lecturers.json


sudo docker exec university_mongodb mongoimport \
  --db university_grades \
  --collection courses \
  --username university_app \
  --password app_password123 \
  --authenticationDatabase university_grades \
  --jsonArray \
  --file /data/json/courses.json

# Импорт оценок
sudo docker exec university_mongodb mongoimport \
  --db university_grades \
  --collection grades \
  --username university_app \
  --password app_password123 \
  --authenticationDatabase university_grades \
  --jsonArray \
  --file /data/json/grades.json

# Импорт записей на курсы
sudo docker exec university_mongodb mongoimport \
  --db university_grades \
  --collection enrollments \
  --username university_app \
  --password app_password123 \
  --authenticationDatabase university_grades \
  --jsonArray \
  --file /data/json/enrollments.json

echo "Data import completed!"
