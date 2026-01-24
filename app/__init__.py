from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-bm-lifestyle'
    
    # Use DATABASE_URL from environment or fallback to local SQLite
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///bm_lifestyle.db'
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/images/products')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin_login'

    from .routes import main
    app.register_blueprint(main)

    return app
