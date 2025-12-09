"""
Flask application configuration.
Contains all configuration settings for different environments.
"""
import os
from datetime import timedelta


class Config:
    """Base configuration."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Session settings
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Database settings (from original config)
    DB_USER = os.environ.get('DB_USER') or "gameuser"
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or "yourpassword"
    DB_HOST = os.environ.get('DB_HOST') or "localhost"
    DB_PORT = int(os.environ.get('DB_PORT') or 3306)
    DB_NAME = os.environ.get('DB_NAME') or "flight_game"
    
    # Game settings (from original config)
    RATE_PER_KM = 0.5
    REWARD_MARKKA = 100
    START_MARKKA = 5_000_000
    START_SANITY = 100
    START_HP = 100
    NUM_AIRPORT_CHOICES = 10
    NUM_CONDUITS = 5
    DOOM_PER_KM = 0.001  # 1 doom tick per 1000 km
    MIN_DOOM_TRAVEL_TICK = 1
    
    # Static files
    STATIC_FOLDER = 'static'
    TEMPLATE_FOLDER = 'templates'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    # Override with secure settings
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
