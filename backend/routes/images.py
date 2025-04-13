from flask import Blueprint, jsonify, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_cors import cross_origin
from bson import ObjectId

images = Blueprint('images', __name__)

@images.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@images.route('', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_user_images():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Get current user ID from JWT token
        current_user_id = get_jwt_identity()
        
        # Get user's images from database
        images = current_app.image_model.get_user_images(current_user_id)
        
        # Format the response
        formatted_images = []
        for image in images:
            formatted_images.append({
                'id': str(image['_id']),
                'original_filename': image['original_filename'],
                'stored_filename': image['stored_filename'],
                'watermark_type': image['watermark_type'],
                'watermark_text': image.get('watermark_text'),
                'created_at': image['created_at'].isoformat(),
                'updated_at': image['updated_at'].isoformat(),
                'url': f"/uploads/images/{image['stored_filename']}"
            })
        
        return jsonify({'images': formatted_images}), 200
        
    except Exception as e:
        print(f"Error fetching images: {str(e)}")
        return jsonify({'error': 'Error fetching images', 'details': str(e)}), 500

@images.route('/<image_id>', methods=['DELETE', 'OPTIONS'])
def delete_image(image_id):
    if request.method == 'OPTIONS':
        return '', 200
        
    # Apply JWT check only for non-OPTIONS requests
    verify_jwt_in_request()
    try:
        # Get current user ID from JWT token
        current_user_id = get_jwt_identity()
        
        # Delete the image
        result = current_app.image_model.delete_image(image_id, current_user_id)
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Image not found or unauthorized'}), 404
            
        return jsonify({'message': 'Image deleted successfully'}), 200
        
    except Exception as e:
        print(f"Error deleting image: {str(e)}")
        return jsonify({'error': 'Error deleting image'}), 500 