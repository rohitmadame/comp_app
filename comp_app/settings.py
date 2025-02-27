from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Security Settings
SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = ["django-complaint-app.up.railway.app"]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    ...
]

# Database Configuration (Keeps SQLite as default but allows switching to PostgreSQL)
DATABASES = {
    'default': {
        'default': dj_database_url.config(default=os.getenv("DATABASE_URL"))
        
    }
}

# Static and Media Files
STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = os.getenv('MEDIA_URL', '/media/')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# Authentication Redirects
LOGIN_REDIRECT_URL = os.getenv('LOGIN_REDIRECT_URL', '/dashboard/')
LOGOUT_REDIRECT_URL = os.getenv('LOGOUT_REDIRECT_URL', '/')

# Localization
LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'en-us')
TIME_ZONE = os.getenv('TIME_ZONE', 'UTC')
USE_I18N = True
USE_TZ = True


