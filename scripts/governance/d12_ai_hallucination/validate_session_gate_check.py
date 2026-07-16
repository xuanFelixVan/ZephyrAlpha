# [BLUEPRINT] MOD-INF-005 | scripts/governance/d12_ai_hallucination/validate_session_gate_check.py | §
# [MODULE] scripts.governance.d12_ai_hallucination.validate_session_gate_check
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
validate_session_gate_check.py — Session 门禁检查完整性校验



对标：OPS-VC-005 §3（Session Log 中必须有 gate_check 记录）

检测内容：
- 检查最新 Session Log 中是否有 gate_check YAML 块
- 检查 12 项 gate_check 是否完整

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: Session 门禁检查完整性校验（OPS-VC-005 §3 — 12项gate_check）
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
from _shared.constants import EXIT_ERROR, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
import argparse

import yaml

GATE_CHECK_ITEMS = {
    "A1_phase_read",
    "A2_blueprint_read",
    "A3_ssot_read",
    "B1_behavior_boundary",
    "B2_hallucination_check",
    "B3_budget_confirmed",
    "B4_dual_editor",
    "C1_encoding_safety",
    "C2_file_safety",
    "C3_secret_management",
    "D1_environment",
    "D2_permission_mode",
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


def main() -> None:
    """入口函数"""
    parser = argparse.ArgumentParser(description="Session 门禁检查完整性校验（OPS-VC-005 §3）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    log_path = find_latest_session_log()
    if not log_path:
        print("[GATE-CHECK] 未找到 Session Log，跳过", file=sys.stderr)
        sys.exit(EXIT_PASS)
    try:
        content = log_path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        print("[GATE-CHECK] 无法读取 Session Log", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    findings = []
    gate_match = re.search("```yaml\\s*\\n(gate_check:.*?)```", content, re.DOTALL)
    if not gate_match:
        findings.append(
            {"type": "MISSING_GATE_CHECK", "detail": "Session Log 中无 gate_check YAML 块", "severity": "MEDIUM"}
        )
    else:
        try:
            gate_data = yaml.safe_load(gate_match.group(1))
            if isinstance(gate_data, dict) and "gate_check" in gate_data:
                checks = gate_data["gate_check"]
                if isinstance(checks, dict):
                    for item in GATE_CHECK_ITEMS:
                        if item not in checks:
                            findings.append(
                                {"type": "MISSING_ITEM", "detail": f"gate_check 缺少项: {item}", "severity": "LOW"}
                            )
        except yaml.YAMLError:
            findings.append({"type": "PARSE_ERROR", "detail": "gate_check YAML 解析失败", "severity": "MEDIUM"})
    if findings:
        print(f"\n[GATE-CHECK] {len(findings)} 个门禁检查问题（{log_path.name}）:", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] {f['detail']}", file=sys.stderr)
    else:
        print(f"[GATE-CHECK] 门禁检查完整（{log_path.name}）", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(1 if findings else 0)
    "入口函数."


if __name__ == "__main__":
    main()
