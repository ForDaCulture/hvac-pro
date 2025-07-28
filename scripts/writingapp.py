import os

# Define the root directory of your project
root_dir = r'C:\Users\jcoul\Dev\ACTIVE\hvac-pro'

# --- The Final, Complete app.py ---
# This version imports and registers all blueprints: auth, main, inventory, and quotes.
app_py_content = '''
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_moment import Moment
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config
from models.user import User
from models.database import init_database

# --- Initialize Extensions (globally) ---
db = SQLAlchemy()
migrate = Migrate()
moment = Moment()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login hook to load a user from the database."""
    return User.get(user_id)

# --- App Factory ---
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app instance
    db.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)
    login_manager.init_app(app)

    # Create database tables if they don't exist
    with app.app_context():
        init_database()

    # --- Register All Blueprints ---
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from inventory import inventory as inventory_blueprint
    app.register_blueprint(inventory_blueprint)

    from quotes import quotes as quotes_blueprint
    app.register_blueprint(quotes_blueprint)
    # --- End Blueprint Registration ---

    # --- Configure Logging ---
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('HVAC Pro startup')

    return app
'''

# --- Script to write the updated file ---
def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"✅ Updated file: {path}")

try:
    full_path = os.path.join(root_dir, 'app.py')
    write_file(full_path, app_py_content)
    print("\n🎉 Your app.py file has been synchronized with all features.")
    print("Please restart your server one last time with 'python run.py'.")
except Exception as e:
    print(f"❌ An error occurred: {e}")