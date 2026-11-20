from app.services.llm import ask_llm
async def review_project(prompt,files,test_report):
    try:
        return await ask_llm('You are a code reviewer. Give concise findings under correctness, maintainability and security. Never claim code is safe merely because tests pass.',f'Request: {prompt}\nFiles: {[f["path"] for f in files]}\nTest report: {test_report}')
    except Exception:
        return 'Demo review: Inspect input validation, edge cases, error handling and file permissions. Passing syntax checks does not guarantee correctness or security. Review all generated source before use.'
