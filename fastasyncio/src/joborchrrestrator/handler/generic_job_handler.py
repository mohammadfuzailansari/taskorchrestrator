import asyncio
import importlib
import logging
import time

class GenericJobHandler:
    def __init__(self, parallel_tasks, sequential_tasks):
        self.parallel_tasks = parallel_tasks
        self.sequential_tasks = sequential_tasks
        self.task_results = {}
   
    
    async def run_parallel_tasks(self):
        """Execute all parallel tasks asynchronously."""
        logging.debug(f'Executing task in parallel : {self.parallel_tasks}')
        return await asyncio.gather(*[self.execute_task(task) for task in self.parallel_tasks])
 
    async def run_sequential_tasks(self):
        """Execute sequential tasks ensuring dependencies are resolved."""
        logging.debug(f'Executing task in seqeuenbce : {self.sequential_tasks}')
        for task in self.sequential_tasks:
            # Gather results of dependent tasks
            dependencies = task.get('dependencies', [])
            concatenated_input = ""

            # Concatenate results from all dependency tasks
            for dependency in dependencies:
                if dependency in self.task_results:
                    task_return_data = "Message: {}, Data: {}".format(*self.task_results[dependency])
                    concatenated_input += task_return_data+ " "

            # Execute the current task with concatenated input
            task_result = await self.execute_task(task, concatenated_input.strip())
            self.task_results[task['name']] = task_result

    async def execute_task(self, task, input_data=None):
        """Execute a single task using the handler class."""
        logging.debug(f'Executing task: {task['name']}')
        
        task_class_name = task['name']
        task_class = await self.load_task_class(task_class_name)
        task_instance = task_class()       

        task_result = await task_instance.execute(input_data)
        # Pass task_result to handler's execute
        self.task_results[task['name']] = task_result
        return task_result
    
    async def load_task_class(self, task_class_name):
        """Dynamically load a task class from the 'job/task' directory."""
        try:
            module_name = f'job.task.{task_class_name.lower()}'
            module = importlib.import_module(module_name)
            task_class = getattr(module, task_class_name)
            return task_class
        except ImportError as e:
            logging.error(f"Error importing task module '{module_name}': {e}")
            raise ValueError(f"Failed to load task class '{task_class_name}': {e}")
        except AttributeError as e:
            logging.error(f"Error finding task class '{task_class_name}' in module '{module_name}': {e}")
            raise ValueError(f"Task class '{task_class_name}' not found in module '{module_name}': {e}")
    
    async def run(self):
        """Run both parallel and sequential tasks and aggregate the response."""
        start_time = time.time()
        await self.run_parallel_tasks()
        logging.debug(f' Total time for parallel execution : {time.time()-start_time}')
        start_time = time.time()
        await self.run_sequential_tasks()
        logging.debug(f' Total time for seqeuntial execution : {time.time()-start_time}')
        logging.debug(f' All task result : {self.task_results}' )
    
    def aggregate_response(self):
        """Aggregate all task responses."""
        return {
            "results": self.task_results
        }
