import json
import logging
from pathlib import Path
from jsonschema import validate, ValidationError
from job_orchestrator.utilities import has_cyclic_dependencies, setup_logging
from job_orchestrator.task_handler import TaskHandler

"""
This module defines the JobOrchestrator class, which orchestrates the execution of jobs based on configurations
specified in JSON files. These configurations are validated against a JSON schema to ensure they meet the required
format. The orchestrator handles job execution, including the management of task dependencies and error handling.

The JobOrchestrator is particularly useful in environments where job configurations need to be dynamically loaded
and validated against a set of rules defined in a schema. It supports logging configuration, path resolution,
job loading, and execution with robust error management.

Classes:
    JobOrchestrator: Manages the setup, validation, and execution of jobs based on JSON configurations.

Dependencies:
    - json: Used for loading and parsing JSON files.
    - logging: Used to log information, warnings, and errors.
    - pathlib.Path: Used for file path manipulations.
    - jsonschema.validate, ValidationError: Used for validating JSON data against a schema.
    - .utilities.has_cyclic_dependencies, setup_logging: Utility functions for checking task dependencies and setting up logging.
    - .task_handler.TaskHandler: Used for executing tasks specified in the job configuration.

Example usage:
    # Assuming the module is part of a package and the necessary JSON files are in the 'config' directory.
    orchestrator = JobOrchestrator("config/job_config.json", "config/job_schema.json")
    orchestrator.start_job("example_job")
"""

class JobOrchestrator:
    """
    Orchestrates the execution of jobs based on configurations specified in a JSON file,
    validated against a JSON schema.
    
    Attributes:
        config_path (str): Path to the job configuration file.
        schema_path (str): Path to the JSON schema file for validation.
        jobs (dict): Loaded and validated job configurations.
    
    Methods:
        __init__(self, config_path, schema_path, log_level): Initializes the JobOrchestrator.
        _resolve_paths(self, config_path, schema_path): Resolves and returns the full paths to the configuration and schema files.
        _load_jobs(self): Loads and validates jobs from the configuration file using the schema.
        _validate_paths(self): Validates the existence of the configuration and schema files.
        start_job(self, job_name): Starts the execution of a specified job by name.
    """
    
    def __init__(self, config_path=None, schema_path=None, log_level=logging.INFO):
        """
        Initializes the JobOrchestrator with optional paths to the configuration and schema files.
        
        Args:
            config_path (str, optional): Path to the job configuration file. Defaults to 'config/job_config.json'.
            schema_path (str, optional): Path to the JSON schema file for validation. Defaults to 'config/job_schema.json'.
            log_level (int): Logging level to use.
        """
        setup_logging(log_level)
        
        # Set default paths if not provided
        config_path = config_path if config_path is not None else 'config/job_config.json'
        schema_path = schema_path if schema_path is not None else 'config/job_schema.json'
        
        # Resolve paths and load jobs
        self.config_path, self.schema_path = self._resolve_paths(config_path, schema_path)
        self.jobs = self._load_jobs()
  
    def _resolve_paths(self, config_path, schema_path):
        """
        Resolves the full paths to the configuration and schema files based on the provided relative paths.
        
        Args:
            config_path (str): Relative path to the job configuration file.
            schema_path (str): Relative path to the JSON schema file.
        
        Returns:
            tuple: A tuple containing the full paths to the configuration and schema files.
        """
        base_dir = Path(__file__).resolve().parent.parent.parent
        full_config_path = base_dir / config_path
        full_schema_path = base_dir / schema_path
        return full_config_path, full_schema_path

    def _load_jobs(self):
        """
        Loads and validates jobs from the configuration file using the schema. Raises exceptions if any errors occur during loading or validation.
        
        Returns:
            dict: The loaded and validated job configurations.
        
        Raises:
            json.JSONDecodeError: If there is an error decoding the JSON configuration file.
            ValidationError: If the configuration does not match the schema.
        """
        self._validate_paths()
        try:
            with self.config_path.open('r') as file:
                jobs = json.load(file)
            with self.schema_path.open('r') as schema_file:
                schema = json.load(schema_file)
            validate(instance=jobs, schema=schema)
        except json.JSONDecodeError as exception:
            logging.error("Error decoding JSON: %s", exception)
            raise
        except ValidationError as exception:
            logging.error("Schema validation error: %s", exception)
            raise
        return jobs

    def _validate_paths(self):
        """
        Validates the existence of the configuration and schema files. Raises FileNotFoundError if any file is missing.
        
        Raises:
            FileNotFoundError: If the configuration file or schema file does not exist.
        """
        if not self.config_path.exists():
            logging.error("Config file %s not found.", self.config_path)
            raise FileNotFoundError(f"Config file {self.config_path} not found.")
        if not self.schema_path.exists():
            logging.error("Schema file %s not found.", self.schema_path)
            raise FileNotFoundError(f"Schema file {self.schema_path} not found.")

    def start_job(self, job_name):
        """
        Starts the execution of a specified job by name. Validates the existence of the job in the configuration and checks for cyclic dependencies.
        
        Args:
            job_name (str): The name of the job to start.
        
        Raises:
            ValueError: If the job is not found in the configuration or if cyclic dependencies are detected.
        """
        job = self.jobs.get('jobs', {}).get(job_name)
        if not job:
            logging.error("Job %s not found in configuration.", job_name)
            raise ValueError(f"Job {job_name} not found in configuration.")
        
        handler_name = job.get('handler', 'job_orchestrator.handlers.generic_job_handler')
        if not handler_name:
            logging.error("No handler specified for job %s, and no default handler is set.", job_name)
            raise ValueError(f"No handler specified for job {job_name}, and no default handler is set.")
        else:
            logging.info("Handler for job %s is set to %s.", job_name, handler_name)

        tasks = job.get('tasks', [])
        if has_cyclic_dependencies(tasks):
            logging.error("Cyclic dependencies detected in job %s.", job_name)
            raise ValueError(f"Cyclic dependencies detected in job {job_name}.")

        task_handler = TaskHandler()
        task_handler.execute_job(handler_name, tasks)
