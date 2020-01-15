
from xmppchat.api import db, login_mgmt
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash # better security features, like hashing
from flask_login import UserMixin

class User(UserMixin, db.Model):
    """
        class User representing a user of the chatsystem
        attributes: id, username,password,automatic created jabber_id, timestamp of registration, timestamp of last login
        the class derives from UserMixin which contains default implementations of the flask_login modul required methods
    """
    __tablename__ = "user_auth"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(35), unique=True, nullable=False)
    passwd = db.Column(db.String(112), nullable=False)
    jabber_id = db.Column(db.String(255), unique=True)
    register_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    def __init__(self, user, email, passwd, jabber_domain="@localhost"):
        """
            constructor for creating an user instance
            Return: None
            Required parameters: user, email, passwd
            all other attributes like jabber_id or register_date is created automatically,
            if the user object is created
        """
        self.username = user
        self.email = email
        self.passwd = self.set_password(passwd)
        self.jabber_id = "{0}{1}".format(user, jabber_domain)
    

    def set_password(self, password, method="sha384"):
        """
        wrapper function of werkzeug security function to generate a password hash
        with default sha394 hash
        Return: string
        Required parameters: password as a string to create the hash of the password
        """
        if not type(password) == str:
            raise TypeError("expected a string as argument in set_password function.")
        return generate_password_hash(password, method=method)

    def verify_password(self, password):
        """
        wrapper function of werkzeug security function to check if a entered password
        matches the password of the user
        Return: boolean (true if passwords are the same, otherwise fals)
        Requried parameters: password e.g. of input field
        """
        return check_password_hash(self.passwd, password)
    
    def get_id(self):
        return (self.user_id)

@login_mgmt.user_loader
def load_user(user_id):
    """
        flask-login manager does nothing know about databases
        needs this function to loading a users id into his session management storage space
        Return: User obj
        Required parameters: user_id to look at the table if the user exists
    """
    return User.query.get(int(user_id))