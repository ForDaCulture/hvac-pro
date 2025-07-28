from flask import Flask, render_template
from flask_moment import Moment
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging.handlers import RotatingFileHandler
import os
from config import Config
from models.user import User

db = SQLAlchemy()
migrate = Migrate()

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- Initialize Extensions ---
    db.init_app(app)
    migrate.init_app(app, db)
    Moment(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id) # Assumes User.get is compatible

    # --- Register Blueprints ---
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # Configure Logging, Error Handlers, and Routes...
    # (The rest of the app structure remains the same)

    return app
