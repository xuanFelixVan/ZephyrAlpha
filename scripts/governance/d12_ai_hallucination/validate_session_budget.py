# [BLUEPRINT] MOD-INF-005 | scripts/governance/d12_ai_hallucination/validate_session_budget.py | §
# [MODULE] scripts.governance.d12_ai_hallucination.validate_session_budget
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d12_ai_hallucination.__init__
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
# [TTL] permanent
"""
validate_session_budget.py — Session 操作预算校验（已废弃）



GOV-AI-005 已于 2026-05-04 删除。本脚本保留以供 reference，不再作为审计门禁使用。

检测内容：
- 解析最新 Session Log 统计操作数量
- 检查新建文件数 <= 5
- 检查处理文件数 <= 20
- 检查 context_budget_used 字段

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: Session 操作预算校验（已废弃——GOV-AI-005 已删除）
dimensions:
- D12
priority: P2
timeout_seconds: 30
warn_only: false
"""


import re
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

BUDGET_LIMITS = {  # noqa: gate-vocab  治本(ARCH-036 P3-A5): 会话预算限额，业务逻辑非系统阈值
    "new_files": 5,
    "processed_files": 20,
    "blueprints": 10,
    "new_modules": 5,
    "deep_reads": 20,
    "knowledge_entries": 10,
}


def find_latest_session_log() -> Path | None:
    """查找最新会话日志"""
    log_dirs = [
        REPO_ROOT / "" / "docs" / "_working" / "audit" / "session_logs",
        REPO_ROOT / "docs" / "_working" / "audit" / "session_logs",
        REPO_ROOT / "session_logs",
    ]
    for log_dir in log_dirs:
        if not log_dir.exists():
            continue
        logs = sorted(log_dir.glob("session-*.md"), reverse=True)
        if logs:
            return logs[0]
    return None
    "查找最新会话日志."


def parse_session_log(filepath: Path) -> dict:
    """parse session log"""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return {}
    stats = {}
    stats["new_files"] = len(re.findall("(?:新建|创建|created?|new)\\s+(?:文件|file)", content, re.IGNORECASE))
    stats["processed_files"] = len(re.findall("(?:修改|编辑|modifi|edit|update)", content, re.IGNORECASE))
    stats["blueprints"] = len(re.findall("(?:蓝图|blueprint)", content, re.IGNORECASE))
    stats["new_modules"] = len(re.findall("(?:新增模块|new module)", content, re.IGNORECASE))
    stats["deep_reads"] = len(re.findall("(?:精读|deep read|read)", content, re.IGNORECASE))
    stats["knowledge_entries"] = len(re.findall("(?:知识条目|knowledge entry)", content, re.IGNORECASE))
    stats["has_context_budget"] = "context_budget_used" in content
    return stats
    "parse session log."


def main() -> None:
    """入口函数"""
    parser = argparse.ArgumentParser(description="Session 操作预算校验（已废弃——GOV-AI-005 于 2026-05-04 删除）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    log_path = find_latest_session_log()
    if not log_path:
        print("[SESSION-BUDGET] 未找到 Session Log，跳过", file=sys.stderr)
        sys.exit(EXIT_PASS)
    stats = parse_session_log(log_path)
    findings = []
    for key, limit in BUDGET_LIMITS.items():
        count = stats.get(key, 0)
        if count > limit:
            findings.append({"metric": key, "count": count, "limit": limit, "severity": "MEDIUM"})
    if not stats.get("has_context_budget", False):
        findings.append({"metric": "context_budget_used", "count": 0, "limit": 1, "severity": "LOW"})
    if findings:
        print(f"\n[SESSION-BUDGET] {len(findings)} 个预算违规（Session: {log_path.name}）:", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] {f['metric']}: {f['count']} > {f['limit']}", file=sys.stderr)
    else:
        print(f"[SESSION-BUDGET] Session 预算合规（{log_path.name}）", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)
    "入口函数."


if __name__ == "__main__":
    main()
