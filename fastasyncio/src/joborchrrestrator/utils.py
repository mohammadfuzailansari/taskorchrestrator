import json
from pathlib import Path

def load_json(file_path):
    # Get the current directory of this script
    current_dir = Path(__file__).resolve().parent
    # Construct the path to the config folder
    config_path = current_dir.parents[1] / file_path

    """Load a JSON file."""
    with open(config_path, 'r') as file:
        return json.load(file)

def detect_cycles(task_graph):
    """Detect cycles in a directed graph of tasks using Depth-First Search."""
    visited = set()
    stack = set()

    def visit(task):
        if task in stack:
            return True  # Cycle found
        if task in visited:
            return False

        visited.add(task)
        stack.add(task)

        for dep in task_graph.get(task, []):
            if visit(dep):
                return True

        stack.remove(task)
        return False

    for task in task_graph:
        if visit(task):
            return True

    return False
