import pytest
from httpx import AsyncClient
from fastapi import FastAPI, status
from unittest.mock import AsyncMock, patch
import os
import sys

# Append the project root directory to sys.path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..'))
sys.path.insert(0, root)  # Insert at the beginning to prioritize
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(1, project_root)  # Insert at the beginning to prioritize
base_src = os.path.join(project_root, 'src')
sys.path.insert(2, base_src)  # Insert at the beginning to prioritize



# Assuming the FastAPI app and JobOrchestrator are imported from their respective modules
from src.main import app
from src.joborchrestrator.orchestrator import JobOrchestrator



@pytest.mark.asyncio
async def test_execute_job_success():
    # Mock JobOrchestrator to simulate successful job execution
    with patch('src.joborchrestrator.orchestrator.JobOrchestrator') as mock_orchestrator:
        mock_instance = mock_orchestrator.return_value
        mock_instance.execute_job = AsyncMock(return_value=None)
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/execute_job/Job1")
            assert response.status_code == status.HTTP_200_OK
            assert response.json() == {"status": "success", "message": "Job 'Job1' executed successfully."}


@pytest.mark.asyncio
async def test_execute_job_value_error():
    # Mock JobOrchestrator to simulate a ValueError
    with patch('joborchrestrator.orchestrator.JobOrchestrator') as mock_orchestrator:
        mock_instance = mock_orchestrator.return_value
        mock_instance.execute_job = AsyncMock(side_effect=ValueError("Invalid job configuration"))
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/execute_job/test_job")
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json() == {"detail": "Invalid job configuration"}

@pytest.mark.asyncio
async def test_execute_job_unexpected_error():
    # Mock JobOrchestrator to simulate an unexpected exception
    with patch('joborchrestrator.orchestrator.JobOrchestrator') as mock_orchestrator:
        mock_instance = mock_orchestrator.return_value
        mock_instance.execute_job = AsyncMock(side_effect=Exception("Server error"))
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/execute_job/test_job")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json() == {"detail": "Internal Server Error"}
            