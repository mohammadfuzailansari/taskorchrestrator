import asyncio
import importlib
import logging
import time

class GenericJobHandler:
    """
    Manages the execution of tasks, both parallel and sequential, and handles dynamic task class loading.
    """
    
    def __init__(self, parallel_tasks, sequential_tasks):
        """
        Initializes the GenericJobHandler with lists of parallel and sequential tasks.
        """
        self.parallel_tasks = parallel_tasks
        self.sequential_tasks = sequential_tasks
        self.task_results = {}
    
    async def run_parallel_tasks(self):
        """
        Executes all parallel tasks asynchronously using asyncio.gather to run them concurrently.
        """
        logging.debug('Executing task in parallel: %s', self.parallel_tasks)
        return await asyncio.gather(*[self.execute_task(task) for task in self.parallel_tasks])
 
    async def run_sequential_tasks(self):
        """
        Executes tasks that have dependencies sequentially, ensuring each task starts after its dependencies.
        """
        logging.debug('Executing task in sequence: %s', self.sequential_tasks)
        for task in self.sequential_tasks:
            dependencies = task.get('dependencies', [])
            task_input_dict = {}

            for dependency in dependencies:
                if dependency in self.task_results:
                    task_input_dict[dependency] = self.task_results[dependency]

            task_result = await self.execute_task(task, task_input_dict)
            self.task_results[task['name']] = task_result

    async def execute_task(self, task, input_data=None):
        """
        Executes a single task by dynamically loading its class and calling its execute method.
        """
        logging.debug('Executing task: %s', task["name"])
        task_class = self.load_task_class(task['name'])
        task_instance = task_class()
        task_result = await task_instance.execute(input_data)
        self.task_results[task['name']] = task_result
        return task_result
    
    def load_task_class(self, task_class_name):
        """
        Dynamically loads a task class from a module based on the task's class name.
        """
        try:
            module_name = f'job.task.{task_class_name.lower()}'
            module = importlib.import_module(module_name)
            task_class = getattr(module, task_class_name)
            return task_class
        except ImportError as e:
            logging.error("Error importing task module '%s': %s", module_name, e)
            raise ValueError(f"Failed to load task class '{task_class_name}': {e}")
        except AttributeError as e:
            logging.error("Error finding task class '%s' in module '%s': %s", task_class_name, module_name, e)
            raise ValueError(f"Task class '{task_class_name}' not found in module '{module_name}': {e}")
    
    async def run(self):
        """
        Orchestrates the execution of both parallel and sequential tasks and aggregates their results.
        """
        start_time = time.perf_counter()
        await self.run_parallel_tasks()
        logging.debug('Total time for parallel execution: %.2f seconds', time.perf_counter() - start_time)
        start_time = time.perf_counter()
        await self.run_sequential_tasks()
        logging.debug('Total time for sequential execution: %.2f seconds', time.perf_counter() - start_time)
        logging.debug('All task results: %s', self.task_results)

    def aggregate_response(self):
        """
        Aggregates and returns all task responses.
        """
        return {
            "results": self.task_results
        }
