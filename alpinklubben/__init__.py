"""

	Title:	__init__.py
    Pkg:    alpinklubben
	Date:	02.11.2018
	Author:	Eskil Uhlving Larsen

"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
# import secrets --> secrets.token_hex(16)
app.config['SECRET_KEY'] = '0b23102c6ef9982b232a0423349365f0'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# New default, pre-define to suppress error
# Must be set before creating the SQLAlchemy-db instance
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Makes sure site.db is created
# If it already exist, the old is used
from alpinklubben.models import User
db.create_all()

from alpinklubben import routes
