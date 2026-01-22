from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-bm-lifestyle'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bm_lifestyle.db'
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/images/products')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin_login'

    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app
