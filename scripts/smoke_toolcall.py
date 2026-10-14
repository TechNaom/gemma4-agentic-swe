"""Smoke test: Gemma 4 tool calling via Gemini's OpenAI-compatible endpoint through LiteLLM (the harness's path)."""
import json
import os
import sys
import time

import litellm
from dotenv import load_dotenv

load_dotenv()
model = sys.argv[1] if len(sys.argv) > 1 else "gemma-4-31b-it"
tools = [{
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read a file from the workspace.",
        "parameters": {
            "type": "object",
            "properties": {"filepath": {"type": "string"}},
            "required": ["filepath"],
        },
    },
}]
start = time.time()
resp = litellm.completion(
    model=f"openai/{model}",
    api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.environ["GEMINI_API_KEY"],
    messages=[{"role": "user", "content": "Open src/app.py to see what it does. Use the tool."}],
    tools=tools,
    num_retries=3,
)
msg = resp.choices[0].message
print(f"model={model} latency={time.time() - start:.1f}s finish={resp.choices[0].finish_reason}")
print("tool_calls:", json.dumps([tc.model_dump() for tc in (msg.tool_calls or [])]))
print("text:", (msg.content or "")[:200])
