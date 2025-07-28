import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration settings."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = FLASK_ENV == 'development'

    # Database: Use PostgreSQL in production, fall back to SQLite for development
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///hvac_business.db'
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

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
