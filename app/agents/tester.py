import os, subprocess, sys

def run_static_checks(project_dir):
    py_files=[]
    for root,_,names in os.walk(project_dir):
        py_files += [os.path.join(root,n) for n in names if n.endswith('.py')]
    syntax=[]
    for path in py_files:
        try:
            with open(path,encoding='utf-8') as f: compile(f.read(),path,'exec')
            syntax.append({'file':os.path.relpath(path,project_dir),'status':'passed'})
        except Exception as exc: syntax.append({'file':os.path.relpath(path,project_dir),'status':'failed','error':str(exc)})
    test_path=os.path.join(project_dir,'test_main.py')
    unit={'status':'skipped','message':'No test_main.py found.'}
    if os.path.exists(test_path):
        try:
            result=subprocess.run([sys.executable,'-m','unittest','discover','-s',project_dir,'-p','test*.py','-v'],capture_output=True,text=True,timeout=10,cwd=project_dir)
            unit={'status':'passed' if result.returncode==0 else 'failed','stdout':result.stdout[-4000:],'stderr':result.stderr[-4000:],'return_code':result.returncode}
        except Exception as exc: unit={'status':'error','message':str(exc)}
    return {'python_syntax':syntax,'unit_tests':unit}
