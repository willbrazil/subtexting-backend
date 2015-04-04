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
		rv = self.app.post('/signup', data=dict(username='will', phone='1111111111'))
		assert rv.status_code == 200
		assert 'OK' in rv.data.decode('utf-8')

	def test_user_sign_up_existing_username(self):
		u = models.User()
		u.username = 'will'
		u.password = 'password!!'
		db.session.add(u)
		db.session.commit()

		rv = self.app.post('/signup', data=dict(username=u.username, phone='1111111111'))
		assert rv.status_code == 200
		assert 'Username already taken' in rv.data.decode('utf-8')

	def test_user_generate_password(self):
		u = models.User()
		password = u.generate_password()
		assert type(password) is str
		assert len(password) == 8

	def test_verify_code(self):
		u = models.User()
		u.username = 'will'
		u.password = 'verify_random'
		db.session.add(u)
		db.session.commit()
		rv = self.app.post('/verify', data=dict(username='will', code='verify_random'))
		assert rv.status_code == 200
		assert 'OK' in rv.data.decode('utf-8')

		rv = self.app.post('/verify', data=dict(username='will', code='not'))
		assert rv.status_code == 200
		assert 'INVALID' in rv.data.decode('utf-8')

	def test_set_registration_id(self):
		u = models.User()
		u.username = 'will'
		u.password = 'verify_random'
		db.session.add(u)
		db.session.commit()

		rv = self.app.post('registration_id', data=dict(username='will', password='verify_random', registration_id='1234'))
		assert rv.status_code == 200
		assert 'OK' in rv.data.decode('utf-8')

		new_user = models.User.query.filter_by(username='will').first()
		assert new_user.registration_id == '1234'

		rv = self.app.post('registration_id', data=dict(username='will', password='invalid_pass_verify_random', registration_id='1234'))
		assert rv.status_code == 403

if __name__ == '__main__':
	unittest.main()	
