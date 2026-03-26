from flask import Blueprint, render_template, request, flash
from models.user_model import User
from utils.crypto_utils import verify_signature
from utils.auth_decorators import login_required

verify_bp = Blueprint('verify', __name__)

@verify_bp.route('/verify', methods=['GET', 'POST'])
@login_required
def verify():
    results = None
    if request.method == 'POST':
        file = request.files.get('file')
        signature = request.form.get('signature')
        mode = request.form.get('mode') # '1' for specific user, '2' for search all
        
        if not file or not signature:
            flash("Vui lòng tải lên file và cung cấp chữ ký.", "danger")
            return render_template('verify.html')
        
        file_data = file.read()
        
        if mode == '1':
            user_id = request.form.get('user_id')
            user = User.query.get(user_id)
            if not user or not user.rsa_public_key:
                flash("User không tồn tại hoặc chưa có Public Key.", "danger")
            else:
                is_valid = verify_signature(user.rsa_public_key, signature, file_data)
                results = {
                    "mode": "1",
                    "is_valid": is_valid,
                    "checked_user": user.username,
                    "checked_name": user.name
                }
        
        elif mode == '2':
            users = User.query.filter(User.rsa_public_key.isnot(None)).all()
            found_user = None
            for user in users:
                if verify_signature(user.rsa_public_key, signature, file_data):
                    found_user = user
                    break
            
            results = {
                "mode": "2",
                "found": found_user is not None,
                "user": found_user.username if found_user else None,
                "name": found_user.name if found_user else None
            }
            
    # Always get list of users for Mode 1 search/select
    all_users = User.query.filter(User.rsa_public_key.isnot(None)).all()
    return render_template('verify.html', users=all_users, results=results)
