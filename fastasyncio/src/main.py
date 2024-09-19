from fastapi import FastAPI, HTTPException
from joborchrrestrator.orchestrator import JobOrchestrator
import uvicorn

app = FastAPI()

@app.post("/execute_job/{job_name}")
async def execute_job(job_name: str):
    try:
        orchestrator = JobOrchestrator("config/job.json", "config/schema.json")
        await orchestrator.execute_job(job_name)
        return {"status": "success", "message": f"Job '{job_name}' executed successfully."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
