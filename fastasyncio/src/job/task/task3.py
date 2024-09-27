from .base_task import BaseTask
import time
import logging
import asyncio

class Task3(BaseTask):
    async def execute(self, input_data: dict) -> dict:
        """Execute Task3."""
        await asyncio.sleep(1)
        #result = f"Return from {self.__class__.__name__} ", input_data if input_data else ""
        data = input_data if input_data else "NO_INPUT"
        result = {self.__class__.__name__ : data}        
        
        logging.debug(f'Executed {self.__class__.__name__} with input : {data}')
        return result
