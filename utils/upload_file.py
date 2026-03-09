import os
from werkzeug.utils import secure_filename

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file(file, upload_folder):

    if not file:
        return None, "No file provided"

    # Check file extension
    if not allowed_file(file.filename):
        return None, "File type not allowed (Allowed: png, jpg, jpeg, pdf)"

    # Check file size
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)

    if file_length > MAX_FILE_SIZE:
        return None, "File too large (max 5MB)"

    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)

    # Simple name conflict resolution
    counter = 1
    name, ext = os.path.splitext(filename)
    while os.path.exists(file_path):
        filename = f"{name}_{counter}{ext}"
        file_path = os.path.join(upload_folder, filename)
        counter += 1

    file.save(file_path)

    return filename, None
