import os
from app.services.executor import run_project_tests_in_docker

def run_static_checks(project_dir):
    py_files=[]
    for root,_,names in os.walk(project_dir):
        for name in names:
            if name.endswith(".py"): py_files.append(os.path.join(root,name))
    syntax=[]
    for path in py_files:
        try:
            with open(path,encoding="utf-8") as f: compile(f.read(),path,"exec")
            syntax.append({"file":os.path.relpath(path,project_dir),"status":"passed"})
        except Exception as exc:
            syntax.append({"file":os.path.relpath(path,project_dir),"status":"failed","error":str(exc)})
    return {"python_syntax":syntax}

async def run_tests(project_dir):
    return await run_project_tests_in_docker(project_dir)
