import uuid
from datetime import datetime
from app import db, bcrypt
from enum import Enum

class UserRole(Enum):
    OPS = 'operations'
    CLIENT = 'client'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    files = db.relationship('File', backref='owner', lazy=True)

    def __init__(self, email, password, role):
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.role = role
        self.is_verified = True
        self.verification_token = str(uuid.uuid4())

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def is_ops_user(self):
        return self.role == UserRole.OPS.value

    def is_client_user(self):
        return self.role == UserRole.CLIENT.value

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    download_token = db.Column(db.String(100), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.original_filename,
            'file_type': self.file_type,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'uploaded_by': self.owner.email
        }