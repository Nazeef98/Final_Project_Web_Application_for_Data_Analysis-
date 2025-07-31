import os
from pathlib import Path

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_default_secret_key'
    
    # Create absolute path for database
    BASE_DIR = Path(__file__).resolve().parent
    DB_PATH = BASE_DIR / 'instance' / 'site.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

     # New: Folder for uploaded files
    UPLOAD_FOLDER = BASE_DIR / 'uploads' # <--- NEW LINE
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 Megabytes limit for uploads <--- NEW LINE (optional but good practice)
    ALLOWED_EXTENSIONS = {'csv'} # <--- NEW LINE (Define allowed file types)