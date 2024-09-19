import asyncio

class ExampleJobHandler:
    async def execute(self, task_result: str) -> str:
        """Process the result of a task execution."""
        new_result = f"Handled by ExampleJobHandler: {task_result}"
        print(new_result)
        await asyncio.sleep(0.5)  # Simulate processing delay
        return new_result

class AnotherJobHandler:
    async def execute(self, task_result: str) -> str:
        """Process the result of a task execution."""
        new_result = f"Handled by AnotherJobHandler: {task_result}"
        print(new_result)
        await asyncio.sleep(0.5)  # Simulate processing delay
        return new_result
