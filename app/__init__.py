import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
mail = Mail()

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load configuration
    from app.config import config_by_name
    app.config.from_object(config_by_name[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.file_routes import file_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(file_bp)
    
    # Create all database tables
    with app.app_context():
        db.create_all()
    
    @app.route('/')
    def index():
        return "Welcome to Secure File Sharing API! How are you doing"
    
    return app