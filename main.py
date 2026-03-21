import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from graph import run_pipeline
from llm_router import LAPTOP_A_URL, LAPTOP_B_URL, GROQ_API_KEY, GEMINI_API_KEY

app = FastAPI(title="Multi-Agent AI Generator")

class GenerateRequest(BaseModel):
    requirement: str

@app.post("/generate")
async def generate(req: GenerateRequest):
    try:
        res = await run_pipeline(req.requirement)
        return {
            "status": "success",
            "project_name": res["project_name"],
            "files_generated": res["files_generated"],
            "tasks_completed": res["tasks_completed"],
            "download_url": f"/download/{res['project_name']}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{project_name}")
async def download(project_name: str):
    zip_path = f"./output/{project_name}.zip"
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(zip_path, filename=f"{project_name}.zip")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/agents/status")
async def agents_status():
    status = {}
    
    # Laptop A (Ollama)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(f"{LAPTOP_A_URL}")
            status["laptop_a_ollama"] = "online" if res.status_code == 200 else "offline"
    except Exception:
        status["laptop_a_ollama"] = "offline"

    # Laptop B (Ollama)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(f"{LAPTOP_B_URL}")
            status["laptop_b_ollama"] = "online" if res.status_code == 200 else "offline"
    except Exception:
        status["laptop_b_ollama"] = "offline"

    # Groq API
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
            status["groq"] = "online" if res.status_code == 200 else "offline"
    except Exception:
        status["groq"] = "offline"

    # Gemini API
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}")
            status["gemini"] = "online" if res.status_code == 200 else "offline"
    except Exception:
        status["gemini"] = "offline"

    return status
