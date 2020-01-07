from flask_wtf import FlaskForm
from wtforms import Form, ValidationError, StringField, BooleanField, PasswordField, SubmitField, validators
from xmppchat.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25), validators.DataRequired()])
    email = StringField('E-Mail Address', [validators.Length(min=6, max=35), validators.DataRequired(), validators.email()])
    password = PasswordField('New Password', [validators.DataRequired(), validators.Length(min=8, max=35), validators.EqualTo('confirm', message="Passwords must be the same!")])
    confirm = PasswordField('Confirm Password', [validators.DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        """
        customized validator for wtforms
        Return: None
        Raise: ValidationError if username does already exist in database
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Please use a different username.")
    
    def validate_email(self, email):
        """
        customized validator for wtforms
        Return: None
        Raise: ValidationError if email does already exist in database
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Please use a different email address.")

