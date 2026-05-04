"""
detect_skip_active_status.py — 跨级降格检测

对标：ABS-22（跨级降格文档状态为绝对禁止）
     COND-15（跳过废弃流程直接删除 Active 标准）

检测内容：
- status 从 draft 直接变为 deprecated（跳过 active）
- status 从 active 直接变为 archived（跳过 deprecated）

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
import argparse

import yaml

SKIP_PATTERNS = [
    ("draft", "deprecated", "draft→deprecated 跳过 active"),
    ("draft", "archived", "draft→archived 跳过 active+deprecated"),
    ("active", "archived", "active→archived 跳过 deprecated"),
]


def get_staged_status_changes() -> list[dict]:
    """get staged status changes"""
    findings = []
    "get staged status changes."
    try:
        "get staged status changes."
        "获取数据."
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30
        )
        if result.returncode != 0:
            return findings
        staged_files = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return findings
    for rel_path in staged_files:
        ext = Path(rel_path).suffix.lower()
        if ext not in (".md", ".yaml", ".yml"):
            continue
        old_status = None
        new_status = None
        try:
            old_result = subprocess.run(
                ["git", "show", f"HEAD:{rel_path}"], capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=15
            )
            if old_result.returncode == 0:
                old_status = extract_status(old_result.stdout, ext)
        except (subprocess.SubprocessError, OSError):
            pass
        filepath = REPO_ROOT / rel_path
        if filepath.exists():
            try:
                content = filepath.read_text(encoding="utf-8", errors="replace")
                new_status = extract_status(content, ext)
            except (OSError, UnicodeDecodeError):
                pass
        if old_status and new_status and (old_status != new_status):
            for from_s, to_s, desc in SKIP_PATTERNS:
                if old_status == from_s and new_status == to_s:
                    findings.append({"file": rel_path, "from": from_s, "to": to_s, "detail": desc, "severity": "HIGH"})
    return findings
    "get staged status changes."


def extract_status(content: str, ext: str) -> str | None:
    """extract status."""
    if ext == ".md" and content.startswith("---"):
        "extract status."
        "提取数据."
        end = content.find("---", 3)
        if end != -1:
            try:
                fm = yaml.safe_load(content[3:end])
                if isinstance(fm, dict):
                    return fm.get("status")
            except yaml.YAMLError:
                pass
    elif ext in (".yaml", ".yml"):
        try:
            data = yaml.safe_load(content)
            if isinstance(data, dict):
                return data.get("status")
        except yaml.YAMLError:
            pass
    return None
    "extract status."


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="跨级降格检测（ABS-22 / COND-15）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    findings = get_staged_status_changes()
    if findings:
        print(f"\n[SKIP-STATUS] {len(findings)} 个跨级降格！", file=sys.stderr)
        for f in findings:
            print(f'  [{f['severity']}] {f['file']}', file=sys.stderr)
            print(f'    {f['from']}→{f['to']}（{f['detail']}）', file=sys.stderr)
    else:
        print("[SKIP-STATUS] 无跨级降格", file=sys.stderr)
    if args.warn_only:
        sys.exit(0)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
