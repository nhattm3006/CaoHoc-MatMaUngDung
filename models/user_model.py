from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True, nullable=False)

    password = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(20), default="user")

    name = db.Column(db.String(100))

    email = db.Column(db.String(100))
    
    # RSA keys for digital signatures
    rsa_public_key = db.Column(db.Text)
    rsa_private_key = db.Column(db.Text)