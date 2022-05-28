from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"


def create_database(app):
    if not (Path(__file__).parent / DB_NAME).exists():
        db.create_all(app=app)
        print('Created Database!')


def create_app():
    from .views import views
    from .auth import auth
    from .models import User

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "10adec989e572b59ece2facf"  # Sample Security Key
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(id1):
        return User.query.get(int(id1))

    create_database(app)

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    return app
