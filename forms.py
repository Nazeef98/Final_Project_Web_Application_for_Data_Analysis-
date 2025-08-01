from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileRequired, FileAllowed
from models import User  # Use the User model from models.py

# db = SQLAlchemy()

class RegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    # Users can login with either username or email
    username_or_email = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')



# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     full_name = db.Column(db.String(100), nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     password_hash = db.Column(db.String(128), nullable=False)
#     # Relationship to uploaded files
#     files = db.relationship('UploadedFile', backref='uploader', lazy=True) # <--- NEW LINE

#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)

#     def __repr__(self):
#         return f'<User {self.username}>'

# class UploadedFile(db.Model): # <--- NEW MODEL
#     id = db.Column(db.Integer, primary_key=True)
#     filename = db.Column(db.String(255), nullable=False)
#     storage_path = db.Column(db.String(500), nullable=False) # Full path where the file is stored
#     upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Link to the User who uploaded it

#     def __repr__(self): 
#         return f'<UploadedFile {self.filename}>'



class UploadForm(FlaskForm): # <--- NEW FORM
    file = FileField('Select CSV File', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV files only!')
    ])
    submit = SubmitField('Upload File')