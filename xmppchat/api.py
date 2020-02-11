from flask import Flask, redirect, render_template, url_for, request, flash, send_from_directory, Response, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.urls import url_parse
import os, json, logging.config

with open("/home/xmppweb/config.json") as config_file:
    config = json.load(config_file)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) #secret key of app
app.config['SQLALCHEMY_DATABASE_URI'] = config.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_BINDS'] = {
    "ejabberd_database": config.get('SQL_EJABBERD_DATABASE_URI')
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
csrf = CSRFProtect()
csrf.init_app(app)

db = SQLAlchemy(app)
login_mgmt = LoginManager(app)
login_mgmt.login_view = 'login' # name of callback method if unauthorized user accessed a login protected site

#Logger
try:
    logging.config.fileConfig('xmppchat/logging/logcfg.conf')
    logger = logging.getLogger('programmLogger')
except KeyError as e:
    print(f"Error appeared!\nmessage: {e}\ncause: no log file found")
except Exception as e:
    logger.exception(e.args)
    print(f"Unexpected Error appeared!\nmessage: {e}\ncause: Cannot access logger!")

# user defined imports
from xmppchat.dynamicContent import navs
from xmppchat.models import User, Archiv # must be imported here otherwise User Model does not exist
from xmppchat.Validator import Validator
from xmppchat.CustomValidatonError import CustomValidationError

@app.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('gochat'))

    if request.method == "POST":
        req_content = request.get_json()
        res = {'feedback': 'login successfull.', 'category': 'success'}
        exit_code = 200
        try:
            Validator.validate_username(req_content["username"])
            Validator.validate_email(req_content["eMail"])
            user = User(req_content["username"], req_content["eMail"], req_content["password"])
            db.session.add(user)
            db.session.commit()
        except KeyError:
            res = {'feedback': 'invalid credentials.', 'category': 'danger'}
            exit_code = 401
        except CustomValidationError as cve:
            res = {'feedback': str(cve), 'category': 'danger'}
            exit_code = 401
        except Exception as e:
            res = {'feedback': 'internal server error', 'category': 'danger'}
            logger.error(e)
            res = {'feedback': "{0}".format(str(e)), 'category': 'danger'}            
            exit_code = 500

        return make_response(jsonify(res), exit_code)
    else:
        return render_template('register.html', navs=navs, currentNav="Go Chat!")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('gochat'))
    
    if request.method == 'POST':
        req_content = request.get_json()
        res = {'redirect_to': '/gochat', 'feedback': 'login successfull.', 'category': 'success'}
        exit_code = 200
        try:
            user = User.query.filter_by(username=req_content["username"]).first()
            if not user or not user.verify_password(req_content["password"]):
                return make_response(jsonify({'redirect_to': '/login', 'feedback': 'invalid login credentials.', 'category': 'danger'}), 401)
            
            if not isinstance(req_content["remember"], bool):
                return make_response(jsonify({'redirect_to': '/login', 'feedback': 'invalid data format.', 'category': 'danger'}), 404)
            login_user(user, remember=req_content["remember"])
        except KeyError:
            res = {'redirect_to': '/login', 'feedback': 'invalid login credentials', 'category': 'danger'}
            exit_code = 401

        return make_response(jsonify(res), exit_code)

    return render_template('login.html', navs=navs, currentNav="Go Chat!")

@app.route("/test_db")
def test_db():
    results = Archiv.query.all()
    return make_response(jsonify({"exit_code": 200, "result": results[0].xml}), 200)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/gochat")
@login_required
def gochat():
    return render_template('gochat.html', navs=navs,currentNav="Go Chat!")
