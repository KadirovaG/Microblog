import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask, request # type: ignore  # noqa: F401
from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_login import LoginManager # type: ignore
from flask_migrate import Migrate # type: ignore
from flask_mail import Mail # type: ignore
from flask_moment import Moment # type: ignore
from flask_babel import Babel, lazy_gettext as _l # type: ignore


app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['POSTS_PER_PAGE'] = 3
app.config['LANGUAGES'] = ['en', 'es']

# Email config
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT') or 25)
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS') is not None
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['ADMINS'] = ['your-email@example.com']

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = _l('Please log in to access this page.')
mail = Mail(app)
moment = Moment(app)


def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES']) or 'en'


babel = Babel(app, locale_selector=get_locale)


if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')


from app import routes, models, errors  # noqa: E402, F401
