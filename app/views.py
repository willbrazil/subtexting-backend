import json
from app import app, db
from flask import request, make_response, url_for, g, Response
import urllib
import urllib2
from .forms import SignupForm 
from .models import User
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
	#messages = [{'from': 'Giancarlo', 'body' : 'Hello my friend!'}, {'from': 'Jess', 'body': 'What is up, love?'}]
	#return json.dumps({'message_count': len(messages), 'messages': messages})
	return 'OK'

@app.route('/contacts', methods=['POST'])
@rest_login_required
def contacts():
	try:
		contact_list = json.loads(request.form['contact_list'])
	except ValueError as e:
		response = make_response(url_for('index'), 404)
		return response
	else:	
		return 'OK'

@app.route('/contacts', methods=['GET'])
@rest_login_required
def get_contacts():
	contact_list = {
	'Jess': 0,
	'Giancarlo': 1
	}

	contact_list = {'contact_list': contact_list}
	return json.dumps(contact_list)

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

	return 'Error..'

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

#TODO: Return invalid response in case login fails.. add decorator for auth
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




def send_password_to_phone(number, password):
	data = urllib.urlencode({'number': number, 'message': "Your key is: %s" % password})	
	print(data)
	req = urllib.urlopen('http://textbelt.com/text', data.encode('utf-8'))
	return True
			