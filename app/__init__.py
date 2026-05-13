from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
# This tells Flask-Login which view handles logins
login.login_view = 'login'  # type: ignore

# The bottom import prevents circular dependencies
from app import routes, models, errors  # noqa: E402, F401