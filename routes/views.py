from functools import wraps
from flask import render_template, redirect, jsonify, make_response, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, unset_jwt_cookies
from sqlalchemy import desc
from . import main
from models import db, Course, Registration, Student, Festival

def jwt_optional(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_app.config['TESTING']:
            try:
                verify_jwt_in_request(optional=True)
            except Exception:
                pass
        return f(*args, **kwargs)
    return wrapper

@main.route('/')
@jwt_optional
def index():
    try:
        current_user_id = get_jwt_identity()
        student = Student.query.filter_by(id=current_user_id).first()

        # Fetch available festivals
        festivals = (
            Festival.query
            .filter(Festival.capacity > Festival.total_seats)
            .order_by(desc(Festival.capacity))
            .limit(9)
            .all()
        )

        # Fetch applied courses for the student
        applied_courses_data = []
        if student:
            applied_courses = db.session.query(Course).join(Registration).filter(
                Registration.student_id == student.id,
                Registration.status == 'Applied'
            ).all()

            applied_courses_data = [{
                'id': course.id,
                'course_name': course.course_name,
                'professor': course.professor,
                'credits': course.credits,
                'department': course.department,
                'year': course.year
            } for course in applied_courses]

        return render_template('index.html', 
                               username=student.name if student else 'User',
                               festivals=festivals,
                               applied_courses=applied_courses_data)
    except Exception as e:
        current_app.logger.error(f"Error in index route: {e}")
        return "Internal Server Error", 500

@main.route('/api/festivals')
@jwt_optional
def api_festivals():
    try:
        festivals = (
            Festival.query
            .filter(Festival.capacity > Festival.total_seats)
            .order_by(desc(Festival.capacity))
            .limit(9)
            .all()
        )

        festivals_data = [festival.to_dict() for festival in festivals]
        return jsonify({"success": True, "festivals": festivals_data})
    except Exception as e:
        current_app.logger.error(f"Error in api_festivals route: {e}")
        return jsonify({"success": False, "error": "An unexpected error occurred"}), 500

@main.route('/festival')
@jwt_optional
def festival():
    return redirect('http://localhost:5002/')

@main.route('/news')
@jwt_optional
def news():
    return redirect('http://localhost:5004/news')

@main.route('/course_registration')
@jwt_optional
def course_registration():
    return redirect('http://localhost:5001/course_registration')

@main.route('/logout')
@jwt_required()
def logout():
    response = make_response(redirect('http://localhost:5006/login'))
    unset_jwt_cookies(response)
    return response

@main.route('/login')
def login():
    return redirect('http://localhost:5006/login')