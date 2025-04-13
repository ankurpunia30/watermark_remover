from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
from database import MongoDB, UserModel, ImageModel, WatermarkMaskModel
import os
from werkzeug.middleware.proxy_fix import ProxyFix

# Initialize MongoDB connection
mongodb = MongoDB()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Configure maximum file size (32MB)
    app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
    
    # Configure maximum request body size
    app.wsgi_app = ProxyFix(app.wsgi_app)
    
    # Configure upload settings
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_PATH'] = 32 * 1024 * 1024  # 32MB max file size
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Add request size limit to environment
    os.environ['FLASK_MAX_CONTENT_LENGTH'] = str(32 * 1024 * 1024)  # 32MB in environment
    
    # Initialize extensions with proper CORS configuration
    CORS(app, 
        resources={
            r"/api/*": {
                "origins": ["http://localhost:5173"],
                "allow_headers": ["Content-Type", "Authorization"],
                "expose_headers": ["Content-Type", "Authorization"],
                "supports_credentials": True,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "max_age": 86400
            },
            r"/uploads/*": {
                "origins": ["http://localhost:5173"],
                "methods": ["GET", "OPTIONS"],
                "supports_credentials": True
            }
        },
        supports_credentials=True
    )
    
    # Configure JWT
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # For testing, remove in production
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Disable CSRF protection for testing
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Initialize MongoDB and store it in app
    mongodb.init_app(app)
    app.mongo = mongodb
    
    # Initialize models
    app.user_model = UserModel(mongodb.db, app.config['USERS_COLLECTION'])
    app.image_model = ImageModel(mongodb.db, app.config['IMAGES_COLLECTION'])
    app.mask_model = WatermarkMaskModel(mongodb.db, app.config['MASKS_COLLECTION'])
    
    # Ensure instance folders exist
    with app.app_context():
        app.user_model.create_indexes()
        app.image_model.create_indexes()
        app.mask_model.create_indexes()
        os.makedirs(app.config['IMAGES_FOLDER'], exist_ok=True)
        os.makedirs(app.config['MASKS_FOLDER'], exist_ok=True)
    
    # Register blueprints with proper URL prefixes
    from routes.auth import auth
    from routes.watermark import watermark
    from routes.images import images
    
    app.register_blueprint(auth, url_prefix='/api/auth')
    app.register_blueprint(watermark, url_prefix='/api/watermark')
    app.register_blueprint(images, url_prefix='/api/images')
    
    # Add route for serving uploaded files
    @app.route('/uploads/images/<path:filename>')
    def serve_image(filename):
        return send_from_directory(app.config['IMAGES_FOLDER'], filename)
    
    @app.route('/uploads/masks/<path:filename>')
    def serve_mask(filename):
        return send_from_directory(app.config['MASKS_FOLDER'], filename)
    
    return app

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    app.run(host='0.0.0.0', port=5000) 