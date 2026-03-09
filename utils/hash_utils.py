import bcrypt


def hash_password(username, password):

    pepper = username[:3]

    text = pepper + password

    hashed = bcrypt.hashpw(text.encode('utf-8'), bcrypt.gensalt())

    return hashed.decode('utf-8')


def check_password(username, password, hashed_password):

    pepper = username[:3]

    text = pepper + password

    return bcrypt.checkpw(text.encode('utf-8'), hashed_password.encode('utf-8'))