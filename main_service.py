import os
from flask import Flask, request, redirect, url_for, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from config import Config
from models import db
from routes import main as main_blueprint

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable testing mode if specified in environment variables
app.config['TESTING'] = os.environ.get('FLASK_TESTING', 'False') == 'True'

# Initialize the database
db.init_app(app)

# Initialize JWT manager
jwt = JWTManager(app)

# JWT configuration
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_SECURE'] = False  # For development; set to True in production
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'  # Set to 'Strict' in production for better security

# Register blueprint for routes
app.register_blueprint(main_blueprint)

@app.route('/')
def index():
    """Redirect to news page or show authentication page if no valid JWT."""
    if app.config['TESTING']:
        return redirect(url_for('main.index'))  # In testing environment, skip auth check
    
    try:
        verify_jwt_in_request()  # Ensure the request has a valid JWT
        return redirect(url_for('main.index'))  # Redirect to the main page
    except Exception:
        return render_template('auth_required.html'), 401  # Show authentication required page if JWT is invalid

@app.before_request
def before_request():
    """Ensure JWT is present for all requests except static files and testing environment."""
    if app.config['TESTING']:
        return  # Skip JWT verification in the testing environment

    if request.endpoint and request.endpoint != 'static':  # Skip static files
        try:
            verify_jwt_in_request()  # Verify JWT in all non-static requests
        except Exception:
            return render_template('auth_required.html'), 401  # Return 401 if JWT verification fails

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    return jsonify({"error": "잘못된 요청입니다."}), 400

@app.errorhandler(401)
@app.errorhandler(422)
def handle_auth_error(error):
    """Handle authentication errors (401 Unauthorized, 422 Unprocessable Entity)."""
    return render_template('auth_required.html'), 401

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 Not Found errors."""
    return jsonify({"error": "요청한 페이지를 찾을 수 없습니다."}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server Error."""
    return jsonify({"error": "서버 내부 오류가 발생했습니다."}), 500

@app.route('/favicon.ico')
def favicon():
    """Serve the favicon."""
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

def create_app():
    """Factory function for creating the app instance."""
    return app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
