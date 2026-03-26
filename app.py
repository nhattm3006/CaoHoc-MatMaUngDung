import os
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

from models.user_model import db, User

from routes.auth_routes import auth_bp
from routes.home_routes import home_bp
from routes.admin_routes import admin_bp
from routes.file_routes import file_bp
from routes.chat_routes import chat_bp
from routes.notification_routes import notification_bp
from routes.profile_routes import profile_bp
from routes.verify_routes import verify_bp
from models.notification_model import Notification
from utils.jwt_utils import decode_token


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db.init_app(app)


app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(file_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(notification_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(verify_bp)

@app.context_processor
def inject_notifications():
    token = request.cookies.get("access_token")
    if token:
        payload = decode_token(token)
        if not isinstance(payload, str):
            username = payload.get("username")
            user = User.query.filter_by(username=username).first()
            if user:
                count = Notification.query.filter_by(user_id=user.id, is_read=False).count()
                return {"unread_notifications_count": count}
    return {"unread_notifications_count": 0}


if __name__ == "__main__":
    app.run(debug=True)