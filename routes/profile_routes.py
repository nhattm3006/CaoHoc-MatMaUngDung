from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from models.user_model import db, User
from utils.auth_decorators import login_required
from utils.hash_utils import hash_password, check_password

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
@login_required
def profile():
    user = User.query.filter_by(username=g.user["username"]).first()
    return render_template('profile.html', user=user)

@profile_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    user = User.query.filter_by(username=g.user["username"]).first()
    user.name = request.form.get('name')
    user.email = request.form.get('email')
    
    db.session.commit()
    flash("Cập nhật thông tin thành công!", "success")
    return redirect(url_for('profile.profile'))

@profile_bp.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    user = User.query.filter_by(username=g.user["username"]).first()
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not check_password(user.username, old_password, user.password):
        flash("Mật khẩu cũ không chính xác.", "danger")
        return redirect(url_for('profile.profile'))
    
    if new_password != confirm_password:
        flash("Mật khẩu mới không khớp.", "danger")
        return redirect(url_for('profile.profile'))
    
    user.password = hash_password(user.username, new_password)
    db.session.commit()
    
    flash("Đổi mật khẩu thành công!", "success")
    return redirect(url_for('profile.profile'))
