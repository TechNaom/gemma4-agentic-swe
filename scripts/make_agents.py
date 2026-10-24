"""Generate one self-contained harness submission directory per ablation config.

k configs share one tool-neutral prompt; only the tool list changes (does *having* a tool help?).
n configs ("nudge") have the same tools as k1-k5 plus a prompt section telling the agent to locate code with
them first (does *using* a tool help?). The pilot showed k agents called graph tools in only 8% of runs.
The harness blocks `!include` paths outside a submission root, so each config gets its own copy.

    python scripts/make_agents.py --model gemma-4-31b-it
"""
import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "agents" / "_template"
OUT = ROOT / "agents"

BASE_TOOLS = ["run_command", "read_file", "edit_file", "write_file", "get_status", "submit_patch"]
GRAPH_TOOLS = ["get_code_neighbors", "search_similar_code", "get_code_subgraph"]

CONFIGS = {
    "k0": {"tools": [], "analyzer": False, "about": "baseline, no graph tools"},
    "k1": {"tools": ["get_code_neighbors"], "analyzer": False, "about": "+ callers/callees"},
    "k2": {"tools": ["search_similar_code"], "analyzer": False, "about": "+ embedding search"},
    "k3": {"tools": ["get_code_subgraph"], "analyzer": False, "about": "+ induced subgraph"},
    "k4": {"tools": GRAPH_TOOLS, "analyzer": False, "about": "+ all graph tools"},
    "k5": {"tools": GRAPH_TOOLS, "analyzer": True, "about": "+ all graph tools + analyzer sub-agent"},
    "n1": {"tools": ["get_code_neighbors"], "analyzer": False, "nudge": True, "about": "k1 + use-the-tools prompt"},
    "n2": {"tools": ["search_similar_code"], "analyzer": False, "nudge": True, "about": "k2 + use-the-tools prompt"},
    "n3": {"tools": ["get_code_subgraph"], "analyzer": False, "nudge": True, "about": "k3 + use-the-tools prompt"},
    "n4": {"tools": GRAPH_TOOLS, "analyzer": False, "nudge": True, "about": "k4 + use-the-tools prompt"},
    "n5": {"tools": GRAPH_TOOLS, "analyzer": True, "nudge": True, "about": "k5 + use-the-tools prompt"},
}

NUDGE = """

## Locate code with the code-intelligence tools first

This repository has pre-built code-intelligence tools: {tools}. Before any `read_file`, `grep` or `find`, use
them to find the symbols involved in the issue. Pass dotted names or short symbol names taken from the problem
statement (for example `module.Class.method` or `function_name`). Then read only the files and line ranges they
point you to. Fall back to `grep` only if the tools return nothing useful.
"""
NUDGE_ANALYZER = """
Start by calling `code_analyzer_agent` with the issue summary; it uses these tools to report the files, lines and
root cause. Then make the fix yourself.
"""

SAMPLING = """\
temperature: 0.2
top_p: 0.95
max_output_tokens: 4096  # 16384 left only half the 32k context for input; pilot overflowed 7x
"""

EVAL_CONFIG = """\
evaluation:
  timeout_seconds: 300
  max_tool_calls: 60
  max_time_minutes: 30
  max_turns: 200
"""


def tool_lines(tools: list[str]) -> str:
    return "".join(f"  - {t}\n" for t in tools)


def build(name: str, cfg: dict, model: str) -> None:
    d = OUT / name
    if d.exists():
        shutil.rmtree(d)
    (d / "prompts").mkdir(parents=True)
    (d / "configs").mkdir()
    prompt = (TEMPLATE / "system.md").read_text(encoding="utf-8")
    if cfg.get("nudge"):
        prompt = prompt.rstrip() + NUDGE.format(tools=", ".join(f"`{t}`" for t in cfg["tools"]))
        if cfg["analyzer"]:
            prompt += NUDGE_ANALYZER
    (d / "prompts" / "system.md").write_text(prompt, encoding="utf-8", newline="\n")
    (d / "configs" / "sampling.yaml").write_text(SAMPLING, encoding="utf-8")
    (d / "eval_config.yaml").write_text(EVAL_CONFIG, encoding="utf-8")

    tools = tool_lines(BASE_TOOLS + cfg["tools"])
    if cfg["analyzer"]:
        tools += "  - agent_tool:\n      config_path: sub_agents/code_analyzer.yaml\n      skip_summarization: true\n"
        (d / "sub_agents").mkdir()
        shutil.copy(TEMPLATE / "analyzer.md", d / "prompts" / "analyzer.md")
        (d / "sub_agents" / "code_analyzer.yaml").write_text(
            "name: code_analyzer_agent\n"
            "description: Read-only helper that locates the code behind an issue.\n"
            f"model: {model}\n"
            "instruction: !include ../prompts/analyzer.md\n"
            f"tools:\n{tool_lines(['read_file'] + GRAPH_TOOLS)}"
            "generate_content_config: !include ../configs/sampling.yaml\n",
            encoding="utf-8",
        )

    (d / "agent.yaml").write_text(
        f"# {name}: {cfg['about']}\n"
        f"name: swe_agent_{name}\n"
        f"model: {model}\n"
        "instruction: !include prompts/system.md\n"
        f"tools:\n{tools}"
        "generate_content_config: !include configs/sampling.yaml\n",
        encoding="utf-8",
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="gemma-4-31b-it")
    args = ap.parse_args()
    for name, cfg in CONFIGS.items():
        build(name, cfg, args.model)
        print(f"{name}: {cfg['about']}")


if __name__ == "__main__":
    main()
