import json, os, re, uuid, zipfile
from datetime import datetime, timezone
from app.config import WORKSPACE_DIR

def safe_id(value):
    cleaned=re.sub(r"[^a-zA-Z0-9_-]","",value)[:60]
    if not cleaned: raise ValueError("Invalid project identifier.")
    return cleaned

def create_project_dir(project_id):
    root=os.path.abspath(WORKSPACE_DIR); path=os.path.abspath(os.path.join(root,safe_id(project_id)))
    if os.path.commonpath([root,path]) != root: raise ValueError("Project path escaped workspace.")
    os.makedirs(path,exist_ok=True); return path

def new_project_id():
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")+"-"+uuid.uuid4().hex[:8]

def write_project_file(project_dir,relative_path,content):
    if not isinstance(relative_path,str) or not isinstance(content,str): raise ValueError("Invalid file entry.")
    normalized=os.path.normpath(relative_path).replace("\\","/")
    if normalized in ("",".","..") or normalized.startswith("../") or normalized.startswith("/") or len(normalized)>180:
        raise ValueError("Unsafe project path rejected.")
    if any(p in ("",".","..") for p in normalized.split("/")): raise ValueError("Invalid project path.")
    if len(content.encode("utf-8"))>500_000: raise ValueError("Generated file exceeds 500 KB.")
    root=os.path.abspath(project_dir); full=os.path.abspath(os.path.join(root,normalized))
    if os.path.commonpath([root,full]) != root: raise ValueError("Unsafe project path rejected.")
    os.makedirs(os.path.dirname(full),exist_ok=True)
    with open(full,"w",encoding="utf-8",newline="\n") as f: f.write(content)

def list_project_files(project_dir):
    result=[]; root=os.path.abspath(project_dir)
    for current,dirs,names in os.walk(root,followlinks=False):
        dirs[:]=[d for d in dirs if not os.path.islink(os.path.join(current,d))]
        for name in names:
            full=os.path.join(current,name)
            if name=="result.json" or os.path.islink(full): continue
            result.append({"path":os.path.relpath(full,root).replace("\\","/"),"size":os.path.getsize(full)})
    return sorted(result,key=lambda x:x["path"])

def save_result(project_dir,result):
    with open(os.path.join(project_dir,"result.json"),"w",encoding="utf-8") as f: json.dump(result,f,indent=2,ensure_ascii=False)

def read_result(project_dir):
    path=os.path.join(project_dir,"result.json")
    if not os.path.isfile(path): return None
    with open(path,encoding="utf-8") as f: return json.load(f)

def zip_project(project_dir,destination):
    root=os.path.abspath(project_dir)
    with zipfile.ZipFile(destination,"w",zipfile.ZIP_DEFLATED) as z:
        for current,dirs,names in os.walk(root,followlinks=False):
            dirs[:]=[d for d in dirs if not os.path.islink(os.path.join(current,d))]
            for name in names:
                full=os.path.join(current,name)
                if name=="result.json" or os.path.islink(full): continue
                z.write(full,os.path.relpath(full,root))
