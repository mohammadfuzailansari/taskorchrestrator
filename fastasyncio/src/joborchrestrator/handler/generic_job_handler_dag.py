import asyncio
import importlib
import logging
import time
import networkx as nx

class GenericJobHandler:
    """
    Manages the execution of tasks, both parallel and sequential, and handles dynamic task class loading.
    """
    
    def __init__(self, job):
        """
        Initializes the GenericJobHandler with tasks and job.
        Builds the dependency graph.
        """
        self.task_results = {}
        self.completed_tasks = set()
        self.ready_queue = []
        self.job = job
        self.tasks = job.get("tasks", [])  
        
        # Build the Directed Acyclic Graph (DAG) from task dependencies
        self.G = nx.DiGraph()
        for task in self.tasks:
            task_name = task["name"]
            self.G.add_node(task_name)
            for dep in task.get("dependencies", []):
                self.G.add_edge(dep, task_name)

        # Topologically sort the graph (to ensure correct order)
        self.sorted_tasks = list(nx.topological_sort(self.G))

    # Lazy Dependency Resolution: Add tasks to ready_queue when their dependencies are satisfied
    def update_ready_tasks(self):
        """
        Lazy Dependency Resolution: Add tasks to ready_queue when their dependencies are satisfied.
        """
        for task in self.sorted_tasks:
            if task not in self.completed_tasks and task not in self.ready_queue:
                # Only resolve dependencies at this point when task is ready to run
                if all(dep in self.completed_tasks for dep in self.G.predecessors(task)):
                    self.ready_queue.append(task)

    # Function to prune the graph by removing completed tasks and dependencies
    def prune_graph(self):
        """
        Prunes the graph by removing completed tasks and their edges to reduce size.
        """
        for task in self.completed_tasks:
            if task in self.G.nodes:
                self.G.remove_node(task)

    async def execute_task(self, task_name):
        """
        Executes a single task by dynamically loading its class and calling its execute method.
        Passes data from completed dependencies to the task if any.
        """
        logging.debug('Executing task: %s', task_name)

        # Prepare input data from dependencies
        input_data = {}
        dependencies = self.G.predecessors(task_name)  # Get dependent tasks        
        #logging.debug(f'self.task_results : {self.task_results}')                
        for dep in dependencies:
            if dep in self.task_results:
                input_data[dep] = self.task_results[dep]  # Include data from completed dependencies

        task_class = self.load_task_class(task_name)
        task_instance = task_class()
        task_result = await task_instance.execute(input_data)
        
        # Store the result in task_results and mark as completed
        self.task_results[task_name] = task_result
        self.completed_tasks.add(task_name)
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

    async def run_tasks(self):
        """
        Orchestrates the execution of tasks (both parallel and sequential) using lazy dependency resolution.
        """
        # Initial call to populate ready_queue with tasks that have no dependencies
        self.update_ready_tasks()

        # Continue until all tasks are completed
        while len(self.completed_tasks) < len(self.sorted_tasks):
            if self.ready_queue:
                # Find tasks that can be run in parallel
                tasks_to_run = self.ready_queue.copy()
                self.ready_queue.clear()  # Clear the ready queue since we are about to execute these tasks
                
                logging.debug(f"Running tasks in parallel: {tasks_to_run}")
                await asyncio.gather(*[self.execute_task(task) for task in tasks_to_run])

                # After pruning, update the ready_queue with newly eligible tasks
                self.update_ready_tasks()
            else:
                logging.debug("No tasks can be run at this stage, waiting for dependencies to resolve.")
                await asyncio.sleep(0.1)  # Introduce a small delay to avoid tight loops

    async def run(self):
        """
        Starts the execution of tasks.
        """
        start_time = time.perf_counter()
        await self.run_tasks()
        logging.debug('Total time for task execution: %.2f seconds', time.perf_counter() - start_time)
        logging.debug('All task results: %s', self.task_results)

