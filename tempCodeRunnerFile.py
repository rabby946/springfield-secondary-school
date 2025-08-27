import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "super-secret-key")
    DATABASE_URL = os.getenv("DATABASE_URL")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    # Upload directories
    UPLOAD_DIRS = {
        'gallery': os.path.join(BASE_DIR, 'static', 'images', 'gallery'),
        'teachers': os.path.join(BASE_DIR, 'static', 'images', 'teachers'),
        'mpos': os.path.join(BASE_DIR, 'static', 'images', 'mpos'),
        'committees': os.path.join(BASE_DIR, 'static', 'images', 'committees'),
        'students': os.path.join(BASE_DIR, 'static', 'images', 'students'), 
        'results': os.path.join(BASE_DIR, 'static', 'files', 'results'),
        'routine': os.path.join(BASE_DIR, 'static', 'files', 'routine')
    }
