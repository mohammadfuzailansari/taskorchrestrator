import os
import sys
import unittest
from unittest.mock import patch, MagicMock


# Calculate the absolute path to the directory containing 'src'
base_threadpool = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
base_src = os.path.join(base_threadpool, 'src')
sys.path.insert(2, base_src)  # Insert at the beginning to prioritize

from job_orchestrator.handlers.generic_job_handler import GenericJobHandler
from job_orchestrator.handlers.job1_handler import Job1Handler


class TestJob1Handler(unittest.TestCase):
    def setUp(self):
        """Setup the common test environment settings."""
        self.job_handler = Job1Handler()
        print("Test class executed : "+self.__class__.__name__)

    @patch('job_orchestrator.handlers.generic_job_handler.GenericJobHandler.execute_tasks')
    def test_before_job(self, mock_execute_tasks):
        """Test the before_job method to ensure it prepares the environment correctly."""
        with patch('builtins.print') as mocked_print:
            self.job_handler.before_job()
            mocked_print.assert_called_with("Preparing Job 1...")

    def test_execute_tasks(self):
        """Test the execute_tasks method to ensure it handles tasks specifically for 'Job 1'."""
        tasks = [{"name": "task1", "details": "Specific details for Job 1"}]
        with patch.object(GenericJobHandler, 'execute_tasks') as mock_super_execute_tasks:
            self.job_handler.execute_tasks(tasks)
            mock_super_execute_tasks.assert_called_once_with(tasks)

    @patch('builtins.print')
    def test_after_job(self, mock_print):
        """Test the after_job method to ensure it handles cleanup and finalization correctly."""
        self.job_handler.after_job()
        mock_print.assert_called_with("Job 1 completed successfully.")

if __name__ == '__main__':
    unittest.main()
