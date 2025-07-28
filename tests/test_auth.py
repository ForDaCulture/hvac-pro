from werkzeug.security import check_password_hash
from models.database import get_db_connection

def test_signup(test_client):
    """Test that the signup page loads and a new user can be created."""
    response = test_client.get('/signup')
    assert response.status_code == 200

    response = test_client.post('/signup', data={
        'email': 'testuser@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Account created successfully! Please log in.' in response.data
    
    with get_db_connection() as conn:
        user = conn.execute('SELECT * FROM users WHERE email = ?', ('testuser@example.com',)).fetchone()
    assert user is not None
    assert check_password_hash(user['password'], 'password123')

def test_login_logout(test_client):
    """Test that a registered user can log in and out."""
    # First, sign up the user
    test_client.post('/signup', data={'email': 'loginuser@example.com', 'password': 'password'})

    # Test login
    response = test_client.post('/login', data={
        'email': 'loginuser@example.com',
        'password': 'password'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Logout' in response.data # Check for logout link on page
    assert b'HVAC Pro Login' not in response.data

    # Test logout
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Logout' not in response.data
