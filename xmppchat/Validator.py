
from xmppchat.models import User
from xmppchat.CustomValidatonError import CustomValidationError

class Validator:

    @staticmethod
    def validate_username(username):
        """
        customized validator for wtforms
        Return: None
        Raise: ValidationError if username does already exist in database
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise CustomValidationError("Please use a different username.")

    @staticmethod
    def validate_email(email):
        """
        customized validator for wtforms
        Return: None
        Raise: ValidationError if email does already exist in database
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise CustomValidationError("Please use a different e-mail address.")