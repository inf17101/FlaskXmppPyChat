
from flask import Flask, redirect, render_template, url_for, request, flash, send_from_directory, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required
import os, json

with open("/home/xmppweb/config.json") as config_file:
    config = json.load(config_file)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) #secret key of app
app.config['SQLALCHEMY_DATABASE_URI'] = config.get('SQLALCHEMY_DATABASE_URI')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_mgmt = LoginManager(app)
login_mgmt.login_view = 'login' # name of callback method if unauthorized user accessed a login protected site

# user defined imports
from xmppchat.registrationform import RegistrationForm
from xmppchat.loginform import LoginForm
from xmppchat.dynamicContent import navs
from xmppchat.models import User # must be imported here otherwise User Model does not exist

@app.route("/", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(form.username.data, form.email.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Thanks for registration!", 'success')
        return redirect(url_for('gochat'))
    return render_template('register.html',form=form, navs=navs, currentNav="Go Chat!")


@app.route("/login", methods=['GET', 'POST'])
def login():
    loginform = LoginForm()

    if loginform.validate_on_submit():
        user = User.query.filter_by(username=loginform.username.data).first()
        if not user or not user.verify_password(loginform.password.data):
            flash("Invalid login credentials, please try again", 'danger')
            return render_template('login.html',form=loginform, navs=navs, currentNav="Go Chat!")
        #login_mgmt.login_user(user)
        return redirect(url_for('gochat'))

    return render_template('login.html',form=loginform, navs=navs, currentNav="Go Chat!")

@app.route("/logout")
# @login_required
def logout():
    #logout_user()
    return redirect(url_for('login'))


@app.route("/gochat")
#@login_required
def gochat():
    return render_template('gochat.html', navs=navs,currentNav="Go Chat!")


