from pymongo import MongoClient, ASCENDING
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson import ObjectId

class MongoDB:
    def __init__(self, app=None):
        self.client = None
        self.db = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.client = MongoClient(app.config['MONGO_URI'])
        self.db = self.client[app.config['MONGO_DB']]
        
        # Create indexes
        self.db[app.config['USERS_COLLECTION']].create_index('email', unique=True)
        self.db[app.config['IMAGES_COLLECTION']].create_index('user_id')
        self.db[app.config['MASKS_COLLECTION']].create_index('image_id')

class UserModel:
    def __init__(self, db, collection_name):
        self.collection = db[collection_name]
    
    def create_indexes(self):
        """Create necessary indexes for the users collection"""
        self.collection.create_index('email', unique=True)
    
    def create_user(self, email, password):
        user = {
            'email': email,
            'password_hash': generate_password_hash(password),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = self.collection.insert_one(user)
        user['_id'] = result.inserted_id
        return user
    
    def get_user_by_email(self, email):
        return self.collection.find_one({'email': email})
    
    def get_user_by_id(self, user_id):
        return self.collection.find_one({'_id': ObjectId(user_id)})
    
    def check_password(self, user, password):
        return check_password_hash(user['password_hash'], password)

class ImageModel:
    def __init__(self, db, collection_name):
        self.collection = db[collection_name]
    
    def create_indexes(self):
        """Create necessary indexes for the images collection"""
        self.collection.create_index([('user_id', ASCENDING)])
        self.collection.create_index([('created_at', ASCENDING)])
    
    def create_image(self, user_id, original_filename, stored_filename, watermark_type,
                    watermark_text=None, watermark_position='center', watermark_opacity=0.5,
                    watermark_pattern='single', watermark_spacing=100, watermark_angle=0,
                    watermark_font_size=24, mask_filename=None, watermark_features=None,
                    original_stored_filename=None, comparison_filename=None, original_image_id=None):
        """Create a new image record with watermark information"""
        image = {
            'user_id': ObjectId(user_id),
            'original_filename': original_filename,
            'stored_filename': stored_filename,
            'watermark_type': watermark_type,
            'watermark_text': watermark_text,
            'watermark_position': watermark_position,
            'watermark_opacity': watermark_opacity,
            'watermark_pattern': watermark_pattern,
            'watermark_spacing': watermark_spacing,
            'watermark_angle': watermark_angle,
            'watermark_font_size': watermark_font_size,
            'mask_filename': mask_filename,
            'watermark_features': watermark_features,
            'original_stored_filename': original_stored_filename,
            'comparison_filename': comparison_filename,
            'original_image_id': ObjectId(original_image_id) if original_image_id else None,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Remove None values
        image = {k: v for k, v in image.items() if v is not None}
        
        result = self.collection.insert_one(image)
        image['_id'] = result.inserted_id
        return image
    
    def get_user_images(self, user_id):
        return list(self.collection.find({'user_id': ObjectId(user_id)}).sort('created_at', -1))
    
    def get_image(self, image_id, user_id):
        return self.collection.find_one({
            '_id': ObjectId(image_id),
            'user_id': ObjectId(user_id)
        })
    
    def delete_image(self, image_id, user_id):
        return self.collection.delete_one({
            '_id': ObjectId(image_id),
            'user_id': ObjectId(user_id)
        })
    
    def set_mask(self, image_id, mask_filename):
        return self.collection.update_one(
            {'_id': ObjectId(image_id)},
            {'$set': {
                'mask_filename': mask_filename,
                'updated_at': datetime.utcnow()
            }}
        )

class WatermarkMaskModel:
    def __init__(self, db, collection_name):
        self.collection = db[collection_name]
    
    def create_indexes(self):
        """Create necessary indexes for the watermark masks collection"""
        self.collection.create_index([('image_id', ASCENDING)])
        self.collection.create_index([('features.type', ASCENDING)])
        self.collection.create_index([('features.num_contours', ASCENDING)])
        self.collection.create_index([('features.total_area', ASCENDING)])
    
    def save_mask(self, image_id, mask_data, features):
        mask = {
            'image_id': ObjectId(image_id),
            'mask_data': mask_data,
            'features': features,
            'created_at': datetime.utcnow()
        }
        result = self.collection.insert_one(mask)
        mask['_id'] = result.inserted_id
        return mask
    
    def find_similar_mask(self, features, threshold=0.85):
        similar_masks = self.collection.find({
            'features.type': features['type'],
            'features.num_contours': {
                '$gte': features['num_contours'] * (1 - threshold),
                '$lte': features['num_contours'] * (1 + threshold)
            },
            'features.total_area': {
                '$gte': features['total_area'] * (1 - threshold),
                '$lte': features['total_area'] * (1 + threshold)
            }
        })
        
        best_match = None
        highest_similarity = 0
        
        for mask in similar_masks:
            similarity = self._calculate_similarity(features, mask['features'])
            if similarity > threshold and similarity > highest_similarity:
                highest_similarity = similarity
                best_match = mask
        
        return best_match
    
    def _calculate_similarity(self, features1, features2):
        # Calculate similarity based on contours and moments
        contours_ratio = min(features1['num_contours'], features2['num_contours']) / max(features1['num_contours'], features2['num_contours'])
        area_ratio = min(features1['total_area'], features2['total_area']) / max(features1['total_area'], features2['total_area'])
        
        return (contours_ratio + area_ratio) / 2 