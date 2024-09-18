import unittest
from unittest.mock import patch, MagicMock
import sys
import os 
import json

# Append the project root directory to sys.path
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..'))
sys.path.insert(0, root)

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(1, project_root)

base_src = os.path.join(project_root, 'src')
sys.path.insert(2, base_src)  # Insert at the beginning to prioritize

from src.main import initiate_job


class TestMainFunction(unittest.TestCase):
    
    @patch('src.main.JobOrchestrator')
    @patch('src.main.setup_logging')
    @patch('sys.exit')
    def test_main_success(self, mock_exit, mock_setup_logging, mock_JobOrchestrator):
        # Set up the mock for JobOrchestrator
        mock_orchestrator_instance = MagicMock()
        mock_JobOrchestrator.return_value = mock_orchestrator_instance

        job_name = 'job1'
        # Run the main function
        initiate_job(job_name)

        # Check that logging was set up
        mock_setup_logging.assert_called_once()

        # Check that JobOrchestrator was initialized with the correct arguments
        mock_JobOrchestrator.assert_called_once_with()

        # Check that start_job was called with the correct job name
        mock_orchestrator_instance.start_job.assert_called_once_with(job_name)      

    @patch('src.main.JobOrchestrator')
    def test_main_with_json_decoder_exception(self, MockJobOrchestrator):
        # Create a mock instance of JobOrchestrator
        mock_orchestrator = MockJobOrchestrator.return_value
        
        # Configure the mock to raise a FileNotFoundError when start_job is called
        mock_orchestrator.start_job.side_effect = json.JSONDecodeError("JSON decode error", "", 0)
        # Run the main function

        job_name = 'job1'
        with self.assertRaises(SystemExit) as cm:
            from src.main import initiate_job 
            initiate_job(job_name)
        
        self.assertEqual(cm.exception.code, 1)

    @patch('src.main.JobOrchestrator')
    def test_main_with_general_exception(self, MockJobOrchestrator):
        # Create a mock instance of JobOrchestrator
        mock_orchestrator = MockJobOrchestrator.return_value
        
        # Configure the mock to raise a FileNotFoundError when start_job is called
        mock_orchestrator.start_job.side_effect = Exception("Test FileNotFoundError")

        job_name = 'job1'

        # Run the main function
        with self.assertRaises(SystemExit) as cm:     
            from src.main import initiate_job       
            initiate_job(job_name)
        
        self.assertEqual(cm.exception.code, 1)

    @patch('src.main.JobOrchestrator')
    def test_main_with_file_not_found_exception(self, MockJobOrchestrator):
        # Create a mock instance of JobOrchestrator
        mock_orchestrator = MockJobOrchestrator.return_value
        
        # Configure the mock to raise a FileNotFoundError when start_job is called
        mock_orchestrator.start_job.side_effect = FileNotFoundError("Test FileNotFoundError")

        job_name = 'job1'

        # Run the main function
        with self.assertRaises(SystemExit) as cm:    
            from src.main import initiate_job 
            initiate_job(job_name)
            
        
        self.assertEqual(cm.exception.code, 1)

if __name__ == '__main__':
    unittest.main()
