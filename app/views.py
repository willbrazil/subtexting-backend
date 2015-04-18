import json
from app import app, db
from flask import request, make_response, url_for, g, Response, jsonify
import urllib
import urllib2
from .forms import SignupForm 
from .models import User, Contact, Message
import config
import os
from functools import wraps 


def check_auth(username, password):
	if username is None or password is None:
		return None

	return User.query.filter_by(username=username, password=password).first()

# Decorator for login
def rest_login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		auth = request.authorization

		if auth is None:
			return Response('Username or password not present', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

		user = check_auth(auth.username, auth.password)
		if not auth or not user:
			return Response('Invalid Login', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

		g.user = user
		return f(*args, **kwargs)
	return decorated_function 

@app.route('/')
def index():
	return 'OK'

@app.route('/contacts', methods=['GET'])
@rest_login_required
def get_contacts():
	user = g.user
	contact_list = {}
	for c in user.contacts:
		contact_list[c.local_id] = c.name

	# remove contacts from db.

	return jsonify({'contact_list': contact_list})

@app.route('/contacts', methods=['POST'])
@rest_login_required
def contacts():

	user = g.user

	try:
		contact_list = json.loads(request.form['contact_list'])

		for key in contact_list.keys():
			if Contact.query.filter_by(local_id=key, user_id=user.id).first() is None:
				c = Contact()
				c.name = contact_list[key]
				c.local_id = key
				c.user_id = user.id
				db.session.add(c)
				db.session.commit()

	except ValueError as e:
		response = Response('Invalid json', 404)
		return response
	else:
		return 'OK'

#todo: improve response so we can indicate errors better.
@app.route('/send', methods=['POST'])
@rest_login_required
def send_message():

	gcm_url = 'https://android.googleapis.com/gcm/send'

	username = g.user.username
	to_local_id = request.form['to_local_id']
	message_body = request.form['message_body']

	api_key = os.environ.get('API_KEY')
	if api_key != None:
		headers = {
				'Authorization': "key=%s" % api_key,
				'Content-Type': 'application/json'
			}

		reg_id = g.user.registration_id
		body = {
				"registration_ids" : [reg_id],
				"data" : {
					"command" : "send_message",
					"local_id": to_local_id,
					"body" : message_body
				},
			}

		data = json.dumps(body)
		data = data.encode('utf-8')
		req = urllib2.Request(gcm_url, data, headers)
		response = None

		try:
			urllib2.urlopen(req)
		except urllib2.HTTPError as e:
			return make_response(url_for('index'), e.code)
		else:
			return 'OK'

		if response != None:
			return 'OK!'

	return make_response(url_for('index'), 500)

@app.route('/signup', methods=['POST'])
def signup():
	form = SignupForm()
	if form.validate():
		u = User()
		u.username = form.username.data
		phone = form.phone.data
		password = u.generate_password()
		u.password = password
		db.session.add(u)
		db.session.commit()

		if app.config['TESTING']:
			return 'OK'

		if send_password_to_phone(phone, password):
			return 'OK'

		return 'ERROR'
	return str(form.errors)

@app.route('/verify', methods=['POST'])
def verify():
	username = request.form['username'] 
	code = request.form['code']
	if code != None and username != None:
		if User.query.filter_by(username=username, password=code).first() != None:
			return 'OK'
	return 'INVALID'

@app.route('/registration_id', methods=['POST'])
@rest_login_required
def set_registration_id():
	reg_id = request.form['registration_id']

	u = g.user
	if u != None:
		u.registration_id = reg_id
		db.session.commit()
		return 'OK'

	return make_response(url_for('index'), 403)

@app.route('/message', methods=['POST'])
@rest_login_required
def add_message():
	user = g.user

	body = request.form['message_body']
	local_id = request.form['local_id']

	contact = user.contacts.filter_by(local_id=local_id).first()

	if contact is None:
		return Response('Invalid Local Id for Contact.', 400)

	contact_id = contact.id

	msg = Message()
	msg.body = body
	msg.contact_id = contact_id

	db.session.add(msg)
	db.session.commit()

	return 'OK'

@app.route('/message', methods=['GET'])
@rest_login_required
def get_messages():
	user = g.user

	messages = []
	for contact in user.contacts.all():
		for message in contact.messages:
			messages.append({'body': message.body, 'local_id': contact.local_id})

	msg_json = json.dumps({'messages': messages})
	return msg_json


def send_password_to_phone(number, password):
	data = urllib.urlencode({'number': number, 'message': "Your key is: %s" % password})	
	print(data)
	req = urllib.urlopen('http://textbelt.com/text', data.encode('utf-8'))
	return True
