import logging
from .generic_job_handler import GenericJobHandler

class Job1Handler(GenericJobHandler):
    async def run(self):
        """Run job1-specific tasks."""
        logging.debug(f'Executing {self.__class__.__name__}')
        return await super().run()
