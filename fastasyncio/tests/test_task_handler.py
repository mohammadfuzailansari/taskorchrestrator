import pytest
from src.joborchrrestrator.task_handler import TaskHandler
from src.job.task import Task1, Task2

def test_task1_execution():
    task = Task1()
    result = task.execute("input")
    assert result == "expected_output_with_input"

def test_task2_execution():
    task = Task2()
    result = task.execute()
    assert result == "expected_output"

def test_task_handler_invalid_task():
    handler = TaskHandler()
    with pytest.raises(ValueError) as excinfo:
        handler.execute_task("InvalidTask")
    assert "Task class does not exist" in str(excinfo.value)
