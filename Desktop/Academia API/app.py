from flask import Flask, Blueprint, jsonify, request
import mysql.connector
from flask_bcrypt import Bcrypt
from decimal import Decimal
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import random
from models import get_student, add_student, add_admin, get_admin, get_matric_no, get_student_matric_no, get_courses_for_student, get_one_student, get_all_students
from database import config
from courses import my_courses

app = Flask(__name__)

bcrypt = Bcrypt(app)
jwt = JWTManager()
auth = Blueprint('auth', __name__)
app.config.from_pyfile('config.py')



# Create app
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'language007'
    jwt.init_app(app)
    app.register_blueprint(auth, url_prefix='/auth/v1')
    # app.register_blueprint(auth)
    return app

def email_exists(email):
    student = get_student(email)
    return student is not None


def generate_matric_no():
    matric_no = 'UNI-' + str(random.randint(1000000, 9999999))
    return matric_no


def generate_random_grade_for_each_course():
    grades = ['A', 'B', 'C', 'D', 'E', 'F']
    return random.choice(grades)


@auth.route('/register_admin', methods=['POST'])
def register_admin():
    data = request.get_json()
    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']
    password = data['password']

    if email_exists(email):
        return jsonify({'message': 'Email already exists'}), 400

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    add_admin(first_name, last_name, email, password_hash)

    return jsonify({'message': 'Admin created successfully'}), 201




@auth.route('/login-admin', methods=['POST'])
def login_admin():
    data = request.get_json()
    email = data['email']
    password = data['password']

    admin = get_admin(email)
    if admin is None:
        return jsonify({'message': 'Invalid email or password'}), 401

    if bcrypt.check_password_hash(admin.password_hash, password):
        access_token = create_access_token(identity=admin.id)
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'message': 'Invalid email or password', 'Login' : 'Successful'}), 401







@auth.route('/register-student', methods=['POST'])
def register():
    data = request.get_json()
    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']
    password = data['password']
    matric_no = generate_matric_no()

    if email_exists(email):
        return jsonify({'message': 'Email already exists'}), 400

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    add_student(first_name, last_name, email, password_hash, matric_no)

    return jsonify({'message': 'Student added successfully', 'matric_no': matric_no }), 201



@auth.route('/access_to_matric_no', methods=['POST'])
def access_to_matric_no():
    data = request.get_json()
    email = data['email']
    password = data['password']

    student = get_student(email)
    if student is None:
        return jsonify({'message': 'Invalid email or password'}), 401

    if bcrypt.check_password_hash(student.password_hash, password):
        access_token = create_access_token(identity=student.id)
        return jsonify({'access_token': access_token, 'Access' :'Granted'}), 200
    else:
        return jsonify({'message': 'Invalid email or password', 'Access' :'Denied'}), 401


# Get matric_no
@auth.route('/matric_no', methods=['GET'])
@jwt_required()
def matric_no():
    student_id = get_jwt_identity()

    if not student_id:
        return jsonify({'message': 'You are not allowed to view this information!', 'status': 401}), 401
    
    matric_no = get_matric_no(student_id)

    if matric_no is not None:
        return jsonify({'This is your matric_no': matric_no}), 200
    else:
        return jsonify({'message': 'id not found', 'status': 404}), 404





# Loigin with matric_no
@auth.route('/student_login', methods=['POST'])
def student_login():
    data = request.get_json()
    matric_no = data['matric_no']
    password = data['password']

    student = get_student_matric_no(matric_no)
    if student is None:
        return jsonify({'message': 'Invalid matric_no or password'}), 401

    if bcrypt.check_password_hash(student.password_hash, password):
        access_token = create_access_token(identity=student.id)
        return jsonify({'access_token': access_token, 'Login': 'Successful'}), 200
    else:
        return jsonify({'message': 'Invalid matric_no or password'}), 401
    




# Get courses
@auth.route('/show_courses', methods=['GET'])
@jwt_required()
def show_courses():
    return jsonify({'School_Courses': my_courses}), 200



