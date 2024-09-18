import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Calculate the absolute path to the directory containing 'threadpool'
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, base_dir)  # Insert at the beginning to prioritize



# Append the project src directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..'))
sys.path.insert(1, project_root)  # Insert at the beginning to prioritize

base_src = os.path.join(project_root, 'src')
sys.path.insert(2, base_src)  # Insert at the beginning to prioritize

from src.job_orchestrator.task_handler import TaskHandler


class TestTaskHandler(unittest.TestCase):

    def setUp(self):
        """Setup the common test environment settings."""
        self.task_handler = TaskHandler()
        self.task_handler.task = {'name': 'jobs.job1.task1'}
        self.task_handler.dependencies_results = {'data': 'test'}



    @patch('job_orchestrator.task_handler.importlib.import_module')
    def test_execute_job_success(self, mock_import_module):
        """Test successful execution of tasks."""
        # Setup mocks
        mock_module = MagicMock()
        mock_handler = MagicMock()
        mock_import_module.return_value = mock_module
        mock_module.Task1 = MagicMock(return_value=mock_handler)
        mock_handler.execute_tasks = MagicMock()

        # Define tasks
        tasks = [{"name": "jobs.job1.task1"}]
        handler_name = "job_orchestrator.handlers.generic_job_handler"

        # Execute
        self.task_handler.execute_job(handler_name, tasks)

        # Verify
        mock_import_module.assert_called_with("job_orchestrator.handlers.generic_job_handler")

    def test_validate_task_module(self):
        """Test validation of task modules."""
        tasks = "jobs.job1.task"
        with patch('job_orchestrator.task_handler.importlib.util.find_spec', return_value=None):
            result = self.task_handler._validate_task_module(tasks)
            self.assertFalse(result)

    @patch('importlib.import_module')
    def test_execute_task_success(self, mock_import_module):
        """Test successful execution of a task."""
        # Setup mocks
        mock_module = MagicMock()
        mock_task_class = MagicMock()
        mock_task_instance = MagicMock()

        # Configure the mocks
        mock_import_module.return_value = mock_module
        mock_module.MyTask = mock_task_class
        mock_task_class.return_value = mock_task_instance
        mock_task_instance.execute.return_value = 'success'

        # Execute the task
        result = self.task_handler.execute_task()

        # Assertions
        mock_import_module.assert_called_once_with('jobs.job1.task1')
        #mock_task_class.assert_called_once()
        #mock_task_instance.execute.assert_called_once_with(self.task_handler.dependencies_results)
        #self.assertEqual(result, 'success')


    @patch('importlib.import_module', side_effect=ImportError("Module not found"))
    def test_execute_task_import_error(self, mock_import_module):
        """Test handling of ImportError during task execution."""
        with self.assertRaises(ImportError):
            self.task_handler.execute_task()

    @patch('importlib.import_module')
    def test_class_does_not_exist(self, mock_import_module):
        """Test the scenario where the specified class does not exist in the module."""
        # Setup a mock module with no class attributes
        mock_module = MagicMock()
        del mock_module.SomeClass  # Ensure 'SomeClass' does not exist
        mock_import_module.return_value = mock_module

        # Simulate the inputs
        task_name = "my_module.SomeClass"
        expected_class_name = "SomeClass"

        # Execute the method
        result = self.task_handler._validate_task_module(task_name)

        # Assertions
        #mock_import_module.assert_called_once_with("my_module")
        self.assertFalse(result)
 


if __name__ == '__main__':
    unittest.main()
