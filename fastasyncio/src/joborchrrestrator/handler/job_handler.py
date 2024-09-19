from .generic_job_handler import GenericJobHandler

class Job1Handler(GenericJobHandler):
    async def run(self):
        """Run job1-specific tasks."""
        parallel_results = await self.run_parallel_tasks()
        sequential_results = await self.run_sequential_tasks()
        return self.aggregate_response(parallel_results, sequential_results)
