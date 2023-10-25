from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired

class SignUpForm(FlaskForm):
    inputFirstName = StringField('First Name', validators=[DataRequired(message='First name is required')])
    inputLastName = StringField('Last Name', validators=[DataRequired(message='Last name is required')])
    inputEmail = StringField('Email', validators=[DataRequired(message='Email is required')])
    inputPassword = PasswordField('Password', validators=[DataRequired(message='Password is required')])
    inputConfirmPassword = PasswordField('Confirm Password', validators=[DataRequired(message='Confirm password is required'), EqualTo('inputPassword', message='Passwords must match')])
    submit = SubmitField('Sign Up')

class SignInForm(FlaskForm):
    inputEmail = StringField('Email', validators=[DataRequired(message='Email is required')])
    inputPassword = PasswordField('Password', validators=[DataRequired(message='Password is required')])
    submit = SubmitField('Sign In')

class ProjectForm(FlaskForm):
    inputName = StringField('Project Name', validators=[DataRequired(message='Please enter a project name')])
    inputDescription = TextAreaField('Project Description', validators=[DataRequired(message='Please enter a project description')])
    inputDeadline = DateField('Deadline', validators=[DataRequired(message='Please enter a deadline')])
    inputStatus = SelectField('Status', coerce=int, validators=[InputRequired()])

    submit = SubmitField('Submit')

class TaskForm(FlaskForm):
    inputDescription = StringField('Task Description', validators=[DataRequired(message='Please enter a task description')])
    inputPriority = SelectField('Priority', coerce=int, validators=[InputRequired()])
    inputDeadline = DateField('Deadline', validators=[DataRequired(message='Please enter a deadline')])
    inputStatus = SelectField('Status', coerce=int, validators=[InputRequired()])
    inputProjectID = SelectField('Project', coerce=int, validators=[InputRequired()])
    submit = SubmitField('Submit')