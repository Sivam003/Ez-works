from flask import Blueprint, request, jsonify, current_app, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User, UserRole
from app.services.email_service import send_verification_email
import uuid

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Create a new client user account"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'message': 'User already exists with this email'}), 409
    
    # Create new client user
    new_user = User(
        email=data['email'],
        password=data['password'],
        role=UserRole.CLIENT.value
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    # Send verification email
    send_verification_email(new_user)
    
    verification_url = url_for(
        'auth.verify_email', 
        token=new_user.verification_token, 
        _external=True
    )
    
    return jsonify({
        'message': 'User registered successfully. Please check your email for verification.',
        'verification_url': verification_url
    }), 201

@auth_bp.route('/verify/<token>', methods=['GET'])
def verify_email(token):
    """Verify user's email address"""
    user = User.query.filter_by(verification_token=token).first()
    
    if not user:
        return jsonify({'message': 'Invalid verification token'}), 404
    
    user.is_verified = True
    user.verification_token = None
    db.session.commit()
    
    return jsonify({'message': 'Email verified successfully. You can now login.'}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login for both ops and client users"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401
    
    if not user.is_verified and user.role == UserRole.CLIENT.value:
        return jsonify({'message': 'Please verify your email before logging in'}), 403
    
    # Create access token
    access_token = create_access_token(identity={
        'user_id': user.id,
        'email': user.email,
        'role': user.role
    })
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user_role': user.role
    }), 200