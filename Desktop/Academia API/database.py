import mysql.connector
from datetime import datetime

config = {
    'user': 'root',
    'password': 'language007',
    'host': 'localhost',
    'database': 'academia',
}


def seup_database():
    config['database'] = None
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(255) NOT NULL,
        last_name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        matric_no VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")

    cursor.execute("""
    CREATE  TABLE IF NOT EXISTS admin(
        id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(255) NOT NULL,
        last_name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")



    cursor.execute("""
    CREATE TABLE courses (
        course_id INT AUTO_INCREMENT PRIMARY KEY,
        course_code VARCHAR(20),
        course VARCHAR(100),
        course_description TEXT,
        course_units INT,
        course_lecturer VARCHAR(100)
);
""")


    cursor.execute("""
    CREATE TABLE the_student_courses (
        student_course_id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT,
        course_id INT ,
        course_code VARCHAR(20),
        course_name VARCHAR(100),
        course_unit INT,
        matric_no VARCHAR(255) NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
    );
""")
