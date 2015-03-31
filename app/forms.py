from flask.ext.wtf import Form
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired

class NewContactForm(Form):
	name = StringField('name', validators=[DataRequired()])
	local_id = IntegerField('local_id', validators=[DataRequired()]) 