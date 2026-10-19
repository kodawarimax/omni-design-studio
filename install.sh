#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Installing omni-design-studio for Codex, Claude Code & Antigravity ==="

# 1. Codex registration
mkdir -p "$HOME/.codex/skills" "$HOME/.codex/prompts"
ln -sfn "$SKILL_DIR" "$HOME/.codex/skills/omni-design-studio"
cp -f "$SKILL_DIR/prompts/omni-design-studio.md" "$HOME/.codex/prompts/omni-design-studio.md"
echo "  ✔ Codex: ~/.codex/skills/omni-design-studio & ~/.codex/prompts/omni-design-studio.md"

# 2. Claude Code registration
mkdir -p "$HOME/.claude/skills" "$HOME/.claude/commands"
ln -sfn "$SKILL_DIR" "$HOME/.claude/skills/omni-design-studio"
cp -f "$SKILL_DIR/commands/omni-design-studio.md" "$HOME/.claude/commands/omni-design-studio.md"
echo "  ✔ Claude Code: ~/.claude/skills/omni-design-studio & ~/.claude/commands/omni-design-studio.md (/omni-design-studio)"

echo "=== Done! Use '\$omni-design-studio' in Codex or '/omni-design-studio' in Claude Code ==="
