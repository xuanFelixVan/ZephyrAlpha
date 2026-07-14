# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/detect_permanent_file_deletion.py | §
# [MODULE] scripts.governance.d6_security.detect_permanent_file_deletion
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d6_security.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""
detect_permanent_file_deletion.py — 永久文件删除检测



对标：PS-STD-012 V1（删除 ttl:permanent 文件为 V1 阻断级违规）
     PS-STD-009 §7（ttl:permanent 永久保留，不删除）

检测内容：
- git staged/working 删除操作中被删文件的 frontmatter 含 ttl: permanent
- ttl: permanent 文件是项目永久资产，删除不可逆

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 永久文件删除检测（PS-STD-012 V1 / PS-STD-009 §7 — ttl:permanent禁止删除）
dimensions:
- D6
priority: P0
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
from _shared.constants import EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
import argparse


def get_deleted_files() -> list[str]:
    """获取已删除文件列表"""
    deleted = []
    for flag in ["--cached", ""]:
        try:
            cmd = ["git", "diff"]
            if flag:
                cmd.append(flag)
            cmd.extend(["--name-only", "--diff-filter=D"])
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30)
            if result.returncode == 0:
                deleted.extend(line.strip() for line in result.stdout.strip().split("\n") if line.strip())
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
    return list(set(deleted))


def get_file_content_at_head(rel_path: str) -> str | None:
    """获取已删除文件列表."""
    try:
        result = subprocess.run(
            ["git", "show", f"HEAD:{rel_path}"], capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=15
        )
        if result.returncode == 0:
            return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None
    "获取 HEAD 版本文件内容."


def check_permanent_deletions() -> list[dict]:
    """检查永久文件删除"""
    findings = []
    deleted = get_deleted_files()
    for rel_path in deleted:
        ext = Path(rel_path).suffix.lower()
        if ext not in (".md", ".yaml", ".yml"):
            continue
        content = get_file_content_at_head(rel_path)
        if content is None:
            continue
        if ext in (".yaml", ".yml"):
            import yaml

            try:
                data = yaml.safe_load(content)
                if isinstance(data, dict) and data.get("ttl") == "permanent":
                    findings.append({"file": rel_path, "ttl": "permanent", "severity": "CRITICAL"})
            except yaml.YAMLError:
                pass
        elif ext == ".md":
            fm = None
            if content.startswith("---"):
                end = content.find("---", 3)
                if end != -1:
                    import yaml

                    try:
                        fm = yaml.safe_load(content[3:end])
                    except yaml.YAMLError:
                        pass
            if isinstance(fm, dict) and fm.get("ttl") == "permanent":
                findings.append({"file": rel_path, "ttl": "permanent", "severity": "CRITICAL"})
    return findings
    "检查永久文件删除."


def main() -> None:
    """入口函数"""
    parser = argparse.ArgumentParser(description="永久文件删除检测（PS-STD-012 V1 / PS-STD-009 §7）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    findings = check_permanent_deletions()
    if findings:
        print(f"\n[PERM-DELETE] {len(findings)} 个 ttl:permanent 文件正在被删除！", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] {f['file']}", file=sys.stderr)
            print(f"    ttl={f['ttl']} — 永久保留文件禁止删除", file=sys.stderr)
    else:
        print("[PERM-DELETE] 无永久文件删除操作", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)
    "入口函数."


if __name__ == "__main__":
    main()
