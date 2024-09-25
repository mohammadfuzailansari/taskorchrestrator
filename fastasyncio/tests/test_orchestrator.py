import pytest
from unittest.mock import patch, MagicMock
from jsonschema import ValidationError
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


from fastasyncio.src.joborchrestrator.job_processor import JobProcessor
from src.joborchrestrator.utils import load_json, detect_cycles


@pytest.fixture
def orchestrator():
    # "config/job.json", "config/schema.json"
    job_file = 'config/job.json'
    schema_file = 'config/schema.json'
    return JobProcessor(job_file, schema_file)

def test_validate_job_file(orchestrator):
    with patch('joborchrestrator.utils.load_json', side_effect=[{"jobs": []}, {}]), \
         patch('jsonschema.validate') as mock_validate:
        orchestrator.validate_job_file()
        mock_validate.assert_called_once()

    with patch('joborchrestrator.utils.load_json', side_effect=[{"jobs": []}, {}]), \
         patch('jsonschema.validate', side_effect=ValidationError("Invalid schema")):
        with pytest.raises(ValueError) as excinfo:
            orchestrator.validate_job_file()
        assert "Job validation failed: Invalid schema" in str(excinfo.value)

def test_get_job_by_name(orchestrator):
    orchestrator.job_data = {'jobs': [{'name': 'test_job'}]}
    job = orchestrator.get_job_by_name('test_job')
    assert job['name'] == 'test_job'

    with pytest.raises(ValueError) as excinfo:
        orchestrator.get_job_by_name('nonexistent_job')
    assert "Job 'nonexistent_job' not found." in str(excinfo.value)

def test_validate_job(orchestrator):
    job = {'name': 'test_job', 'handler': 'handler_name', 'tasks': [{'name': 'task1', 'dependencies': []}]}
    with patch('joborchrestrator.utils.detect_cycles', return_value=False):
        orchestrator.validate_job(job)  # Should not raise

    job['tasks'][0]['dependencies'].append('task1')  # Introduce a cycle
    with patch('joborchrestrator.utils.detect_cycles', return_value=True):
        with pytest.raises(ValueError) as excinfo:
            orchestrator.validate_job(job)
        assert "Job 'test_job' has cyclic dependencies." in str(excinfo.value)

@pytest.mark.asyncio
async def test_execute_job(orchestrator):
    with patch.object(orchestrator, 'validate_job_file'), \
         patch.object(orchestrator, 'get_job_by_name', return_value={'name': 'test_job', 'tasks': []}), \
         patch.object(orchestrator, 'validate_job'), \
         patch('joborchrestrator.task_handler.TaskHandler.execute_tasks', return_value=Future()) as mock_execute_tasks:
        mock_execute_tasks.return_value.set_result(None)
        await orchestrator.execute_job('test_job')
       #mock_execute_tasks.assert_called_once()

