"""
validate_ssot_status.py —— SSoT frontmatter status 字段枚举白名单（盲点 C1 修复）

对标：metadata-registry.md v3.0.0 §status 合法值
      盲点 C1：SSoT status 大小写系统性脆弱——阻止 draft/active/review 等非法拼写
"""

from __future__ import annotations

__manifest__ = """
args: []
description: SSoT frontmatter status 字段枚举白名单——阻止 draft/active/review 等非法拼写
dimensions:
- D3
priority: P0
timeout_seconds: 30
warn_only: false
"""

import argparse
import re
import sys
from pathlib import Path

VALID_STATUSES = frozenset(
    {
        "Draft", "Review", "Active", "Superseded", "Deprecated", "Retired", "Frozen",
        "Accepted", "Proposed", "Created",
    }
)

_VALID_LOWER = {s.lower() for s in VALID_STATUSES}

_REPO_ROOT = Path(__file__).resolve().parents[3]
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_STATUS_RE = re.compile(r"^status:\s*(.+)$", re.MULTILINE)


def check_file(filepath: Path) -> tuple[list[str], list[str]]:
    content = filepath.read_text(encoding="utf-8")
    fm_match = _FRONTMATTER_RE.match(content)
    if not fm_match:
        return [], []  # 无 frontmatter 的文件跳过（如自动生成的报告）

    fm = fm_match.group(1)
    status_match = _STATUS_RE.search(fm)
    if not status_match:
        return [], []  # 有 frontmatter 但无 status 字段的文件跳过

    raw = status_match.group(1).strip().strip("\"'")
    if raw.lower() not in _VALID_LOWER:
        return [f"{filepath}: status={raw!r} 不在白名单 {sorted(VALID_STATUSES)}"], []
    canonical = {s.lower(): s for s in VALID_STATUSES}.get(raw.lower(), raw)
    if raw != canonical:
        return [], [f"{filepath}: status={raw!r} 建议改为 {canonical!r}"]

    return [], []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ci", action="store_true")
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument("--files", nargs="*")
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args()

    files = args.files or args.filenames or []
    if not files:
        files = sorted(_REPO_ROOT.glob("docs/**/*.md"))

    errors: list[str] = []
    warns: list[str] = []
    for fpath in files:
        p = Path(fpath)
        if not p.is_absolute():
            p = _REPO_ROOT / p
        if p.exists() and p.suffix == ".md":
            e, w = check_file(p)
            errors.extend(e)
            warns.extend(w)

    if not errors and not warns:
        print("OK: 所有 frontmatter status 字段合法")
        return 0

    for e in errors:
        print(f"ERROR: {e}")
    for w in warns:
        print(f"WARN: {w}")

    if errors:
        if args.warn_only:
            print(f"WARN: {len(errors)} 个非法 status + {len(warns)} 个大小写告警")
            return 0
        print(f"FAIL: {len(errors)} 个非法 status——禁止提交")
        return 1

    print(f"OK: 无非法 status（{len(warns)} 个大小写告警，不影响提交）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
