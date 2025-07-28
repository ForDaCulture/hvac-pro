import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration settings."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = FLASK_ENV == 'development'

    # --- THIS IS THE CORRECTED LINE ---
    # Use PostgreSQL in production, fall back to SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///hvac_business.db'
    
    # Optional: silence a deprecation warning
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Fix for Heroku's old "postgres://" prefix
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

    # API Keys
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    
    # Business Information
    BUSINESS_INFO = {
        'name': os.environ.get('BUSINESS_NAME', 'HVAC Pro Services'),
        'email': os.environ.get('BUSINESS_EMAIL', 'info@hvacpro.com'),
        'phone': os.environ.get('BUSINESS_PHONE', '+1234567890'),
        'address': os.environ.get('BUSINESS_ADDRESS', '123 Business St'),
        'hourly_rate': float(os.environ.get('HOURLY_RATE', '85'))
    }

    # Ensure SECRET_KEY is set in production
    if FLASK_ENV == 'production' and not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for production environment")