import concurrent.futures
import logging
import os
from job_orchestrator.task_handler import TaskHandler
from job_orchestrator.utilities import setup_logging


"""
This module defines the GenericJobHandler class, which manages the execution of a set of tasks, handling dependencies
and providing options for parallel execution. The class is designed to handle tasks that may have dependencies on the
completion of other tasks and can execute tasks in parallel where possible. It uses a ThreadPoolExecutor to manage
parallel task execution and keeps track of task dependencies to execute dependent tasks sequentially after their
dependencies have been resolved.

The GenericJobHandler is particularly useful in systems that require complex task management and execution strategies,
such as workflow engines, batch processing systems, or automation frameworks.

Classes:
    GenericJobHandler: Manages the setup, validation, and execution of tasks based on JSON configurations.

Dependencies:
    - concurrent.futures: Used for managing parallel execution of tasks.
    - logging: Used to log information, warnings, and errors.
    - os: Used to retrieve the number of CPUs for setting the default number of worker threads.
    - ..task_handler.TaskHandler: Used for executing individual tasks.

Example usage:
    # Assuming the module is part of a package and the necessary task configurations are defined.
    handler = GenericJobHandler(max_workers=10)
    tasks = [
        {"name": "module.task1"},
        {"name": "module.task2", "dependencies": ["module.task1"]},
        {"name": "module.task3", "dependencies": ["module.task2"]}
    ]
    handler.execute_tasks(tasks)
    print(handler.aggregate_results())
"""

class GenericJobHandler:
    """
    Base class which manages the execution of a set of tasks, handling dependencies and providing options for parallel execution.
    """
    def __init__(self, max_workers=None, log_level=logging.INFO):
        """
        Initializes the GenericJobHandler with optional control over the number of worker threads.
        """
        setup_logging(log_level)
        self.results = {}
        self.task_dependencies = {}
        self.completed_tasks = set()
        self.tasks = []
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)

    def before_job(self):
        """Logs the beginning of job execution."""
        logging.info("Starting job...")

    def execute_tasks(self, tasks):
        """
        Orchestrates the execution of given tasks, managing parallel and sequential execution based on dependencies.
        """
        self.tasks = tasks
        self._prepare_task_dependencies()
        self._execute_parallel_tasks()
        self._execute_sequential_tasks()

    def _prepare_task_dependencies(self):
        """Prepares a mapping of tasks to their dependencies for efficient management during execution."""
        for task in self.tasks:
            self.task_dependencies[task['name']] = set(task.get('dependencies', []))
            logging.debug("Task %s dependencies: %s", task['name'], self.task_dependencies[task['name']])

    def _execute_parallel_tasks(self):
        """Executes tasks that have no dependencies in parallel using a ThreadPoolExecutor."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            parallel_tasks = [task for task in self.tasks if not task.get('dependencies', [])]
            futures = {executor.submit(TaskHandler(task).execute_task): task['name'] for task in parallel_tasks}
            
            for future in concurrent.futures.as_completed(futures):
                task_name = futures[future]
                try:
                    self.results[task_name] = future.result()
                    self.completed_tasks.add(task_name)
                    logging.info("Parallel task %s completed successfully.", task_name)
                except Exception as exc:
                    logging.error("Parallel task %s generated an exception: %s", task_name, exc)
    
    def _execute_sequential_tasks(self):
        """Executes tasks with dependencies sequentially, ensuring that each task's dependencies have been completed."""
        for task in self.tasks:
            if task.get('dependencies') and self.task_dependencies[task['name']].issubset(self.completed_tasks):
                dependencies_results = {dep: self.results[dep] for dep in task.get('dependencies', [])}
                task_handler = TaskHandler(task, dependencies_results)
                result = task_handler.execute_task()
                self.results[task['name']] = result
                self.completed_tasks.add(task['name'])
                logging.info("\tSequential task %s completed successfully.", task['name'])

    def after_job(self):
        """Logs the completion of all tasks, indicating the job has finished successfully."""
        logging.info("Job completed successfully.")

    def error_job(self, error):
        """Logs any errors that occur during the job execution."""
        logging.error("Error occurred: %s", error)
    
    def aggregate_results(self):
        """Aggregates and returns the results from all completed tasks."""
        return self.results
    