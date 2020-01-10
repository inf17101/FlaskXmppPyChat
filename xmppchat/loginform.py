from flask_wtf import FlaskForm
from wtforms import Form, ValidationError, StringField, BooleanField, PasswordField, SubmitField, validators
#from xmppchat.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25), validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired(), validators.Length(min=8, max=35)])
    submit = SubmitField('Sign In')

    
        
       
