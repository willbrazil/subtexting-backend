import os
import unittest
import json

from app import app

class TestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		self.app = app.test_client()
		print('Setting up...')

	def tearDonw(self):
		print('Tearing down...')

	def test_index(self):
		rv = self.app.get('/')	
		assert 'OK'	in rv.data.decode('utf-8')

	def test_post_user_list_invalid_json(self):
		invalid_list_json = '[{contact: }]'
		rv = self.app.post('/contacts', data=dict(contact_list=invalid_list_json))
		assert rv.status_code == 404

	def test_post_user_list(self):
		contact_list = [{'name': 'Jess', 'local_id': 0 }, {'name': 'Giancarlo', 'local_id': 1}]
		rv = self.app.post('/contacts', data=dict(contact_list= json.dumps(contact_list)))
		print(rv.data)
		assert 'OK' in rv.data.decode('utf-8')

	def test_get_contact_list_empty_db(self):
		rv = self.app.get('/contacts')
		print(rv.data	)
		assert '{"contact_list": []}' in rv.data.decode('utf-8')


	def test_post_user_list(self):
		rv = self.app.post('/send', data=dict(to_local_id=0, message_body="Hello, World!"))
		assert  rv.status_code == 401

if __name__ == '__main__':
	unittest.main()	
