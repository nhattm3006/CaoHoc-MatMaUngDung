from .user_model import db


class File(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    filename = db.Column(db.String(255), nullable=False)

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    status = db.Column(db.Integer, default=0)  # 1 = "Chia sẻ", 0 = "Riêng tư"

    # shared_with: -1 (Private), 0 (All), "[id1, id2, ...]" (Specific users)
    shared_with = db.Column(db.String(255), default="-1")

    owner = db.relationship('User', backref=db.backref('files', lazy=True))
