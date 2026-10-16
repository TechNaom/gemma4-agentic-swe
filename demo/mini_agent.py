"""A glass-box coding agent: the same think -> tool -> result loop as the competition agent, printed step by step.

It works on a copy of demo/toy_project (a shop module with one planted bug) and can only use four tools,
all confined to that copy: list_files, read_file, edit_file, run_tests. No general shell access.

    python demo/mini_agent.py          # run straight through
    python demo/mini_agent.py --step   # pause after every step (press Enter to continue)
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import litellm
from dotenv import load_dotenv

GEMINI_OPENAI_BASE = "https://generativelanguage.googleapis.com/v1beta/openai/"
TOY = Path(__file__).resolve().parent / "toy_project"

BUG_REPORT = (
    "Customers report that discounts are wrong: a 10% discount on a 200 item charges 20 instead of 180. "
    "Fix the bug in the shop module. The tests in test_shop.py describe the expected behaviour."
)

SYSTEM = (
    "You are a software engineer fixing a bug. Work step by step with the tools: find the code, read it, "
    "fix it with edit_file, then run_tests to check. When all tests pass, reply with a one-sentence summary "
    "and no tool call. Before each tool call, say in one short sentence what you are about to do and why."
)

TOOLS = [
    {"type": "function", "function": {
        "name": "list_files", "description": "List the files in the project.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "read_file", "description": "Read a file in the project.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "edit_file", "description": "Replace one exact snippet of text in a file with new text.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}, "old": {"type": "string"}, "new": {"type": "string"}},
            "required": ["path", "old", "new"]}}},
    {"type": "function", "function": {
        "name": "run_tests", "description": "Run the project's unit tests and return the output.",
        "parameters": {"type": "object", "properties": {}}}},
]


class Workspace:
    """The agent's sandbox: a throwaway copy of the toy project."""

    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix="mini_agent_"))
        shutil.copytree(TOY, self.root, dirs_exist_ok=True)

    def _path(self, rel: str) -> Path:
        p = (self.root / rel).resolve()
        if self.root.resolve() not in p.parents and p != self.root.resolve():
            raise ValueError("path outside the project")
        return p

    def list_files(self):
        return "\n".join(sorted(p.name for p in self.root.glob("*.py")))

    def read_file(self, path):
        return self._path(path).read_text(encoding="utf-8")

    def edit_file(self, path, old, new):
        p = self._path(path)
        text = p.read_text(encoding="utf-8")
        if text.count(old) != 1:
            return f"ERROR: the old text appears {text.count(old)} times; it must appear exactly once."
        p.write_text(text.replace(old, new), encoding="utf-8")
        return "OK, file edited."

    def run_tests(self):
        r = subprocess.run([sys.executable, "-m", "unittest", "-v", "test_shop"], cwd=self.root,
                           capture_output=True, text=True, timeout=60)
        return (r.stdout + r.stderr)[-3000:]

    def diff(self):
        import difflib
        a = (TOY / "shop.py").read_text(encoding="utf-8").splitlines(keepends=True)
        b = (self.root / "shop.py").read_text(encoding="utf-8").splitlines(keepends=True)
        return "".join(difflib.unified_diff(a, b, "before/shop.py", "after/shop.py"))


def banner(title, body="", colour="36"):
    print(f"\n\033[1;{colour}m=== {title} ===\033[0m")
    if body:
        print(body.rstrip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", action="store_true", help="pause after every step")
    ap.add_argument("--model", default="gemma-4-31b-it")
    ap.add_argument("--max-steps", type=int, default=12)
    args = ap.parse_args()
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    os.system("")  # enable colours on Windows terminals

    ws = Workspace()
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": BUG_REPORT}]
    banner("BRIEFING (what the agent is told)", f"[instructions] {SYSTEM}\n\n[bug report] {BUG_REPORT}", "35")
    banner("SANDBOX", f"A throwaway copy of the project at {ws.root}", "35")

    for step in range(1, args.max_steps + 1):
        if args.step:
            input("\n  (press Enter for the next step)")
        resp = litellm.completion(
            model=f"openai/{args.model}", api_base=GEMINI_OPENAI_BASE, api_key=os.environ["GEMINI_API_KEY"],
            messages=messages, tools=TOOLS, temperature=0.2, num_retries=3,
        )
        msg = resp.choices[0].message
        calls = msg.tool_calls or []
        banner(f"STEP {step}: GEMMA THINKS", msg.content or "(no words, straight to a tool)", "33")
        messages.append({"role": "assistant", "content": msg.content or "",
                         "tool_calls": [c.model_dump() for c in calls] or None})

        if not calls:
            banner("AGENT SAYS IT IS DONE", "", "32")
            break
        for call in calls:
            name, raw = call.function.name, call.function.arguments or "{}"
            kwargs = json.loads(raw)
            banner(f"STEP {step}: TOOL CALL -> {name}", json.dumps(kwargs, indent=2) if kwargs else "(no arguments)", "34")
            try:
                result = getattr(ws, name)(**kwargs)
            except Exception as e:  # unknown tool or bad arguments go back to the model as an error
                result = f"ERROR: {e}"
            banner(f"STEP {step}: RESULT (what Gemma sees next)", result[:2000], "37")
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    banner("WHAT THE AGENT CHANGED (the patch)", ws.diff() or "(nothing)", "32")
    banner("FINAL CHECK (tests run by us, not the agent)", ws.run_tests(), "32")


if __name__ == "__main__":
    main()
