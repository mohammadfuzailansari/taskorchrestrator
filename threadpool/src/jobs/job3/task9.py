import time
import logging

from job_orchestrator.utilities import setup_logging

from ..task import Task

class Task9(Task):
    def __init__(self):
        # Configure logging at the initialization level of each task
        setup_logging()

    def execute(self, dependent_response=None):
        """
        Execute the task, optionally with an input.
        
        Args:
            dependent_response (str, optional): Input for the task execution. Defaults to None.
        
        Returns:
            str: A message indicating the result of the task execution.
        
        Raises:
            ValueError: If the input is None or empty.
        """
        task_name = self.__class__.__name__
        if dependent_response is None or (isinstance(dependent_response, dict) and not dependent_response):
            logging.info("Starting execution of %s", task_name)
            time.sleep(1)  # Simulate a delay to mimic task processing
            logging.info("End Executing %s", task_name)
            return f"From {task_name}"
        else:
            logging.info("Starting execution of %s with input: %s", task_name, dependent_response)
            time.sleep(1)  # Simulate a delay to mimic task processing
            logging.info("End Executing %s with input: %s", task_name, dependent_response)
            return f"From {task_name} with {dependent_response}"
        