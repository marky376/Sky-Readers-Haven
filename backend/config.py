import os

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.getenv('DB_USER', 'your_username')}:{os.getenv('DB_PASSWORD', 'your_password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', 5432)}/{os.getenv('DB_NAME', 'sky_readers_haven')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API configuration
    API_KEY = os.getenv('API_KEY', 'AIzaSyDHqP9cfL3eoHmDoWNc2X8QLhEH8jK0vBg')
    API_SECRET = os.getenv('API_SECRET', 'your_api_secret')

    # JWT configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'fa8f61cb0212e3208d2d82bd2e437212')  # For session management
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'fa8f61cb0212e3208d2d82bd2e437212')  # For JWT

    # Logging configuration
    LOG_FILE = os.getenv('LOG_FILE', '/var/log/sky_readers_haven.log')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Other configurations
    # Add any additional configurations here
