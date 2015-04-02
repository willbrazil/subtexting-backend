from app import db

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, index=True, unique=True)
	password = db.Column(db.String)	
	contacts = db.relationship('Contact', backref='user', lazy='dynamic')

	def __repr__(self):
		return "<User %r>" % self.username

class Contact(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	local_id = db.Column(db.Integer)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))