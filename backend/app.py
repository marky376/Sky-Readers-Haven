from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import os

# Initialize extensions
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name="default"):
    """Application factory pattern"""
    from .config import config
    
    # Get the directory of the current file
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    app = Flask(__name__, 
               template_folder=os.path.join(basedir, "templates"),
               static_folder=os.path.join(basedir, "static"))
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Import models so Flask-Migrate can detect them
    from . import models
    
    # Register blueprints
    from .routes import main
    app.register_blueprint(main)
    
    return app
