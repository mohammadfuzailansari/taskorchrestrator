import asyncio
from .handlers import ExampleJobHandler, AnotherJobHandler
from job.task.task1 import Task1
from job.task.task2 import Task2
from job.task.task3 import Task3

class JobHandler:
    def __init__(self, parallel_tasks, sequential_tasks, handler_class_name):
        self.parallel_tasks = parallel_tasks
        self.sequential_tasks = sequential_tasks
        self.handler_class_name = handler_class_name
        self.handler_class = self.get_handler_class(handler_class_name)
    
    def get_handler_class(self, handler_class_name):
        """Retrieve the handler class by name."""
        handler_classes = {
            'ExampleJobHandler': ExampleJobHandler,
            'AnotherJobHandler': AnotherJobHandler,
            # Add more handlers here as needed
        }
        handler_class = handler_classes.get(handler_class_name)
        if not handler_class:
            raise ValueError(f"Handler class '{handler_class_name}' not found.")
        return handler_class()
    
    async def run_parallel_tasks(self):
        """Execute all parallel tasks asynchronously."""
        await asyncio.gather(*[self.execute_task(task) for task in self.parallel_tasks])
    
    async def run_sequential_tasks(self):
        """Execute sequential tasks ensuring dependencies are resolved."""
        for task in self.sequential_tasks:
            await self.execute_task(task)
    
    async def execute_task(self, task):
        """Execute a single task using the handler class."""
        print(f"Executing task: {task['name']}")
        # Map task name to task class
        task_classes = {
            'Task1': Task1,
            'Task2': Task2,
            'Task3': Task3,
            # Add more tasks here as needed
        }
        task_class = task_classes.get(task['name'])
        if not task_class:
            raise ValueError(f"Task class '{task['name']}' not found.")
        task_instance = task_class()
        input_data = ""  # For simplicity, assuming empty input
        task_result = await task_instance.execute(input_data)
        # Pass task_result to handler's execute
        handler_result = await self.handler_class.execute(task_result)
        print(f"Task '{task['name']}' handled with result: {handler_result}")
    
    async def run(self):
        """Run both parallel and sequential tasks."""
        await self.run_parallel_tasks()
        await self.run_sequential_tasks()
