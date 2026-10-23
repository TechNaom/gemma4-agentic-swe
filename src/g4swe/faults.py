"""Planted-bug generator (piece B): break a known-correct patch in one small, realistic way.

Each operator mutates the task's gold patch once and writes <instance_id>__<operator>.patch. A good verifier
should reject every mutant; a mutant that still resolves shows the tests cannot tell that fix from a broken one.

Operators (each mirrors a common human mistake):
  flip_compare   ==/!=, </>=, >/<=, in/not in, is/is not        inverted logic, off-by-one boundary
  off_by_one     integer literal n -> n + 1                    boundary error
  bool_swap      True <-> False                                 wrong default or flag
  drop_line      delete one added line                          incomplete fix
  drop_file      drop one file from a multi-file patch          forgot a related change
  remove_raise   `raise ...` -> `pass`                          swallowed error
  return_none    `return <expr>` -> `return None`               wrong output

Only lines the gold patch adds (`+` lines) are mutated, so the mutant still applies to the same base commit.

    python -m g4swe.faults --tasks D:/gemma-4-developer-agent/tasks.jsonl \
        --task-file experiments/valid_tasks.txt --out faults/patches
"""
from __future__ import annotations

import argparse
import json
import random
import re
from dataclasses import asdict, dataclass
from pathlib import Path

COMPARE_SWAPS = [
    (r"(?<![=!<>])==(?!=)", "!="), (r"!=", "=="),
    (r"(?<![<>=!])<(?![<=])", ">="), (r"(?<![<>=!-])>(?![>=])", "<="),
    (r"<=", ">"), (r">=", "<"),
    (r"\bnot in\b", "in"), (r"(?<!not )\bin\b(?= )", "not in"),
    (r"\bis not\b", "is"), (r"\bis\b(?! not)", "is not"),
]
STRING = re.compile(r"""("[^"\\]*(?:\\.[^"\\]*)*"|'[^'\\]*(?:\\.[^'\\]*)*')""")


@dataclass
class Mutant:
    instance_id: str
    operator: str
    file: str
    before: str
    after: str


# ---------------------------------------------------------------- diff parsing

@dataclass
class FileDiff:
    header: list[str]   # '--- a/x', '+++ b/x' (and any 'diff --git' lines before them)
    hunks: list[list[str]]  # each hunk: '@@ ... @@' line followed by body lines

    @property
    def path(self) -> str:
        plus = next((h for h in self.header if h.startswith("+++ ")), "+++ b/?")
        return plus[6:] if plus.startswith("+++ b/") else plus[4:]

    def render(self) -> list[str]:
        out = list(self.header)
        for h in self.hunks:
            out += h
        return out


def parse_patch(patch: str) -> list[FileDiff]:
    files: list[FileDiff] = []
    cur: FileDiff | None = None
    lines = patch.splitlines()
    for i, line in enumerate(lines):
        next_line = lines[i + 1] if i + 1 < len(lines) else ""
        starts_file = line.startswith("diff --git") or (
            line.startswith("--- ") and next_line.startswith("+++ ") and (cur is None or cur.hunks)
        )
        if starts_file:
            cur = FileDiff(header=[line], hunks=[])
            files.append(cur)
        elif cur is not None and not cur.hunks and (line.startswith(("--- ", "+++ ", "index ", "new file", "deleted file", "similarity", "rename"))):
            cur.header.append(line)
        elif line.startswith("@@") and cur is not None:
            cur.hunks.append([line])
        elif cur is not None and cur.hunks:
            cur.hunks[-1].append(line)
    return files


def render_patch(files: list[FileDiff]) -> str:
    return "\n".join(line for f in files for line in f.render()) + "\n"


