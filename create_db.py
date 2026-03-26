from app import app
from models.user_model import db, User
from models.file_model import File
from models.chat_model import Conversation, Message
from models.notification_model import Notification
from utils.hash_utils import hash_password
from utils.crypto_utils import generate_rsa_keys

with app.app_context():

    db.drop_all()
    db.create_all()

    # Generate keys for admin
    pub, priv = generate_rsa_keys()
    admin = User(
        username="admin",
        password=hash_password("admin", "123"),
        role="admin",
        rsa_public_key=pub,
        rsa_private_key=priv
    )

    # Generate keys for user
    pub1, priv1 = generate_rsa_keys()
    user = User(
        username="user1",
        password=hash_password("user1", "123"),
        role="user",
        rsa_public_key=pub1,
        rsa_private_key=priv1
    )

    # Generate keys for user2
    pub2, priv2 = generate_rsa_keys()
    user2 = User(
        username="user2",
        password=hash_password("user2", "123"),
        role="user",
        rsa_public_key=pub2,
        rsa_private_key=priv2
    )

    db.session.add(admin)
    db.session.add(user)
    db.session.add(user2)

    db.session.commit()

    print("Database recreated with hashed passwords")