@auth.route('/register_courses', methods=['POST'])
@jwt_required()
def register_courses():
    data = request.get_json()
    student_id = get_jwt_identity()
    course_id = data['course_id']
    course_code = data['course_code']
    course_name = data['course_name']
    course_unit = data['course_unit']

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    # Fetch the matric_no of the student based on the student_id
    student_query = "SELECT matric_no FROM students WHERE id = %s"
    cursor.execute(student_query, (student_id,))
    student_result = cursor.fetchone()

    if student_result is None:
        return jsonify({'message': 'Student not found'}), 404

    matric_no = student_result[0]

    # Insert the course record with the matric_no
    query = "INSERT INTO the_student_courses (student_id, course_id, course_code, course_name, course_unit, matric_no) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (student_id, course_id, course_code, course_name, course_unit, matric_no))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Course added successfully'}), 201


@auth.route('/get_courses', methods=['GET'])
@jwt_required()
def get_courses():
    student_id = get_jwt_identity()

    if not student_id:
        return jsonify({'message': 'You are not allowed to view this information!', 'status': 401}), 401
    
    courses = get_courses_for_student(student_id)

    if courses is not None:
        return jsonify({'courses': courses}), 200
    else:
        return jsonify({'message': 'Student not found', 'status': 404}), 404






@auth.route('/view_profile', methods=['GET'])
@jwt_required()
def view_profile():
    student_id = get_jwt_identity()

    if not student_id:
        return jsonify({'message': 'You are not allowed to view this information!', 'status': 401}), 401
    
    student = get_one_student(student_id)
    print('studentttt', student)

    if student is not None:
        courses = get_courses_for_student(student_id)
        student_data = {
            'student_id': student[0],
            'first_name': student[1],
            'last_name': student[2],
            'email': student[3],
            'matric_no': student[4],
        }
        return jsonify({'Your registration details' : student_data, 'Your courses' : courses}), 200
    else:
        return jsonify({'message': 'Student not found', 'status': 404}), 404
    



# Admin viewing single student/courses with matric_no
@auth.route('/view_student/<matric_no>', methods=['GET'])
@jwt_required()
def view_student(matric_no):
    student = get_student_matric_no(matric_no)

    if student is not None:
        student_id = student.id
        courses = get_courses_for_student(student.id)
        student_data = {
            'student_id': student_id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'email': student.email,
            'matric_no': student.matric_no,
        }
        print('studentttt', student_data, courses   )
        return jsonify({'Student details' : student_data, 'Student courses' : courses}), 200
    else:
        return jsonify({'message': 'Student not found', 'status': 404}), 404
    



# Admin viewing all students/courses
@auth.route('/view_all_students', methods=['GET'])
@jwt_required()
def view_all_students():
    students = get_all_students()

    if students is not None:
        return jsonify({'Students': students}), 200
    else:
        return jsonify({'message': 'Students not found', 'status': 404}), 404
    



# Update studnet profile
@auth.route('/update_profile', methods=['PUT'])
@jwt_required()
def update_profile():
    student_id = get_jwt_identity()
    data = request.get_json()
    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    query = "UPDATE students SET first_name = %s, last_name = %s, email = %s WHERE id = %s"
    cursor.execute(query, (first_name, last_name, email, student_id))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Profile updated successfully!', 'first_name': first_name, 'last_name': last_name, 'email': email}), 200


# Admin viewing all students registered for a particular course
@auth.route('/view_students_for_course/<course_id>', methods=['GET'])
@jwt_required()
def view_students_for_course(course_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM the_student_courses WHERE course_code= %s"
    cursor.execute(query, (course_id,))
    students = cursor.fetchall()
    if not students:
        return jsonify({'message': 'No student registered for this course', 'status': 404}), 404
    else:
        return jsonify({'Students': students}), 200
    



# Admins can view all courses a student registered for
@auth.route('/view_courses_for_student/<student_id>', methods=['GET'])
@jwt_required()
def view_courses_for_student(student_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM the_student_courses WHERE student_id = %s"
    cursor.execute(query, (student_id,))
    courses = cursor.fetchall()
    if not courses:
        return jsonify({'message': 'No course registered for this student', 'status': 404}), 404
    else:
        return jsonify({'Student and courses': courses}), 200