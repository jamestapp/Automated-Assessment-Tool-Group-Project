from itsdangerous import URLSafeTimedSerializer
from AAT import app

#contains code to generate tokens for users to confirm emails and reset passwords

# code sourced from Real Python. 2015. Available at: https://realpython.com/handling-email-confirmation-in-flask/ 

def generate_email_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

def generate_password_confirmation_token(hashed_password):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(hashed_password, salt=app.config['SECURITY_PASSWORD_SALT'])

def confirm_email_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email

def confirm_password_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        hashed_password = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return hashed_password