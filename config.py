import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-jwt-secret')
    SECRET_KEY = os.getenv('API_GATEWAY_SECRET_KEY', 'default-api-gateway-secret')
    SQLALCHEMY_DATABASE_URI = f"mysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = False  # Set to True in production
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

class TestConfig(Config):
    JWT_SECRET_KEY = os.getenv('TEST_JWT_SECRET_KEY')
    TESTING = True
    JWT_REQUIRED = False
    SQLALCHEMY_DATABASE_URI = f"mysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', 'P*ssW0rd')}@{os.getenv('DB_HOST', 'mysql')}/{os.getenv('DB_NAME', 'festival_db')}"
    SECRET_KEY = os.getenv('TEST_FESTIVAL_SERVICE_SECRET_KEY')
    