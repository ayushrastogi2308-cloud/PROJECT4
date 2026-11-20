import os
from app.agents.planner import plan_task
from app.agents.developer import generate_files
from app.agents.tester import run_static_checks
from app.agents.debugger import propose_fixes
from app.agents.reviewer import review_project
from app.services.executor import run_python_in_docker
from app.services.storage import new_project_id,create_project_dir,write_project_file,list_project_files,save_result
from app.config import MAX_REPAIR_ITERATIONS

async def run_workflow(prompt):
    project_id=new_project_id(); project_dir=create_project_dir(project_id); events=[]
    plan,plan_mode=await plan_task(prompt); events.append({'agent':'Planner','status':'completed','detail':'Created task breakdown.'})
    generated,dev_mode=await generate_files(prompt,plan)
    for item in generated: write_project_file(project_dir,item['path'],item['content'])
    events.append({'agent':'Developer','status':'completed','detail':f'Generated {len(generated)} files.'})
    report=run_static_checks(project_dir); events.append({'agent':'Tester','status':'completed','detail':'Ran syntax and available unit-test checks.'})
    repairs=0
    while repairs < max(0,min(MAX_REPAIR_ITERATIONS,2)):
        failed=any(x['status']=='failed' for x in report.get('python_syntax',[])) or report.get('unit_tests',{}).get('status')=='failed'
        if not failed: break
        proposal=await propose_fixes(generated,report); fixes=proposal.get('files',[]) if isinstance(proposal,dict) else []
        if not fixes: break
        for item in fixes:
            if isinstance(item.get('path'),str) and isinstance(item.get('content'),str): write_project_file(project_dir,item['path'],item['content'])
        repairs+=1; report=run_static_checks(project_dir)
        events.append({'agent':'Debugger','status':'completed','detail':f'Applied repair iteration {repairs}.'})
    main_py=os.path.join(project_dir,'main.py')
    if os.path.exists(main_py):
        with open(main_py,encoding='utf-8') as f: execution=await run_python_in_docker(f.read())
    else: execution={'status':'skipped','stdout':'','stderr':'No main.py generated.'}
    events.append({'agent':'Execution','status':execution.get('status','unknown'),'detail':'Docker execution attempted only if enabled.'})
    review=await review_project(prompt,generated,report); events.append({'agent':'Reviewer','status':'completed','detail':'Produced review notes.'})
    result={'project_id':project_id,'prompt':prompt,'plan':plan,'files':list_project_files(project_dir),'test_report':report,'execution':execution,'review':review,'events':events,'modes':{'planner':plan_mode,'developer':dev_mode},'repairs_applied':repairs}
    save_result(project_dir,result); return result
