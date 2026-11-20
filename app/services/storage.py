import json, os, re, uuid, zipfile
from datetime import datetime, timezone
from app.config import WORKSPACE_DIR

def safe_id(value): return re.sub(r'[^a-zA-Z0-9_-]', '', value)[:60]
def new_project_id(): return datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:6]
def create_project_dir(project_id):
    path = os.path.join(WORKSPACE_DIR, safe_id(project_id)); os.makedirs(path, exist_ok=True); return path

def write_project_file(project_dir, relative_path, content):
    normalized = os.path.normpath(relative_path).replace('\\', '/')
    if normalized.startswith('../') or normalized in ('..', '.') or normalized.startswith('/'):
        raise ValueError('Unsafe project path rejected.')
    full = os.path.abspath(os.path.join(project_dir, normalized))
    if not full.startswith(os.path.abspath(project_dir) + os.sep): raise ValueError('Unsafe project path rejected.')
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f: f.write(content)

def list_project_files(project_dir):
    result=[]
    for root, _, names in os.walk(project_dir):
        for name in names:
            if name == 'result.json': continue
            full=os.path.join(root,name); result.append({'path':os.path.relpath(full,project_dir).replace('\\','/'),'size':os.path.getsize(full)})
    return sorted(result,key=lambda x:x['path'])
def save_result(project_dir,result):
    with open(os.path.join(project_dir,'result.json'),'w',encoding='utf-8') as f: json.dump(result,f,indent=2,ensure_ascii=False)
def read_result(project_dir):
    path=os.path.join(project_dir,'result.json')
    if not os.path.exists(path): return None
    with open(path,encoding='utf-8') as f: return json.load(f)
def zip_project(project_dir,destination):
    with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as z:
        for root,_,names in os.walk(project_dir):
            for name in names:
                if name != 'result.json':
                    full=os.path.join(root,name); z.write(full,os.path.relpath(full,project_dir))
