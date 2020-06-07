
from xmppchat.models import User
from xmppchat.CustomValidatonError import CustomValidationError
import re

class Validator:

    @staticmethod
    def validate_username(user_name):
        """
        customized validator for registration/login
        Return: None
        Raise: CustomValidationError - Exception
        """
        if not user_name.islower():
            raise CustomValidationError("Invalid username. Only lower case allowed.")
        if not user_name:
            raise CustomValidationError("Please use a different username.")
        user = User.query.filter_by(username=user_name).first()
        if user:
            raise CustomValidationError("Please use a different username.")

    @staticmethod
    def validate_email(e_mail):
        """
        customized validator for registration/login
        Return: None
        Raise: CustomValidationError - Exception
        """
        if not e_mail:
            raise CustomValidationError("Please use a different e-mail address.")
        
        user = User.query.filter_by(email=e_mail).first()
        if user:
            raise CustomValidationError("Please use a different e-mail address.")

    @staticmethod
    def contains_invalid_characters(string, search=re.compile(r"^[a-zA-Z][a-zA-Z0-9]+$").search):
        """
            validate if username contains invalid characters
            string: string to search
            search: regex definition for valid username
            Return: False if string is valid, otherwise True
        """
        if string is None:
            return True
        return not bool(search(string))
