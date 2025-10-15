from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import json
import os
from datetime import datetime
from supabase import create_client, Client
from typing import Optional

app = FastAPI(title="Vulnerability Scanner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase_url = os.getenv("VITE_SUPABASE_URL")
supabase_key = os.getenv("VITE_SUPABASE_ANON_KEY")
supabase: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

class ScanRequest(BaseModel):
    target: str
    tool: str
    options: Optional[str] = ""

class ScanResponse(BaseModel):
    scan_id: str
    status: str
    message: str

def save_scan_result(tool: str, target: str, result: str, status: str):
    if supabase:
        try:
            data = {
                "tool": tool,
                "target": target,
                "result": result,
                "status": status,
                "created_at": datetime.utcnow().isoformat()
            }
            supabase.table("scans").insert(data).execute()
        except Exception as e:
            print(f"Error saving to database: {e}")

def run_nmap(target: str, options: str = "") -> dict:
    try:
        cmd = f"nmap {options} -oX - {target}"
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            timeout=300
        )
        output = result.stdout if result.returncode == 0 else result.stderr
        save_scan_result("nmap", target, output, "completed" if result.returncode == 0 else "failed")
        return {
            "tool": "nmap",
            "target": target,
            "output": output,
            "status": "completed" if result.returncode == 0 else "failed"
        }
    except subprocess.TimeoutExpired:
        return {"tool": "nmap", "target": target, "output": "Scan timeout", "status": "timeout"}
    except Exception as e:
        return {"tool": "nmap", "target": target, "output": str(e), "status": "error"}

def run_nikto(target: str, options: str = "") -> dict:
    try:
        cmd = f"nikto -h {target} {options} -Format json -output /tmp/nikto_output.json"
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=600
        )

        try:
            with open("/tmp/nikto_output.json", "r") as f:
                output = f.read()
        except:
            output = result.stdout if result.stdout else result.stderr

        save_scan_result("nikto", target, output, "completed" if result.returncode == 0 else "failed")
        return {
            "tool": "nikto",
            "target": target,
            "output": output,
            "status": "completed" if result.returncode == 0 else "failed"
        }
    except subprocess.TimeoutExpired:
        return {"tool": "nikto", "target": target, "output": "Scan timeout", "status": "timeout"}
    except Exception as e:
        return {"tool": "nikto", "target": target, "output": str(e), "status": "error"}

def run_nuclei(target: str, options: str = "") -> dict:
    try:
        cmd = f"nuclei -u {target} {options} -json-export /tmp/nuclei_output.json"
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=600
        )

        try:
            with open("/tmp/nuclei_output.json", "r") as f:
                output = f.read()
        except:
            output = result.stdout if result.stdout else result.stderr

        save_scan_result("nuclei", target, output, "completed")
        return {
            "tool": "nuclei",
            "target": target,
            "output": output,
            "status": "completed"
        }
    except subprocess.TimeoutExpired:
        return {"tool": "nuclei", "target": target, "output": "Scan timeout", "status": "timeout"}
    except Exception as e:
        return {"tool": "nuclei", "target": target, "output": str(e), "status": "error"}

@app.get("/")
def read_root():
    return {"message": "Vulnerability Scanner API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/scan/nmap")
async def scan_nmap(request: ScanRequest, background_tasks: BackgroundTasks):
    result = run_nmap(request.target, request.options)
    return result

@app.post("/scan/nikto")
async def scan_nikto(request: ScanRequest, background_tasks: BackgroundTasks):
    result = run_nikto(request.target, request.options)
    return result

@app.post("/scan/nuclei")
async def scan_nuclei(request: ScanRequest, background_tasks: BackgroundTasks):
    result = run_nuclei(request.target, request.options)
    return result

@app.get("/scans")
async def get_scans():
    if not supabase:
        return {"scans": []}
    try:
        response = supabase.table("scans").select("*").order("created_at", desc=True).limit(50).execute()
        return {"scans": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/scans/{scan_id}")
async def get_scan(scan_id: str):
    if not supabase:
        raise HTTPException(status_code=404, detail="Database not configured")
    try:
        response = supabase.table("scans").select("*").eq("id", scan_id).maybeSingle().execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Scan not found")
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
