from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin # <--- NEW IMPORT
from datetime import datetime # <--- NEW IMPORT

db = SQLAlchemy()

class User(db.Model, UserMixin): # <--- INHERIT UserMixin
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
        # Relationship to uploaded files
    # files = db.relationship('UploadedFile', backref='uploader', lazy=True) # <--- NEW LINE
    files = db.relationship('UploadedFile', backref='user', lazy='dynamic')


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
    
class UploadedFile(db.Model): # <--- NEW MODEL
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    storage_path = db.Column(db.String(500), nullable=False) # Full path where the file is stored
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Link to the User who uploaded it
    uploader = db.relationship('User', backref='uploaded_files')

    def __repr__(self):
        return f'<UploadedFile {self.filename}>'