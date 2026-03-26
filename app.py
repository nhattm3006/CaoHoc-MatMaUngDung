from flask import Flask

from models.user_model import db

from routes.auth_routes import auth_bp
from routes.home_routes import home_bp
from routes.admin_routes import admin_bp
from routes.file_routes import file_bp
from routes.chat_routes import chat_bp
from routes.notification_routes import notification_bp
from routes.profile_routes import profile_bp
from routes.verify_routes import verify_bp
from models.notification_model import Notification
from models.user_model import User
from flask import session


app = Flask(__name__)

app.secret_key = "secret_key"

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
    if "username" in session:
        user = User.query.filter_by(username=session["username"]).first()
        if user:
            count = Notification.query.filter_by(user_id=user.id, is_read=False).count()
            return {"unread_notifications_count": count}
    return {"unread_notifications_count": 0}


if __name__ == "__main__":
    app.run(debug=True)