from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from sign_package.models import User

class RegistrationForm(FlaskForm):

	name = StringField('Name', validators=[DataRequired(), 
							Length(min=2, max =20)])
	username = StringField('Username', validators=[DataRequired(), 
							Length(min=2, max =20)])

	email = StringField('Email', validators= [DataRequired(), Email() ])
	password = PasswordField('Password', validators=[DataRequired() ])
	confirm_password = PasswordField('Confirm Password', 
										validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')

	def validate_username(self, username):
		user = User.query.filter_by(username = username.data).first()
		if user:
			raise ValidationError('Username is already taken select another username')

	def validate_email(self, email):
		email = User.query.filter_by(email = email.data).first()
		if email:
			raise ValidationError('Email is already used by another user')

class LoginForm(FlaskForm):

	username = StringField('Username', validators=[DataRequired(), 
							Length(min=2, max =20)])
	password = PasswordField('Password', validators=[DataRequired() ])
	submit = SubmitField('Login')


