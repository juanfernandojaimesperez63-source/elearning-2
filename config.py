import os
from pathlib import Path
RAIZ = Path(__file__).resolve().parent
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
    DB_PATH = str(RAIZ / 'elearning.db')
    UPLOAD_DIR = str(RAIZ / 'uploads')
    MAX_PDF_MB = 10
    MAX_CONTENT_LENGTH = 12 * 1024 * 1024
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
