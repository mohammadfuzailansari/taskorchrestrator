import os
import sys
# Append the project root directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..'))
sys.path.insert(0, project_root)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(1, project_root)

import logging
from job_orchestrator.job import JobOrchestrator
from job_orchestrator.utilities import setup_logging


"""
This module is designed to execute specific jobs configured through JSON files using the JobOrchestrator class.
It includes functionality to set up logging, read job configurations, and handle the execution of jobs with robust
error management. The module can be used in environments where jobs need to be executed with pre-defined configurations
and where error handling and logging are crucial for maintaining system integrity.

Functions:
    main(job_name): The main entry point for the module. It configures logging, initializes the JobOrchestrator with the
                    specified job configuration and schema files, and executes the job while handling various exceptions.

Example usage:
    If this script is executed directly (i.e., not imported), it will read the job configuration from 'config/job_config.json'
    and the schema from 'config/job_schema.json', attempt to execute the job named 'job1', and handle any errors that occur.
"""

def initiate_job(job_name):
    """
    Main function to execute a job using the JobOrchestrator.
    
    This function sets up the configuration path, initializes the JobOrchestrator,
    and attempts to start a specified job. It handles exceptions by logging them
    and exiting the program with an error status.
    
    Args:
        job_name (str): The name of the job to be executed, which should correspond to one of the jobs
                        defined in the job configuration file.
    
    Raises:
        FileNotFoundError: If the configuration or schema files are not found.
        json.JSONDecodeError: If there is an error parsing the JSON configuration.
        Exception: For any other exceptions that may occur during job execution.
    """
    setup_logging()  # Configure the logging based on predefined settings.
        
    try:
        # Initialize the JobOrchestrator and start the specified job
        orchestrator = JobOrchestrator('config/job_config.json','config/job_schema.json')
        orchestrator.start_job(job_name)
        logging.info("Successfully executed job: %s", job_name)   
    except Exception as e:
        logging.error("Failed to execute job: %s", e, exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    job_name = 'job1'  # Name of the job to be executed
    initiate_job(job_name)
