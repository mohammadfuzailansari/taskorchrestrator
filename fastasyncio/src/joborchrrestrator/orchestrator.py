from jsonschema import validate, ValidationError
from .task_handler import TaskHandler
from .utils import load_json, detect_cycles

class JobOrchestrator:
    def __init__(self, job_file: str, schema_file: str):
        self.job_file = job_file
        self.schema_file = schema_file
        self.job_data = load_json(job_file)
        self.schema_data = load_json(schema_file)
        
    def validate_job_file(self):
        """Validates the job JSON file against the schema."""
        try:
            validate(instance=self.job_data, schema=self.schema_data)
        except ValidationError as e:
            raise ValueError(f"Job validation failed: {e.message}")
    
    def get_job_by_name(self, job_name: str):
        """Find the job by name."""
        for job in self.job_data['jobs']:
            if job['name'] == job_name:
                return job
        raise ValueError(f"Job '{job_name}' not found.")
    
    def validate_job(self, job):
        """Validates the job's handler class and checks for cyclic dependencies."""
        if 'handler' not in job:
            raise ValueError(f"Job '{job['name']}' does not have a handler class.")
        
        # Validate cyclic dependencies in the tasks
        task_graph = {task['name']: task.get('dependencies', []) for task in job['tasks']}
        if detect_cycles(task_graph):
            raise ValueError(f"Job '{job['name']}' has cyclic dependencies.")
    
    async def execute_job(self, job_name: str):
        """Executes the specified job."""
        self.validate_job_file()  # Validate the overall structure of the job.json
        job = self.get_job_by_name(job_name)
        self.validate_job(job)

        # Pass the job to TaskHandler for execution
        task_handler = TaskHandler(job)
        await task_handler.execute_tasks()
