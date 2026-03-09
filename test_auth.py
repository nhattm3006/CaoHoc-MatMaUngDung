from app import app
from services.auth_service import authenticate
from utils.hash_utils import hash_password, check_password

def test_bcrypt_logic():
    print("Testing Bcrypt logic directly...")
    username = "testuser"
    password = "password123"
    hashed = hash_password(username, password)
    
    print(f"Hashed password: {hashed}")
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    
    assert check_password(username, password, hashed) is True
    assert check_password(username, "wrongpass", hashed) is False
    assert check_password("diffuser", password, hashed) is False
    print("SUCCESS: Bcrypt logic works.")

def test_auth_service():
    print("\nTesting authentication service...")
    with app.app_context():
        # admin/123 in DB
        user = authenticate("admin", "123")
        if user and user['username'] == 'admin':
            print("SUCCESS: Admin authentication works with Bcrypt.")
        else:
            print("FAILURE: Admin authentication failed.")

        wrong = authenticate("admin", "wrong")
        if not wrong:
            print("SUCCESS: Wrong password rejected.")
        else:
            print("FAILURE: Wrong password accepted!")

def test_routes():
    print("\nTesting routes with Flask test client...")
    with app.test_client() as client:
        # Test login action
        resp = client.post('/login', data={'username': 'admin', 'password': '123'}, follow_redirects=True)
        assert resp.status_code == 200
        assert b"Home" in resp.data
        print("SUCCESS: Login action works with Bcrypt.")

if __name__ == "__main__":
    test_bcrypt_logic()
    test_auth_service()
    test_routes()
