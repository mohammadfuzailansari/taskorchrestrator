import pytest
from fastapi.testclient import TestClient
from src.main import app  # Ensure this is the correct import

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Task Orchestrator!"}  # Adjust according to the actual response

# Add more tests for other endpoints as needed
