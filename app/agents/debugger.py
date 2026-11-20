from app.services.llm import ask_llm, extract_json
SYSTEM='''You are a cautious debugger. Return ONLY JSON: {"files":[{"path":"relative/path","content":"full corrected content"}],"explanation":"brief explanation"}. Suggest minimal fixes. Never add destructive or network-accessing behavior.'''
async def propose_fixes(files,test_report):
    try: return extract_json(await ask_llm(SYSTEM,str({'files':files,'test_report':test_report})))
    except Exception as exc: return {'files':[],'explanation':f'No automatic repair applied: {exc}'}
