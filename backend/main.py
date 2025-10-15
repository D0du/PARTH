from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import json
import os
from datetime import datetime
import shutil
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
        if not _docker_available():
            return {"tool": "nmap", "target": target, "output": "Docker CLI not available in backend container", "status": "error"}

        image = os.getenv("NMAP_IMAGE", "instrumentisto/nmap")
        # instrumentisto/nmap sets entrypoint to `nmap`, so only pass arguments
        cmd = ["docker", "run", "--rm", image]
        if options:
            cmd.extend(options.split())
        cmd.extend(["-oX", "-", target])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        output = result.stdout if result.stdout else result.stderr
        status = "completed" if result.returncode == 0 else "failed"
        save_scan_result("nmap", target, output, status)
        return {"tool": "nmap", "target": target, "output": output, "status": status}
    except subprocess.TimeoutExpired:
        return {"tool": "nmap", "target": target, "output": "Scan timeout", "status": "timeout"}
    except Exception as e:
        return {"tool": "nmap", "target": target, "output": str(e), "status": "error"}

def run_nikto(target: str, options: str = "") -> dict:
    try:
        if not _docker_available():
            return {"tool": "nikto", "target": target, "output": "Docker CLI not available in backend container", "status": "error"}

        image = os.getenv("NIKTO_IMAGE", "sullo/nikto")
        cmd = ["docker", "run", "--rm", image, "-h", target]
        if options:
            cmd.extend(options.split())
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        output = result.stdout if result.stdout else result.stderr
        status = "completed" if result.returncode == 0 else "failed"
        save_scan_result("nikto", target, output, status)
        return {"tool": "nikto", "target": target, "output": output, "status": status}
    except subprocess.TimeoutExpired:
        return {"tool": "nikto", "target": target, "output": "Scan timeout", "status": "timeout"}
    except Exception as e:
        return {"tool": "nikto", "target": target, "output": str(e), "status": "error"}

def run_nuclei(target: str, options: str = "") -> dict:
    try:
        if not _docker_available():
            return {"tool": "nuclei", "target": target, "output": "Docker CLI not available in backend container", "status": "error"}

        image = os.getenv("NUCLEI_IMAGE", "projectdiscovery/nuclei:latest")
        cmd = ["docker", "run", "--rm", image, "-u", target, "-json"]
        if options:
            # insert options just before target flags if needed; simplest append
            cmd[4:4] = options.split()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        output = result.stdout if result.stdout else result.stderr
        status = "completed" if result.returncode == 0 else "failed"
        save_scan_result("nuclei", target, output, status)
        return {"tool": "nuclei", "target": target, "output": output, "status": status}
    except subprocess.TimeoutExpired:
        return {"tool": "nuclei", "target": target, "output": "Scan timeout", "status": "timeout"}
    except Exception as e:
        return {"tool": "nuclei", "target": target, "output": str(e), "status": "error"}

def _docker_available() -> bool:
    docker_bin = shutil.which("docker")
    return bool(docker_bin)

def run_sslyze(target: str, options: str = "") -> dict:
    """Run SSLyze using its official Docker image to avoid local deps."""
    try:
        if not _docker_available():
            return {"tool": "sslyze", "target": target, "output": "Docker CLI not available in backend container", "status": "error"}

        image = os.getenv("SSLYZE_IMAGE", "nablac0d3/sslyze")
        # SSLyze expects host:port (default to :443 if not provided)
        target_with_port = target if ":" in target else f"{target}:443"
        cmd = [
            "docker", "run", "--rm", image,
            "--regular",
            target_with_port,
        ]
        if options:
            # options string split safely
            cmd[3:3] = options.split()

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        output = result.stdout if result.returncode == 0 else result.stderr
        status = "completed" if result.returncode == 0 else "failed"
        save_scan_result("sslyze", target_with_port, output, status)
        return {"tool": "sslyze", "target": target_with_port, "output": output, "status": status}
    except subprocess.TimeoutExpired:
        return {"tool": "sslyze", "target": target, "output": "Scan timeout", "status": "timeout"}
    except Exception as e:
        return {"tool": "sslyze", "target": target, "output": str(e), "status": "error"}

def run_zap_baseline(target: str, options: str = "") -> dict:
    """Run OWASP ZAP baseline scan via Docker image."""
    try:
        if not _docker_available():
            return {"tool": "zap-baseline", "target": target, "output": "Docker CLI not available in backend container", "status": "error"}

        image = os.getenv("ZAP_IMAGE", "owasp/zap2docker-stable")
        # Use -I to ignore failures and ensure exit code 0 when only warnings
        base_cmd = [
            "docker", "run", "--rm",
            image,
            "zap-baseline.py",
            "-t", target,
            "-I",
        ]
        if options:
            base_cmd.extend(options.split())

        result = subprocess.run(base_cmd, capture_output=True, text=True, timeout=3600)
        output = result.stdout if result.stdout else result.stderr
        status = "completed" if result.returncode == 0 else "failed"
        save_scan_result("zap-baseline", target, output, status)
        return {"tool": "zap-baseline", "target": target, "output": output, "status": status}
    except subprocess.TimeoutExpired:
        return {"tool": "zap-baseline", "target": target, "output": "Scan timeout", "status": "timeout"}
    except Exception as e:
        return {"tool": "zap-baseline", "target": target, "output": str(e), "status": "error"}

