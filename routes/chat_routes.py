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
    
    if not participant_ids:
        flash("Please select at least one person to message.")
        return redirect(url_for('chat.chat'))
    
    participants = User.query.filter(User.id.in_([int(pid) for pid in participant_ids])).all()
    participants.append(user) # Add current user
    
    # If 2 people total (1 selected + self) and no group name, check if 1-on-1 exists
    if len(participants) == 2 and not group_name:
        # Simple check for existing 1-on-1
        existing = Conversation.query.filter_by(is_group=False).all()
        for conv in existing:
            if set(conv.participants) == set(participants):
                return redirect(url_for('chat.chat', conv_id=conv.id))
    
    # Create new conversation
    is_group = len(participants) > 2 or bool(group_name)
    new_conv = Conversation(
        name=group_name if is_group else None,
        is_group=is_group,
        participants=participants
    )
    
    db.session.add(new_conv)
    db.session.commit()
    
    return redirect(url_for('chat.chat', conv_id=new_conv.id))

@chat_bp.route('/chat/send/<int:conv_id>', methods=['POST'])
@login_required
def send_message(conv_id):
    user = User.query.filter_by(username=session["username"]).first()
    conv = Conversation.query.get_or_404(conv_id)
    
    if user not in conv.participants:
        return jsonify({"error": "Unauthorized"}), 403
    
    content = request.form.get('content')
    if not content:
        return redirect(url_for('chat.chat', conv_id=conv_id))
    
    new_msg = Message(
        conversation_id=conv_id,
        sender_id=user.id,
        content=content
    )
    
    db.session.add(new_msg)
    db.session.commit()
    
    return redirect(url_for('chat.chat', conv_id=conv_id))
