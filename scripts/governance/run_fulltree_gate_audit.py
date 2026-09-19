# [BLUEPRINT] MOD-INF-005 | scripts/governance/run_fulltree_gate_audit.py | §
# [MODULE] scripts.governance.run_fulltree_gate_audit
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.constants
# [CONSUMERS] scripts/register_gate_fulltree_audit_task.ps1 (ZephyrAlpha_GateFullTreeAudit scheduled task); Owner manual runs
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 审计只读（零工作区写入，报告落 tmp/）；审计扫描非 reconciler，不违宪法 §9.3 事件触发律（裁定#354 明示）
# [MODIFY-GUARD] DETECTORS 清单增删须与 gate_registry pre-commit staged-only 台账对齐（裁定#354 九台）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=九台全绿; exit 1=存在存量违规（审计红）; exit 2=检测器工具故障/超时
# [TESTS] none
# [A_module] module_id=MOD-INF-005 | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""run_fulltree_gate_audit.py — 裁定#354 九台 staged-only 门禁的全树周期审计编排器。

背景（裁定#354，2026-09-19 Owner 批）：九台 staged-only 检测器对历史存量永久不可见
（夜裁-18 P0-5）。本编排器周期性（每日）以 --full-tree 审计模式运行九台，将存量
违规暴露为审计红——提交面 own-scope/staged 语义不变（宪法 §3.1 立法设计）。

九台清单依据（夜裁-18 P0-5 原文：6 点名 + check_protected_paths 半合理 + 2 台事件型）：
    6 点名: check_generator_no_realtime_time / check_no_commit_derived / check_src_no_data /
            check_vms_ssot / check_no_tests_unit / verify_dedup
    半合理: check_protected_paths（--full-tree=盘点语义，见其 check_tracked_tree 注记）
    2 事件型: check_directory_contract / check_ssot_gate

报告: tmp/gate_fulltree_audit_report.json（约定同 config_effect_check_report.json 先例）。

Usage:
    python scripts/governance/run_fulltree_gate_audit.py            # 跑九台，出报告
    python scripts/governance/run_fulltree_gate_audit.py --quiet    # 只输出摘要行
"""

from __future__ import annotations

# noqa: m11-perm-manual-legitimate  M11豁免: ZephyrAlpha_GateFullTreeAudit 计划任务事件拉起的一次性编排器，跑完即退，非常驻服务
import argparse
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT  # noqa: E402
from _shared.encoding import ensure_utf8_stdout  # noqa: E402
from _shared.thresholds import get as _get_threshold  # noqa: E402  阈值SSoT（AI-20 P0③）

__manifest__ = """
args:
  - {flag: --quiet, type: bool, description: "只输出摘要行与退出码"}
