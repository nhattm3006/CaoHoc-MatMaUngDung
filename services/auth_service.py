from models.user_model import User
from utils.hash_utils import check_password


def authenticate(username, password):

    user = User.query.filter_by(username=username).first()

    if not user:
        return None

    if check_password(username, password, user.password):

        return {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }

    return None