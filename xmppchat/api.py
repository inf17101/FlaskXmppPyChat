from flask import Flask, redirect, render_template, url_for, request, flash, send_from_directory, Response, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
from pykafka import KafkaClient
from kafka.admin import KafkaAdminClient, NewTopic
from kafka import errors
import redis, uuid
from werkzeug.urls import url_parse
import os, json, logging.config, threading

#Setup Logger
try:
    logging.config.fileConfig('xmppchat/logging/logcfg.conf')
    logger = logging.getLogger('programmLogger')
except KeyError as e:
    print(f"Error appeared!\nmessage: {e}\ncause: no log file found")
    exit(1)
except Exception as e:
    print(f"Unexpected Error appeared!\nmessage: {str(e)}\ncause: Cannot access logger!")
    exit(1)

try:
    with open("/home/xmppweb/config.json") as config_file:
        config = json.load(config_file)
except IOError as e:
    logger.error("could not start app and import configuration: " + str(e))
    exit(1)
except Exception as e:
    logger.error("unkown error appeared. Could not import configuration." + str(e))
    exit(1)

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

# set up redis for in-memory database, only used for platform ejabberd
red = redis.StrictRedis(decode_responses=True)

# user defined imports
from xmppchat.dynamicContent import navs
from xmppchat.models import User, Archiv # must be imported here otherwise User Model does not exist
from xmppchat.Validator import Validator
from xmppchat.CustomValidatonError import CustomValidationError
from xmppchat.xmppclient import EchoBot
from xmppchat.UserManagement import UserManagement

session_dict = {}

def get_kafka_client():
    """
        initialize kafka client of module pykafka
    """
    return KafkaClient(hosts=f'{config["apache_kafka_ip"]}:{config["apache_kafka_port"]}')

@login_required
@app.route('/stream')
def stream():
    """
        SSE to send recieved messages over xmpp to client or web frontend
    """
    def event_stream(user_id):
        pubsub = red.pubsub()
        global session_dict
        stream_id = session_dict[user_id]["stream_id"]
        pubsub.subscribe(stream_id)
        for message in pubsub.listen():
            yield 'data: %s\n\n' % message['data']
    return Response(event_stream(current_user.user_id), mimetype="text/event-stream", status=200)


@login_required
@app.route('/kafkastream/')
def get_messages():
    """
        SSE to send recieved messages from pykafka to client or web frontend,
        also used to send chat history of kafka to the client
    """
    client = get_kafka_client()
    def events(user_id):
        global session_dict
        for i in client.topics[session_dict[user_id]['topic']].get_simple_consumer():
            print("message:", i.value.decode())
            yield 'data: {0}\n\n'.format(i.value.decode())
    return Response(events(current_user.user_id), mimetype="text/event-stream")

def create_sleekxmpp_client(user, req_content):
    """
        method to create a sleekxmpp instance and prepare it
        req_content: required parameter of request content to create the object
        return: Object of custom sleekxmpp instance
    """
    global session_dict
    full_jid = f'{req_content["username"]}@{config["ejabberd_domain"]}'
    stream_id = str(uuid.uuid4())
    xmpp_client = EchoBot(full_jid, req_content["password"], stream_id)
    session_dict[user.user_id] = {"xmpp_object": xmpp_client, "stream_id": stream_id, "requested_platform": "xmpp"}
    plugins = ['xep_0030', 'xep_0004', 'xep_0060', 'xep_0199', 'xep_0313']

    for item in plugins:
        xmpp_client.register_plugin(item)
    return xmpp_client

def get_url_chatpage(current_user_id):
    """
        return redirect for api route depending on the selected platform of the user
        e.g. ejabberd or apache kafka backend
    """
    global session_dict
    return (url_for('gochat') if session_dict[current_user_id]['requested_platform'] == 'xmpp' else url_for('gochat_kafka'))

