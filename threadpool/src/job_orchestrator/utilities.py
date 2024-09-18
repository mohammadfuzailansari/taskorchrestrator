import logging

"""
This module provides utility functions for setting up logging configurations, converting string formats,
and detecting cyclic dependencies in task configurations. It is designed to be used in applications where
task management and execution order are critical, particularly in systems that involve complex dependency
relationships.

Functions:
    - setup_logging: Configures the logging level and format for the application.
    - convert_to_camel_case: Converts snake_case strings to CamelCase.
    - has_cyclic_dependencies: Checks for cyclic dependencies in a list of tasks.
    - detect_cycle: Detects cycles in task dependencies using an iterative approach.

Example usage is provided at the end of the module to demonstrate how to detect cyclic dependencies.
"""

def setup_logging(log_level=logging.INFO):
    """
    Configures logging for the application with a specified log level and format.
    
    Args:
        log_level (int): The logging level threshold. Messages less severe than `log_level` will be ignored.
                         Default is logging.INFO.
    """
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

def convert_to_camel_case(snake_str):
    """
    Converts a snake_case string to CamelCase.
    
    Args:
        snake_str (str): The snake_case string to convert.
    
    Returns:
        str: The converted CamelCase string.
    """
    camel_case_str = ''.join(word.capitalize() for word in snake_str.split('_'))
    return camel_case_str

def has_cyclic_dependencies(tasks):
    """
    Checks for cyclic dependencies in the task configurations using an iterative approach.
    
    Args:
        tasks (list of dict): A list of task dictionaries, each containing a 'name' and optional 'dependencies'.
    
    Returns:
        bool: True if a cyclic dependency is detected, otherwise False.
    """
    task_map = {task['name']: task.get('dependencies', []) for task in tasks}
    for task_name in task_map:
        if detect_cycle(task_map, task_name):
            return True
    return False

def detect_cycle(task_map, start_task):
    """
    Detects a cycle starting from a specific task using an iterative approach to avoid deep recursion issues.
    
    Args:
        task_map (dict): A dictionary mapping task names to their respective list of dependencies.
        start_task (str): The task name from which to start the cycle detection.
    
    Returns:
        bool: True if a cycle is detected, otherwise False.
    """
    visited = set()
    stack = [(start_task, None)]  # Stack of (current_node, parent_node)

    while stack:
        current_node, parent_node = stack.pop()
        if current_node in visited:
            continue
        visited.add(current_node)

        for neighbor in task_map.get(current_node, []):
            if neighbor == parent_node:
                continue  # Avoid going back to the parent node
            if neighbor in visited:
                return True  # Cycle detected
            stack.append((neighbor, current_node))

    return False
