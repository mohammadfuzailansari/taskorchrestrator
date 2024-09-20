from fastapi import FastAPI, HTTPException
from joborchrestrator.orchestrator import JobOrchestrator
import uvicorn
import logging

app = FastAPI()

# Configure logging at the application level
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.post("/execute_job/{job_name}")
async def execute_job(job_name: str):
    try:
        orchestrator = JobOrchestrator("config/job.json", "config/schema.json")
        await orchestrator.execute_job(job_name)
        return {"status": "success", "message": f"Job '{job_name}' executed successfully."}
    except ValueError as e:
        logging.error('ValueError: %s', e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error('Unexpected error: %s', e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
