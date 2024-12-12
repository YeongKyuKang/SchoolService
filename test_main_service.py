import unittest
import os
import time
import json
from unittest.mock import patch
from flask import url_for
from main_service import app, db
from sqlalchemy.exc import OperationalError

class TestMainService(unittest.TestCase):
    def setUp(self):
        """Set up for each test: initialize the app, configure the database, and wait for MySQL."""
        app.config['TESTING'] = True
        os.environ['FLASK_TESTING'] = 'True'

        # Use environment variables or fallback to default values for CI environment
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL', 
            f"mysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', 'P*ssW0rd')}"
            f"@{os.getenv('DB_HOST', 'mysql')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'main_db')}"
        )

        # Initialize the app's test client and the database
        self.app = app.test_client()
        self._wait_for_mysql()

    def _wait_for_mysql(self):
        """Ensure MySQL is available before running tests."""
        retries = 30
        while retries > 0:
            try:
                with app.app_context():
                    db.engine.connect()
                return
            except OperationalError:
                retries -= 1
                time.sleep(2)
        raise Exception("MySQL not available after retries")

    def test_home_redirect(self):
        """Test the home route redirects to the main index."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/main.index' in response.location)

    def test_index_unauthenticated(self):
        """Test that unauthenticated users are redirected to login."""
        response = self.app.get(url_for('main.index'))
        self.assertEqual(response.status_code, 401)
        self.assertIn('로그인이 필요한 서비스입니다.', response.data)

    @patch('requests.get')  # Mock external requests
    def test_festival_page(self, mock_get):
        """Test the festival page redirects correctly."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'festivals': []}  # Mock response
        response = self.app.get('/festival')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.startswith('http://localhost:5002'))

    @patch('requests.get')  # Mock external requests
    def test_news_page(self, mock_get):
        """Test the news page redirects correctly."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'news': []}  # Mock response
        response = self.app.get('/news')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.startswith('http://localhost:5004/news'))

    @patch('requests.get')  # Mock external requests
    def test_api_festivals(self, mock_get):
        """Test the API for festivals."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'festivals': [], 'success': True}
        
        response = self.app.get('/api/festivals')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('success', data)
        self.assertTrue(data['success'])

        # Ensure festivals key exists in the response
        self.assertIn('festivals', data)

    @patch('requests.get')  # Mock external requests
    def test_course_registration_page(self, mock_get):
        """Test the course registration page redirects correctly."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'courses': []}  # Mock response
        response = self.app.get('/course_registration')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.startswith('http://localhost:5001/course_registration'))

    @patch('requests.get')  # Mock external requests
    def test_logout(self, mock_get):
        """Test the logout route redirects to the login page."""
        response = self.app.get('/logout')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.startswith('http://localhost:5006/login'))

    @patch('main_service.views.jwt_required')  # Mock JWT decorator for authenticated route
    def test_index_authenticated(self, mock_jwt_required):
        """Test that authenticated users can access the index route."""
        with self.app:
            # Simulate authentication (mock JWT token or other methods)
            self.client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer <your_jwt_token_here>'
            response = self.app.get(url_for('main.index'))
            self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
