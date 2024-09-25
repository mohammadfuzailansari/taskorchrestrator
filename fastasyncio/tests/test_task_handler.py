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



from fastasyncio.src.joborchrestrator.task_processor import TaskProcessor 

# Sample job data to be used in tests
job_data = {
    "handler": "joborchrestrator.handler.Job1Handler",
    "tasks": [
        {"name": "Task1", "dependencies": []},
        {"name": "Task2", "dependencies": ["Task1"]}
    ]
}

@pytest.fixture
def task_handler():
    return TaskProcessor(job_data)

def test_get_parallel_tasks(task_handler):
    parallel_tasks = task_handler.get_parallel_tasks()
    assert len(parallel_tasks) == 1
    assert parallel_tasks[0]['name'] == 'Task1'

def test_get_sequential_tasks(task_handler):
    sequential_tasks = task_handler.get_sequential_tasks()
    assert len(sequential_tasks) == 1
    assert sequential_tasks[0]['name'] == 'Task2'

def test_load_handler_class(task_handler):
    with patch('importlib.import_module') as mock_import_module:
        mock_module = MagicMock()
        mock_class = MagicMock()
        mock_import_module.return_value = mock_module
        mock_module.Job1Handler = mock_class
        
        handler_class = task_handler.load_handler_class()
        assert handler_class == mock_class

@pytest.mark.asyncio
async def test_execute_tasks(task_handler):
    with patch.object(task_handler, 'get_parallel_tasks', return_value=[{'name': 'Task1'}]), \
         patch.object(task_handler, 'get_sequential_tasks', return_value=[{'name': 'Task2'}]), \
         patch.object(task_handler, 'load_handler_class') as mock_load_handler_class:
        
        mock_handler_instance = MagicMock()
        mock_handler_instance.run = MagicMock(return_value=Future())
        mock_handler_instance.run.return_value.set_result("Done")
        mock_load_handler_class.return_value = MagicMock(return_value=mock_handler_instance)
        
        result = await task_handler.execute_tasks()
        assert result == "Done"
