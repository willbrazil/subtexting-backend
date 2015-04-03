from flask.ext.wtf import Form
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, EqualTo
from app import db
from .models import User

class NewContactForm(Form):
	name = StringField('name', validators=[DataRequired()])
	local_id = IntegerField('local_id', validators=[DataRequired()]) 

class SignupForm(Form):
	username = StringField('username', validators=[DataRequired()])
	#password = StringField('password', validators=[DataRequired(), EqualTo('confirm', 'Passwords do not match.')])
	#confirm = StringField('confirm', validators=[DataRequired()])

	def validate(self):
		rv = Form.validate(self)
		if not rv:
			return False

		user = User.query.filter_by(username=self.username.data).first()
		if user == None:
			return True

		self.username.errors.append('Username already taken.')
		return False