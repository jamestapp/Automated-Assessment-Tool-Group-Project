from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email, Regexp, NumberRange

class StudentRegistrationForm(FlaskForm):
    
    name = StringField(
        "Name",
        validators=[
            DataRequired(),
            Regexp(
                "^[a-zA-z]{1,}[a-zA-z ]*$",
                message="Your name can only contain letters, and cannot have any leading spaces.",
            ),
        ],
    )
    userno = StringField(
        "Userno",
        validators=[
            DataRequired(),
            Regexp(
                "^[a-zA-z0-9]{1,}[a-zA-z0-9]*$",
                message="Your number can only contain letters, and cannot have any leading or trailing spaces.",
            ),
        ],
    )
    annual_intake = IntegerField(
        "Year group",
        validators=[
        DataRequired(),
        NumberRange(min=2000, max=2050, message='Please input the year of your course start date')
        ]
    )

    email = EmailField(
        "Email",
        validators=[
            DataRequired(),
            Email(message="Invalid email address"),
            EqualTo("confirmEmail", message="Email addresses must match"),
        ],
    )
    confirmEmail = EmailField(
        "Confirm Email",
        validators=[DataRequired(), Email(message="Invalid email address")],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            EqualTo("confirmPassword", message="Passwords must match"),
        ],
    )
    confirmPassword = PasswordField("Confirm", validators=[DataRequired()])
    submit = SubmitField("Register")

class LecturerRegistrationForm(FlaskForm):
    
    name = StringField(
        "Name",
        validators=[
            DataRequired(),
            Regexp(
                "^[a-zA-z]{1,}[a-zA-z ]*$",
                message="Your name can only contain letters, and cannot have any leading spaces.",
            ),
        ],
    )
    userno = StringField(
        "Userno",
        validators=[
            DataRequired(),
            Regexp(
                "^[a-zA-z0-9]{1,}[a-zA-z0-9]*$",
                message="Your number can only contain letters, and cannot have any leading or trailing spaces.",
            ),
        ],
    )

    email = EmailField(
        "Email",
        validators=[
            DataRequired(),
            Email(message="Invalid email address"),
            EqualTo("confirmEmail", message="Email addresses must match"),
        ],
    )
    confirmEmail = EmailField(
        "Confirm Email",
        validators=[DataRequired(), Email(message="Invalid email address")],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            EqualTo("confirmPassword", message="Passwords must match"),
        ],
    )
    confirmPassword = PasswordField("Confirm", validators=[DataRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    userno = StringField("Userno", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class ChangePasswordForm(FlaskForm):
    oldPassword = PasswordField("Old Password", validators=[DataRequired()])
    newPassword = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            EqualTo("confirmPassword", message="Passwords must match"),
        ],
    )
    confirmPassword = PasswordField("Confirm", validators=[DataRequired()])

class UpdateDetailsForm(FlaskForm):
    user_id = StringField('User_id', validators=[Regexp('^\w{6,12}$', message='Your username should be between 6 and 12 characters long and can only contain letters and numbers.')])
    name = StringField('Name', validators=[Regexp('^[a-zA-z]{1,}[a-zA-z ]*$', message='Your name can only contain letters, and cannot have any leading spaces.')])


class ForgotForm(FlaskForm):
    email = EmailField('Email Address', validators=[DataRequired(), Email('Invalid email address')])

class PasswordRecoveryForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirmPassword', message='Passwords must match')])
    confirmPassword = PasswordField('Confirm', validators=[DataRequired()])

#Create Aseesments(Qizhen Ye)-------------------------------------------------------------
class AssessmentDetailsForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    type = StringField('Type', validators=[DataRequired()])
    

class QuestionDetailsForm(FlaskForm):
    question_text = TextAreaField('Title', validators=[DataRequired()])
    explanation = TextAreaField('Type', validators=[DataRequired()])

class ChoiceDetailsForm(FlaskForm):
    choice_text = StringField('Title', validators=[DataRequired()])
    is_correct = SelectField('Right answer', choices=[('True', 'True'), ('False', 'False')])
    submit = SubmitField('Submit')
class TrueFalseDetailsForm(FlaskForm):
    is_true = SelectField('Right or Wrong', choices=[('True', 'True'), ('False', 'False')])