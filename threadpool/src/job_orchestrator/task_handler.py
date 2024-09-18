import importlib
import logging
from importlib.util import find_spec
from job_orchestrator.utilities import convert_to_camel_case


"""
This module defines the TaskHandler class, which facilitates the dynamic loading and execution of tasks based on
specified handler modules and classes. It is particularly useful in systems that require modular task execution
where tasks can be defined in separate modules and executed dynamically based on runtime configurations.

The TaskHandler class supports:
- Dynamic import of task handler classes.
- Execution of tasks with or without dependencies.
- Validation of task modules before execution to ensure the specified tasks and handlers exist.

Classes:
    TaskHandler: Manages the dynamic loading and execution of tasks.

Dependencies:
    - importlib: Used for importing modules dynamically based on string names.
    - logging: Used to log information, warnings, and errors.
    - .utilities.convert_to_camel_case: A utility function to convert snake_case strings to CamelCase.

Example usage:
    # Assuming the existence of a task module 'my_tasks.task1' with a class 'Task1'
    tasks = [{"name": "my_tasks.task1"}]
    handler = TaskHandler()
    handler.execute_job('my_tasks.task_handler', tasks)
"""

class TaskHandler:
    """
    TaskHandler is responsible for dynamically loading and executing tasks
    based on a specified handler module and class.
    
    Handles the execution of a single task, managing dynamic loading and execution.
    """

    def __init__(self, task=None, dependencies_results=None, log_level=logging.INFO):
        logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
        self.task = task
        self.dependencies_results = dependencies_results

    def execute_job(self, handler_name, tasks):
        """
        Executes a job by loading the appropriate handler and running the specified tasks.
        
        Args:
            handler_name (str): The full module and class name of the handler.
            tasks (list): A list of tasks to be executed by the handler.
        """
        logging.debug("Attempting to execute job with handler: %s", handler_name)
        
        _, handler_class = handler_name.rsplit('.', 1)
          
        # as per naming convention converting filename (snake case) to class name (pascal case)
        handler_class = convert_to_camel_case(handler_class)

        handler = None
        
        # Validate all task modules before execution
        if not all(self._validate_task_module(task['name']) for task in tasks):
            logging.error("Validation failed: One or more task modules are invalid.")
            return
        
        try:
            # Dynamically import the module and get the handler class
            module = importlib.import_module(handler_name)
            handler = getattr(module, handler_class)()
            
            # Execute the job lifecycle methods
            handler.before_job()
            handler.execute_tasks(tasks)
            handler.after_job()

            return True

        except Exception as e:
            logging.error("An error occurred while executing the job", exc_info=True)
            if handler and hasattr(handler, 'error_job'):
                handler.error_job(e)
            return False

    def _validate_task_module(self, task_name):
        """
        Validates that the class for a given task exists within its module.
        
        Args:
            task_name (str): The full module and class name of the task in the format 'module.ClassName'.
        
        Returns:
            bool: True if the class exists within the module, False otherwise.
        """
        try:         
            # as per naming convention converting filename (snake case) to class name (pascal case)
            class_name = convert_to_camel_case(task_name.split('.')[-1])

            if find_spec(task_name) is None:
                logging.error("Module %s does not exist.",task_name)
                return False
            
            module = importlib.import_module(task_name)
            task_class = getattr(module, class_name, None)
            
            if task_class is None:
                logging.error("Class %s does not exist in %s.",class_name,task_name)
                return False
            
            return True
        except Exception as e:
            logging.error("An error occurred while validating task module: %s",e)
            return False       

    def execute_task(self):
        """Dynamically load and execute a task based on its module and class name, passing dependencies results."""
        task_name = self.task['name']
        module = importlib.import_module(task_name)
        
        # as per naming convention converting filename (snake case) to class name (pascal case)
        class_name = convert_to_camel_case(task_name.split('.')[-1])        

        task_class = getattr(module, class_name)
        task_instance = task_class()
        return task_instance.execute(self.dependencies_results)
      