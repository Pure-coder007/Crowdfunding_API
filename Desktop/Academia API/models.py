import mysql.connector
from database import config
from mysql.connector import Error

from courses import my_courses

class User():
    def __init__(self, id, first_name, last_name, email, password, matric_no):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = password
        self.matric_no = matric_no

    @classmethod
    def get(cls, user_id):
        pass


def add_student(first_name, last_name, email, password, matric_no):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    query = "INSERT INTO students (first_name, last_name, email, password, matric_no) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (first_name, last_name, email, password, matric_no))

    connection.commit()
    cursor.close()
    connection.close()

    return True


def add_admin(first_name, last_name, email, password):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    query = "INSERT INTO admin (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (first_name, last_name, email, password))

    connection.commit()
    cursor.close()
    connection.close()

    return True



def get_student(email):
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        query = "SELECT id, first_name, last_name, email, password, matric_no FROM students WHERE email=%s"
        cursor.execute(query, (email,))

        user = cursor.fetchone()

        if not user:
            return None

        return User(*user)
    except Error as e:
        
        print(f"Database error: {e}")
        return None
    finally:
        cursor.close()
        connection.close()





def get_student_matric_no(matric_no):
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        query = "SELECT id, first_name, last_name, email, password, matric_no FROM students WHERE matric_no=%s"
        cursor.execute(query, (matric_no,))

        user = cursor.fetchone()

        if not user:
            return None

        return User(*user)
    except Error as e:
        
        print(f"Database error: {e}")
        return None
    finally:
        cursor.close()
        connection.close()



def get_admin(email):
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        query = "SELECT * FROM admin WHERE email=%s"
        cursor.execute(query, (email,))

        user = cursor.fetchone()

        if not user:
            return None

        return User(*user)
    except Error as e:
        
        print(f"Database error: {e}")
        return None
    finally:
        cursor.close()
        connection.close()




def get_matric_no(id):
    try:
        connection = mysql.connector.connect(**config)

        cursor = connection.cursor()

        print('id to search:', id)

        query = "SELECT matric_no FROM students WHERE id = %s"
        cursor.execute(query, (id,))

        matric_no = cursor.fetchone()
        if matric_no is not None:
            print('matric_no :', matric_no)
            return matric_no[0]
        else:
            return {'message': 'id not found', 'status': 404}, 404
    
    except Exception as e:
        print(f"Error fetching user requests: {str(e)}")
        return None
    finally:
        cursor.close()
        connection.close()

        

def get_courses_for_student(student_id):
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM student_courses WHERE student_id = %s"
        cursor.execute(query, (student_id,))
        courses = cursor.fetchall()
        return courses
    except Exception as e:
        print("Error getting courses for student:", e)
        return None
    finally:
        cursor.close()
        connection.close()






def get_one_student(id):
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        query = "SELECT id, first_name, last_name, email,  matric_no FROM students WHERE id=%s"
        cursor.execute(query, (id,))
        student = cursor.fetchone()
        if student is not None:
            return student
        else:
            return {'message': 'Student not found', 'status': 404}, 404
    except Exception as e:
        print("Error getting student:", e)
        return None
    finally:
        cursor.close()
        connection.close()



# Admin viewin all students and their courses
def get_all_students():
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT s.id AS student_id, s.first_name, s.last_name, s.email, s.matric_no, 
                   GROUP_CONCAT(DISTINCT sc.course_name) AS course_names, 
                   GROUP_CONCAT(DISTINCT sc.course_unit) AS course_units
            FROM students s
            LEFT JOIN student_courses sc ON s.id = sc.student_id
            GROUP BY s.id, s.first_name, s.last_name, s.email, s.matric_no
        """
        cursor.execute(query)
        students = cursor.fetchall()
        return students
    except Exception as e:
        print("Error getting students with courses:", e)
        return None
    finally:
        cursor.close()
        connection.close()
