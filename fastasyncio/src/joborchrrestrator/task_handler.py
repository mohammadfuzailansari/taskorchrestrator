from .handler.job_handler import JobHandler

class TaskHandler:
    def __init__(self, job_data):
        self.job_data = job_data
        self.tasks = job_data.get("tasks", [])
        self.handler_class_name = job_data.get("handler")
        
    def get_parallel_tasks(self):
        """Returns a list of tasks that can be executed in parallel (no dependencies)."""
        return [task for task in self.tasks if not task.get('dependencies')]
    
    def get_sequential_tasks(self):
        """Returns a list of tasks that must be executed sequentially due to dependencies."""
        return [task for task in self.tasks if task.get('dependencies')]
    
    async def execute_tasks(self):
        """Execute tasks for the job."""
        parallel_tasks = self.get_parallel_tasks()
        sequential_tasks = self.get_sequential_tasks()

        # Initialize JobHandler with tasks and handler class
        job_handler = JobHandler(parallel_tasks, sequential_tasks, self.handler_class_name)
        await job_handler.run()
