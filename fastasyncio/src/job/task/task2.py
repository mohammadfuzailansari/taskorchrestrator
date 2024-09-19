from .base_task import BaseTask

class Task2(BaseTask):
    async def execute(self, input_data: str = "") -> str:
        """Execute Task2."""
        result = f"Task2 executed. Input was: {input_data}"
        return result