def recount_hunk(hunk: list[str]) -> list[str]:
    """Rewrite the @@ header's line counts after lines were removed from the hunk body."""
    m = re.match(r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@(.*)", hunk[0])
    if not m:
        return hunk
    old = sum(1 for l in hunk[1:] if l.startswith((" ", "-")) or l == "")
    new = sum(1 for l in hunk[1:] if l.startswith((" ", "+")) or l == "")
    return [f"@@ -{m.group(1)},{old} +{m.group(2)},{new} @@{m.group(3)}"] + hunk[1:]


def balanced(code: str) -> bool:
    """True if the line opens and closes the same number of brackets (a complete statement)."""
    bare = STRING.sub("''", code)
    return sum(bare.count(c) for c in "([{") == sum(bare.count(c) for c in ")]}")


def added_sites(files: list[FileDiff]):
    """Yield (file_index, hunk_index, line_index, code) for every added code line outside docstrings.

    Docstring state is tracked over the post-image (context + added lines) of each hunk; it is a heuristic,
    since a hunk can start inside a string that opened earlier in the file.
    """
    for fi, f in enumerate(files):
        for hi, h in enumerate(f.hunks):
            in_doc = False
            for li, line in enumerate(h[1:], start=1):
                if line.startswith("-") or line.startswith("\\"):
                    continue
                code = line[1:] if line[:1] in "+ " else line
                quotes = code.count('"""') + code.count("'''")
                was_in_doc = in_doc
                in_doc = in_doc ^ (quotes % 2 == 1)
                if was_in_doc or quotes:
                    continue  # inside or on the boundary of a docstring
                if line.startswith("+") and code.strip() and not code.strip().startswith("#"):
                    yield fi, hi, li, code


# ---------------------------------------------------------------- operators

def _outside_strings(code: str, pattern: str, repl: str) -> str | None:
    """Apply one regex replacement to the first match that is not inside a string literal."""
    spans = [m.span() for m in STRING.finditer(code)]
    for m in re.finditer(pattern, code):
        if not any(a <= m.start() < b for a, b in spans):
            return code[:m.start()] + re.sub(pattern, repl, m.group(0)) + code[m.end():]
    return None


def line_mutation(op: str, code: str) -> str | None:
    stripped = code.strip()
    if op == "flip_compare":
        for pattern, repl in COMPARE_SWAPS:
            if (new := _outside_strings(code, pattern, repl)) is not None:
                return new
    elif op == "off_by_one":
        spans = [m.span() for m in STRING.finditer(code)]
        for m in re.finditer(r"(?<![\w.])(\d+)(?![\w.])", code):
            if not any(a <= m.start() < b for a, b in spans):
                return code[:m.start()] + str(int(m.group(1)) + 1) + code[m.end():]
    elif op == "bool_swap":
        new = _outside_strings(code, r"\bTrue\b", "False")
        return new if new is not None else _outside_strings(code, r"\bFalse\b", "True")
    elif op == "remove_raise" and stripped.startswith("raise") and balanced(code):
        return code[: len(code) - len(code.lstrip())] + "pass"
    elif op == "return_none" and stripped.startswith("return ") and stripped != "return None" and balanced(code):
        return code[: len(code) - len(code.lstrip())] + "return None"
    return None


LINE_OPS = ["flip_compare", "off_by_one", "bool_swap", "remove_raise", "return_none"]
OPERATORS = LINE_OPS + ["drop_line", "drop_file"]


def mutate(instance_id: str, patch: str, op: str, rng: random.Random) -> tuple[str, Mutant] | None:
    files = parse_patch(patch)
    if op == "drop_file":
        py = [i for i, f in enumerate(files) if f.path.endswith(".py")]
        if len(py) < 2:
            return None
        drop = rng.choice(py)
        kept = [f for i, f in enumerate(files) if i != drop]
        return render_patch(kept), Mutant(instance_id, op, files[drop].path, f"{len(files)} files", f"{len(kept)} files")

    sites = list(added_sites(files))
    rng.shuffle(sites)
    for fi, hi, li, code in sites:
        if op == "drop_line":
            if code.rstrip().endswith(":") or code.strip().startswith("@") or not balanced(code):
                continue  # dropping a block opener, decorator or partial statement is a syntax error, not a plausible bug
            hunk = files[fi].hunks[hi]
            files[fi].hunks[hi] = recount_hunk(hunk[:li] + hunk[li + 1:])
            return render_patch(files), Mutant(instance_id, op, files[fi].path, code.strip(), "<deleted>")
        new = line_mutation(op, code)
        if new is not None and new != code:
            files[fi].hunks[hi][li] = "+" + new
            return render_patch(files), Mutant(instance_id, op, files[fi].path, code.strip(), new.strip())
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tasks", required=True, help="tasks.jsonl")
    ap.add_argument("--task-file", help="Only these instance_ids (one per line)")
    ap.add_argument("--out", default="faults/patches")
    ap.add_argument("--operators", nargs="*", default=OPERATORS, choices=OPERATORS)
    ap.add_argument("--seed", type=int, default=20261023)
    args = ap.parse_args()

    keep = set(Path(args.task_file).read_text().split()) if args.task_file else None
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest = []
    for line in open(args.tasks, encoding="utf-8"):
        task = json.loads(line)
        if keep is not None and task["instance_id"] not in keep:
            continue
        for op in args.operators:
            rng = random.Random(f"{args.seed}:{task['instance_id']}:{op}")
            res = mutate(task["instance_id"], task["patch"], op, rng)
            if res is None:
                continue
            text, m = res
            (out / f"{task['instance_id']}__{op}.patch").write_text(text, encoding="utf-8")
            manifest.append(asdict(m))
    (out.parent / "manifest.jsonl").write_text("\n".join(json.dumps(m) for m in manifest) + "\n", encoding="utf-8")

    from collections import Counter
    per_op = Counter(m["operator"] for m in manifest)
    print(f"{len(manifest)} mutants from {len({m['instance_id'] for m in manifest})} tasks -> {out}")
    for op in args.operators:
        print(f"  {op:13} {per_op[op]}")


if __name__ == "__main__":
    main()
