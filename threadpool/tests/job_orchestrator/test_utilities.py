import os
import sys
import unittest
from unittest.mock import patch, MagicMock

import logging

# Calculate the absolute path to the directory containing 'threadpool'
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, base_dir)  # Insert at the beginning to prioritize

# Append the project root directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(1, project_root)  # Insert at the beginning to prioritize

base_src = os.path.join(project_root, 'src')
sys.path.insert(2, base_src)  # Insert at the beginning to prioritize



from src.job_orchestrator.utilities import *

class TestUtilityFunctions(unittest.TestCase):

    def test_setup_logging(self):
        """Test the setup_logging function to ensure it sets the logging level correctly."""
        with patch('logging.basicConfig') as mocked_logging:
            setup_logging(log_level=logging.DEBUG)
            mocked_logging.assert_called_once_with(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    def test_convert_to_camel_case(self):
        """Test the convert_to_camel_case function with various inputs."""
        self.assertEqual(convert_to_camel_case("snake_case"), "SnakeCase")
        self.assertEqual(convert_to_camel_case("example_function_name"), "ExampleFunctionName")
        self.assertEqual(convert_to_camel_case(""), "")

    def test_has_cyclic_dependencies(self):
        """Test the has_cyclic_dependencies function with different task configurations."""
        tasks_with_cycle = [
            {"name": "task1", "dependencies": ["task2"]},
            {"name": "task2", "dependencies": ["task3"]},
            {"name": "task3", "dependencies": ["task1"]}
        ]
        tasks_without_cycle = [
            {"name": "task1", "dependencies": ["task2"]},
            {"name": "task2", "dependencies": ["task3"]},
            {"name": "task3", "dependencies": []}
        ]
        self.assertTrue(has_cyclic_dependencies(tasks_with_cycle))
        self.assertFalse(has_cyclic_dependencies(tasks_without_cycle))

    def test_detect_cycle(self):
        """Test the detect_cycle function directly with a simple cycle and no cycle cases."""
        task_map_with_cycle = {
            "task1": ["task2"],
            "task2": ["task3"],
            "task3": ["task1"]
        }
        task_map_without_cycle = {
            "task1": ["task2"],
            "task2": ["task3"],
            "task3": []
        }
        self.assertTrue(detect_cycle(task_map_with_cycle, "task1"))
        self.assertFalse(detect_cycle(task_map_without_cycle, "task1"))

if __name__ == '__main__':
    unittest.main()
