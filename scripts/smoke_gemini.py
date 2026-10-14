"""Smoke test: one call to hosted Gemma 4 through the Gemini API."""
import os
import sys
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()
model = sys.argv[1] if len(sys.argv) > 1 else "gemma-4-31b-it"
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

start = time.time()
resp = client.models.generate_content(
    model=model,
    contents="Write a Python one-liner that reverses a string s. Reply with code only.",
)
print(f"model={model} latency={time.time() - start:.1f}s")
print(resp.text)
print("usage:", resp.usage_metadata)
