from flask import Flask, flash, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
import os
from flask_mail import Mail


app = Flask(__name__)
app.config["SECRET_KEY"] = "3EF255B3542D4CBB41C7B57474287"
app.config["SECURITY_PASSWORD_SALT"] = "D3CDF67955C3AB3725D7E6591AD65"

basedir = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "AAT.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True


db = SQLAlchemy(app)

# set up flask login
login_manager = LoginManager()
login_manager.init_app(app)

# set up mail
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "AATMailServer@gmail.com"
app.config["MAIL_PASSWORD"] = "awsvtliehjdjhusx"
app.config["MAIL_USE_SSL"] = True
mail = Mail(app)

from AAT import routes, models

# Addtion---------------------------------------------------
from AAT.models import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()
