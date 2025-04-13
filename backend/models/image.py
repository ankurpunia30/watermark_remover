from datetime import datetime
from models.user import db
import os

class Image(db.Model):
    """Image model for storing image metadata and watermark information"""
    __tablename__ = 'images'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False, unique=True)
    original_stored_filename = db.Column(db.String(255), nullable=True)
    comparison_filename = db.Column(db.String(255), nullable=True)
    watermark_type = db.Column(db.String(50), nullable=True)
    watermark_text = db.Column(db.String(255), nullable=True)
    watermark_position = db.Column(db.String(50), default='center')
    watermark_opacity = db.Column(db.Float, default=0.5)
    watermark_pattern = db.Column(db.String(50), default='single')
    watermark_spacing = db.Column(db.Integer, default=100)
    watermark_angle = db.Column(db.Float, default=0.0)
    watermark_font_size = db.Column(db.Integer, default=24)
    mask_filename = db.Column(db.String(255), nullable=True)
    watermark_features = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Image, self).__init__(**kwargs)
    
    def set_mask(self, mask_filename):
        self.mask_filename = mask_filename
    
    def to_dict(self):
        """Convert image object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'stored_filename': self.stored_filename,
            'original_stored_filename': self.original_stored_filename,
            'comparison_filename': self.comparison_filename,
            'watermark_type': self.watermark_type,
            'watermark_text': self.watermark_text,
            'watermark_position': self.watermark_position,
            'watermark_opacity': self.watermark_opacity,
            'watermark_pattern': self.watermark_pattern,
            'watermark_spacing': self.watermark_spacing,
            'watermark_angle': self.watermark_angle,
            'watermark_font_size': self.watermark_font_size,
            'mask_filename': self.mask_filename,
            'url': url_for('static', filename=f'uploads/{self.stored_filename}', _external=True),
            'original_url': url_for('static', filename=f'uploads/{self.original_stored_filename}', _external=True) if self.original_stored_filename else None,
            'comparison_url': url_for('static', filename=f'uploads/{self.comparison_filename}', _external=True) if self.comparison_filename else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Image {self.filename}>'

    @staticmethod
    def get_user_images(user_id):
        """Get all images for a user"""
        return Image.query.filter_by(user_id=user_id).order_by(Image.created_at.desc()).all()

    @staticmethod
    def get_image(image_id, user_id=None):
        """Get image by ID, optionally filtering by user_id"""
        query = Image.query.filter_by(id=image_id)
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        return query.first()

    def delete_files(self):
        """Delete image and associated files"""
        try:
            # Delete image files
            for filename in [self.stored_filename, self.original_stored_filename, self.comparison_filename]:
                if filename:
                    file_path = os.path.join(current_app.config['IMAGES_FOLDER'], filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
            
            # Delete mask file if exists
            if self.mask_filename:
                mask_path = os.path.join(current_app.config['MASKS_FOLDER'], self.mask_filename)
                if os.path.exists(mask_path):
                    os.remove(mask_path)
            
            return True
        except Exception as e:
            current_app.logger.error(f"Error deleting files for image {self.id}: {str(e)}")
            return False

class WatermarkMask:
    def __init__(self, db):
        self.db = db
        self.collection = db.watermark_masks
    
    def save_mask(self, image_id, mask_data, features):
        """
        Save watermark mask and its features to MongoDB
        """
        document = {
            'image_id': image_id,
            'mask_data': mask_data,
            'features': features,
            'created_at': datetime.utcnow()
        }
        return self.collection.insert_one(document)
    
    def find_similar_mask(self, features, threshold=0.85):
        """
        Find similar watermark mask based on features
        """
        # Implement similarity search logic here
        # This could use various techniques like feature matching, template matching, etc.
        similar_masks = self.collection.find({
            'features.type': features['type']
            # Add more sophisticated matching criteria
        })
        
        # Process and return the best match
        best_match = None
        highest_similarity = 0
        
        for mask in similar_masks:
            similarity = self._calculate_similarity(features, mask['features'])
            if similarity > threshold and similarity > highest_similarity:
                highest_similarity = similarity
                best_match = mask
        
        return best_match
    
    def _calculate_similarity(self, features1, features2):
        """
        Calculate similarity between two sets of features
        """
        # Implement similarity calculation based on your feature extraction method
        # This could use various metrics like cosine similarity, etc.
        # For now, return a placeholder similarity score
        return 0.9  # Placeholder 