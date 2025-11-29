// 02_seed.js
// Seed the database with sample teachers, students, courses and grades.

const dbName = process.env.MONGO_INITDB_DATABASE || 'appdb';
const appDB = db.getSiblingDB(dbName);

print(`Seeding database: ${dbName}`);

const FORCE = process.env.FORCE_SEED === 'true' || false;

const preCount = (colName) => appDB[colName].countDocuments({});

if (!FORCE && (preCount('students') > 0 || preCount('teachers') > 0 || preCount('courses') > 0 || preCount('grades') > 0)) {
  print('Existing data detected; skipping seeding (set FORCE_SEED=true to force).');
  quit(0);
}

const randomInt = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

// Simple name pools
const firstNames = ['Иван', 'Петр', 'Сергей', 'Алексей', 'Андрей', 'Ольга', 'Елена', 'Мария', 'Анна', 'Наталья'];
const lastNames = ['Иванов', 'Петров', 'Сидоров', 'Смирнов', 'Кузнецов', 'Новикова', 'Попова', 'Леонова', 'Волкова'];
const departments = ['Информатика', 'Математика', 'Физика'];
const specializationsPool = ['Базы данных', 'Программирование', 'Машинное обучение', 'Теория графов', 'Сети'];

function makeFullName() {
  const last = lastNames[Math.floor(Math.random() * lastNames.length)];
  const first = firstNames[Math.floor(Math.random() * firstNames.length)];
  const middle = ['Иванович', 'Петрович', 'Сергеевич', 'Алексеевич', 'Андреевич', 'Петровна', 'Ивановна'][Math.floor(Math.random() * 7)];
  return `${last} ${first} ${middle}`;
}

// Clear existing data when forcing
if (FORCE) {
  appDB.students.drop();
  appDB.teachers.drop();
  appDB.courses.drop();
  appDB.grades.drop();
  print('Dropped existing collections to force reseed');
}

const teachersCount = 5;
const studentsCount = 50;
const coursesCount = 8;

// Create teachers
const teachers = [];
for (let i = 0; i < teachersCount; i++) {
  const teacherId = `PR-${2025}-${String(i+1).padStart(3,'0')}`;
  const fullName = makeFullName();
  const department = departments[i % departments.length];
  const specialization = [specializationsPool[i % specializationsPool.length]];
  const inserted = appDB.teachers.insertOne({
    teacherId: teacherId,
    fullName,
    email: `${teacherId.toLowerCase()}@university.ru`,
    department,
    position: ['Доцент', 'Профессор', 'Ассистент'][i % 3],
    phone: `+7-900-000-${String(100 + i).slice(-3)}`,
    specialization
  });
  teachers.push(inserted.insertedId);
}
print(`Inserted ${teachers.length} teachers`);

// Create courses
const courses = [];
for (let i = 0; i < coursesCount; i++) {
  const code = `COURSE-${2025}-${String(i+1).padStart(3,'0')}`;
  const teacherId = teachers[i % teachers.length];
  const semester = randomInt(1, 8);
  const inserted = appDB.courses.insertOne({
    courseCode: code,
    courseName: `Курс ${i+1} (${code})`,
    description: `Описание курса ${i+1}`,
    department: departments[i % departments.length],
    credits: randomInt(2, 5),
    semester: semester,
    hours: 36 + randomInt(0, 24),
    teacherId: teacherId,
    startDate: new Date('2025-09-01'),
    endDate: new Date('2025-12-15'),
    maxStudents: 30
  });
  courses.push(inserted.insertedId);
}
print(`Inserted ${courses.length} courses`);

// Create students
const students = [];
const groupBuckets = ['БО-1-1', 'БО-1-2', 'БО-2-1', 'БО-2-2', 'БО-3-1'];
for (let i = 0; i < studentsCount; i++) {
  const studentCode = `STU-${2024}-${String(i+1).padStart(3,'0')}`;
  const fullName = makeFullName();
  const course = randomInt(1, 4);
  const inserted = appDB.students.insertOne({
    studentId: studentCode,
    fullName,
    email: `${studentCode.toLowerCase()}@university.ru`,
    phone: `+7-900-111-${String(100 + i).slice(-3)}`,
    program: 'Информатика',
    course: course,
    enrollmentDate: new Date('2023-09-01'),
    status: 'active',
    group: groupBuckets[i % groupBuckets.length]
  });
  students.push(inserted.insertedId);
}
print(`Inserted ${students.length} students`);

// Create grades — assign each student to a few courses
let gradesInserted = 0;
for (let s = 0; s < students.length; s++) {
  // Each student gets 2-4 grades
  const cCount = randomInt(2, 4);
  const used = new Set();
  for (let j = 0; j < cCount; j++) {
    let courseIdx;
    do { courseIdx = Math.floor(Math.random() * courses.length); } while (used.has(courseIdx));
    used.add(courseIdx);
    const courseId = courses[courseIdx];
    const teacherId = teachers[courseIdx % teachers.length];
    const gradeVal = parseFloat((Math.random() * 4 + 1).toFixed(1)); // 1.0 to 5.0
    const status = Math.random() > 0.2 ? 'final' : 'interim';
    appDB.grades.insertOne({
      studentId: students[s],
      courseId: courseId,
      grade: gradeVal,
      gradeType: ['экзамен', 'зачёт', 'контрольная', 'практика'][Math.floor(Math.random() * 4)],
      gradeDate: new Date(),
      notes: 'Сгенерированная тестовая оценка',
      status,
      teacher: teacherId
    });
    gradesInserted++;
  }
}
print(`Inserted ${gradesInserted} grades`);

print('Seeding finished');

// Report counts
print('Final counts:');
printjson({
  students: appDB.students.countDocuments({}),
  teachers: appDB.teachers.countDocuments({}),
  courses: appDB.courses.countDocuments({}),
  grades: appDB.grades.countDocuments({})
});
