import pytest
from src.joborchrrestrator.handler.job_handler import JobHandler

def test_job_handler_parallel_execution():
    handler = JobHandler()
    parallel_tasks = [Task1(), Task2()]
    results = handler.execute_parallel_tasks(parallel_tasks)
    assert len(results) == len(parallel_tasks)
    # Add specific assertions based on your task output

def test_job_handler_sequential_execution():
    handler = JobHandler()
    sequential_tasks = [Task1(), Task2()]
    results = handler.execute_sequential_tasks(sequential_tasks)
    assert len(results) == len(sequential_tasks)
    # Add specific assertions based on your task output
