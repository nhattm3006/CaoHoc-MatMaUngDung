from flask import Blueprint, render_template, redirect, url_for, flash, g
from models.user_model import db, User
from models.notification_model import Notification
from utils.auth_decorators import login_required

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/notifications')
@login_required
def list_notifications():
    user = User.query.filter_by(username=g.user["username"]).first()
    notifications = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notifications)

@notification_bp.route('/notifications/read_all', methods=['POST'])
@login_required
def read_all():
    user = User.query.filter_by(username=g.user["username"]).first()
    Notification.query.filter_by(user_id=user.id, is_read=False).update({Notification.is_read: True})
    db.session.commit()
    flash("Đã đánh dấu tất cả là đã đọc.")
    return redirect(url_for('notification.list_notifications'))
