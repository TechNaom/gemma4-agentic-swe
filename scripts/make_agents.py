"""Generate one self-contained harness submission directory per ablation config.

Every config shares the same system prompt, sampling and budget; only the tool list changes.
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
}

SAMPLING = """\
temperature: 0.2
top_p: 0.95
max_output_tokens: 16384
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
    shutil.copy(TEMPLATE / "system.md", d / "prompts" / "system.md")
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
