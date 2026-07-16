# [BLUEPRINT] MOD-INF-005 | scripts/fix_freeze_manifest.py | §
# [MODULE] scripts.fix_freeze_manifest
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""Fix freezemanifest.yaml - comprehensive repair of all corrupted desc fields."""

from pathlib import Path

p = Path("src/zephyr/shared/contracts/freezemanifest.yaml")
text = p.read_text(encoding="utf-8")

# Replace all =>? with ⇒
text = text.replace("=>?", "⇒")

# Fix all desc lines with unclosed quotes
# Pattern: desc: "some text⇒more text⇒  (missing closing quote)
lines = text.split("\n")
fixed = []
for line in lines:
    stripped = line.strip()
    if stripped.startswith("desc:") and stripped.count('"') % 2 != 0:
        # Has unclosed quote - add closing quote
        line = line.rstrip() + '"'
    # Also fix note: lines with unclosed quotes
    if stripped.startswith("note:") and stripped.count('"') % 2 != 0:
        line = line.rstrip() + '"'
    # Fix lines in change_control that have unclosed quotes
    if stripped.startswith('- "') and stripped.count('"') % 2 != 0:
        line = line.rstrip() + '"'
    fixed.append(line)

text = "\n".join(fixed)

# Also fix any remaining broken patterns
text = text.replace("补参⇒", "补参⇒完成")
text = text.replace("所⇒consumer ⇒owner", "所有 consumer 的 owner")
text = text.replace("更新⇒freezemanifest.yaml", "更新 freezemanifest.yaml")

p.write_text(text, encoding="utf-8")

import yaml

try:
    d = yaml.safe_load(text)
    print(f"YAML OK, top keys: {list(d.keys())[:5]}")
except yaml.parser.ParserError as e:
    print(f"Still broken at line {e.problem_mark.line}: {e.problem}")
    # Show the problematic area
    bad_lines = text.split("\n")
    start = max(0, e.problem_mark.line - 3)
    end = min(len(bad_lines), e.problem_mark.line + 3)
    for i in range(start, end):
        marker = ">>>" if i == e.problem_mark.line - 1 else "   "
        print(f"{marker} {i + 1}: {bad_lines[i]}")
