from functools import wraps
from flask import render_template, redirect, url_for, request, jsonify, make_response, current_app
from flask_jwt_extended import jwt_required, unset_jwt_cookies, verify_jwt_in_request
from models import Notice, db
from . import notice

def jwt_optional(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_app.config['TESTING']:
            try:
                verify_jwt_in_request(optional=True)
            except Exception as e:
                pass
        return f(*args, **kwargs)
    return wrapper

@notice.route('/notice/news')
@jwt_optional
def index():
    return render_template('news_main.html')

@notice.route('/notice/news/<int:notice_id>')
@jwt_optional
def news_item(notice_id):
    notice = Notice.query.get_or_404(notice_id)
    return render_template('news_item.html', notice=notice)

@notice.route('/main')
def main():
    return redirect('http://kangyk.com/main')

@notice.route('/festival')
def festival():
    return redirect('http://kangyk.com/festival')

@notice.route('/course_registration')
def course():
    return redirect('http://kangyk.com/course_registration')

@notice.route('/login')
@jwt_optional
def login():
    response = make_response(redirect('http://kangyk.com/login'))
    unset_jwt_cookies(response)
    return response

@notice.route('/notice/api/notices')
def get_notices():
    notices = Notice.query.order_by(Notice.date.desc()).all()
    return jsonify([{
        'id': notice.id,
        'title': notice.title,
        'content': notice.content,
        'date': notice.date.isoformat()
    } for notice in notices])

