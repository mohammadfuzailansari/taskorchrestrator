from .base_task import BaseTask

class Task1(BaseTask):
    async def execute(self, input_data: str = "") -> str:
        """Execute Task1."""
        result = f"Task1 executed. Input was: {input_data}"
        return result
