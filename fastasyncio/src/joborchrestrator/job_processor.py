from jsonschema import validate, ValidationError  # Tools for JSON schema validation
from .task_processor import TaskProcessor  # Importing the TaskProcessor class for task execution
from .utils import load_json, detect_cycles  # Utility functions for loading JSON and detecting cycles

class JobProcessor:
    """
    Processes the execution of jobs based on configurations specified in JSON files.
    
    Attributes:
        job_file (str): The file path to the job configuration JSON.
        schema_file (str): The file path to the JSON schema for validating the job configuration.
        job_data (dict): Loaded job configuration data.
        schema_data (dict): Loaded schema data for validation.
    """
    
    def __init__(self, job_file: str, schema_file: str):
        """
        Initializes the JobProcessor with paths to the job and schema JSON files.
        
        Args:
            job_file (str): The file path to the job configuration JSON.
            schema_file (str): The file path to the JSON schema for validating the job configuration.
        """
        self.job_file = job_file  # Storing the job file path
        self.schema_file = schema_file  # Storing the schema file path
        self.job_data = load_json(job_file)  # Loading job data from the job configuration file
        self.schema_data = load_json(schema_file)  # Loading schema data from the schema file
        
    def validate_job_file(self):
        """
        Validates the job JSON file against the schema.
        
        Raises:
            ValueError: If the job data does not conform to the schema.
        """
        try:
            validate(instance=self.job_data, schema=self.schema_data)  # Validating the job data against the schema
        except ValidationError as e:
            raise ValueError(f"Job validation failed: {e.message}")  # Raising an error if validation fails
    
    def get_job_by_name(self, job_name: str):
        """
        Retrieves a job configuration by its name.
        
        Args:
            job_name (str): The name of the job to retrieve.
        
        Returns:
            dict: The job configuration.
        
        Raises:
            ValueError: If no job with the given name is found.
        """
        for job in self.job_data['jobs']:  # Iterating through jobs in the job data
            if job['name'] == job_name:  # Checking if the job name matches
                return job  # Returning the job configuration
        raise ValueError(f"Job '{job_name}' not found.")  # Raising an error if no job is found
    
    def validate_job(self, job):
        """
        Validates a job's configuration, particularly its handler class and task dependencies.
        
        Args:
            job (dict): The job configuration to validate.
        
        Raises:
            ValueError: If the job does not have a handler or if cyclic dependencies are detected.
        """
        if 'handler' not in job:
            raise ValueError(f"Job '{job['name']}' does not have a handler class.")  # Checking for handler class
        
        task_graph = {task['name']: task.get('dependencies', []) for task in job['tasks']}  # Creating a graph of tasks
        if detect_cycles(task_graph):
            raise ValueError(f"Job '{job['name']}' has cyclic dependencies.")  # Checking for cyclic dependencies
    
    async def execute_job(self, job_name: str):
        """
        Executes the specified job asynchronously.
        
        Args:
            job_name (str): The name of the job to execute.
        
        Raises:
            ValueError: If the job or its configuration is invalid.
        """
        self.validate_job_file()  # Validating the job file
        job = self.get_job_by_name(job_name)  # Retrieving the job by name
        self.validate_job(job)  # Validating the job

        task_processor = TaskProcessor(job)  # Creating an instance of TaskHandler with the job
        await task_processor.execute_tasks()  # Executing the tasks asynchronously
