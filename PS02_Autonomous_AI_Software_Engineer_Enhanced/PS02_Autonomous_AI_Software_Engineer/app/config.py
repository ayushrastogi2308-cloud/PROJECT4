import os
from dotenv import load_dotenv
load_dotenv()
LLM_BASE_URL = os.getenv('LLM_BASE_URL', 'https://api.openai.com/v1').rstrip('/')
LLM_API_KEY = os.getenv('LLM_API_KEY', '')
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4o-mini')
ENABLE_DOCKER_EXECUTION = os.getenv('ENABLE_DOCKER_EXECUTION', 'false').lower() == 'true'
DOCKER_IMAGE = os.getenv('DOCKER_IMAGE', 'python:3.12-slim')
EXECUTION_TIMEOUT_SECONDS = int(os.getenv('EXECUTION_TIMEOUT_SECONDS', '8'))
MAX_REPAIR_ITERATIONS = int(os.getenv('MAX_REPAIR_ITERATIONS', '1'))
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'workspace'))
