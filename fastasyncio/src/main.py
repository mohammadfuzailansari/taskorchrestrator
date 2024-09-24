import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from joborchrestrator.orchestrator import JobOrchestrator
import logging

# Initialize the FastAPI application
app = FastAPI()

# Set up logging with a specific format and debug level to capture detailed information
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_orchestrator():
    """
    Dependency injection function that creates and returns an instance of JobOrchestrator.
    This function is used by FastAPI's dependency injection system to provide an orchestrator instance.
    
    Returns:
        JobOrchestrator: An instance of JobOrchestrator configured with job and schema JSON files.
    """
    return JobOrchestrator("config/job.json", "config/schema.json")

@app.post("/execute_job/{job_name}")
async def execute_job(job_name: str, orchestrator: JobOrchestrator = Depends(get_orchestrator)):
    """
    FastAPI endpoint to execute a job by its name using the JobOrchestrator.
    This endpoint handles POST requests and uses dependency injection to get an orchestrator instance.
    
    Args:
        job_name (str): The name of the job to execute.
        orchestrator (JobOrchestrator): An instance of JobOrchestrator to handle the job execution.
        
    Returns:
        dict: A dictionary with the status and message of the job execution.
        
    Raises:
        HTTPException: An exception with appropriate status code and detail message when an error occurs.
    """
    try:
        # Attempt to execute the job using the orchestrator
        await orchestrator.execute_job(job_name)
        # Return a success message if the job is executed successfully
        return {"status": "success", "message": f"Job '{job_name}' executed successfully."}
    except ValueError as e:
        # Log and raise an HTTP 400 error if a ValueError occurs (e.g., job not found or validation fails)
        logging.error('ValueError: %s', e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log and raise an HTTP 500 error for any other unexpected errors
        logging.error('Unexpected error: %s', e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    # Run the FastAPI app with Uvicorn, listening on all interfaces on port 8000, with auto-reload enabled
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