@app.route("/register", methods=["GET", "POST"])
def register():
    """
        registers a user on platform ejabberd and kafka
        and inserts the user into the user database
    """
    if current_user.is_authenticated:
        return get_url_chatpage(current_user.user_id)

    if request.method == "POST":
        req_content = request.get_json()
        if not req_content:
            return make_response(jsonify({'feedback': 'invalid post data.', 'category': 'danger'}), 404)

        res, exit_code = {'feedback': 'registration successfull.', 'category': 'success'}, 200
        topic_id = str(uuid.uuid4())
        try:
            Validator.validate_username(req_content["username"])
            Validator.validate_email(req_content["eMail"])
            user_reg_obj = UserManagement(config['ejabberd_ip'], config['ejabberd_ssh_user'], priv_key=config['ejabberd_ssh_private_key'], sudo_passwd=config['ejabberd_ssh_sudo_password'])
            return_code = user_reg_obj.create_user_remotely(req_content["username"], req_content["password"], config["ejabberd_domain"])
            if return_code != 0:
                raise CustomValidationError("Error. User was not created. Please try again.")

            kafka_admin_client = KafkaAdminClient(bootstrap_servers=f'{config["apache_kafka_ip"]}:{config["apache_kafka_port"]}')
            topic_list = [NewTopic(name=topic_id, num_partitions=1, replication_factor=1)]
            kafka_admin_client.create_topics(new_topics=topic_list, validate_only=False)
            
            user = User(req_content["username"], req_content["eMail"], req_content["password"], topic_id)
            db.session.add(user)
            db.session.commit()
        except KeyError as e:
            loggger.error(str(e))
            res, exit_code = {'feedback': 'invalid credentials.', 'category': 'danger'}, 401
        except CustomValidationError as cve:
            logger.error(cvstr(e))
            res, exit_code = {'feedback': str(cve), 'category': 'danger'}, 401
        except Exception as e:
            db.session.rollback()
            return_code = user_reg_obj.delete_user_remotely(req_content["username"], config["ejabberd_domain"])
            if return_code != 0:
                res, exit_code = {'feedback': 'User could not be created. Another error occurred while handling an internal error.', 'category': 'danger'}, 500
            else:
                res, exit_code = {'feedback': 'Users could not be created due to an internal error.', 'category': 'danger'}, 500
            logger.error(e)

        return make_response(jsonify(res), exit_code)
    else:
        return render_template('register.html', navs=navs, currentNav="Go Chat!")


@app.route("/login", methods=['GET', 'POST'])
def login():
    """
        logs a user into a specific platform e.g. ejabberd or kafka
        creates the appropriate client for this platform, which let the api
        interact with the platform over python clients (sleekxmpp, pykafka)
    """
    if current_user.is_authenticated:
        return redirect(get_url_chatpage(current_user.user_id))
    
    if request.method == 'POST':
        req_content = request.get_json()
        try:
            user = User.query.filter_by(username=req_content["username"]).first()
            if not user or not user.verify_password(req_content["password"]):
                return make_response(jsonify({'redirect_to': '/login', 'feedback': 'invalid login credentials.', 'category': 'danger'}), 401)
            
            if not isinstance(req_content["remember"], bool):
                return make_response(jsonify({'redirect_to': '/login', 'feedback': 'invalid data format.', 'category': 'danger'}), 404)

            global session_dict
            if user.user_id in session_dict:
                return make_response(jsonify({'redirect_to': '/gochat' if session_dict[user.user_id]['requested_platform'] == 'xmpp' else '/gochat-kafka', 'feedback': 'you are already logged in.', 'category': 'danger'}), 404)

        except KeyError:
            return make_response(jsonify({'redirect_to': '/login', 'feedback': 'invalid data format.', 'category': 'danger'}), 404)

        if req_content.get('requested_platform') == 'xmpp':
            xmpp_client = create_sleekxmpp_client(user, req_content)

            if xmpp_client.connect((config.get("ejabberd_ip"), config.get("ejabberd_port")), use_tls=True):
                t1 = threading.Thread(target=xmpp_client.process, kwargs={'block': True}, daemon=True)
                t1.start()
                login_user(user, remember=req_content["remember"]) # if no errors log user in
                return make_response(jsonify({'redirect_to': '/gochat', 'feedback': 'login successfull.', 'category': 'success'}), 200)
            return make_response(jsonify({'redirect_to': '/login', 'feedback': 'internal error: login not successfull.', 'category': 'danger'}), 500)
        elif req_content.get('requested_platform') == 'kafka':
            try:
                kafka_client = get_kafka_client()
                kafka_producer = kafka_client.topics[user.kafka_topic_id].get_producer()
            except Exception as e:
                logger.error(str(e))
                return make_response(jsonify({'redirect_to': '/login', 'feedback': 'internal error: login not successfull.', 'category': 'danger'}), 500)

            session_dict[user.user_id] = {"kafka_producer_object": kafka_producer, "topic": user.kafka_topic_id, "requested_platform": "kafka"}
            login_user(user, remember=req_content["remember"]) # if no errors log user in
            return make_response(jsonify({'redirect_to': '/gochat', 'feedback': 'login successfull.', 'category': 'success'}), 200)
        else:
            return make_response(jsonify({'redirect_to': '/login', 'feedback': 'invalid platform. Expected platform kafka or xmpp', 'category': 'danger'}), 404)

    return render_template('login.html', navs=navs, currentNav="Go Chat!")

