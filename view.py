from app import app
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask_login import login_user, login_required, logout_user, current_user, login_with_roots
from app import db
from models import Users, hashpass, mergeTwoListsAsDict, Sms_approve, API
import requests
import time
import re
import json

# index
@app.route('/')
def index():
	return render_template('index.html')

# Роут на страницы с информацией о компании
@app.route('/<template>/info')
def info(template):
	reqired_templates = ['start-business', 'about', 'business', 'capabilities', 'contacts', 'events', 'gaming', 'stream']
	if template not in reqired_templates:
		return render_template( 'index.html' )
	return render_template( template + '.html' )

# Регистрация
@app.route('/registration', methods=['POST'])
def reg_user():
	if request.method == 'POST':
		phone = request.form['phone']
		phone = re.sub("\D", "", phone)
		password = request.form['password']
		confirm = request.form['confirm']

		user = Users.query.filter(Users.phone==phone).first()
		sms = Sms_approve.query.filter(Sms_approve.phone == phone, Sms_approve.action == 'reg').first()
		if sms:
			if sms.status == 0:
				return json.dumps({'error':'Вы не подтвердили смс'})
			if user and sms.status == 1:
				return json.dumps({'error':'Такой пользователь уже зарегистрирован'})
		else:
			return json.dumps({'error':'Вы не отправили смс'})

		if phone == '' or password == '' or confirm == '':
			return json.dumps({'error':'Не все поля заполнены'})
		if confirm != password:
			return json.dumps({'error':'Пароли не совпадают'})
		user = Users(phone=phone, password=password)

		# Добавить юзера в банк по апи
		#add_user = user.add_user()
		#if add_user['ok'] != True:
		#	return json.dumps({'error':'Не получилось добавить в систему'})

		db.session.add(user)
		db.session.commit()
		login_user(user)

	return json.dumps({'success':'Успех'})

# Вход
@app.route('/login', methods=['POST'])
def log_user():
	if request.method == 'POST':
		phone = request.form['phone']
		phone = re.sub("\D", "", phone)
		password = request.form['password']
		if phone == '' or password == '':
			return json.dumps({'error':'Не все поля заполнены'})
		user = Users.query.filter(Users.phone==phone, Users.password==hashpass(password)).first()
		if user:
			if user.roots == 0:
				return json.dumps({'error':'Вы не прошли подтверждение'})
			login_user(user)
			return json.dumps({'test':'User exist'})
		else:
			return json.dumps({'error':'Телефон и пароль не совпадают'})
	else:
		return json.dumps({'error':'Request method error'})

# Выход
@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

# Отправить код по смс
@app.route('/sms', methods=['POST'])
def sms():
	if request.method == 'POST':
		timelimit = int(time.time())
		phone = request.form['phone']
		sms_type = request.form['type'] 

		phone = re.sub("\D", "", phone)

		if len(str(phone)) < 11:
			return json.dumps({'error':'Телефон введен не верно'})

		re_sms = Sms_approve.query.filter(Sms_approve.phone==phone, Sms_approve.action==sms_type).first()

		# Было ли отправлено смс по этому номеру, на конкретное действие
		if re_sms:
			if (timelimit - re_sms.time) < 60:
				return json.dumps({'error':'Повторное смс будет доступно через 60 секунд'})
			elif re_sms.action == 'reg' and re_sms.status == 1:
				return json.dumps({'error':'Такой пользователь уже зарегистрирован'}) # Если код уже использован и подтвержден
			else:
				re_sms.generate_code()
				re_sms.update_time()
				re_sms.status = 0
				# Отправить повторное смс по апи
				#send = re_sms.send_sms()
				db.session.commit()
		else:
			if current_user.is_authenticated:
				sms = Sms_approve(user_id=current_user.id, action=sms_type, phone=phone)
			else:
				sms = Sms_approve(action=sms_type, phone=phone)

			# Отправить смс по апи
			#send = sms.send_sms()
			db.session.add(sms)
			db.session.commit()

	else:
		return json.dumps({'error':'Request method error'})

	return json.dumps({'success':'Успех'})

# Проверка кода смс
@app.route('/sms_check', methods=['POST'])
def sms_check():
	if request.method == 'POST':
		phone = request.form['phone']
		phone = re.sub("\D", "", phone)
		sms_type = request.form['type'] 
		code = request.form['code']
		timelimit = int(time.time())

		sms = Sms_approve.query.filter(Sms_approve.status==0, Sms_approve.phone==phone, Sms_approve.action==sms_type, Sms_approve.code==code).first()

		if sms:
			if (timelimit - sms.time) > (60 * 60):
				return json.dumps({'error':'Проверочный код истек, отправьте повторное смс'})
			sms.status = 1
			db.session.commit()
		else:
			return json.dumps({'error':'Код смс введен не верно'})

	else:
		return json.dumps({'error':'Request method error'})

	return json.dumps({'success':'Успех'})