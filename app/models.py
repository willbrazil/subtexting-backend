from app import db
import random

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, index=True, unique=True)
	password = db.Column(db.String)
	registration_id = db.Column(db.String)
	contacts = db.relationship('Contact', backref='user', lazy='dynamic')

	def generate_password(self):
		set = [1,2,7,9,'a','b','z', 'x']
		random.shuffle(set)
		return ''.join([str(x) for x in set])

	def __repr__(self):
		return "<User %r>" % self.username

class Contact(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	local_id = db.Column(db.Integer)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	messages = db.relationship('Message', backref='contact', lazy='dynamic')

class Message(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String)
	contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'))