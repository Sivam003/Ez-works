import pytest
import json
import os
import io
from flask_jwt_extended import create_access_token
from app import create_app, db
from app.models import User, UserRole, File

@pytest.fixture
def client():
    app = create_app('testing')
    
    # Create uploads folder for test
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            
            # Clean up files after test
            for file in os.listdir(app.config['UPLOAD_FOLDER']):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            
            db.session.remove()
            db.drop_all()

@pytest.fixture
def ops_token(client):
    """Create a token for operations user"""
    with client.application.app_context():
        user = User(
            email='testops@example.com',
            password='password123',
            role=UserRole.OPS.value
        )
        user.is_verified = True
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity={
            'user_id': user.id,
            'email': user.email,
            'role': user.role
        })
        
        return access_token, user.id

@pytest.fixture
def client_token(client):
    """Create a token for client user"""
    with client.application.app_context():
        user = User(
            email='testclient@example.com',
            password='password123',
            role=UserRole.CLIENT.value
        )
        user.is_verified = True
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity={
            'user_id': user.id,
            'email': user.email,
            'role': user.role
        })
        
        return access_token, user.id

def test_file_upload_ops_user(client, ops_token):
    """Test file upload by operations user"""
    token, user_id = ops_token
    
    # Create a test file
    data = {}
    data['file'] = (io.BytesIO(b"test file content"), "test_file.docx")
    
    response = client.post(
        '/file/upload',
        data=data,
        headers={'Authorization': f'Bearer {token}'},
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'File uploaded successfully' in data['message']
    assert 'file_id' in data
    
    # Verify file exists in database
    with client.application.app_context():
        file = File.query.get(data['file_id'])
        assert file is not None
        assert file.original_filename == 'test_file.docx'
        assert file.file_type == 'docx'
        assert file.user_id == user_id

def test_file_upload_client_user(client, client_token):
    """Test file upload by client user (should be forbidden)"""
    token, _ = client_token
    
    # Create a test file
    data = {}
    data['file'] = (io.BytesIO(b"test file content"), "test_file.docx")
    
    response = client.post(
        '/file/upload',
        data=data,
        headers={'Authorization': f'Bearer {token}'},
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'Only Operations users can upload files' in data['message']

def test_file_upload_invalid_extension(client, ops_token):
    """Test file upload with invalid extension"""
    token, _ = ops_token
    
    # Create a test file with invalid extension
    data = {}
    data['file'] = (io.BytesIO(b"test file content"), "test_file.txt")
    
    response = client.post(
        '/file/upload',
        data=data,
        headers={'Authorization': f'Bearer {token}'},
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'File type not allowed' in data['message']

def test_list_files_client_user(client, client_token, ops_token):
    """Test listing files by client user"""
    ops_token, ops_user_id = ops_token
    client_token, _ = client_token
    
    # Upload a file as ops user
    data = {}
    data['file'] = (io.BytesIO(b"test file content"), "test_file.docx")
    
    client.post(
        '/file/upload',
        data=data,
        headers={'Authorization': f'Bearer {ops_token}'},
        content_type='multipart/form-data'
    )
    
    # List files as client user
    response = client.get(
        '/file/list',
        headers={'Authorization': f'Bearer {client_token}'}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'Files retrieved successfully' in data['message']
    assert len(data['files']) == 1
    assert data['files'][0]['filename'] == 'test_file.docx'

def test_list_files_ops_user(client, ops_token):
    """Test listing files by ops user (should be forbidden)"""
    token, _ = ops_token
    
    response = client.get(
        '/file/list',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'Only Client users can list files' in data['message']

def test_download_link_client_user(client, client_token, ops_token):
    """Test getting download link by client user"""
    ops_token, _ = ops_token
    client_token, _ = client_token
    
    # Upload a file as ops user
    data = {}
    data['file'] = (io.BytesIO(b"test file content"), "test_file.docx")
    
    upload_response = client.post(
        '/file/upload',
        data=data,
        headers={'Authorization': f'Bearer {ops_token}'},
        content_type='multipart/form-data'
    )
    
    upload_data = json.loads(upload_response.data)
    file_id = upload_data['file_id']
    
    # Get download link as client user
    response = client.get(
        f'/file/download/{file_id}',
        headers={'Authorization': f'Bearer {client_token}'}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'success'
    assert 'download_link' in data
    assert '/file/download-file/' in data['download_link']

def test_download_file_client_user(client, client_token, ops_token):
    """Test downloading file by client user"""
    ops_token, _ = ops_token
    client_token, _ = client_token
    
    # Upload a file as ops user
    file_content = b"test file content"
    data = {}
    data['file'] = (io.BytesIO(file_content), "test_file.docx")
    
    upload_response = client.post(
        '/file/upload',
        data=data,
        headers={'Authorization': f'Bearer {ops_token}'},
        content_type='multipart/form-data'
    )
    
    upload_data = json.loads(upload_response.data)
    file_id = upload_data['file_id']
    
    # Get download link as client user
    link_response = client.get(
        f'/file/download/{file_id}',
        headers={'Authorization': f'Bearer {client_token}'}
    )
    
    link_data = json.loads(link_response.data)
    download_link = link_data['download_link']
    token = download_link.rsplit('/', 1)[1]
    
    # Download file using token
    response = client.get(
        f'/file/download-file/{token}',
        headers={'Authorization': f'Bearer {client_token}'}
    )
    
    assert response.status_code == 200
    assert response.data == file_content

def test_download_file_ops_user(client, ops_token):
    """Test downloading file by ops user (should be forbidden)"""
    token, _ = ops_token
    
    # Try to access download-file endpoint as ops user with a random token
    response = client.get(
        '/file/download-file/random-token',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'Access denied' in data['message']