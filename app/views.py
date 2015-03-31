import json
from app import app
from flask import request, make_response, url_for
import urllib.request as urllib2
import urllib

@app.route('/')
def index():
	#messages = [{'from': 'Giancarlo', 'body' : 'Hello my friend!'}, {'from': 'Jess', 'body': 'What is up, love?'}]
	#return json.dumps({'message_count': len(messages), 'messages': messages})
	return 'OK'

@app.route('/contacts', methods=['POST'])
def contacts():
	try:
		contact_list = json.loads(request.form['contact_list'])
	except ValueError as e: 
		response = make_response(url_for('index'), 404)
		return response
	else:	
		return 'OK'

@app.route('/contacts', methods=['GET'])
def get_contacts():
	contact_list = {
	'Jess': 0,
	'Giancarlo': 1
	}

	contact_list = {'contact_list': contact_list}
	return json.dumps(contact_list)

@app.route('/send', methods=['POST'])
def send_message():

	gcm_url = 'https://android.googleapis.com/gcm/send'

	to_local_id = request.form['to_local_id']
	message_body = request.form['message_body']

	headers = {
			'Authorization': "API_KEY_GOES_HERE8",
			'Content-Type': 'application/json'
		}

	body = {
			"registration_ids" : ["DEVICE ID GOES HERE"],
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
	except urllib.error.HTTPError as e:
		return make_response(url_for('index'), e.code)
	else:
		return 'OK'

	if response != None:
		return 'OK!'

	return 'Error..'