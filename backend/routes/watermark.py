from flask import Blueprint, request, jsonify, current_app, url_for, after_this_request
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from werkzeug.utils import secure_filename
import os
from utils.image_processing import (
    generate_unique_filename,
    add_text_watermark,
    detect_watermark,
    extract_watermark_features,
    remove_watermark,
    save_processed_image,
    save_mask,
    create_comparison_image,
    save_comparison
)
import cv2
from datetime import datetime
from flask_cors import cross_origin

watermark = Blueprint('watermark', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@watermark.route('/add', methods=['POST'])
@jwt_required()
def add_watermark():
    """Add watermark to image"""
    temp_image_path = None
    try:
        # Check if user is authenticated
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': 'Unauthorized'}), 401

        # Check if image file is provided
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        if not image_file or not allowed_file(image_file.filename):
            return jsonify({'error': 'Invalid image file'}), 400

        # Get and validate watermark text
        watermark_text = request.form.get('text', '').strip()
        if not watermark_text:
            return jsonify({'error': 'Watermark text is required'}), 400

        # Get watermark parameters with defaults
        try:
            opacity = float(request.form.get('opacity', 0.5))
            if not 0 <= opacity <= 1:
                raise ValueError("Opacity must be between 0 and 1")
            
            angle = float(request.form.get('angle', 30))
            font_size = int(request.form.get('fontSize')) if request.form.get('fontSize') else None
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

        # Create necessary directories
        os.makedirs(current_app.config['TEMP_FOLDER'], exist_ok=True)
        os.makedirs(current_app.config['IMAGES_FOLDER'], exist_ok=True)
        os.makedirs(current_app.config['MASKS_FOLDER'], exist_ok=True)

        # Save uploaded image temporarily
        original_filename = secure_filename(image_file.filename)
        temp_image_path = os.path.join(current_app.config['TEMP_FOLDER'], f"temp_{original_filename}")
        image_file.save(temp_image_path)

        # Process image
        current_app.logger.debug(f"Processing image with text='{watermark_text}', opacity={opacity}, angle={angle}")
        watermarked_image, mask = add_text_watermark(
            temp_image_path,
            watermark_text,
            opacity=opacity,
            angle=angle,
            font_size=font_size
        )

        # Generate unique filenames
        stored_filename = generate_unique_filename(original_filename)
        mask_filename = f"mask_{stored_filename}"
        original_stored_filename = f"original_{stored_filename}"
        
        # Save original image
        original_path = os.path.join(current_app.config['IMAGES_FOLDER'], original_stored_filename)
        cv2.imwrite(original_path, cv2.imread(temp_image_path))

        # Save processed image and mask
        watermarked_path = save_processed_image(watermarked_image, stored_filename, current_app.config['IMAGES_FOLDER'])
        mask_path = save_mask(mask, mask_filename, current_app.config['MASKS_FOLDER'])

        # Create comparison image
        comparison = create_comparison_image(original_path, watermarked_path)
        comparison_filename = save_comparison(comparison, original_filename, current_app.config['IMAGES_FOLDER'])

        # Save to database using ImageModel
        image = current_app.image_model.create_image(
            user_id=current_user_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            watermark_type='text',
            watermark_text=watermark_text,
            watermark_opacity=opacity,
            watermark_angle=angle,
            mask_filename=mask_filename,
            original_stored_filename=original_stored_filename,
            comparison_filename=comparison_filename
        )

        # Generate URLs
        image_url = url_for('serve_image', filename=stored_filename, _external=True)
        original_url = url_for('serve_image', filename=original_stored_filename, _external=True)
        comparison_url = url_for('serve_image', filename=comparison_filename, _external=True)

        return jsonify({
            'message': 'Watermark added successfully',
            'image': {
                'id': str(image['_id']),
                'user_id': str(image['user_id']),
                'original_filename': original_filename,
                'stored_filename': stored_filename,
                'original_stored_filename': original_stored_filename,
                'comparison_filename': comparison_filename,
                'watermark_type': 'text',
                'watermark_text': watermark_text,
                'watermark_opacity': opacity,
                'watermark_angle': angle,
                'mask_filename': mask_filename,
                'url': image_url,
                'original_url': original_url,
                'comparison_url': comparison_url
            }
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error adding watermark: {str(e)}")
        return jsonify({'error': str(e)}), 500

    finally:
        if temp_image_path and os.path.exists(temp_image_path):
            try:
                os.remove(temp_image_path)
                current_app.logger.debug(f"Cleaned up temporary file: {temp_image_path}")
            except Exception as e:
                current_app.logger.error(f"Error cleaning up temporary file: {str(e)}")

@watermark.route('/remove', methods=['POST'])
@jwt_required()
def remove_watermark_route():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        if not image_file or not allowed_file(image_file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Get current user ID
        user_id = get_jwt_identity()
        
        # Get original image ID if provided
        original_image_id = request.form.get('original_image_id')
        
        # If we have an original image ID, verify ownership and get the mask
        if original_image_id:
            original_image = current_app.image_model.get_image(original_image_id, user_id)
            if not original_image:
                return jsonify({'error': 'Original watermarked image not found or unauthorized'}), 403
                
            # Get the mask filename from the original image
            mask_filename = original_image.get('mask_filename')
            if not mask_filename:
                return jsonify({'error': 'No mask found for this watermark'}), 400
                
            mask_path = os.path.join(current_app.config['MASKS_FOLDER'], mask_filename)
            if not os.path.exists(mask_path):
                return jsonify({'error': 'Watermark mask file not found'}), 400
        
        # Save uploaded image temporarily
        original_filename = secure_filename(image_file.filename)
        stored_filename = generate_unique_filename(original_filename)
        temp_image_path = os.path.join(current_app.config['TEMP_FOLDER'], stored_filename)
        image_file.save(temp_image_path)
        
        try:
            if original_image_id:
                # Get original image path - Note: we already have original_image from above
                original_path = os.path.join(current_app.config['IMAGES_FOLDER'], 
                                          original_image['original_stored_filename'])
                watermarked_path = os.path.join(current_app.config['IMAGES_FOLDER'], 
                                             original_image['stored_filename'])
                
                # Use the original mask to remove watermark
                result = remove_watermark(temp_image_path, mask_path)
            else:
                # Try to detect and remove watermark automatically
                result = remove_watermark(temp_image_path)
            
            # Save processed image
            processed_filename = f"processed_{stored_filename}"
            processed_path = save_processed_image(
                result,
                processed_filename,
                current_app.config['IMAGES_FOLDER']
            )
            
            # Create comparison with all three stages
            comparison = create_comparison_image(original_path, watermarked_path, processed_path)
            comparison_filename = save_comparison(comparison, original_filename, current_app.config['IMAGES_FOLDER'])
            
            # Save to database
            image = current_app.image_model.create_image(
                user_id=user_id,
                original_filename=original_filename,
                stored_filename=processed_filename,
                comparison_filename=comparison_filename,
                watermark_type='removed',
                original_image_id=original_image_id
            )
            
            # Generate URLs
            image_url = url_for('serve_image', filename=processed_filename, _external=True)
            comparison_url = url_for('serve_image', filename=comparison_filename, _external=True)
            
            return jsonify({
                'message': 'Watermark removed successfully',
                'image': {
                    'id': str(image['_id']),
                    'user_id': str(image['user_id']),
                    'original_filename': original_filename,
                    'stored_filename': processed_filename,
                    'comparison_filename': comparison_filename,
                    'watermark_type': 'removed',
                    'url': image_url,
                    'comparison_url': comparison_url
                }
            }), 200
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
                
    except Exception as e:
        print(f"Error removing watermark: {str(e)}")
        return jsonify({'error': str(e)}), 500

@watermark.route('/images', methods=['GET', 'OPTIONS'])
def get_user_images():
    # Handle OPTIONS request without JWT requirement
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        return response, 200

    # For actual GET requests, verify JWT
    verify_jwt_in_request()
    
    try:
        user_id = get_jwt_identity()
        current_app.logger.debug(f"Fetching images for user: {user_id}")
        
        # Use the ImageModel to get user images
        images_list = current_app.image_model.get_user_images(user_id)
        current_app.logger.debug(f"Found {len(images_list)} images")
        
        # Format the images
        formatted_images = []
        for image in images_list:
            # Generate URLs for all image versions
            image_url = url_for('serve_image', filename=image['stored_filename'], _external=True)
            original_url = url_for('serve_image', filename=image['original_stored_filename'], _external=True) if 'original_stored_filename' in image else None
            comparison_url = url_for('serve_image', filename=image['comparison_filename'], _external=True) if 'comparison_filename' in image else None
            
            # Format the image data
            formatted_image = {
                'id': str(image['_id']),
                'user_id': str(image['user_id']),
                'original_filename': image['original_filename'],
                'stored_filename': image['stored_filename'],
                'original_stored_filename': image.get('original_stored_filename'),
                'comparison_filename': image.get('comparison_filename'),
                'watermark_type': image['watermark_type'],
                'watermark_text': image.get('watermark_text'),
                'watermark_opacity': image.get('watermark_opacity'),
                'watermark_angle': image.get('watermark_angle'),
                'mask_filename': image.get('mask_filename'),
                'url': image_url,
                'original_url': original_url,
                'comparison_url': comparison_url,
                'created_at': image['created_at'].isoformat() if 'created_at' in image else None,
                'updated_at': image['updated_at'].isoformat() if 'updated_at' in image else None
            }
            
            # Remove None values
            formatted_image = {k: v for k, v in formatted_image.items() if v is not None}
            formatted_images.append(formatted_image)
        
        return jsonify({
            'images': formatted_images,
            'total_count': len(formatted_images)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting user images: {str(e)}")
        return jsonify({'error': str(e)}), 500

@watermark.route('/images/<image_id>', methods=['DELETE'])
@jwt_required()
def delete_image(image_id):
    try:
        user_id = get_jwt_identity()
        image = current_app.image_model.get_image(image_id)
        
        if not image:
            return jsonify({'error': 'Image not found'}), 404
            
        if str(image['user_id']) != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
            
        current_app.image_model.delete_image(image_id)
        return jsonify({'message': 'Image deleted successfully'}), 200
        
    except Exception as e:
        print(f"Error deleting image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@watermark.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response 