@app.route("/get_chathistory", methods=["POST"])
@login_required
@csrf.exempt
def get_chathistory():
    """
        sends client the chat history, used only for platform ejabberd
    """
    post_data = request.get_json()
    if not post_data:
        logger.error("post data is missing.")
        return make_response({"feedback": "missing post data"}, 401)
    try:
        results = Archiv.get_chat_history(post_data["username"])
    except KeyError as e:
        logger.error(str(e))
        return make_response({"feedback": "invalid post data"}, 401)

    return make_response(jsonify({post_data["username"]: results}), 200)

@app.route("/logout")
@login_required
def logout():
    """
        loggs a user out,
        deletes the entry of the global session_dict
    """
    global session_dict
    try:
        if not current_user.user_id in session_dict:
            logger.error(f"cannot logout user with id {current_user.user_id}. user has no session.")
            flash('cannot logout user. User has no session.')

        if session_dict[current_user.user_id].get("requested_platform") == "xmpp":
            session_dict[current_user.user_id]["xmpp_object"].disconnect()

        del session_dict[current_user.user_id]
        logger.info(session_dict)
        logout_user()
    except KeyError as e:
        logger.error(str(e))
        flash("user session error.", "danger")
    except Exception:
        logger.error(str(e))
        flash("unexpected error appeared.", "danger")
    return redirect(url_for('login'))


@app.route("/gochat")
@login_required
def gochat():
    """
        sends the client the gochat.html which users can use to chat with somebody,
        used only if user uses platform ejabberd in the backend
    """
    global session_dict
    if session_dict[current_user.user_id]['requested_platform'] == 'kafka':
        return redirect(url_for('gochat_kafka'))
    response_database = User.query.with_entities(User.username).filter_by(user_id=current_user.user_id).first()
    return render_template('gochat.html', navs=navs,currentNav="Go Chat!", username=response_database[0])

@app.route("/gochat-kafka")
@login_required
def gochat_kafka():
    """
        sends the client the gochat-kafka.html which users can use to chat with somebody,
        used only if user uses platform apache kafka in the backend
    """
    if session_dict[current_user.user_id]['requested_platform'] == 'xmpp':
        return redirect(url_for('gochat'))
    response_database = User.query.with_entities(User.username).filter_by(user_id=current_user.user_id).first()
    return render_template('gochat-kafka.html', navs=navs,currentNav="Go Chat!", username=response_database[0])


