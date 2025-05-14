from flask import current_app

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def get_file_extension(filename):
    """Get the file extension from filename"""
    return filename.rsplit('.', 1)[1].lower()