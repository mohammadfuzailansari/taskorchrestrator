import importlib  # Used for dynamically loading modules
from .handler import GenericJobHandler, Job1Handler  # Import specific job handlers

class TaskProcessor:
    """
    Handles the organization and execution of tasks based on their dependencies.
    
    Attributes:
        job_data (dict): Data about the job including tasks and their handlers.
        tasks (list): List of tasks extracted from job_data.
        handler_class_name (str): The name of the handler class for executing tasks.
    """
    
    def __init__(self, job_data):
        """
        Initializes the TaskHandler with job data.
        
        Args:
            job_data (dict): The job data containing tasks and their respective handlers.
        """
        self.job_data = job_data  # Store the job data passed to the handler
        self.tasks = job_data.get("tasks", [])  # Extract tasks from the job data, default to empty list if none
        self.handler_class_name = job_data.get("handler", None)  # Get the handler class name from job data
    
    def get_parallel_tasks(self):
        """
        Retrieves tasks that can be executed in parallel, i.e., tasks with no dependencies.
        
        Returns:
            list: A list of tasks without dependencies.
        """
        # List comprehension to filter out tasks without dependencies
        return [task for task in self.tasks if not task.get('dependencies')]
    
    def get_sequential_tasks(self):
        """
        Retrieves tasks that must be executed sequentially, i.e., tasks that have dependencies.
        
        Returns:
            list: A list of tasks with dependencies.
        """
        # List comprehension to filter out tasks with dependencies
        return [task for task in self.tasks if task.get('dependencies')]
    
    def load_handler_class(self):
        """
        Dynamically loads the handler class based on the handler_class_name attribute.
        
        Returns:
            class: The handler class from the specified module.
        
        Raises:
            ValueError: If the handler class cannot be loaded due to ImportError or AttributeError.
        """
        try:
            # Split the handler class name to get module and class name
            handler_module, handler_class_name = self.handler_class_name.rsplit('.', 1)
            # Dynamically import the module
            module = importlib.import_module(f'.{handler_module}', package='joborchrestrator')
            # Get the class from the module
            handler_class = getattr(module, handler_class_name)
            return handler_class
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Failed to load handler class '{self.handler_class_name}': {e}")
        
    async def execute_tasks(self):
        """
        Executes all tasks by organizing them into parallel and sequential groups and using the appropriate handler.
        
        Returns:
            The result of the task execution, typically the output of the job handler's run method.
        """
        parallel_tasks = self.get_parallel_tasks()  # Get tasks that can be run in parallel
        sequential_tasks = self.get_sequential_tasks()  # Get tasks that need to be run sequentially
      
        handler_class = self.load_handler_class()  # Load the appropriate handler class
        job_handler = handler_class(parallel_tasks, sequential_tasks)  # Instantiate the handler
        
        return await job_handler.run()  # Execute the tasks using the handler and return the result
