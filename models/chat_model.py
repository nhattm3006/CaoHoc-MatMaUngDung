from models.user_model import db, User
from datetime import datetime

# Join table for Conversation participants
conversation_participants = db.Table('conversation_participants',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('conversation_id', db.Integer, db.ForeignKey('conversation.id'), primary_key=True)
)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100)) # Optional for groups
    is_group = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # E2EE Fields
    is_secure = db.Column(db.Boolean, default=False)
    user_a_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_b_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    public_key_a = db.Column(db.Text)
    public_key_b = db.Column(db.Text)
    encrypted_private_key_a = db.Column(db.Text)
    encrypted_private_key_b = db.Column(db.Text)
    salt_a = db.Column(db.String(100))
    salt_b = db.Column(db.String(100))
    iv_a = db.Column(db.String(100))
    iv_b = db.Column(db.String(100))
    
    participants = db.relationship('User', secondary=conversation_participants, backref='conversations')
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade="all, delete-orphan")

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    nonce = db.Column(db.String(100)) # IV for AES-GCM
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    sender = db.relationship('User', backref='sent_messages')
