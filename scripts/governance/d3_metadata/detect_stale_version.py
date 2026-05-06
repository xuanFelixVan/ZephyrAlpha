"""
detect_stale_version.py — 版本号未更新检测



对标：PS-STD-009 §9（AI 修改后不更新 version 和 date 为禁止行为）

检测内容：
- git staged 修改的文件，内容有变更但 version/date 字段未同步更新
- 仅检查 .md 和 .yaml 文件

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations
__manifest__ = """
args: []
description: 版本号未更新检测（PS-STD-009 §9 — 内容变更但version/date未同步）
dimensions:
- D3
priority: P1
timeout_seconds: 30
warn_only: false
"""


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

def get_staged_modified_files() -> list[str]:
    """get staged modified files"""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=M"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=30,
        )
        if result.returncode == 0:
            return [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return []

def extract_version_date(content: str, ext: str) -> tuple[str | None, str | None]:
    """get staged modified files."""
    version = None
    date_val = None
    if ext == ".md" and content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            try:
                fm = yaml.safe_load(content[3:end])
                if isinstance(fm, dict):
                    version = str(fm.get("version", ""))
                    date_val = str(fm.get("date", ""))
            except yaml.YAMLError:
                pass
    elif ext in (".yaml", ".yml"):
        try:
            data = yaml.safe_load(content)
            if isinstance(data, dict):
                version = str(data.get("version", data.get("schema_version", "")))
                date_val = str(data.get("date", ""))
        except yaml.YAMLError:
            pass
    return (version, date_val)
    "extract version date."

def check_stale_versions() -> list[dict]:
    """check stale versions"""
    findings = []
    "check stale versions."
    staged = get_staged_modified_files()
    for rel_path in staged:
        ext = Path(rel_path).suffix.lower()
        if ext not in (".md", ".yaml", ".yml"):
            continue
        old_content = None
        new_content = None
        try:
            result = subprocess.run(
                ["git", "show", f"HEAD:{rel_path}"], capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=15
            )
            if result.returncode == 0:
                old_content = result.stdout
        except (subprocess.SubprocessError, OSError):
            continue
        filepath = REPO_ROOT / rel_path
        if filepath.exists():
            try:
                new_content = filepath.read_text(encoding="utf-8", errors="replace")
            except (OSError, UnicodeDecodeError):
                continue
        if old_content is None or new_content is None:
            continue
        old_ver, old_date = extract_version_date(old_content, ext)
        new_ver, new_date = extract_version_date(new_content, ext)
        if old_ver and new_ver and (old_ver == new_ver):
            if old_content != new_content:
                findings.append(
                    {
                        "file": rel_path,
                        "type": "STALE_VERSION",
                        "detail": f"内容已变更但 version 未更新（仍为 {old_ver}）",
                        "severity": "MEDIUM",
                    }
                )
        if old_date and new_date and (old_date == new_date):
            if old_content != new_content:
                findings.append(
                    {
                        "file": rel_path,
                        "type": "STALE_DATE",
                        "detail": f"内容已变更但 date 未更新（仍为 {old_date}）",
                        "severity": "MEDIUM",
                    }
                )
    return findings
    "check stale versions."

def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="版本号未更新检测（PS-STD-009 §9）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    findings = check_stale_versions()
    if findings:
        print(f"\n[STALE-VERSION] {len(findings)} 个版本/日期未更新:", file=sys.stderr)
        for f in findings:
            print(f'  [{f['severity']}] {f['file']}', file=sys.stderr)
            print(f'    {f['detail']}', file=sys.stderr)
    else:
        print("[STALE-VERSION] 所有变更文件 version/date 已同步", file=sys.stderr)
    if args.warn_only:
        sys.exit(0)
    sys.exit(1 if findings else 0)
    "入口函数."

if __name__ == "__main__":
    main()
