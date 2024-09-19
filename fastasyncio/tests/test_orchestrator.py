import pytest
import json
from pathlib import Path
from fastapi.testclient import TestClient
from src.joborchrrestrator.orchestrator import JobOrchestrator
from src.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_job_orchestrator_loads_config():
    # Assuming you have a method to load the configuration in JobOrchestrator
    orchestrator = JobOrchestrator()
    config_path = Path(__file__).resolve().parent.parent / 'config' / 'job.json'
    with open(config_path, 'r') as file:
        expected_config = json.load(file)
    assert orchestrator.config == expected_config

def test_execute_job(client):
    response = client.post("/execute_job/Job1", json={})
    assert response.status_code == 200
    assert "expected_key" in response.json()  # Adjust according to the expected response

def test_invalid_job(client):
    response = client.post("/execute_job/InvalidJob", json={})
    assert response.status_code == 400  # Or whatever status code you expect
    assert "detail" in response.json()
