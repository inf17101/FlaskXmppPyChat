from flask import Flask, redirect, render_template, url_for, request, flash, send_from_directory, Response, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.urls import url_parse
import os, json, logging.config, threading

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
from xmppchat.xmppclient import EchoBot

session_dict = {}
i = 0

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

@app.route("/get_chathistory", methods=["POST"])
#@login_required
@csrf.exempt
def get_chathistory():
    post_data = request.get_json()
    if not post_data:
        logger.error("post data is missing.")
        return make_response({"feedback": "missing post data", "category": "danger"}, 401)
    try:
        results = Archiv.get_chat_history(post_data["username"])
    except KeyError:
        return make_response({"feedback": "invalid post data", "category": "danger"}, 401)
    """       
    chat_messages = []
    for item in results:
        chat_messages.append({
            item.
        })
    """
    #print(results)
    return make_response(jsonify({"exit_code": 200, post_data["username"]: results}), 200)

@app.route("/logout")
@login_required
def logout():
    global session_dict
    session_dict[current_user.user_id].disconnect()
    print("logout of {}".format(current_user))
    #xmpp_client.disconnect()
    logger.info(session_dict)
    logout_user()
    return redirect(url_for('login'))


@app.route("/gochat")
@login_required
def gochat():
    global session_dict
    global i
    print(i)
    if i == 0:
        xmpp_client = EchoBot("testuser2@ejabberd-server", "hallo123")
    if i == 1:
        xmpp_client = EchoBot("test@ejabberd-server", "hallo123")
        i = 0

    i += 1        
    session_dict[current_user.user_id] = xmpp_client
    print("login of {}".format(current_user), id(xmpp_client))
    plugins = ['xep_0030', 'xep_0004', 'xep_0060', 'xep_0199', 'xep_0313']

    xmpp_client['feature_mechanisms'].unencrypted_plain = True

    for item in plugins:
        xmpp_client.register_plugin(item)

    if xmpp_client.connect(("10.10.8.10", 5222)):
        print("connected")
        t1 = threading.Thread(target=xmpp_client.process, kwargs={'block': True}, daemon=True)
        t1.start()
    
    logger.info(session_dict)
    return render_template('gochat.html', navs=navs,currentNav="Go Chat!")
