from flask import Flask, redirect, render_template, url_for, request, flash, send_from_directory, Response, jsonify, make_response
#from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.urls import url_parse
import os, json, logging.config
"""
with open("/home/xmppweb/config.json") as config_file:
    config = json.load(config_file)
"""
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) #secret key of app
#app.config['SQLALCHEMY_DATABASE_URI'] = config.get('SQLALCHEMY_DATABASE_URI')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
csrf = CSRFProtect()
csrf.init_app(app)

#db = SQLAlchemy(app)
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
#from xmppchat.registrationform import RegistrationForm
from xmppchat.loginform import LoginForm
from xmppchat.dynamicContent import navs
from xmppchat.models import User # must be imported here otherwise User Model does not exist
from xmppchat.Validator import Validator
from xmppchat.CustomValidatonError import CustomValidationError

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        req_content = request.get_json()
        res = {'feedback': 'login successfull.', 'category': 'success'}
        exit_code = 200
        try:
            Validator.validate_username(req_content["username"])
            Validator.validate_email(req_content["eMail"])
            user = User(req_content["username"], req_content["eMail"], req_content["password"])
        except KeyError:
            res = {'feedback': 'invalid credentials.', 'category': 'danger'}
            exit_code = 404
        except CustomValidationError as cve:
            res = {'feedback': str(cve), 'category': 'danger'}
            exit_code = 404
        except Exception:
            res = {'feedback': 'internal server error', 'category': 'danger'}
            exit_code = 500

        return make_response(jsonify(res), exit_code)
    else:
        return render_template('register.html', navs=navs, currentNav="Go Chat!")


@app.route("/login", methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('gochat'))

    loginform = LoginForm()

    if request.method == 'POST' and loginform.validate_on_submit():
        user = User.query.filter_by(username=loginform.username.data).first()
        if user is None or not user.verify_password(loginform.password.data):
            flash("Invalid login credentials. Please try again!", 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=loginform.remember_me.data)
        next_url = request.args.get('next')
        if not next_url or url_parse(next_url).netloc != '':
            next_url = url_for('gochat')
        return redirect(next_url)

    return render_template('login.html',form=loginform, navs=navs, currentNav="Go Chat!")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/gochat")
@login_required
def gochat():
    return render_template('gochat.html', navs=navs,currentNav="Go Chat!")