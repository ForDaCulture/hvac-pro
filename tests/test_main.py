def test_dashboard_unauthenticated(test_client):
    """Test that an unauthenticated user is redirected from the dashboard."""
    response = test_client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'HVAC Pro Login' in response.data # Should be on login page

def test_dashboard_authenticated(test_client):
    """Test that an authenticated user can access the dashboard."""
    # Sign up and log in a user
    test_client.post('/signup', data={'email': 'mainuser@example.com', 'password': 'password'})
    test_client.post('/login', data={'email': 'mainuser@example.com', 'password': 'password'})

    response = test_client.get('/')
    assert response.status_code == 200
    assert b"Today's Schedule" in response.data
