from flask import Flask,g,current_app
from flask_sqlalchemy import SQLAlchemy
from flask_rbac import RBAC
from flask_login import LoginManager,current_user

import sys 
reload(sys) 
sys.setdefaultencoding('utf8') 

app = Flask(__name__)
app.config.from_object('config')
db=SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


from app import views,models


db.create_all()
