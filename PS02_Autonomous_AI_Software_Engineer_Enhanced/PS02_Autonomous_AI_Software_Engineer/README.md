# PS02 — Autonomous AI Software Engineer (Enhanced MVP)

An educational multi-agent software engineering workspace. It plans a natural-language task, generates files, performs static checks, optionally runs generated project tests and a Python entrypoint in restricted Docker containers, supports bounded repair attempts, and produces review notes.

> This is an enhanced MVP, not a guarantee of full autonomy or a guaranteed evaluator score. The official detailed PS02 problem statement was not supplied. See `docs/RUBRIC_ALIGNMENT.md`.

## Features
- Planner, Developer, Tester, Debugger, Reviewer and Orchestrator modules.
- OpenAI-compatible LLM API integration and demo fallback.
- Project path and file-size validation; ZIP export.
- Static Python syntax checks.
- Optional Docker execution: no network, read-only filesystem/mounts, CPU/memory/PID limits, non-root user and dropped capabilities.
- Bounded repair loop and structured workflow report.
- Responsive dashboard with keyboard focus and accessible status labels.

## Setup
Python 3.10+.

Windows PowerShell:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your provider key to `.env` as `LLM_API_KEY`. Without it, demo fallback content is used.

Run:
```bash
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000

## Isolated execution
Install and start Docker Desktop, then set `ENABLE_DOCKER_EXECUTION=true` in `.env`. Generated project tests and entrypoint code are only run through the Docker runner, never directly as host subprocesses. Docker is a risk-reduction layer, not a perfect security boundary. Use a disposable VM for untrusted code.

## Tests
```bash
python -m unittest discover -s tests -v
```
App tests validate storage path handling and request validation. Generated project tests require Docker.

## API
- `GET /api/health`
- `POST /api/run` with `{"prompt":"..."}`
- `GET /api/projects`
- `GET /api/projects/{project_id}`
- `GET /api/projects/{project_id}/files`
- `GET /api/projects/{project_id}/download`

See `docs/RUBRIC_ALIGNMENT.md` and `docs/SUBMISSION_CHECKLIST.md`.
