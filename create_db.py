from app import app
from models.user_model import db, User
from models.file_model import File
from models.chat_model import Conversation, Message
from models.notification_model import Notification
from utils.hash_utils import hash_password

with app.app_context():

    db.drop_all()
    db.create_all()

    admin = User(
        username="admin",
        password=hash_password("admin", "123"),
        role="admin"
    )

    user = User(
        username="user1",
        password=hash_password("user1", "123"),
        role="user"
    )

    user2 = User(
        username="user2",
        password=hash_password("user2", "123"),
        role="user"
    )

    db.session.add(admin)
    db.session.add(user)
    db.session.add(user2)

    db.session.commit()

    print("Database recreated with hashed passwords")