from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from models.user_model import db, User
from models.chat_model import Conversation, Message
from utils.auth_decorators import login_required
from datetime import datetime
import json

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat')
@chat_bp.route('/chat/<int:conv_id>')
@login_required
def chat(conv_id=None):
    user = User.query.filter_by(username=session["username"]).first()
    
    # Get all conversations user is part of
    conversations = user.conversations
    
    # Sort conversations by latest message or creation time
    # (Simplified: just latest first)
    conversations.sort(key=lambda x: x.created_at, reverse=True)
    
    active_conversation = None
    messages = []
    if conv_id:
        active_conversation = Conversation.query.get_or_404(conv_id)
        if user not in active_conversation.participants:
            flash("You do not have permission to view this conversation.")
            return redirect(url_for('chat.chat'))
        messages = Message.query.filter_by(conversation_id=conv_id).order_by(Message.timestamp.asc()).all()
    
    # Get list of other users for the "New Message" modal
    all_users = User.query.filter(User.id != user.id).all()
    
    return render_template('chat.html', 
                           conversations=conversations, 
                           active_conversation=active_conversation,
                           messages=messages,
                           all_users=all_users,
                           current_user=user)

@chat_bp.route('/chat/new', methods=['POST'])
@login_required
def new_conversation():
    user = User.query.filter_by(username=session["username"]).first()
    participant_ids = request.form.getlist('participants')
    group_name = request.form.get('group_name')
    is_secure = request.form.get('is_secure') == 'true'
    
    if not participant_ids:
        flash("Please select at least one person to message.")
        return redirect(url_for('chat.chat'))
    
    participants = User.query.filter(User.id.in_([int(pid) for pid in participant_ids])).all()
    participants.append(user)
    
    if is_secure and len(participants) != 2:
        flash("Bảo mật (E2EE) chỉ hỗ trợ chat 1-1.")
        return redirect(url_for('chat.chat'))
    
    if not is_secure and len(participants) == 2 and not group_name:
        existing = Conversation.query.filter_by(is_group=False, is_secure=False).all()
        for conv in existing:
            if set(conv.participants) == set(participants):
                return redirect(url_for('chat.chat', conv_id=conv.id))
    
    is_group = len(participants) > 2 or bool(group_name)
    user_b_id = None
    if is_secure and not is_group:
        # For 1-on-1 secure chat, the other person is user_b
        other_user = [p for p in participants if p.id != user.id][0]
        user_b_id = other_user.id

    new_conv = Conversation(
        name=group_name if is_group else None,
        is_group=is_group,
        is_secure=is_secure,
        user_a_id=user.id if is_secure else None,
        user_b_id=user_b_id,
        participants=participants
    )
    
    db.session.add(new_conv)
    db.session.commit()
    return redirect(url_for('chat.chat', conv_id=new_conv.id))

@chat_bp.route('/chat/init_secure/<int:conv_id>', methods=['POST'])
@login_required
def init_secure_chat(conv_id):
    user = User.query.filter_by(username=session["username"]).first()
    conv = Conversation.query.get_or_404(conv_id)
    if not conv.is_secure or conv.user_a_id != user.id:
        return jsonify({"error": "Unauthorized"}), 403
    conv.public_key_a = request.form.get('public_key')
    conv.encrypted_private_key_a = request.form.get('encrypted_private_key')
    conv.salt_a = request.form.get('salt')
    conv.iv_a = request.form.get('iv')
    
    # Notify User B that User A has initialized the secure chat
    from models.notification_model import Notification
    notif = Notification(
        user_id=conv.user_b_id,
        message=f"{user.username} đã thiết lập phòng chat bảo mật. Hãy tham gia.",
        link=url_for('chat.chat', conv_id=conv_id)
    )
    db.session.add(notif)
    db.session.commit()
    return jsonify({"success": True})

@chat_bp.route('/chat/join/<int:conv_id>', methods=['POST'])
@login_required
def join_secure_chat(conv_id):
    user = User.query.filter_by(username=session["username"]).first()
    conv = Conversation.query.get_or_404(conv_id)
    if not conv.is_secure or user not in conv.participants or conv.user_a_id == user.id:
        return jsonify({"error": "Unauthorized"}), 403
    conv.user_b_id = user.id
    conv.public_key_b = request.form.get('public_key')
    conv.encrypted_private_key_b = request.form.get('encrypted_private_key')
    conv.salt_b = request.form.get('salt')
    conv.iv_b = request.form.get('iv')
    
    # Notify User A
    from models.notification_model import Notification
    notif = Notification(
        user_id=conv.user_a_id,
        message=f"{user.username} đã tham gia trò chuyện bảo mật.",
        link=url_for('chat.chat', conv_id=conv_id)
    )
    db.session.add(notif)
    db.session.commit()
    return jsonify({"success": True})

@chat_bp.route('/chat/send/<int:conv_id>', methods=['POST'])
@login_required
def send_message(conv_id):
    user = User.query.filter_by(username=session["username"]).first()
    conv = Conversation.query.get_or_404(conv_id)
    
    if user not in conv.participants:
        return jsonify({"error": "Unauthorized"}), 403
    
    content = request.form.get('content')
    nonce = request.form.get('nonce') # For E2EE
    
    if not content:
        return redirect(url_for('chat.chat', conv_id=conv_id))
    
    new_msg = Message(
        conversation_id=conv_id,
        sender_id=user.id,
        content=content,
        nonce=nonce
    )
    
    db.session.add(new_msg)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({"success": True})
        
    return redirect(url_for('chat.chat', conv_id=conv_id))
