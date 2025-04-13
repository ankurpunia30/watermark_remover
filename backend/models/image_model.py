from datetime import datetime
from bson.objectid import ObjectId

class ImageModel:
    def __init__(self, db):
        self.db = db
        self.collection = db.images

    def create_image(self, user_id, original_filename, stored_filename, watermark_type,
                    watermark_text=None, watermark_opacity=None, watermark_angle=None,
                    mask_filename=None, original_stored_filename=None, comparison_filename=None,
                    original_image_id=None):
        """Create a new image document"""
        image = {
            'user_id': user_id,
            'original_filename': original_filename,
            'stored_filename': stored_filename,
            'watermark_type': watermark_type,
            'watermark_text': watermark_text,
            'watermark_opacity': watermark_opacity,
            'watermark_angle': watermark_angle,
            'mask_filename': mask_filename,
            'original_stored_filename': original_stored_filename,
            'comparison_filename': comparison_filename,
            'original_image_id': original_image_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Remove None values
        image = {k: v for k, v in image.items() if v is not None}
        
        result = self.collection.insert_one(image)
        image['_id'] = result.inserted_id
        return image

    def get_image(self, image_id, user_id=None):
        """Get image by ID and optionally verify user ownership"""
        try:
            query = {'_id': ObjectId(image_id)}
            if user_id:
                query['user_id'] = user_id
            return self.collection.find_one(query)
        except:
            return None

    def get_user_images(self, user_id):
        """Get all images for a user"""
        cursor = self.collection.find({'user_id': user_id}).sort('created_at', -1)
        return list(cursor)

    def delete_image(self, image_id):
        """Delete image by ID"""
        return self.collection.delete_one({'_id': ObjectId(image_id)}) 