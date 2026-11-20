import json
from app.services.llm import ask_llm, extract_json
SYSTEM='''You are a careful software project planner. Return ONLY valid JSON with keys project_name, summary, language, tasks (array), files (array of {path,purpose}). Keep scope small and educational. Do not request secrets or destructive operations.'''
async def plan_task(prompt):
    try:
        data=extract_json(await ask_llm(SYSTEM,prompt))
        if not isinstance(data.get('tasks'),list) or not isinstance(data.get('files'),list): raise ValueError('Invalid plan schema')
        return data,'llm'
    except Exception as exc:
        return {'project_name':'AI Generated Starter Project','summary':'Demo-mode plan. Configure an LLM API key for prompt-specific planning.','language':'Python',
                'tasks':['Understand requirements','Design the project structure','Implement core functionality','Add tests and error handling','Document how to run the project'],
                'files':[{'path':'main.py','purpose':'Application entry point'},{'path':'test_main.py','purpose':'Unit tests'},{'path':'README.md','purpose':'Project instructions'}], 'demo_note':str(exc)},'demo'
