from .base_task import BaseTask

class Task3(BaseTask):
    async def execute(self, input_data: str = "") -> str:
        """Execute Task3."""
        result = f"Task3 executed. Input was: {input_data}"
        return result
