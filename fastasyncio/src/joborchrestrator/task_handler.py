import importlib
from .handler import GenericJobHandler, Job1Handler

class TaskHandler:
    def __init__(self, job_data):
        self.job_data = job_data
        self.tasks = job_data.get("tasks", [])
        self.handler_class_name = job_data.get("handler", None)
    
    def get_parallel_tasks(self):
        """Returns a list of tasks that can be executed in parallel (no dependencies)."""
        return [task for task in self.tasks if not task.get('dependencies')]
    
    def get_sequential_tasks(self):
        """Returns a list of tasks that must be executed sequentially due to dependencies.""" 
        return [task for task in self.tasks if task.get('dependencies')]
    
    def load_handler_class(self):
        """Load the handler class dynamically based on the handler_class_name."""
        try:
            # Extract module and class names from the handler_class_name
            handler_module, handler_class_name = self.handler_class_name.rsplit('.', 1)
          
            # Import the handler module dynamically
            module = importlib.import_module(f'.{handler_module}', package='joborchrestrator')
            # Retrieve the handler class from the module
            handler_class = getattr(module, handler_class_name)
            return handler_class
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Failed to load handler class '{self.handler_class_name}': {e}")
        
    async def execute_tasks(self):
        """Execute tasks for the job."""
        parallel_tasks = self.get_parallel_tasks()
        sequential_tasks = self.get_sequential_tasks()
      
        handler_class = self.load_handler_class()
        
        # Determine which handler to use
        job_handler = handler_class(parallel_tasks, sequential_tasks)
        
        return await job_handler.run()
