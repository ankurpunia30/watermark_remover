import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Basic Flask Config
    SECRET_KEY = os.getenv('SECRET_KEY', 'watermark-secret-key')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Image Folders
    IMAGES_FOLDER = os.path.join(UPLOAD_FOLDER, 'images')
    MASKS_FOLDER = os.path.join(UPLOAD_FOLDER, 'masks')
    TEMP_FOLDER = os.path.join(UPLOAD_FOLDER, 'temp')
    
    # MongoDB Configuration
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    MONGO_DB = os.getenv('MONGO_DB', 'watermark_db')
    
    # Collections
    USERS_COLLECTION = 'users'
    IMAGES_COLLECTION = 'images'
    MASKS_COLLECTION = 'watermark_masks'
    
    # Ensure upload directories exist
    @staticmethod
    def init_app(app):
        os.makedirs(Config.IMAGES_FOLDER, exist_ok=True)
        os.makedirs(Config.MASKS_FOLDER, exist_ok=True)
        os.makedirs(Config.TEMP_FOLDER, exist_ok=True)

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 