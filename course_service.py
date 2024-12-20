from flask import Flask, request, redirect, url_for, jsonify, render_template, send_from_directory, abort
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity, jwt_required
from flask_sqlalchemy import SQLAlchemy
from config import Config, TestConfig
from models import db
from routes import course as course_blueprint
import os

app = Flask(__name__)
env = os.environ.get('FLASK_ENV')

if env == 'testing':
    app.config.from_object(TestConfig)
    app.config['TESTING'] = True
else:
    app.config.from_object(Config)
    app.config['TESTING'] = os.environ.get('FLASK_TESTING', 'False') == 'True'
    
# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(course_blueprint)

# JWT configuration
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  # Set to True in production
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'  # Set to 'Strict' in production
app.config['JWT_ERROR_MESSAGE_KEY'] = 'error'


@app.before_request
def before_request():
    if app.config['TESTING'] or not app.config.get('JWT_REQUIRED', True):
        return  # 테스트 환경이거나 JWT가 필요하지 않으면 JWT 검증 건너뛰기

    if request.endpoint and request.endpoint != 'static':
        try:
            verify_jwt_in_request()
        except Exception as e:
            if request.is_json:
                return jsonify({"error": "로그인이 필요한 서비스입니다.", "redirect": url_for('course.login', _external=True)}), 401
            return render_template('auth_required.html')

@app.route('/course_registration')
def course_registration():
    try:
        verify_jwt_in_request()
        return render_template('course_service.html')
    except Exception as e:
       return render_template('auth_required.html'), 401


@app.errorhandler(400)
def bad_request(error):
    
    return jsonify({"error": "잘못된 요청입니다."}), 400

@app.errorhandler(401)
@app.errorhandler(422)
def handle_auth_error(error):
    
    return render_template('auth_required.html'), 401

@app.errorhandler(404)
def not_found_error(error):
    
    return jsonify({"error": "요청한 페이지를 찾을 수 없습니다."}), 404

@app.errorhandler(500)
def internal_error(error):
    
    return jsonify({"error": "서버 내부 오류가 발생했습니다."}), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
