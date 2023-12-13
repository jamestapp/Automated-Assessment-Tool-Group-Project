from datetime import datetime
from AAT import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    userno = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(120), unique=True)
    hashed_password = db.Column(db.String(16))
    assessments = db.relationship("Assessment", secondary="user_assessment")
    results = db.relationship("Result", backref="student")
    userType = db.Column(db.String(16))
    confirmed = db.Column(db.Boolean())
    annual_intake = db.Column(db.Integer)

    # prevents password from being read
    @property
    def password(self):
        raise AttributeError("Password is not readable.")

    # transforms password into hashed password
    @password.setter
    def password(self, password):
        self.hashed_password = generate_password_hash(password)

    # checks if a given plaintext password is equal to the hashed password
    def verify_password(self, password):
        return check_password_hash(self.hashed_password, password)


class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    type = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    questions = db.relationship("Question", backref="assessment")
    results = db.relationship("Result", backref="assessment")


user_assessment = db.Table(
    "user_assessment",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column(
        "assessment_id", db.Integer, db.ForeignKey("assessment.id"), primary_key=True
    ),
)


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attempt = db.Column(db.Integer)
    score = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessment.id"))
    answers = db.relationship("Answers", backref="answers")


class Answers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.Text)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"))
    result_id = db.Column(db.Integer, db.ForeignKey("result.id"))


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    question_text = db.Column(db.Text)
    explanation = db.Column(db.Text)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessment.id"))
    choices = db.relationship("Choice", backref="question", lazy="dynamic")
    truefalse = db.relationship("TrueFalse", backref="question", uselist=False)
    feedback = db.relationship("Feedback", backref="question", uselist=False)
    answers = db.relationship("Answers", backref="question_answers")


class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    choice_text = db.Column(db.Text)
    is_correct = db.Column(db.String(10))
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"))


class TrueFalse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_true = db.Column(db.String(10))
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"))


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))
    feedback_text = db.Column(db.Text)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
