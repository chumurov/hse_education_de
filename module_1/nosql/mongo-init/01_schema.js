// 01_schema.js
// Create collections, JSON Schema validation, indexes, and seed sample data

const dbName = process.env.MONGO_INITDB_DATABASE || 'appdb';
const appDB = db.getSiblingDB(dbName);

print(`Applying schema to database: ${dbName}`);

// Drop existing collections if they exist (idempotent when run for testing)
const safeDrop = (col) => {
  try { appDB[col].drop(); print(`Dropped ${col}`); } catch (e) { print(`${col} did not exist`); }
};

// (We purposely do not drop collections automatically in production; this is handy for dev)
// safeDrop('students'); safeDrop('teachers'); safeDrop('courses'); safeDrop('grades');

// Students collection
const studentsValidator = {
  $jsonSchema: {
    bsonType: 'object',
    required: ['studentId', 'fullName', 'email', 'program', 'course', 'enrollmentDate', 'status', 'group'],
    properties: {
      studentId: { bsonType: 'string' },
      fullName: { bsonType: 'string' },
      email: { bsonType: 'string' },
      phone: { bsonType: 'string' },
      program: { bsonType: 'string' },
      course: { bsonType: 'int', minimum: 1, maximum: 6 },
      enrollmentDate: { bsonType: 'date' },
      status: { enum: ['active', 'inactive', 'graduated', 'expelled'] },
      group: { bsonType: 'string' }
    }
  }
};

// Teachers collection
const teachersValidator = {
  $jsonSchema: {
    bsonType: 'object',
    required: ['teacherId', 'fullName', 'email', 'department', 'position'],
    properties: {
      teacherId: { bsonType: 'string' },
      fullName: { bsonType: 'string' },
      email: { bsonType: 'string' },
      department: { bsonType: 'string' },
      position: { bsonType: 'string' },
      phone: { bsonType: 'string' },
      specialization: { bsonType: 'array', items: { bsonType: 'string' } }
    }
  }
};

// Courses collection
const coursesValidator = {
  $jsonSchema: {
    bsonType: 'object',
    required: ['courseCode', 'courseName', 'department', 'credits', 'semester', 'hours', 'teacherId', 'startDate', 'endDate', 'maxStudents'],
    properties: {
      courseCode: { bsonType: 'string' },
      courseName: { bsonType: 'string' },
      description: { bsonType: 'string' },
      department: { bsonType: 'string' },
      credits: { bsonType: 'int', minimum: 0 },
      semester: { bsonType: 'int', minimum: 1 },
      hours: { bsonType: 'int', minimum: 0 },
      teacherId: { bsonType: 'objectId' },
      startDate: { bsonType: 'date' },
      endDate: { bsonType: 'date' },
      maxStudents: { bsonType: 'int', minimum: 0 }
    }
  }
};

// Grades collection
const gradesValidator = {
  $jsonSchema: {
    bsonType: 'object',
    required: ['studentId', 'courseId', 'grade', 'gradeType', 'gradeDate', 'status', 'teacher'],
    properties: {
      studentId: { bsonType: 'objectId' },
      courseId: { bsonType: 'objectId' },
      grade: { bsonType: ['double', 'int'], minimum: 0 },
      gradeType: { bsonType: 'string' },
      gradeDate: { bsonType: 'date' },
      notes: { bsonType: 'string' },
      status: { enum: ['draft', 'interim', 'final'] },
      teacher: { bsonType: 'objectId' }
    }
  }
};

// Create collections with validation if they don't exist
const createIfMissing = (name, validator) => {
  const existing = appDB.getCollectionNames().indexOf(name) >= 0;
  if (!existing) {
    appDB.createCollection(name, { validator: validator, validationAction: 'warn' });
    print(`Created collection ${name} with validator`);
  } else {
    // Update validator
    appDB.runCommand({ collMod: name, validator: validator, validationAction: 'warn' });
    print(`Updated validator for ${name}`);
  }
};

createIfMissing('students', studentsValidator);
createIfMissing('teachers', teachersValidator);
createIfMissing('courses', coursesValidator);
createIfMissing('grades', gradesValidator);

// Create recommended indexes
appDB.students.createIndex({ studentId: 1 }, { unique: true });
appDB.students.createIndex({ email: 1 }, { unique: false });
appDB.students.createIndex({ group: 1 });

appDB.teachers.createIndex({ teacherId: 1 }, { unique: true });
appDB.teachers.createIndex({ email: 1 });

appDB.courses.createIndex({ courseCode: 1 }, { unique: true });
appDB.courses.createIndex({ semester: 1 });
appDB.courses.createIndex({ teacherId: 1 });

appDB.grades.createIndex({ studentId: 1 });
appDB.grades.createIndex({ courseId: 1 });
appDB.grades.createIndex({ studentId: 1, courseId: 1 }, { unique: true });
appDB.grades.createIndex({ gradeDate: 1 });

print('Indexes created');

// Insert sample data only if collections are empty
const ensureSample = () => {
  if (appDB.students.countDocuments({}) === 0) {
    const studentId = appDB.students.insertOne({
      studentId: 'БО-2024-001',
      fullName: 'Иванов Иван Иванович',
      email: 'ivan@university.ru',
      phone: '+7-999-123-4567',
      program: 'Информатика',
      course: 2,
      enrollmentDate: new Date('2023-09-01'),
      status: 'active',
      group: 'БО-2-1'
    }).insertedId;
    print('Inserted sample student');

    const teacherId = appDB.teachers.insertOne({
      teacherId: 'ПРЕ-2024-001',
      fullName: 'Петров Петр Петрович',
      email: 'petrov@university.ru',
      department: 'Информатика',
      position: 'Доцент',
      phone: '+7-999-987-6543',
      specialization: ['Базы данных', 'Программирование']
    }).insertedId;
    print('Inserted sample teacher');

    const courseId = appDB.courses.insertOne({
      courseCode: 'BD-2024-001',
      courseName: 'Базы данных',
      description: 'Введение в системы управления базами данных',
      department: 'Информатика',
      credits: 3,
      semester: 4,
      hours: 48,
      teacherId: teacherId,
      startDate: new Date('2024-09-01'),
      endDate: new Date('2024-12-15'),
      maxStudents: 30
    }).insertedId;
    print('Inserted sample course');

    appDB.grades.insertOne({
      studentId: studentId,
      courseId: courseId,
      grade: 4.5,
      gradeType: 'экзамен',
      gradeDate: new Date('2024-12-15'),
      notes: 'Хорошо решена практическая часть',
      status: 'final',
      teacher: teacherId
    });
    print('Inserted sample grade');
  } else {
    print('Collections already have data, skipping sample insertions');
  }
};

ensureSample();

print('Schema application finished');
