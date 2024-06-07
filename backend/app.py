from flask import Flask, flash, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import bcrypt
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_password'

mail = Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"

class SignupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Handle the signup route.

    If the request method is POST, validate the signup form.
    If the form is valid, create a new user, add it to the database, and send a confirmation email.
    Flash a success message and redirect to the login page.
    If the request method is GET, render the signup template.

    Returns:
        If the request method is POST and the form is valid, redirect to the login page.
        If the request method is GET, render the signup template.
    """
    if request.method == 'POST':
        form = SignupForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(name=form.name.data, email=form.email.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()

            token = s.dumps(form.email.data, salt='email-confirm')
            msg = Message('Confirm Email', sender='noreply@demo.com', recipients=[form.email.data])
            link = url_for('confirm_email', token=token, _external=True)
            msg.body = 'Your link is {}'.format(link)
            mail.send(msg)

            flash('A confirmation email has been sent via email.', 'success')
            return redirect(url_for('login'))
            
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html')

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'
    user = User.query.filter_by(email=email).first_or_404()
    user.confirmed = True
    db.session.add(user)
    db.session.commit()
    return '<h1>Your email is confirmed. Thanks!</h1>'

if __name__ == "__main__":
    app.run(debug=True)
