import os
from app.agents.planner import plan_task
from app.agents.developer import generate_files
from app.agents.tester import run_static_checks, run_tests
from app.agents.debugger import propose_fixes
from app.agents.reviewer import review_project
from app.services.executor import run_python_in_docker
from app.services.storage import new_project_id,create_project_dir,write_project_file,list_project_files,save_result
from app.config import MAX_REPAIR_ITERATIONS

async def run_workflow(prompt):
    project_id=new_project_id(); project_dir=create_project_dir(project_id); events=[]
    plan,plan_mode=await plan_task(prompt)
    events.append({"agent":"Planner","status":"completed","detail":"Produced structured project plan."})
    generated,dev_mode=await generate_files(prompt,plan)
    if len(generated)>30: raise ValueError("Generated project exceeded 30-file limit.")
    for item in generated: write_project_file(project_dir,item["path"],item["content"])
    events.append({"agent":"Developer","status":"completed","detail":f"Generated {len(generated)} files."})
    test_report=run_static_checks(project_dir); test_report["unit_tests"]=await run_tests(project_dir)
    events.append({"agent":"Tester","status":"completed","detail":"Static checks and isolated unit tests attempted."})
    repairs=0; limit=max(0,min(MAX_REPAIR_ITERATIONS,2))
    while repairs<limit:
        failed=any(x["status"]=="failed" for x in test_report["python_syntax"]) or test_report["unit_tests"].get("status")=="failed"
        if not failed: break
        proposal=await propose_fixes(generated,test_report); fixes=proposal.get("files",[]) if isinstance(proposal,dict) else []
        if not fixes: break
        for item in fixes:
            if isinstance(item.get("path"),str) and isinstance(item.get("content"),str):
                write_project_file(project_dir,item["path"],item["content"])
        repairs+=1; generated=fixes
        test_report=run_static_checks(project_dir); test_report["unit_tests"]=await run_tests(project_dir)
        events.append({"agent":"Debugger","status":"completed","detail":f"Bounded repair iteration {repairs}."})
    main_path=os.path.join(project_dir,"main.py")
    execution={"status":"skipped","stdout":"","stderr":"No main.py or Docker execution disabled."}
    if os.path.isfile(main_path):
        with open(main_path,encoding="utf-8") as f: execution=await run_python_in_docker(f.read())
    events.append({"agent":"Execution","status":execution.get("status","unknown"),"detail":"Uses configured isolated Docker runner only."})
    review=await review_project(prompt,generated,test_report)
    events.append({"agent":"Reviewer","status":"completed","detail":"Produced code review."})
    result={"project_id":project_id,"prompt":prompt,"plan":plan,"files":list_project_files(project_dir),
            "test_report":test_report,"execution":execution,"review":review,"events":events,
            "modes":{"planner":plan_mode,"developer":dev_mode},"repairs_applied":repairs,
            "safety":{"generated_code_executed_on_host":False,"human_review_required":True}}
    save_result(project_dir,result); return result
