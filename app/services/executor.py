import asyncio, os, shutil, tempfile
from app.config import ENABLE_DOCKER_EXECUTION, DOCKER_IMAGE, EXECUTION_TIMEOUT_SECONDS

async def run_python_in_docker(source_code):
    if not ENABLE_DOCKER_EXECUTION:
        return {'status':'skipped','stdout':'','stderr':'Docker execution is disabled. Set ENABLE_DOCKER_EXECUTION=true in .env.'}
    if not shutil.which('docker'):
        return {'status':'unavailable','stdout':'','stderr':'Docker CLI not found. Install and start Docker Desktop.'}
    with tempfile.TemporaryDirectory(prefix='ps02-run-') as tmp:
        with open(os.path.join(tmp,'main.py'),'w',encoding='utf-8') as f: f.write(source_code)
        cmd=['docker','run','--rm','--network','none','--read-only','--tmpfs','/tmp:rw,noexec,nosuid,size=16m',
             '--memory','128m','--cpus','0.5','--pids-limit','64','--cap-drop','ALL','--security-opt','no-new-privileges',
             '--user','65534:65534','--mount',f'type=bind,src={tmp},dst=/work,readonly','-w','/work',DOCKER_IMAGE,'python','-I','/work/main.py']
        proc=None
        try:
            proc=await asyncio.create_subprocess_exec(*cmd,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
            out,err=await asyncio.wait_for(proc.communicate(),timeout=EXECUTION_TIMEOUT_SECONDS)
            return {'status':'passed' if proc.returncode==0 else 'failed','return_code':proc.returncode,'stdout':out.decode(errors='replace')[-6000:],'stderr':err.decode(errors='replace')[-6000:]}
        except asyncio.TimeoutError:
            if proc: proc.kill(); await proc.communicate()
            return {'status':'timeout','stdout':'','stderr':'Execution exceeded time limit.'}
        except Exception as exc: return {'status':'error','stdout':'','stderr':str(exc)}
