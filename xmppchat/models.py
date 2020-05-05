
from xmppchat.api import db, login_mgmt
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash # better security features, like hashing
from flask_login import UserMixin
import re

regex = re.compile(r"from='([A-Za-z0-9]+)@[A-Za-z0-9-]+")

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
    kafka_topic_id = db.Column(db.String(36))
    register_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    def __init__(self, user, email, passwd, topic_id, jabber_domain="@localhost"):
        """
            constructor for creating an user instance
            Return: None
            Required parameters: user, email, passwd
            all other attributes like jabber_id or register_date is created automatically,
            if the user object is created
        """
        self.username = user.lower()
        self.email = email
        self.passwd = self.set_password(passwd)
        self.jabber_id = "{0}{1}".format(user, jabber_domain)
        self.kafka_topic_id = topic_id
    

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
        Return: boolean (true if passwords are the same, otherwise false)
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


class Archiv(db.Model):

    __bind_key__ = "ejabberd_database"
    __tablename__ = "archive"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = db.Column(db.String(191), nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)
    peer = db.Column(db.String(191), nullable=False)
    bare_peer = db.Column(db.String(191), nullable=False)
    xml = db.Column(db.String, nullable=False)
    txt = db.Column(db.String, nullable=True)
    kind = db.Column(db.String(10), nullable=True)
    nick = db.Column(db.String(191), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @staticmethod
    def get_chat_history(username):
        POSITION_XML = 1
        chat_rosters = Archiv.query.filter_by(username=username).group_by("bare_peer").all()
        chat_rosters_bare_peers = [roster.bare_peer for roster in chat_rosters]
        chat_msgs = {}
        for bare_peer in chat_rosters_bare_peers:
            list_peer_msgs = []
            results = Archiv.query.with_entities(Archiv.txt, Archiv.xml, Archiv.created_at, Archiv.kind).filter_by(username=username).filter_by(bare_peer=bare_peer).all()
            for item in results:
                match = re.findall(regex, item[POSITION_XML])
                list_peer_msgs.append({"txt": item[0], "timestamp": item[2].strftime('%Y-%m-%d %H:%M:%S'), "type": item[3], "from": match[0]})
            list_peer_msgs_sorted = list(sorted(list_peer_msgs, key=lambda k: k["timestamp"]))
            chat_msgs[bare_peer.split('@')[0]] = list_peer_msgs_sorted
        return chat_msgs



