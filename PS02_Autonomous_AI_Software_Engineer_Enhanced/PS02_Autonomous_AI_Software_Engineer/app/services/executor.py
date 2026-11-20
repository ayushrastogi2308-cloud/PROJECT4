import asyncio, os, shutil, tempfile
from app.config import ENABLE_DOCKER_EXECUTION, DOCKER_IMAGE, EXECUTION_TIMEOUT_SECONDS

async def _docker(command):
    try:
        proc = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        out, err = await asyncio.wait_for(proc.communicate(), timeout=max(2, EXECUTION_TIMEOUT_SECONDS))
        return {"status": "passed" if proc.returncode == 0 else "failed", "return_code": proc.returncode,
                "stdout": out.decode(errors="replace")[-8000:], "stderr": err.decode(errors="replace")[-8000:]}
    except asyncio.TimeoutError:
        proc.kill(); await proc.communicate()
        return {"status": "timeout", "stdout": "", "stderr": "Execution timed out."}
    except Exception as exc:
        return {"status": "error", "stdout": "", "stderr": str(exc)}

def _base_command(mount_src, mount_dst):
    return ["docker","run","--rm","--network","none","--read-only",
            "--tmpfs","/tmp:rw,noexec,nosuid,size=32m","--memory","192m","--cpus","0.5",
            "--pids-limit","64","--cap-drop","ALL","--security-opt","no-new-privileges",
            "--user","65534:65534","--mount",f"type=bind,src={mount_src},dst={mount_dst},readonly",
            "-w",mount_dst,DOCKER_IMAGE]

async def run_project_tests_in_docker(project_dir):
    if not ENABLE_DOCKER_EXECUTION:
        return {"status":"skipped","stdout":"","stderr":"Docker execution disabled; enable it in .env."}
    if not shutil.which("docker"):
        return {"status":"unavailable","stdout":"","stderr":"Docker CLI not found."}
    project_dir = os.path.abspath(project_dir)
    if not os.path.isdir(project_dir):
        return {"status":"error","stdout":"","stderr":"Project directory not found."}
    cmd = _base_command(project_dir, "/workspace") + ["python","-I","-m","unittest","discover","-s","/workspace","-p","test*.py","-v"]
    return await _docker(cmd)

async def run_python_in_docker(source_code):
    if not ENABLE_DOCKER_EXECUTION:
        return {"status":"skipped","stdout":"","stderr":"Docker execution disabled."}
    if not shutil.which("docker"):
        return {"status":"unavailable","stdout":"","stderr":"Docker CLI not found."}
    with tempfile.TemporaryDirectory(prefix="ps02-run-") as tmp:
        with open(os.path.join(tmp,"main.py"),"w",encoding="utf-8") as f: f.write(source_code)
        cmd = _base_command(tmp,"/work") + ["python","-I","/work/main.py"]
        return await _docker(cmd)
