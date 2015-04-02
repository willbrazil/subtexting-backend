import os
import unittest
import json

from app import app, db, models
from config import basedir

class TestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
		self.app = app.test_client()
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

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
		pass


	def test_post_user_list(self):
		rv = self.app.post('/send', data=dict(to_local_id=0, message_body="Hello, World!"))
		assert  rv.status_code == 401

	def test_user_sign_up(self):
		rv = self.app.post('/signup', data=dict(username='will', password='pass', confirm='pass'))
		assert rv.status_code == 200
		assert 'OK' in rv.data.decode('utf-8')

	def test_user_sign_up_existing_username(self):
		u = models.User()
		u.username = 'will'
		u.password = 'password!!'
		db.session.add(u)
		db.session.commit()

		rv = self.app.post('/signup', data=dict(username=u.username, password='randompass', confirm='randompass'))
		assert rv.status_code == 200
		assert 'Username already taken' in rv.data.decode('utf-8')

if __name__ == '__main__':
	unittest.main()	
