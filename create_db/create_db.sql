BEGIN TRANSACTION;

DROP TABLE IF EXISTS students;

CREATE TABLE students (
id_person INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
firstname VARCHAR (32),
lastname VARCHAR (32),
email VARCHAR(32)
);

INSERT INTO students (id_person, firstname, lastname, email) VALUES (1, 'Anton', 'Lushnikov', 'antonlushnikow@gmail.com');

DROP TABLE IF EXISTS categories;

CREATE TABLE categories (
id_category INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
title VARCHAR (32),
description VARCHAR (256)
);

INSERT INTO categories (id_category, title, description) VALUES (1, 'Программирование', 'Курсы программирования');

DROP TABLE IF EXISTS courses;

CREATE TABLE courses (
id_course INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
title VARCHAR (32),
id_category INTEGER,
description VARCHAR (256)
);

INSERT INTO courses (id_course, title, id_category, description) VALUES (1, 'Python для начинающих', 1, 'От новичка до джуниора');

DROP TABLE IF EXISTS courses_students;

CREATE TABLE courses_students (
id_course_student INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
id_course INTEGER,
id_student INTEGER
);

INSERT INTO courses_students (id_course_student, id_course, id_student) VALUES (1, 1, 1);

COMMIT TRANSACTION;