@app.route("/send_message", methods=["POST"])
@login_required
@csrf.exempt
def send_message():
    """
        used to allow users sending messages to other users,
        decides which client is used to send messages based on the platform selected
    """
    if not current_user.is_authenticated:
        return make_response(jsonify({"feedback": "not authorized."}), 401)
    global session_dict
    try:
        JSON_Data = request.get_json()
        if not all(key in JSON_Data for key in ("msg_body", "from", "to", "msg_type", "msg_subject")):
            return make_response(jsonify({"feedback": "invalid post data for sending messages."}), 401)

        JSON_Data['msg_body'] = JSON_Data['msg_body'].replace('\n', '<br>')
        if session_dict[current_user.user_id]['requested_platform'] == 'xmpp':
            session_dict[current_user.user_id]["xmpp_object"].push_message(JSON_Data["to"]+"@ejabberd-server", JSON_Data["msg_body"], JSON_Data["msg_subject"], JSON_Data["msg_type"])
            msg_timestamp = datetime.today().strftime('%Y-%m-%d %H:%M')
            return make_response(jsonify({"feedback": "success", "timestamp": msg_timestamp}), 200)

        elif session_dict[current_user.user_id]['requested_platform'] == 'kafka':
            sql = 'SELECT kafka_topic_id, c.peer_id FROM contacts as c INNER JOIN user_auth as a ON c.peer_id= a.user_id WHERE c.user_id= :user_id AND c.peer_id IN (SELECT user_id FROM user_auth WHERE username= :peer_user);'
            result_proxy = db.session.execute(sql, {'user_id': current_user.user_id, 'peer_user': JSON_Data['to']})
            peer_kafka_topic, peer_id = result_proxy.fetchone()
            if not peer_kafka_topic or not peer_id:
                return make_response(jsonify({"feedback": "chat peer not found"}), 401)

            msg_timestamp = datetime.today().strftime('%Y-%m-%d %H:%M')
            msg = {"msg": JSON_Data['msg_body'], "from": JSON_Data['from'], "to": JSON_Data['to'], "timestamp": msg_timestamp, "type": "chat"}
            session_dict[current_user.user_id]['kafka_producer_object'].produce(json.dumps(msg).encode())

            if peer_id in session_dict:
                session_dict[peer_id]['kafka_producer_object'].produce(json.dumps(msg).encode())
            else:
                kafka_client = get_kafka_client()
                topic = kafka_client.topics[peer_kafka_topic]
                with topic.get_producer() as kafka_producer:
                    kafka_producer.produce(json.dumps(msg).encode())
            return make_response(jsonify({"feedback": "success", "timestamp": msg_timestamp}), 200)

        return make_response(jsonify({"feedback": "wrong plattform"}), 404)
    except Exception as e:
        logger.error(str(e))
        return make_response(jsonify({"feedback": "internal server error. Please try again."}), 500)


@app.route("/add_contact", methods=["POST"])
@login_required
@csrf.exempt
def add_contact():
    """
        Adds a contact to a user's contact list,
        chooses the right client depending on the platform selected
    """
    global session_dict
    if not current_user.is_authenticated:
        return make_response(jsonify({"feedback": "not authorized."}), 401)

    try:
        JSON_Data = request.get_json()
        if not JSON_Data or not all(key in JSON_Data for key in ("username", "requested_platform")):
            return make_response(jsonify({"feedback": "invalid post data."}), 404)

        user_name = JSON_Data.get("username")
        if Validator.contains_invalid_characters(user_name):
            return make_response(jsonify({"feedback": "invalid username."}), 403)
        result = User.query.filter_by(username=user_name).first()

        if not result:
            return make_response(jsonify({"feedback": "username does not exist."}), 404)

        if result.user_id == current_user.user_id:
            return make_response(jsonify({"feedback": "invalid username. You cannot write with yourself."}), 403)

        if JSON_Data.get("requested_platform") == "xmpp":
            session_dict[current_user.user_id]["xmpp_object"].update_roster(f'{user_name}@{config["ejabberd_domain"]}', name=user_name, subscription='both')
            return make_response(jsonify({"feedback": "added contact successfully."}), 200)
        elif JSON_Data.get("requested_platform") == "kafka":
            try:
                sql = 'INSERT INTO contacts VALUES((SELECT user_id FROM user_auth WHERE username=:username),:user_id), (:user_id, (SELECT user_id FROM user_auth WHERE username=:username));'
                db.session.execute(sql, {'user_id': current_user.user_id, 'username': user_name})
                db.session.commit()
                return make_response(jsonify({"feedback": "added contact successfully."}), 200)
            except exc.IntegrityError as e:
                return make_response(jsonify({"feedback": "Contact relationship does already exist."}), 404)

        return make_response(jsonify({"feedback": "error wrong platform."}), 404)
    except Exception as e:
        logger.error(str(e))
        return make_response(jsonify({"feedback": "contact has not been added due to an internal failure."}), 500)

@app.route("/privacy_policy")
@login_required
@csrf.exempt
def privacy_policy():
    """
        sends the html document of the privacy policy
    """
    return render_template('privacyPolicy.html', navs=navs, currentNav="Privacy Policy")

@app.route("/imprint")
@login_required
@csrf.exempt
def imprint():
    """
        sends the html document of the impressum
    """
    return render_template('imprint.html', navs=navs, currentNav="Imprint")


