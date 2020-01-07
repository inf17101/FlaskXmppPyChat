
from flask import Flask, redirect, render_template, url_for, request, flash, send_from_directory, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required
import os, json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) #secret key of app
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://xmppweb:jK5S/v=CnE8;$!.>@localhost:3306/XmppWebDB1'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_mgmt = LoginManager(app)
# login_mgmt.login_view = 'login' # name of callback method if unauthorized user accessed a login protected site

# user defined imports
from xmppchat.registrationform import RegistrationForm
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


@app.route("/gochat")
# @login_required
def gochat():
    return render_template('gochat.html', navs=navs,currentNav="Go Chat!")


