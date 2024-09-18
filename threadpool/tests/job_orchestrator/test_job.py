import unittest
import json
import os
import sys
from unittest.mock import MagicMock, mock_open, patch
import logging

from jsonschema import ValidationError

# Append the project src directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..'))
sys.path.insert(0, project_root)  # Insert at the beginning to prioritize

base_src = os.path.join(project_root, 'src')
sys.path.insert(1, base_src)  # Insert at the beginning to prioritize


from src.job_orchestrator.job import JobOrchestrator
from src.job_orchestrator.task_handler import TaskHandler
from src.job_orchestrator.utilities import setup_logging

class TestJobOrchestrator(unittest.TestCase):

    def setUp(self):
        """
        Setup common properties for tests.
        """
        self.config_path = "config/job_config.json"
        self.schema_path = "config/job_schema.json"
        self.job_orchestrator = JobOrchestrator(self.config_path, self.schema_path)
        self.log_level = logging.INFO

    @patch('builtins.open', new_callable=mock_open, read_data='{"jobs": {"example_job": {"handler": "handler", "tasks": []}}}')
    @patch('json.load')
    @patch('jsonschema.validate')
    def test_load_jobs_success(self, mock_validate, mock_json_load, mock_open):
        """
        Test successful loading of jobs from the configuration file.
        """
        # Setup the return value for json.load to return the JSON directly
        mock_json_load.return_value = {"jobs": {"example_job": {"handler": "handler", "tasks": []}}}
        
        # Execute the method to load jobs
        jobs = self.job_orchestrator._load_jobs()
        
        # Assertions to ensure all components are called correctly
        mock_json_load.assert_called()
        self.assertIn('example_job', jobs['jobs'])

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='{"invalid_json')
    @patch('json.load', side_effect=json.JSONDecodeError("Expecting value", "doc", 0))
    def test_load_jobs_failure(self, mock_json_load, mock_open):
        """
        Test handling of JSON decoding errors during job loading.
        """
        with self.assertRaises(json.JSONDecodeError):
            self.job_orchestrator._load_jobs()

    @patch('logging.basicConfig')
    @patch('pathlib.Path.open')
    @patch('json.load')
    @patch('jsonschema.validate')
    def test_successful_initialization_and_job_loading(self, mock_validate, mock_json_load, mock_open, mock_logging):
        """Test successful initialization and job loading."""
        # Setup mock returns
        mock_json_load.side_effect = [
            {"jobs": {"example_job": {"handler": "handler_name", "tasks": []}}},  # config file
            {}  # schema file
        ]
        mock_open.return_value.__enter__.return_value = MagicMock()

        # Create an instance of JobOrchestrator
        orchestrator = JobOrchestrator(self.config_path, self.schema_path, self.log_level)

        # Assertions to ensure proper calls
        mock_open.assert_called()
        mock_json_load.assert_called()
        #mock_validate.assert_called()
        self.assertIsInstance(orchestrator, JobOrchestrator)

    @patch('pathlib.Path.exists', side_effect=[False])
    def test_file_not_found_error(self, mock_exists):
        """Test handling of file not found error."""
        with self.assertRaises(FileNotFoundError):
            JobOrchestrator(self.config_path, self.schema_path, self.log_level)

    @patch('pathlib.Path.open')
    @patch('json.load', side_effect=json.JSONDecodeError("Expecting value", "doc", 0))
    def test_json_decode_error(self, mock_json_load, mock_open):
        """Test handling of JSON decoding errors."""
        with self.assertRaises(json.JSONDecodeError):
            JobOrchestrator(self.config_path, self.schema_path, self.log_level)

    @patch('src.job_orchestrator.job.Path')
    @patch('src.job_orchestrator.job.json.load')
    @patch('src.job_orchestrator.job.validate')
    @patch('src.job_orchestrator.job.open', new_callable=mock_open)
    @patch('src.job_orchestrator.job.TaskHandler')
    def test_start_job_success(self, mock_task_handler, mock_open_file, mock_validate, mock_json_load, mock_path):
        """
        Test if the job starts successfully with a valid configuration.
        """
        # Mocking path existence and JSON data
        mock_path.return_value.exists.return_value = True
        mock_json_load.return_value = {
            "jobs":{
                "job1": {
                "handler": "job_orchestrator.handlers.generic_job_handler",
                "tasks": [
                    { "name": "jobs.job1.task1" },
                    { "name": "jobs.job1.task2" }
                ]
                }
            }
        }
        # Creating an instance of JobOrchestrator and starting a job
        orchestrator = JobOrchestrator("config/job_config.json", "config/job_schema.json")
        result = orchestrator.start_job("job1")

        # Asserting that the job handler and tasks were called correctly
        mock_task_handler().execute_job.assert_called_once_with("job_orchestrator.handlers.generic_job_handler",[{'name': 'jobs.job1.task1'}, {'name': 'jobs.job1.task2'}])
        mock_validate.assert_called_once()  # Schema validation was performed

  
    @patch('src.job_orchestrator.job.Path')
    @patch('src.job_orchestrator.job.json.load')
    @patch('src.job_orchestrator.job.validate')
    @patch('src.job_orchestrator.job.open', new_callable=mock_open)
    def test_json_validation_error(self, mock_open_file, mock_validate, mock_json_load, mock_path):
        """
        Test if the orchestrator raises a ValidationError when schema validation fails.
        """
        mock_path.return_value.exists.return_value = True
        mock_json_load.return_value = {
            "jobs":{
                "job1": {
                "handler": "job_orchestrator.handlers.generic_job_handler",
                "tasks": [
                    { "name": "jobs.job1.task1" },
                    { "name": "jobs.job1.task2" }
                ]
                }
            }
        }
        mock_validate.side_effect = ValidationError("Schema validation error")

        with self.assertRaises(ValidationError):
            orchestrator = JobOrchestrator("config/job_config.json", "config/job_schema.json")
            orchestrator.start_job("job1")

    @patch('src.job_orchestrator.job.has_cyclic_dependencies')
    @patch('src.job_orchestrator.job.Path')
    @patch('src.job_orchestrator.job.json.load')
    @patch('src.job_orchestrator.job.validate')
    @patch('src.job_orchestrator.job.open', new_callable=mock_open)
    def test_cyclic_dependency(self, mock_open_file, mock_validate, mock_json_load, mock_path, mock_has_cyclic_dependencies):
        """
        Test if the orchestrator raises an exception for cyclic dependencies in tasks.
        """
        mock_path.return_value.exists.return_value = True
        mock_json_load.return_value = {
            "jobs":{
                "job1": {
                "handler": "job_orchestrator.handlers.generic_job_handler",
                "tasks": [
                    { "name": "jobs.job1.task1", "dependencies": ["jobs.job1.task2"]},
                    { "name": "jobs.job1.task2", "dependencies": ["jobs.job1.task1"] }
                ]
                }
            }
        }
        mock_has_cyclic_dependencies.return_value = True  # Simulate cyclic dependencies

        orchestrator = JobOrchestrator("config/job_config.json", "config/job_schema.json")

        with self.assertRaises(ValueError) as context:
            orchestrator.start_job("job1")

        self.assertIn("Cyclic dependencies detected", str(context.exception))

    @patch('src.job_orchestrator.job.Path')
    @patch('src.job_orchestrator.job.json.load')
    @patch('src.job_orchestrator.job.open', new_callable=mock_open)
    def test_job_not_found(self, mock_open_file, mock_json_load, mock_path):
        """
        Test if the orchestrator raises a ValueError when the job is not found in the config.
        """
        mock_path.return_value.exists.return_value = True
        mock_json_load.return_value = {"jobs": {}}

        orchestrator = JobOrchestrator("config/job_config.json", "config/job_schema.json")

        with self.assertRaises(ValueError) as context:
            orchestrator.start_job("job1")

        self.assertIn("Job job1 not found", str(context.exception))

    

if __name__ == "__main__":
    unittest.main()