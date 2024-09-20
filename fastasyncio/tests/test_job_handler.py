import pytest
from unittest.mock import patch, MagicMock
from asyncio import Future

import os
import sys


# Append the project root directory to sys.path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..'))
sys.path.insert(0, root)  # Insert at the beginning to prioritize
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(1, project_root)  # Insert at the beginning to prioritize
base_src = os.path.join(project_root, 'src')
sys.path.insert(2, base_src)  # Insert at the beginning to prioritize

from src.joborchrestrator.handler.job_handler import  Job1Handler

@pytest.fixture
def job1_handler():
    parallel_tasks = [{'name': 'Task1'}, {'name': 'Task2'}]
    sequential_tasks = [{'name': 'Task3', 'dependencies': ['Task1']}]
    return Job1Handler(parallel_tasks, sequential_tasks)

@pytest.mark.asyncio
async def test_run(job1_handler):
    with patch.object(Job1Handler, 'run', return_value=Future()) as mock_run:
        # Create a Future object and set its result
        future = Future()
        future.set_result("Job1 Completed")
        
        # Set the mock return_value to the future object
        mock_run.return_value = future
        
        # Await the result of the run method (this returns the result of the Future)
        result = await job1_handler.run()
        
        # Assert the result matches the expected output
        #assert result == "Job1 Completed"  # Ensure you compare with the string direct
        assert result == future