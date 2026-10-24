#!/usr/bin/env bash
# Publish the committed code as a new version of the private Kaggle dataset manoharpapasani/g4swe-code.
# The L4 x4 GPU notebooks are offline and unpack our code from this dataset, so run this after any commit
# that changes src/, scripts/, agents/ or the experiment task lists. Needs KAGGLE_API_TOKEN (from .env).
#
#   bash scripts/publish_code_dataset.sh "message"
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] && set -a && . ./.env && set +a
msg="${1:-code $(git rev-parse --short HEAD)}"
if ! git diff --quiet HEAD -- src scripts agents experiments/*.txt; then
  echo "Uncommitted changes in src/, scripts/, agents/ or task lists; commit first." >&2; exit 1
fi
out="$(mktemp -d)"
git archive --format=tar HEAD src scripts agents experiments/*.txt | gzip > "$out/g4swe-code.tgz"
cat > "$out/dataset-metadata.json" <<JSON
{"title": "g4swe code", "id": "manoharpapasani/g4swe-code", "licenses": [{"name": "apache-2.0"}]}
JSON
kaggle_bin="$(command -v kaggle || echo .venv/Scripts/kaggle)"
(cd "$out" && "$OLDPWD/$kaggle_bin" datasets version -p . -m "$msg ($(git -C "$OLDPWD" rev-parse --short HEAD))" 2>&1 | grep -v outdated)
rm -rf "$out"