def run_zap_api_scan(target: str, options: str = "") -> dict:
    """Run OWASP ZAP API scan via Docker image. Target should be an OpenAPI/Swagger URL."""
    try:
        if not _docker_available():
            return {"tool": "zap-api", "target": target, "output": "Docker CLI not available in backend container", "status": "error"}

        image = os.getenv("ZAP_IMAGE", "owasp/zap2docker-stable")
        base_cmd = [
            "docker", "run", "--rm",
            image,
            "zap-api-scan.py",
            "-t", target,
            "-f", "openapi",
            "-I",
        ]
        if options:
            base_cmd.extend(options.split())

        result = subprocess.run(base_cmd, capture_output=True, text=True, timeout=3600)
        output = result.stdout if result.stdout else result.stderr
        status = "completed" if result.returncode == 0 else "failed"
        save_scan_result("zap-api", target, output, status)
        return {"tool": "zap-api", "target": target, "output": output, "status": status}
    except subprocess.TimeoutExpired:
        return {"tool": "zap-api", "target": target, "output": "Scan timeout", "status": "timeout"}
    except Exception as e:
        return {"tool": "zap-api", "target": target, "output": str(e), "status": "error"}

def run_openvas_placeholder(target: str, options: str = "") -> dict:
    """Placeholder endpoint explaining OpenVAS setup complexity.
    OpenVAS requires a running manager and feed sync which can take several minutes.
    """
    message = (
        "OpenVAS/GVM requires a persistent service and database. "
        "Use a dedicated container like 'immauss/openvas' and connect to its web UI. "
        "This API currently returns a placeholder instead of running a full scan."
    )
    save_scan_result("openvas", target, message, "unavailable")
    return {"tool": "openvas", "target": target, "output": message, "status": "unavailable"}

def start_openvas_service(options: str = "") -> dict:
    """Start OpenVAS service container if not running and return access info."""
    try:
        if not _docker_available():
            return {"tool": "openvas", "target": "localhost", "output": "Docker CLI not available in backend container", "status": "error"}

        # Check if container exists and is running
        inspect = subprocess.run(["docker", "inspect", "-f", "{{.State.Running}}", "openvas"], capture_output=True, text=True)
        if inspect.returncode == 0 and inspect.stdout.strip() == "true":
            output = "OpenVAS already running. UI: http://localhost:9392 (user: admin)"
            save_scan_result("openvas", "localhost", output, "running")
            return {"tool": "openvas", "target": "localhost", "output": output, "status": "running"}

        # If not existing or stopped, attempt to run
        password = os.getenv("OPENVAS_ADMIN_PASSWORD", "admin")
        run_cmd = [
            "docker", "run", "-d", "--name", "openvas",
            "-p", "9392:9392",
            "-e", f"PASSWORD={password}",
            "immauss/openvas"
        ]
        if options:
            run_cmd.extend(options.split())
        result = subprocess.run(run_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            output = result.stderr
            save_scan_result("openvas", "localhost", output, "failed")
            return {"tool": "openvas", "target": "localhost", "output": output, "status": "failed"}

        output = "OpenVAS starting. Initial feed sync may take several minutes. UI: http://localhost:9392 (user: admin)"
        save_scan_result("openvas", "localhost", output, "starting")
        return {"tool": "openvas", "target": "localhost", "output": output, "status": "starting"}
    except Exception as e:
        return {"tool": "openvas", "target": "localhost", "output": str(e), "status": "error"}

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

@app.post("/scan/sslyze")
async def scan_sslyze(request: ScanRequest, background_tasks: BackgroundTasks):
    result = run_sslyze(request.target, request.options)
    return result

@app.post("/scan/zap-baseline")
async def scan_zap_baseline(request: ScanRequest, background_tasks: BackgroundTasks):
    result = run_zap_baseline(request.target, request.options)
    return result

@app.post("/scan/zap-api")
async def scan_zap_api(request: ScanRequest, background_tasks: BackgroundTasks):
    result = run_zap_api_scan(request.target, request.options)
    return result

@app.post("/scan/openvas")
async def scan_openvas(request: ScanRequest, background_tasks: BackgroundTasks):
    result = run_openvas_placeholder(request.target, request.options)
    return result

@app.post("/scan/openvas-start")
async def openvas_start(request: ScanRequest, background_tasks: BackgroundTasks):
    result = start_openvas_service(request.options)
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
