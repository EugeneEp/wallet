from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from sqlalchemy import and_
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from models import Users, Transactions, Wallets, hashpass, hashcsv, mergeTwoListsAsDict, Sms_approve, API, timeToDate, dateToTime, movementTranslate
import requests
import time as timec
import glob
import os
import re
import csv
import json

wallet = Blueprint('wallet', __name__, template_folder = 'templates')

# Все транзакции
@wallet.route('/')
@login_required
def index():
	page = request.args.get('page')
	page = int(page) if page and page.isdigit() else 1

	date_from = request.args.get('from')
	date_end = request.args.get('to')
	filters = []

	if date_from and date_from != "":
		filters.append(Transactions.time > dateToTime(date_from))
	if date_end and date_end != "":
		filters.append(Transactions.time < dateToTime(date_end))

	transactions = current_user.transactions.filter(and_(*filters)).order_by(Transactions.id.desc()).paginate(page=page, per_page=8)

	for i in transactions.items:
		i.time = timeToDate(i.time)
		i.movement_type = movementTranslate(i.movement_type)

	return render_template('wallet/mywallet.html', t=transactions)

# Профиль
@wallet.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
	if request.method == 'GET':
		identity = {'fullname': '', 'passport': '', 'passportIssuedAt': ''}
		if current_user.identity:
			identity.update(json.loads(current_user.identity))
		return render_template('wallet/profile.html', identity=identity)
	else:
		fullname = request.form['fullname']
		passport = request.form['passport']
		passportIssuedAt = request.form['passportIssuedAt']

		if fullname == '' and passport == '' and passportIssuedAt == '':
			return json.dumps({'error':'Не все поля заполнены'})
		
		fullnameArr = fullname.split()
		passport = passport.replace(' ', '')

		if len(fullnameArr) < 3:
			return json.dumps({'error':'ФИО введено не корректно'})

		identity = {
			'fullname': fullname,
			'lastName': fullnameArr[0],
			'firstName': fullnameArr[1],
			'secondName': fullnameArr[2],
			'passport': passport,
			'passportIssuedAt':passportIssuedAt
		}

		identity = json.dumps(identity)

		current_user.identity = identity

		db.session.add(current_user)
		db.session.commit()

		return json.dumps({'success':'Данные успешно отправлены'})

# Загрузить аватарку
@wallet.route('/profile_picture', methods=['POST'])
@login_required
def profile_picture():
	if request.method == 'POST':
		if request.files['img']:
			for x in glob.glob('static/upload/profile/' + str(current_user.id) + '.png'):
				os.unlink(x)
			f = request.files['img']
			ext = f.filename.split('.')[1]
			f.filename = str(current_user.id) + '.png'
			
			try:
				f.save('static/upload/profile/' + f.filename)
			except:
				return json.dumps({'error':'Что-то пошло не так'})

			return json.dumps({'success':'Успех'})
		else:
			return json.dumps({'error':'Файл не найден'})
	else:
		return json.dumps({'error':'Метод не найден'})

# Пополнить кошелек
@wallet.route('/charge', methods=['GET', 'POST'])
@login_required
def charge():
	if request.method == 'GET':
		return render_template('wallet/charge.html')
	else:
		return json.dumps({'error':'Метод еще не готов'})

# Перевод
@wallet.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
	if request.method == 'GET':
		return render_template('wallet/transfer.html')
	else:
		return json.dumps({'error':'Метод еще не готов'})

# Создать ссылку для сбора средств на 
@wallet.route('/moneybank', methods=['GET', 'POST'])
@login_required
def moneybank():
	if request.method == 'GET':
		return render_template('wallet/moneybank.html')
	else:
		return json.dumps({'error':'Метод еще не готов'})

# Создать ссылку на пожертвования
@wallet.route('/donate', methods=['GET', 'POST'])
@login_required
def donate():
	if request.method == 'GET':
		return render_template('wallet/donate.html')
	else:
		return json.dumps({'error':'Метод еще не готов'})

@wallet.route('/partner')
@login_required
def partner():
	return render_template('wallet/partner.html')

@wallet.route('/csv', methods=['POST'])
@login_required
def csv_transactions():
	if request.method == 'POST':
		try:

			mylist = [['Дата', 'Тип транзакции', 'Статус', 'Сумма']]

			date_from = request.form['from']
			date_end = request.form['to']
			filters = []

			if date_from and date_from != "":
				filters.append(Transactions.time > dateToTime(date_from))
			if date_end and date_end != "":
				filters.append(Transactions.time < dateToTime(date_end))
			


			transactions = current_user.transactions.filter(and_(*filters)).order_by(Transactions.id.desc()).all()

			for t in transactions:
				t.time = timeToDate(t.time)
				t.movement_type = movementTranslate(t.movement_type)
				mylist.append([t.time, t.movement_type, t.status, t.amount])

			
			link = hashcsv(current_user.id)

			with open(link, 'w', newline='', encoding='cp1251') as myfile:
				wr = csv.writer(myfile, delimiter=";")
				for x in mylist:
					wr.writerow(x)

			return json.dumps({'link': '/' + link + '?t=' + str(timec.time())})

		except:
			return json.dumps({'error':'Что-то пошло не так'})
	else:
		return json.dumps({'error':'Метод не найден'})

