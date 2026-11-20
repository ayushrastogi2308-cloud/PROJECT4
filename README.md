# PS02 — Autonomous AI Software Engineer

A modular educational MVP that accepts a software task, plans it, generates files, runs syntax/unit checks, optionally executes Python in an isolated Docker container, and produces review notes.

## Features
- Web dashboard built with HTML, CSS and JavaScript.
- FastAPI backend.
- Planner, Developer, Tester, Debugger and Reviewer agents.
- OpenAI-compatible LLM API integration.
- Demo fallback mode when no API key is configured.
- Project file storage and ZIP download.
- Optional Docker execution with network disabled, read-only root filesystem, CPU/memory/process limits, dropped capabilities and timeout.

## Requirements
Python 3.10+. Docker Desktop is optional. An OpenAI-compatible API key is optional for the demo fallback.

## Windows PowerShell setup
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```
Edit `.env` and set `LLM_API_KEY` and `LLM_MODEL` if using a real model. With a blank key, the workflow uses a fixed demo student-record project and is not prompt-specific AI generation.

Run:
```powershell
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000

## macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Optional Docker execution
Install and start Docker Desktop, then set `ENABLE_DOCKER_EXECUTION=true` in `.env`. The executor runs Python in a short-lived container with network disabled and resource restrictions. Do not execute untrusted generated code directly on your host. Docker is defense-in-depth, not a perfect security boundary; a disposable VM is safer for highly untrusted workloads.

## API
- `GET /api/health`
- `POST /api/run` with JSON body `{"prompt":"Create a Python calculator with tests"}`
- `GET /api/projects`
- `GET /api/projects/{project_id}`
- `GET /api/projects/{project_id}/files`
- `GET /api/projects/{project_id}/download`

## Architecture
Browser → FastAPI → Orchestrator → Planner → Developer → Tester → (bounded Debugger repair) → optional Docker execution → Reviewer → saved report.

## Important limitations
This is a college-project starter MVP, not a production-grade autonomous engineer. LLM output can be wrong or unsafe. The demo fallback is not an autonomous LLM. Unit tests are run by the backend on generated project files; for untrusted prompts/code, use an isolated disposable environment and review the code. Add authentication, rate limits, persistent database storage, WebSocket progress, stronger sandboxing, human approval gates and evaluation metrics before production use.
