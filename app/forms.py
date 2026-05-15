from flask_babel import _  # type: ignore # Import this!
from wtforms import TextAreaField  # type: ignore
from wtforms.validators import Length  # type: ignore
from flask_wtf import FlaskForm  # type: ignore
from wtforms import StringField, PasswordField, BooleanField, SubmitField  # type: ignore
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo  # type: ignore
import sqlalchemy as sa  # type: ignore
from app import db
from app.models import User

class LoginForm(FlaskForm):
    # Wrap labels in _()
    username = StringField(_('Username'), validators=[DataRequired()])
    password = PasswordField(_('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_('Remember Me'))
    submit = SubmitField(_('Sign In'))

class RegistrationForm(FlaskForm):
    username = StringField(_('Username'), validators=[DataRequired()])
    email = StringField(_('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_('Register'))

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            # Wrap error messages in _()
            raise ValidationError(_('Please use a different username.'))

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError(_('Please use a different email address.'))
        
class EditProfileForm(FlaskForm):
    username = StringField(_('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_('About me'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(
                User.username == username.data))
            if user is not None:
                raise ValidationError(_('Please use a different username.'))
            
class EmptyForm(FlaskForm):
    submit = SubmitField(_('Submit'))

class PostForm(FlaskForm):
    post = TextAreaField(_('Say something'), validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_('Submit'))

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_('Request Password Reset'))

class ResetPasswordForm(FlaskForm):
    password = PasswordField(_('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_('Request Password Reset'))