from flask import Flask
from flask import redirect
from flask import url_for
from flask import request
from flask import jsonify
from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required

app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy(app)

from models import Users
login_manager = LoginManager(app)
@login_manager.user_loader
def user_loader(user_id):
    return Users.query.get(user_id)
@login_manager.unauthorized_handler
def unauthorized():
	if request.method == 'POST':
		return jsonify({'error':'Нужно авторизоваться'});
	else:
		return redirect(url_for('index'))