import pytest
import json
import os
from app import create_app, db
from app.models import User, UserRole

@pytest.fixture
def client():
    app = create_app('testing')
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_signup(client):
    """Test client user registration"""
    response = client.post(
        '/auth/signup',
        data=json.dumps({
            'email': 'testclient@example.com',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    assert response.status_code == 201
    assert 'User registered successfully' in data['message']
    assert 'verification_url' in data
    
    # Check that user was created in database
    with client.application.app_context():
        user = User.query.filter_by(email='testclient@example.com').first()
        assert user is not None
        assert user.role == UserRole.CLIENT.value
        assert not user.is_verified
        assert user.verification_token is not None

def test_email_verification(client):
    """Test email verification"""
    # First create a user
    response = client.post(
        '/auth/signup',
        data=json.dumps({
            'email': 'testclient@example.com',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    # Get the verification token from database
    with client.application.app_context():
        user = User.query.filter_by(email='testclient@example.com').first()
        token = user.verification_token
    
    # Verify email
    response = client.get(f'/auth/verify/{token}')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert 'Email verified successfully' in data['message']
    
    # Check that user is now verified
    with client.application.app_context():
        user = User.query.filter_by(email='testclient@example.com').first()
        assert user.is_verified
        assert user.verification_token is None

def test_login_client_user(client):
    """Test client user login"""
    # Create and verify user
    with client.application.app_context():
        user = User(
            email='testclient@example.com',
            password='password123',
            role=UserRole.CLIENT.value
        )
        user.is_verified = True
        db.session.add(user)
        db.session.commit()
    
    # Login
    response = client.post(
        '/auth/login',
        data=json.dumps({
            'email': 'testclient@example.com',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    assert response.status_code == 200
    assert 'Login successful' in data['message']
    assert 'access_token' in data
    assert data['user_role'] == UserRole.CLIENT.value

def test_login_ops_user(client):
    """Test operations user login"""
    # Create ops user
    with client.application.app_context():
        user = User(
            email='testops@example.com',
            password='password123',
            role=UserRole.OPS.value
        )
        user.is_verified = True
        db.session.add(user)
        db.session.commit()
    
    # Login
    response = client.post(
        '/auth/login',
        data=json.dumps({
            'email': 'testops@example.com',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    assert response.status_code == 200
    assert 'Login successful' in data['message']
    assert 'access_token' in data
    assert data['user_role'] == UserRole.OPS.value

def test_login_unverified_client(client):
    """Test login attempt with unverified client user"""
    # Create unverified client user
    with client.application.app_context():
        user = User(
            email='unverified@example.com',
            password='password123',
            role=UserRole.CLIENT.value
        )
        db.session.add(user)
        db.session.commit()
    
    # Try to login
    response = client.post(
        '/auth/login',
        data=json.dumps({
            'email': 'unverified@example.com',
            'password': 'password123'
        }),
        content_type='application/json'
    )
    
    data = json.loads(response.data)
    assert response.status_code == 403
    assert 'verify your email' in data['message'].lower()