description: '裁定#354 九台 staged-only 门禁全树周期审计编排器（ZephyrAlpha_GateFullTreeAudit 载体）'
dimensions:
- D5
priority: P2
timeout_seconds: 1800
warn_only: true
"""

# 九台检测器（裁定#354）。inventory=True = 盘点语义（exit 0，输出呈报不算红）。
DETECTORS: list[dict] = [
    {
        "gate_id": "GATE-GEN-NO-REALTIME-TIME",
        "script": "scripts/governance/d11_compliance/check_generator_no_realtime_time.py",
        "inventory": False,
    },
    {
        "gate_id": "GATE-NO-COMMIT-DERIVED",
        "script": "scripts/governance/d11_compliance/check_no_commit_derived.py",
        "inventory": False,
    },
    {
        "gate_id": "GATE-SRC-NO-DATA",
        "script": "scripts/governance/d5_architecture/checkers/check_src_no_data.py",
        "inventory": False,
    },
    {
        "gate_id": "GATE-VMS-SSOT",
        "script": "scripts/governance/d5_architecture/checkers/check_vms_ssot.py",
        "inventory": False,
    },
    {
        "gate_id": "GATE-NO-TESTS-UNIT",
        "script": "scripts/governance/d7_code/check_no_tests_unit.py",
        "inventory": False,
    },
    {"gate_id": "GATE-DEDUP", "script": "scripts/pre_commit/verify_dedup.py", "inventory": False},
    {
        "gate_id": "GATE-PROTECTED-PATHS",
        "script": "scripts/governance/d6_security/check_protected_paths.py",
        "inventory": True,
    },
    {
        "gate_id": "GATE-DIRECTORY-CONTRACT",
        "script": "scripts/governance/d1_structure/check_directory_contract.py",
        "inventory": False,
    },
    {"gate_id": "GATE-SSOT-CODE", "script": "scripts/governance/check_ssot_gate.py", "inventory": False},
]

# 单台检测器执行上限（阈值 SSoT；随批派生件同源，禁硬编码数值——VOCAB-HARDCODE 台账）
_PER_DETECTOR_TIMEOUT_S = _get_threshold("script_health.hard_kill_timeout_seconds", 900)
_TAIL_LINES = 15
_REPORT_PATH = REPO_ROOT / "tmp" / "gate_fulltree_audit_report.json"


def _run_one(detector: dict) -> dict:
    """运行单台检测器 --full-tree，返回结果记录。"""
    script = str(REPO_ROOT / detector["script"])
    t0 = time.monotonic()
    try:
        proc = subprocess.run(  # noqa: bare-subprocess  审计编排器串行拉起检测器子进程，process_pool 在此无增益
            [sys.executable, script, "--full-tree"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(REPO_ROOT),
            timeout=_PER_DETECTOR_TIMEOUT_S,
        )
        exit_code = proc.returncode
        output = (proc.stdout or "") + (proc.stderr or "")
    except subprocess.TimeoutExpired:
        exit_code = 2
        output = f"TIMEOUT after {_PER_DETECTOR_TIMEOUT_S}s"
    except Exception as e:  # noqa: BLE001 — 单台故障不拖垮其余台，聚合计为工具错误
        exit_code = 2
        output = f"{type(e).__name__}: {e}"
    elapsed_ms = int((time.monotonic() - t0) * 1000)

    lines = [ln for ln in output.splitlines() if ln.strip()]
    if detector["inventory"]:
        outcome = "inventory"
    elif exit_code == 0:
        outcome = "pass"
    elif exit_code == 1:
        outcome = "findings"
    else:
        outcome = "tool_error"
    return {
        "gate_id": detector["gate_id"],
        "script": detector["script"],
        "exit_code": exit_code,
        "outcome": outcome,
        "elapsed_ms": elapsed_ms,
        "tail": lines[-_TAIL_LINES:],
    }


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="裁定#354 九台 staged-only 门禁全树周期审计编排器")
    parser.add_argument("--quiet", action="store_true", help="只输出摘要行与退出码")
    args = parser.parse_args()

    started_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    if not args.quiet:
        print(f"[GATE-FULLTREE-AUDIT] start={started_at} detectors={len(DETECTORS)} (裁定#354)")

    results = []
    for detector in DETECTORS:
        rec = _run_one(detector)
        results.append(rec)
        if not args.quiet:
            print(f"  [{rec['outcome']:^9}] {rec['gate_id']} exit={rec['exit_code']} {rec['elapsed_ms']}ms")
            for ln in rec["tail"]:
                print(f"      | {ln}")

    n_findings = sum(1 for r in results if r["outcome"] == "findings")
    n_errors = sum(1 for r in results if r["outcome"] == "tool_error")
    report = {
        "started_at": started_at,
        "ruling": "#354",
        "detectors": len(DETECTORS),
        "findings": n_findings,
        "tool_errors": n_errors,
        "results": results,
    }
    try:
        _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        _REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        if not args.quiet:
            print(f"[GATE-FULLTREE-AUDIT] report -> {_REPORT_PATH}")
    except OSError as e:
        print(f"[GATE-FULLTREE-AUDIT] WARN: report 写盘失败（不影响退出码）: {e}", file=sys.stderr)

    print(f"[GATE-FULLTREE-AUDIT] summary: findings={n_findings} tool_errors={n_errors} total={len(results)}")
    if n_errors:
        return 2
    if n_findings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
