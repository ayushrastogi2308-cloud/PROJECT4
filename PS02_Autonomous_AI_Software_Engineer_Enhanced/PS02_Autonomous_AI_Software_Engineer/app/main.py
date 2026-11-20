import os,re,tempfile
from fastapi import FastAPI,HTTPException
from fastapi.responses import HTMLResponse,FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field
from app.config import WORKSPACE_DIR,LLM_API_KEY,ENABLE_DOCKER_EXECUTION
from app.orchestrator import run_workflow
from app.services.storage import read_result,list_project_files,zip_project
app=FastAPI(title='PS02 Autonomous AI Software Engineer',version='1.0.0')
os.makedirs(WORKSPACE_DIR,exist_ok=True)
STATIC_DIR=os.path.join(os.path.dirname(__file__),'static')
app.mount('/static',StaticFiles(directory=STATIC_DIR),name='static')
class RunRequest(BaseModel): prompt:str=Field(min_length=8,max_length=5000)
@app.get('/',response_class=HTMLResponse)
async def home():
    with open(os.path.join(STATIC_DIR,'index.html'),encoding='utf-8') as f:return f.read()
@app.get('/api/health')
async def health():return {'status':'ok','llm_configured':bool(LLM_API_KEY),'docker_execution_enabled':ENABLE_DOCKER_EXECUTION}
@app.post('/api/run')
async def run(req:RunRequest):
    try:return await run_workflow(req.prompt)
    except Exception as exc:raise HTTPException(500,detail=f'Workflow failed: {exc}')
@app.get('/api/projects')
async def projects():
    items=[]
    for pid in sorted(os.listdir(WORKSPACE_DIR),reverse=True):
        path=os.path.join(WORKSPACE_DIR,pid)
        if os.path.isdir(path):
            data=read_result(path)
            if data:items.append({'project_id':pid,'prompt':data.get('prompt',''),'files':len(data.get('files',[]))})
    return items
@app.get('/api/projects/{project_id}')
async def get_project(project_id:str):
    if re.fullmatch(r'[a-zA-Z0-9_-]+',project_id) is None:raise HTTPException(400,'Invalid project ID')
    data=read_result(os.path.join(WORKSPACE_DIR,project_id))
    if not data:raise HTTPException(404,'Project not found')
    return data
@app.get('/api/projects/{project_id}/files')
async def get_files(project_id:str):
    if re.fullmatch(r'[a-zA-Z0-9_-]+',project_id) is None:raise HTTPException(400,'Invalid project ID')
    path=os.path.join(WORKSPACE_DIR,project_id)
    if not os.path.isdir(path):raise HTTPException(404,'Project not found')
    return list_project_files(path)
@app.get('/api/projects/{project_id}/download')
async def download(project_id:str):
    if re.fullmatch(r'[a-zA-Z0-9_-]+',project_id) is None:raise HTTPException(400,'Invalid project ID')
    path=os.path.join(WORKSPACE_DIR,project_id)
    if not os.path.isdir(path):raise HTTPException(404,'Project not found')
    tmp=tempfile.NamedTemporaryFile(delete=False,suffix='.zip');tmp.close();zip_project(path,tmp.name)
    return FileResponse(tmp.name,filename=f'{project_id}.zip',media_type='application/zip')
