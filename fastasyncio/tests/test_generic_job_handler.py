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


from src.joborchrestrator.handler.generic_job_handler import GenericJobHandler  # Adjust the import according to your project structure

@pytest.fixture
def job_handler():
    parallel_tasks = [{'name': 'Task1'}, {'name': 'Task2'}]
    sequential_tasks = [{'name': 'Task3', 'dependencies': ['Task1']}]
    return GenericJobHandler(parallel_tasks, sequential_tasks)

@pytest.mark.asyncio
async def test_run_parallel_tasks(job_handler):
    with patch.object(job_handler, 'execute_task', return_value=Future()) as mock_execute_task:
        mock_execute_task.return_value.set_result("Task Completed")
        result = await job_handler.run_parallel_tasks()
        #assert result == ["Task Completed", "Task Completed"]
        assert mock_execute_task.call_count == 2

@pytest.mark.asyncio
async def test_run_sequential_tasks(job_handler):
    job_handler.task_results = {'Task1': ('Completed', 'Data1')}
    with patch.object(job_handler, 'execute_task', return_value=Future()) as mock_execute_task:
        mock_execute_task.return_value.set_result("Task3 Completed")
        await job_handler.run_sequential_tasks()
        mock_execute_task.assert_called_once_with({'name': 'Task3', 'dependencies': ['Task1']}, 'Message: Completed, Data: Data1')

@pytest.mark.asyncio
async def test_execute_task(job_handler):
    task = {'name': 'Task1'}
    with patch.object(job_handler, 'load_task_class') as mock_load_task_class:
        mock_task_instance = MagicMock()
        mock_task_class = MagicMock(return_value=mock_task_instance)
        mock_load_task_class.return_value = mock_task_class
        mock_task_instance.execute = MagicMock(return_value=Future())
        mock_task_instance.execute.return_value.set_result("Execution Success")

        result = await job_handler.execute_task(task)
        assert result == "Execution Success"     

def test_load_task_class(job_handler):
    with patch('importlib.import_module') as mock_import_module:
        mock_module = MagicMock()
        mock_class = MagicMock()
        mock_import_module.return_value = mock_module
        mock_module.Task1 = mock_class
        
        handler_class = job_handler.load_task_class('Task1')
        assert handler_class == mock_class

@pytest.mark.asyncio
async def test_run(job_handler):
    with patch.object(job_handler, 'run_parallel_tasks', return_value=Future()) as mock_run_parallel, \
         patch.object(job_handler, 'run_sequential_tasks', return_value=Future()) as mock_run_sequential:
        mock_run_parallel.return_value.set_result(None)
        mock_run_sequential.return_value.set_result(None)
        await job_handler.run()
        mock_run_parallel.assert_awaited_once()
        mock_run_sequential.assert_awaited_once()
