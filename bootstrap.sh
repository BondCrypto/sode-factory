#!/usr/bin/env bash
# sode-factory bootstrap — run ONCE per machine after `git clone`, from the repo root.
#
# What it does (idempotent; safe to re-run):
#   1. Links the Claude Code harness memory directory for THIS folder to the repo's own `memory/`, so the
#      advisor's memory is version-controlled and a fresh clone starts with the full NOW anchor.
#      Claude Code resolves memory at ~/.claude/projects/<cwd with "/" replaced by "-">/memory/.
#      If the harness already created a real directory there with content, its files are MERGED into
#      `memory/` (never deleted) before the link is made.
#   2. Verifies the repo carries the advisor entry point (CLAUDE.md · role prompt · memory index · NOW anchor).
#   3. Prints the exact next step: open Claude Code here and paste the role prompt.
#
# It installs nothing, needs no network, and touches only ~/.claude/projects/<this folder>/memory.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

fail() { echo "bootstrap: FAIL — $*" >&2; exit 1; }
ok()   { echo "bootstrap: ok   — $*"; }

# 1. Entry-point files must exist (the repo is the source of truth for all of them).
for f in CLAUDE.md docs/references/sode_advisor_role_prompt.md memory/MEMORY.md memory/current_state.md \
         docs/design/sode_factory_architecture.md docs/design/sode_factory_build_sessions.md; do
  [[ -f "$f" ]] || fail "missing $f (clone incomplete?)"
done
ok "entry point present (CLAUDE.md · role prompt · memory index · NOW anchor · spec set)"

# 2. Harness memory link.
HARNESS_KEY="$(printf '%s' "$ROOT" | sed 's#/#-#g')"
HARNESS_DIR="$HOME/.claude/projects/$HARNESS_KEY"
TARGET="$HARNESS_DIR/memory"
mkdir -p "$HARNESS_DIR"

if [[ -L "$TARGET" ]]; then
  if [[ "$(readlink "$TARGET")" == "$ROOT/memory" ]]; then
    ok "harness memory already linked → $ROOT/memory"
  else
    ln -sfn "$ROOT/memory" "$TARGET"
    ok "harness memory re-pointed → $ROOT/memory (was: $(readlink "$TARGET"))"
  fi
elif [[ -d "$TARGET" ]]; then
  # A real directory: merge its files into the repo memory (no overwrite of repo files), then replace with a link.
  merged=0
  shopt -s nullglob dotglob
  for f in "$TARGET"/*; do
    base="$(basename "$f")"
    if [[ ! -e "$ROOT/memory/$base" ]]; then
      mv "$f" "$ROOT/memory/$base"; merged=$((merged+1))
    else
      mv "$f" "$ROOT/memory/${base%.md}.harness-copy.md" 2>/dev/null || mv "$f" "$ROOT/memory/$base.harness-copy"
      merged=$((merged+1))
    fi
  done
  shopt -u nullglob dotglob
  rmdir "$TARGET"
  ln -sfn "$ROOT/memory" "$TARGET"
  ok "harness memory had $merged file(s); merged into $ROOT/memory (review any *.harness-copy*), then linked"
else
  ln -sfn "$ROOT/memory" "$TARGET"
  ok "harness memory linked → $ROOT/memory"
fi

# 3. Verify the link resolves to the NOW anchor.
[[ -f "$TARGET/current_state.md" ]] || fail "link made but $TARGET/current_state.md not readable"
ok "verified: $TARGET/current_state.md resolves"

cat <<EOF

bootstrap: DONE.
Next:
  1. Open Claude Code in this folder:  $ROOT
  2. Paste the role prompt (everything below its "PASTE BELOW THIS LINE" marker):
       docs/references/sode_advisor_role_prompt.md
  3. Say: start S1
Re-run this script any time; it only re-checks and re-links.
EOF
