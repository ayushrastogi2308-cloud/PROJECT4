import json
import httpx
from app.config import LLM_BASE_URL, LLM_API_KEY, LLM_MODEL

class LLMError(RuntimeError): pass

async def ask_llm(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    if not LLM_API_KEY:
        raise LLMError('No LLM_API_KEY configured. Demo fallback will be used.')
    headers = {'Authorization': f'Bearer {LLM_API_KEY}', 'Content-Type': 'application/json'}
    payload = {'model': LLM_MODEL, 'temperature': temperature, 'messages': [
        {'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': user_prompt}]}
    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(f'{LLM_BASE_URL}/chat/completions', headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

def extract_json(text: str):
    text = text.strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[-1]
        if text.endswith('```'): text = text[:-3]
    start, end = text.find('{'), text.rfind('}')
    if start < 0 or end <= start: raise ValueError('Model did not return a JSON object.')
    return json.loads(text[start:end+1])
