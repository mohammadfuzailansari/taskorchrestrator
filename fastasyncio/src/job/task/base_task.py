from abc import ABC, abstractmethod

class BaseTask(ABC):
    @abstractmethod
    async def execute(self, input_data: str) -> str:
        """Execute the task with the given input data."""
        pass
