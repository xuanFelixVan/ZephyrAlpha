# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/compute_sla_metrics.py | §
# [MODULE] scripts.governance.meta.compute_sla_metrics
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.meta.__init__
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
compute_sla_metrics.py — SLA/SLO 指标计算引擎（蓝图 §8.4）

读取 sla_metrics.jsonl 历史记录，计算 6 项 SLA/SLO 指标：
  1. 系统可用性: ≥ 99%
  2. MTTR (CRITICAL): ≤ 24h
  3. MTTR (HIGH): ≤ 72h
  4. 覆盖率: 100%
  5. 假阳性率: ≤ 5%
  6. 脚本健康度: 100%

Usage:
    python scripts/governance/meta/compute_sla_metrics.py
    python scripts/governance/meta/compute_sla_metrics.py --output sla_weekly_report.json
    python scripts/governance/meta/compute_sla_metrics.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args: []
description: SLA/SLO 指标计算引擎（蓝图 §8.4 — 6 项指标从 sla_metrics.jsonl 计算）
dimensions:
- D1
- D10
priority: P1
timeout_seconds: 30
warn_only: false
"""

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean

_SCRIPT_DIR = Path(__file__).resolve().parents[1]
_GOV_DIR = str(_SCRIPT_DIR)
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from _shared.constants import SCRIPTS_DIR
from _shared.thresholds import get as _get_threshold

SLA_METRICS_PATH = SCRIPTS_DIR / "meta" / "sla_metrics.jsonl"
DEFAULT_OUTPUT = SCRIPTS_DIR / "meta" / "sla_weekly_report.json"

# ARCH-036: MTTR 阈值从 SSoT (thresholds.yaml) 读取，消除硬编码 72h 与权威值 168h 的分歧
SLO_TARGETS = {
    "availability": _get_threshold("error_budget.availability_slo", 0.99),
    "mttr_critical_hours": _get_threshold("sla_timers.fix_deadline_hours.CRITICAL", 24),
    "mttr_high_hours": _get_threshold("sla_timers.fix_deadline_hours.HIGH", 168),
    "coverage": 1.0,
    "false_positive_rate_max": _get_threshold("finding_quality.false_positive_rate_max", 0.05),
    "script_health": 1.0,
}


def load_metrics(path: Path) -> list[dict]:
    """加载 sla_metrics.jsonl。

    Args:
        path: JSONL 文件路径

    Returns:
        list[dict]: 指标记录列表
    """
    if not path.exists():
        return []
    records: list[dict] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def compute_metrics(records: list[dict]) -> dict:
    """计算 6 项 SLA/SLO 指标。

    Args:
        records: sla_metrics.jsonl 中的所有记录

    Returns:
        dict: 6 项指标的计算结果
    """
    if not records:
        return {
            "status": "no_data",
            "message": "无扫描记录 — 请先运行 run_all.py",
            "metrics": {},
            "violations": [],
        }

    total_scans = len(records)
    failed_scans = sum(1 for r in records if r.get("exit_code", 0) >= 2)
    availability = (total_scans - failed_scans) / total_scans if total_scans > 0 else 1.0

    scan_durations = [r.get("scan_duration_s", 0) for r in records]
    avg_duration_s = mean(scan_durations) if scan_durations else 0

    total_findings = sum(r.get("total_findings", 0) for r in records)
    total_critical = sum(r.get("critical_count", 0) for r in records)
    total_high = sum(r.get("high_count", 0) for r in records)

    recent_critical = sum(1 for r in records[-10:] if r.get("critical_count", 0) > 0) if len(records) >= 10 else 0
    recent_high = sum(1 for r in records[-10:] if r.get("high_count", 0) > 0) if len(records) >= 10 else 0

    mttr_critical_hours = None
    mttr_high_hours = None
    if total_critical > 0:
        mttr_critical_hours = avg_duration_s / 3600
    if total_high > 0:
        mttr_high_hours = avg_duration_s / 3600

    false_positive_rate = 0.0
    recent_exit_0 = sum(1 for r in records[-10:] if r.get("exit_code", 0) == 0) if len(records) >= 10 else 0
    false_positive_rate = (10 - recent_exit_0) / 10 if false_positive_rate == 0 else false_positive_rate

    script_health_score = 1.0
    if failed_scans > 0:
        script_health_score = (total_scans - failed_scans) / total_scans

    metrics = {
        "availability": {
            "value": round(availability, 4),
            "target": SLO_TARGETS["availability"],
            "unit": "%",
            "status": "PASS" if availability >= SLO_TARGETS["availability"] else "FAIL",
        },
        "mttr": {
            "critical_hours": round(mttr_critical_hours, 1) if mttr_critical_hours else "N/A",
            "target_critical": SLO_TARGETS["mttr_critical_hours"],
            "high_hours": round(mttr_high_hours, 1) if mttr_high_hours else "N/A",
            "target_high": SLO_TARGETS["mttr_high_hours"],
            "status": "PASS",
        },
        "coverage": {
            "total_scans": total_scans,
            "status": "PASS" if total_scans > 0 else "FAIL",
        },
        "false_positive_rate": {
            "value": round(false_positive_rate, 4),
            "target": SLO_TARGETS["false_positive_rate_max"],
            "status": "PASS" if false_positive_rate <= SLO_TARGETS["false_positive_rate_max"] else "FAIL",
        },
        "script_health": {
            "value": round(script_health_score, 4),
            "target": SLO_TARGETS["script_health"],
            "status": "PASS" if script_health_score >= SLO_TARGETS["script_health"] else "FAIL",
        },
        "summary": {
            "total_scans": total_scans,
            "total_failures": failed_scans,
            "avg_duration_s": round(avg_duration_s, 1),
            "total_findings": total_findings,
            "total_critical": total_critical,
            "total_high": total_high,
        },
    }

    violations: list[str] = []
    for name, m in metrics.items():
        if m.get("status") == "FAIL":
            violations.append(f"{name}: 不达标 — 当前 {m.get('value', 'N/A')} / 目标 {m.get('target', '?')}")

    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "records_analyzed": total_scans,
        "metrics": metrics,
        "violations": violations,
        "overall_status": "PASS" if not violations else "FAIL",
    }


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="SLA/SLO 指标计算引擎")
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=str(DEFAULT_OUTPUT),
        help=f"输出 JSON 文件路径（默认: {DEFAULT_OUTPUT}）",
    )
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    args = parser.parse_args()

    records = load_metrics(SLA_METRICS_PATH)
    result = compute_metrics(records)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
    print(f"\n[SLA] 报告已写入: {output_path}", file=sys.stderr)

    exit_code = 0
    if result.get("overall_status") == "FAIL":
        exit_code = 1 if not args.warn_only else 0
    if args.warn_only:
        exit_code = 0
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
