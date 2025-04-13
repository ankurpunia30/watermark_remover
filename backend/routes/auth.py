from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, verify_jwt_in_request
from database import UserModel
import re

auth = Blueprint('auth', __name__)

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    email = data['email'].lower().strip()
    password = data['password']
    
    try:
        user_model = UserModel(current_app.mongo.db, current_app.config['USERS_COLLECTION'])
        user = user_model.get_user_by_email(email)
        
        if not user or not user_model.check_password(user, password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        access_token = create_access_token(identity=str(user['_id']))
        return jsonify({
            'message': 'Signed in successfully',
            'access_token': access_token,
            'user': {
                'id': str(user['_id']),
                'email': user['email']
            }
        }), 200
    except Exception as e:
        print(f"Error during signin: {str(e)}")
        return jsonify({'error': 'Error during sign in'}), 500

@auth.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    email = data['email'].lower().strip()
    password = data['password']
    
    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400
    
    try:
        user_model = UserModel(current_app.mongo.db, current_app.config['USERS_COLLECTION'])
        
        if user_model.get_user_by_email(email):
            return jsonify({'error': 'Email already registered'}), 409
        
        user = user_model.create_user(email, password)
        access_token = create_access_token(identity=str(user['_id']))
        return jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'user': {
                'id': str(user['_id']),
                'email': user['email']
            }
        }), 201
    except Exception as e:
        print(f"Error during signup: {str(e)}")
        return jsonify({'error': 'Error creating user'}), 500

@auth.route('/me', methods=['GET'])
@jwt_required()
def get_user():
    try:
        # Get user ID from token
        current_user_id = get_jwt_identity()
        if not current_user_id:
            print("No user ID in token")
            return jsonify({'error': 'Invalid token'}), 401
            
        # Get user from database
        user_model = UserModel(current_app.mongo.db, current_app.config['USERS_COLLECTION'])
        user = user_model.get_user_by_id(current_user_id)
        
        if not user:
            print(f"User not found for ID: {current_user_id}")
            return jsonify({'error': 'User not found'}), 404
        
        # Return user data
        return jsonify({
            'id': str(user['_id']),
            'email': user['email'],
            'created_at': user['created_at'].isoformat(),
            'updated_at': user['updated_at'].isoformat()
        }), 200
    except Exception as e:
        print(f"Error getting user profile: {str(e)}")
        return jsonify({'error': 'Error retrieving user profile'}), 500