import json, httpx
from app.config import LLM_BASE_URL, LLM_API_KEY, LLM_MODEL

class LLMError(RuntimeError): pass

async def ask_llm(system_prompt,user_prompt,temperature=0.2):
    if not LLM_API_KEY: raise LLMError("No LLM_API_KEY configured.")
    payload={"model":LLM_MODEL,"temperature":temperature,"max_tokens":6000,
             "messages":[{"role":"system","content":system_prompt},{"role":"user","content":user_prompt}]}
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(75,connect=10)) as client:
            response=await client.post(f"{LLM_BASE_URL}/chat/completions",
                headers={"Authorization":f"Bearer {LLM_API_KEY}","Content-Type":"application/json"},json=payload)
            response.raise_for_status(); content=response.json()["choices"][0]["message"]["content"]
            if not isinstance(content,str) or not content.strip(): raise LLMError("Empty model response.")
            return content
    except LLMError: raise
    except Exception as exc: raise LLMError(f"LLM request failed: {type(exc).__name__}: {exc}") from exc

def extract_json(text):
    text=text.strip()
    if text.startswith("```"):
        text=text.split("\n",1)[-1]
        if text.endswith("```"): text=text[:-3]
    start,end=text.find("{"),text.rfind("}")
    if start<0 or end<=start: raise ValueError("Model did not return a JSON object.")
    return json.loads(text[start:end+1])
