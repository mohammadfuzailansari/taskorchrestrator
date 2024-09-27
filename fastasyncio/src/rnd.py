import networkx as nx
import asyncio

# Example task graph with dependencies
task_graph = {
    "Task1": [],
    "Task2": [],
    "Task3": ["Task2"],
    "Task4": ["Task2"],
    "Task5": ["Task2"]
}

# Build the Directed Acyclic Graph (DAG)
G = nx.DiGraph()
for task, deps in task_graph.items():
    G.add_node(task)
    for dep in deps:
        G.add_edge(dep, task)

# Topologically sort the graph (to ensure correct order)
sorted_tasks = list(nx.topological_sort(G))

# Maintain a set of completed tasks
completed_tasks = set()

# Maintain a queue of tasks ready to be executed
ready_queue = []

# Lazy Dependency Resolution: Add tasks to ready_queue when their dependencies are satisfied
def update_ready_tasks(G):
    for task in sorted_tasks:
        if task not in completed_tasks and task not in ready_queue:
            # Only resolve dependencies at this point when task is ready to run
            if all(dep in completed_tasks for dep in G.predecessors(task)):
                ready_queue.append(task)

# Function to prune the graph by removing completed tasks and dependencies
def prune_graph(G, completed_tasks):
    for task in completed_tasks:
        if task in G.nodes:
            # Remove the task from the graph
            G.remove_node(task)

# Simulate task execution
async def execute_task(task):
    print(f"Executing {task}")
    await asyncio.sleep(1)  # Simulate time taken to execute the task
    print(f"Completed {task}")

# Run the tasks sequentially or in parallel based on the ready tasks
async def run_tasks(G):
    global completed_tasks
    
    # Initial call to populate ready_queue with tasks that have no dependencies
    update_ready_tasks(G)

    # Continue until all tasks are completed
    while len(completed_tasks) < len(sorted_tasks):
        if ready_queue:
            # Find tasks that can be run in parallel
            tasks_to_run = ready_queue.copy()
            ready_queue.clear()  # Clear the ready queue since we are about to execute these tasks
            
            print(f"Running in parallel: {tasks_to_run}")
            await asyncio.gather(*[execute_task(task) for task in tasks_to_run])

            # Mark tasks as completed and prune the graph
            completed_tasks.update(tasks_to_run)
            prune_graph(G, completed_tasks)

            # After pruning, update the ready_queue with newly eligible tasks
            update_ready_tasks(G)
        else:
            print("No tasks can be run at this stage, waiting for dependencies to resolve.")
            await asyncio.sleep(0.1)  # Introduce a small delay to avoid tight loops

# Run the main task orchestration loop
asyncio.run(run_tasks(G))
