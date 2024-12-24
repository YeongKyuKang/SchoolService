from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response
from flask_jwt_extended import JWTManager, create_access_token, set_access_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.routing import BuildError
from config import Config
from models import db, User
from datetime import timedelta
from urllib.parse import urlparse
import pymysql
from bcrypt import hashpw, gensalt

app = Flask(__name__, static_url_path='/static')
app.config.from_object(Config)
db.init_app(app)
jwt = JWTManager(app)


# MySQL DB 접속 정보 (대조용)
DB_CONFIG_SOURCE = {
    'host': '3.39.192.56',
    'user': 'admin',
    'password': 'P*ssword123',
    'database': 'university'
}

# MySQL DB 접속 정보 (저장용)
DB_CONFIG_DEST = {
    'host': '121.160.41.222',
    'user': 'admin',
    'password': 'P*ssword123',
    'database': 'user_db'
}

# JWT 설정 추가
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  # 개발 환경에서는 False, 프로덕션에서는 True로 설정
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            student_id = request.form.get('student_id')
            password = request.form.get('password')

            if not student_id or not password:
                return jsonify({"error": "Student ID and password are required"}), 400

            user = User.query.filter_by(student_id=student_id).first()

            if user and check_password_hash(user.password_hash, password):
                access_token = create_access_token(identity=str(user.user_id))
                redirect_url = f"http://kangyk.com/main"

                # JWT 토큰을 쿠키에 저장
                response = make_response(jsonify({
                    'success': True,
                    'message': '로그인 성공',
                    'redirect_url': redirect_url
                }))
                set_access_cookies(response, access_token)

                # 로그인 후 원래 URL로 리디렉션
                return response, 200
            else:
                return jsonify({
                    'success': False,
                    'message': '잘못된 사용자 이름 또는 비밀번호입니다.'
                }), 401
        except Exception as e:
            return jsonify({"error": "로그인 처리 중 오류가 발생했습니다."}), 500

    return render_template('login.html')

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/redirect_to_register')
def redirect_to_register():
    return redirect(url_for('register'))

@app.route('/signup', methods=['POST'])
def signup():
    # 요청 데이터 가져오기
    data = request.json

    # 필수 데이터 검증
    required_fields = ['student_id', 'email', 'password', 'department', 'name', 'phone_number']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400

    student_id = data['student_id']
    email = data['email']
    password = data['password']
    department = data['department']
    name = data['name']
    phone_number = data['phone_number']

    # MySQL 데이터베이스 연결 및 대조
    try:
        connection = pymysql.connect(**DB_CONFIG_SOURCE)
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # `student_info` 테이블에서 이메일과 학번으로만 대조
        query = """
            SELECT * 
            FROM student_info 
            WHERE email = %s 
              AND student_id = %s
        """
        cursor.execute(query, (email, student_id))
        result = cursor.fetchone()

        if not result:
            return jsonify({'error': 'User information does not match any record in student_info database'}), 400
    except pymysql.MySQLError as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

    # MySQL 대상 데이터베이스에 회원 정보 저장
    try:
        connection = pymysql.connect(**DB_CONFIG_DEST)
        cursor = connection.cursor()
        
        if User.query.filter_by(student_id=student_id).first():
            return jsonify({"success": False, "message": "이미 등록된 학번입니다."}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"success": False, "message": "이미 등록된 이메일입니다."}), 400

        # 비밀번호 해싱
        password_hash = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

        # `users` 테이블에 데이터 삽입
        insert_query = """
            INSERT INTO users (student_id, email, department, name, phone_number, password_hash)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (student_id, email, department, name, phone_number, password_hash))
        connection.commit()
    except pymysql.MySQLError as e:
        return jsonify({'error': f'Failed to save user information: {str(e)}'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

    # 회원가입 성공 메시지 반환
    return jsonify({'message': 'Sign up successful! Your information has been saved.'}), 200

@app.errorhandler(400)
def bad_request(error):
   return jsonify({"error": "잘못된 요청입니다."}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "인증되지 않은 접근입니다."}), 401

@app.errorhandler(500)
def internal_server_error(error):
   return jsonify({"error": "서버 내부 오류가 발생했습니다."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)

