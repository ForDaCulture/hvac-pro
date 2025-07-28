import pytest
from app import create_app
from models.database import init_database, get_db_connection

@pytest.fixture(scope='module')
def test_app():
    """Create and configure a new app instance for each test module."""
    app = create_app({
        'TESTING': True,
        'DATABASE_URL': 'sqlite:///:memory:',  # Use an in-memory database for tests
        'WTF_CSRF_ENABLED': False, # Disable CSRF for simpler form testing
        'LOGIN_DISABLED': False
    })

    with app.app_context():
        init_database() # Initialize the in-memory database schema

    yield app

@pytest.fixture()
def test_client(test_app):
    """A test client for the app."""
    return test_app.test_client()

@pytest.fixture()
def runner(test_app):
    """A test runner for the app's Click commands."""
    return test_app.test_cli_runner()
