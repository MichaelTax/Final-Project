import pytest
from app import app  # Assuming your Flask app is initialized here # Import the module where your MongoDB collection is defined

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_main_page(client):
    response = client.get('/')
    assert b'Welcome' in response.data
    assert response.status_code == 200

