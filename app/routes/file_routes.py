import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from app.models import File, User
from app.services.file_service import allowed_file, get_file_extension

file_bp = Blueprint('file', __name__, url_prefix='/file')

@file_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """Upload a file (only for OPS users)"""
    # Get current user ID from JWT
    current_user_data = get_jwt_identity()  # This is a dictionary
    user = User.query.get(current_user_data['user_id'])  # Extract user_id

    if not user:
        return jsonify({"msg": "User not found"}), 404

    if user.role != 'operations':
        return jsonify({"msg": "Only Operations can upload files"}), 403

    if 'file' not in request.files:
        return jsonify({"msg": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({
            'message': f'File type not allowed. Supported types: {", ".join(current_app.config["ALLOWED_EXTENSIONS"])}'
        }), 400

    original_filename = secure_filename(file.filename)
    file_extension = get_file_extension(original_filename)
    unique_filename = f"{uuid.uuid4()}.{file_extension}"

    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)

    new_file = File(
        filename=unique_filename,
        original_filename=original_filename,
        file_type=file_extension,
        user_id=user.id
    )

    db.session.add(new_file)
    db.session.commit()

    return jsonify({
        'message': 'File uploaded successfully',
        'file_id': new_file.id,
        'filename': original_filename
    }), 201


@file_bp.route('/list', methods=['GET'])
@jwt_required()
def list_files():
    """List all files (only for Client users)"""
    current_user_data = get_jwt_identity()
    user = User.query.get(current_user_data['user_id'])

    if not user:
        return jsonify({'message': 'User not found'}), 404

    if not user.is_client_user():
        return jsonify({'message': 'Only Client users can list files'}), 403

    all_files = File.query.all()
    files_list = [file.to_dict() for file in all_files]

    return jsonify({
        'message': 'Files retrieved successfully',
        'files': files_list
    }), 200


@file_bp.route('/download/<int:file_id>', methods=['GET'])
@jwt_required()
def get_download_link(file_id):
    """Get encrypted download link (only for Client users)"""
    current_user_data = get_jwt_identity()
    user = User.query.get(current_user_data['user_id'])

    if not user:
        return jsonify({'message': 'User not found'}), 404

    if not user.is_client_user():
        return jsonify({'message': 'Only Client users can download files'}), 403

    file = File.query.get(file_id)
    if not file:
        return jsonify({'message': 'File not found'}), 404

    download_url = url_for(
        'file.download_file',
        token=file.download_token,
        _external=True
    )

    return jsonify({
        'message': 'success',
        'download_link': download_url
    }), 200


@file_bp.route('/download-file/<token>', methods=['GET'])
@jwt_required()
def download_file(token):
    """Download file using encrypted token (only for Client users)"""
    current_user_data = get_jwt_identity()
    user = User.query.get(current_user_data['user_id'])

    if not user:
        return jsonify({'message': 'User not found'}), 404

    if not user.is_client_user():
        return jsonify({'message': 'Access denied'}), 403

    file = File.query.filter_by(download_token=token).first()
    if not file:
        return jsonify({'message': 'Invalid download link'}), 404

    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        file.filename,
        as_attachment=True,
        download_name=file.original_filename
    )
