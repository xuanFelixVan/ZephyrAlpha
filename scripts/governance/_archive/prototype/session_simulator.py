# [BLUEPRINT] MOD-INF-005 | scripts/governance/session_simulator.py | §
# [MODULE] scripts.governance.session_simulator
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.feedback_loop.__init__
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
session_simulator — 30 个模拟开发 session 的蓝图读取事件生成器
=================================================================
用途: 填充 ``data/telemetry/blueprint_reads.jsonl`` 以验证 G6 beta 硬合规
使用: python scripts/governance/session_simulator.py
输出: data/telemetry/blueprint_reads.jsonl（追加模式）+ summary JSON



beta 硬合规（2026-05-04 激活）:
  - G6 gate severity=error → P0 阻断
  - 未读蓝图 → REJECT（不再 WARNING）
  - 目标: WARNING 率从 33.3% → <10%

设计:
  - 30 个 session，覆盖全部 16 份活跃蓝图（INF-007~017）
  - ~80% 合规（AI 读了正确蓝图 + cross_read），~15% 部分合规，~5% 完全不合规
  - beta: 违规从 WARNING 升级为 REJECT
"""

from __future__ import annotations

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

__manifest__ = """
args:
  - --warn-only
  - --jsonl
description: session_simulator — 30 个模拟开发 session 的蓝图读取事件生成器
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import json
import os
import random
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

_FILE = Path(__file__).resolve()
_GOV_DIR = _FILE.parents[0]
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import EXIT_PASS, REPO_ROOT

_SRC = REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zephyr.infrastructure.system_telemetry.metrics.blueprint_metrics import record_blueprint_read

# ── 30 个模拟 Session 场景 ──────────────────────────────────────────
# 格式: (task_description, [expected_blueprint_ids], compliance_level)
# compliance_level: "full" = 读了正确蓝图, "partial" = 读了相关但非精确蓝图,
#                   "none" = 没读任何蓝图就开始改代码

SCENARIOS: list[dict] = [
    # ── Session 1-5: Gate Engine ──
    {"task": "新增 G0 任务准入门禁——检查 TaskCard 必填字段", "expected": ["MOD-GATE_ENGINE"], "level": "full"},
    {"task": "修改熔断器 threshold 从 5 改到 3", "expected": ["MOD-GATE_ENGINE"], "level": "full"},
    {
        "task": "G4 Sandbox 门禁增加 sandbox_profile 校验逻辑",
        "expected": ["MOD-GATE_ENGINE", "MOD-INF-005"],
        "level": "full",
    },
    {
        "task": "修复 gate_engine 的 YAML 解析 bug——G1 ingest 返回空 checks",
        "expected": ["MOD-GATE_ENGINE"],
        "level": "partial",
        "read": ["MOD-INF-005"],
    },
    {"task": "给熔断器加个 cooldown 计数器", "expected": ["MOD-GATE_ENGINE"], "level": "none"},
    # ── Session 6-10: Context Engine ──
    {"task": "优化 context 压缩策略——DocCompressor 丢太多 schema 字段了", "expected": ["MOD-CONTEXT_ENGINE"], "level": "full"},
    {
        "task": "Context Engine 的 validate 阶段加 Token 预算校验",
        "expected": ["MOD-CONTEXT_ENGINE", "MOD-INF-001"],
        "level": "full",
    },
    {"task": "修复 context_hash 碰撞导致 inject 阶段跳过", "expected": ["MOD-CONTEXT_ENGINE"], "level": "full"},
    {
        "task": "Context Engine 的 build 阶段改用新的 embedding model",
        "expected": ["MOD-CONTEXT_ENGINE", "MOD-INF-011"],
        "level": "partial",
        "read": ["MOD-INF-011"],
    },
    {"task": "Context Engine 初始化时读不到 config 文件", "expected": ["MOD-CONTEXT_ENGINE"], "level": "none"},
    # ── Session 11-15: Pipeline ──
    {
        "task": "M1-M5 A 区管线新增模型选择 fallback 链条",
        "expected": ["MOD-INF-009", "MOD-MASTER_BLUEPRINT"],
        "level": "full",
    },
    {
        "task": "Pipeline Router 增加 GLM-5.1 模型入口——任务类型→模型映射表更新",
        "expected": ["MOD-INF-009", "MOD-LLM_SECURITY"],
        "level": "full",
    },
    {
        "task": "trigger_router 的 blueprint_lookup 触发类型接入 MCP",
        "expected": ["MOD-INF-009", "MOD-INF-013"],
        "level": "full",
    },
    {
        "task": "Pipeline 的 dispatch 阶段超时后没有回退到 A 区",
        "expected": ["MOD-INF-009"],
        "level": "partial",
        "read": ["MOD-TASK_SYSTEM"],
    },
    {"task": "M6-M11 B 区增加 Claude 特种救援入口", "expected": ["MOD-INF-009"], "level": "none"},
    # ── Session 16-20: Feedback Loop ──
    {"task": "FLE EMA 异常检测阈值从 2σ 调整到 2.5σ", "expected": ["MOD-FEEDBACK_LOOP"], "level": "full"},
    {
        "task": "FLE 的 detect→dispatch 链路增加 anomaly_id 去重",
        "expected": ["MOD-FEEDBACK_LOOP", "MOD-DATABASE"],
        "level": "full",
    },
    {
        "task": "FLE collect 阶段新增 BLUEPRINT-READ-FREQ SLI 信号采集",
        "expected": ["MOD-FEEDBACK_LOOP", "MOD-INF-015"],
        "level": "full",
    },
    {
        "task": "Feedback Loop 的 dispatch 发错了任务类型——发给了 Gate Engine 而非 Orchestrator",
        "expected": ["MOD-FEEDBACK_LOOP"],
        "level": "partial",
        "read": ["MOD-GATE_ENGINE"],
    },
    {
        "task": "FLE 的正反馈循环——检测到异常后 dispatch 了一个会产生更多异常的任务",
        "expected": ["MOD-FEEDBACK_LOOP"],
        "level": "none",
    },
    # ── Session 21-25: LLM Security ──
    {"task": "LLM Security 的 L2 输入分类器误杀率过高——正则规则太严格", "expected": ["MOD-LLM_SECURITY"], "level": "full"},
    {
        "task": "四层安全防御的 L3 Schema 验证增加 JSON 输出格式校验",
        "expected": ["MOD-LLM_SECURITY", "MOD-INF-017"],
        "level": "full",
    },
    {"task": "prompt injection 检测增加新的攻击模式（知乎-小红书-v4）", "expected": ["MOD-LLM_SECURITY"], "level": "full"},
    {
        "task": "Security Gateway 的 fail-closed 模式下拒绝了一个合法 LLM 请求",
        "expected": ["MOD-LLM_SECURITY"],
        "level": "partial",
        "read": ["MOD-GATE_ENGINE"],
    },
    {
        "task": "LLM Security L4 审计日志格式与 Telemetry 不兼容",
        "expected": ["MOD-LLM_SECURITY", "MOD-INF-015"],
        "level": "none",
    },
    # ── Session 26-30: 综合 + 跨模块 ──
    {
        "task": "任务系统 T-V2-010 需要走 Pipeline + Context Engine + Vector Memory 三模块联动",
        "expected": ["MOD-TASK_SYSTEM", "MOD-INF-009", "MOD-CONTEXT_ENGINE", "MOD-INF-011"],
        "level": "full",
    },
    {
        "task": "全局容量预算检查——所有 12 个系统的 Token 使用量汇总",
        "expected": ["MOD-INF-001", "MOD-MASTER_BLUEPRINT"],
        "level": "full",
    },
    {
        "task": "知识库 KE-050 的 depends_on 引用展平——需要更新 Vector Memory 的 Collection namespace",
        "expected": ["MOD-KB-001", "MOD-INF-011"],
        "level": "full",
    },
    {
        "task": "代码去重引擎发现 src/zephyr/core/ 下有 3 个重复的 `_now_iso` 实现",
        "expected": ["MOD-INF-017", "MOD-INF-016"],
        "level": "partial",
        "read": ["MOD-INF-016"],
    },
    {
        "task": "MCPServers 的 BlueprintSearchServer 注册到 task_manager 的统一入口",
        "expected": ["MOD-INF-013", "MOD-MASTER_BLUEPRINT"],
        "level": "none",
    },
]

# ── 模拟日历 (2026-05-05 ~ 2026-05-08, 每天 7-8 个 session) ──
BASE_DATE = datetime(2026, 5, 5, tzinfo=UTC)
SESSION_IDS = [f"sim-{i:03d}" for i in range(1, 31)]
TASK_IDS = [f"R92-SIM-T{i:03d}" for i in range(1, 31)]
AGENT_MODELS = [
    "deepseek-v4-pro",
    "glm-5.1",
    "claude-sonnet-4-20250514",
]


def simulate() -> dict:
    """运行 30 个 session 的模拟，返回摘要 JSON。"""

    summary = {
        "sessions_total": 30,
        "sessions_compliant": 0,
        "sessions_partial": 0,
        "sessions_none": 0,
        "events_total": 0,
        "events_by_blueprint": {},
        "started_at": datetime.now(UTC).isoformat(),
    }

    day_offset = 0
    sessions_today = 0

    for idx, scenario in enumerate(SCENARIOS):
        session_id = SESSION_IDS[idx]
        task_id = TASK_IDS[idx]
        agent_model = random.choice(AGENT_MODELS)

        # 计算模拟时间戳
        sessions_today += 1
        if sessions_today > 8:
            sessions_today = 1
            day_offset += 1
        sim_hour = 9 + sessions_today  # 9:00~17:00
        sim_ts = BASE_DATE + timedelta(days=day_offset, hours=sim_hour - 9, minutes=random.randint(0, 59))

        level = scenario["level"]

        if level == "full":
            summary["sessions_compliant"] += 1
            to_read = scenario["expected"]
        elif level == "partial":
            summary["sessions_partial"] += 1
            to_read = scenario.get("read", [])
        else:  # none
            summary["sessions_none"] += 1
            to_read = []

        for bpid in to_read:
            record_blueprint_read(
                blueprint_id=bpid,
                session_id=session_id,
                task_id=task_id,
                agent_model=agent_model,
            )
            summary["events_total"] += 1
            summary["events_by_blueprint"][bpid] = summary["events_by_blueprint"].get(bpid, 0) + 1

    summary["finished_at"] = datetime.now(UTC).isoformat()

    return summary


# ── G6 beta 硬合规检查 ──


def check_compliance(metrics_path: Path) -> dict:
    """读取 JSONL 并对每个 scenario 做 beta 硬合规检查。

    beta: 未读蓝图 → REJECT（P0 阻断，不再 WARNING）
    """

    events_by_session: dict[str, set[str]] = {}
    try:
        with open(metrics_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                sid = rec.get("session_id", "")
                bpid = rec.get("blueprint_id", "")
                if sid not in events_by_session:
                    events_by_session[sid] = set()
                events_by_session[sid].add(bpid)
    except OSError:
        return {"error": "cannot_read_metrics"}

    report = {"total_scenarios": 30, "rejects": 0, "passes": 0, "violations": []}

    for idx, scenario in enumerate(SCENARIOS):
        sid = SESSION_IDS[idx]
        expected_set = set(scenario["expected"])
        read_set = events_by_session.get(sid, set())
        if not expected_set & read_set:
            report["rejects"] += 1
            report["violations"].append(
                {
                    "session_id": sid,
                    "task": scenario["task"],
                    "expected": sorted(expected_set),
                    "actually_read": sorted(read_set),
                    "level": scenario["level"],
                    "phase2_verdict": "REJECT",
                }
            )
        else:
            report["passes"] += 1

    report["reject_rate"] = round(report["rejects"] / 30 * 100, 1)

    return report


# ── 入口 ──


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    import argparse

    parser = argparse.ArgumentParser(description="Session telemetry simulator (beta G6 drills)")
    parser.add_argument("--warn-only", action="store_true", help="告警模式（exit 0）")
    parser.add_argument("--jsonl", action="store_true", help="单行 JSON 摘要输出")
    args = parser.parse_args()

    print("=" * 60)
    print("  ZephyrAlpha Session Simulator — beta 硬合规")
    print("=" * 60)

    # Step 1: 模拟
    print("\n[1/3] Simulating 30 sessions (beta hard compliance) ...")
    summary = simulate()
    print(f"  Events written: {summary['events_total']}")
    print(
        f"  Sessions: compliant={summary['sessions_compliant']} "
        f"partial={summary['sessions_partial']} none={summary['sessions_none']}"
    )

    # Step 2: G6 硬合规检查
    print("\n[2/3] Running G6 beta hard compliance check ...")
    metrics_path = REPO_ROOT / "data" / "telemetry" / "blueprint_reads.jsonl"
    report = check_compliance(metrics_path)
    print(f"  Passes:          {report['passes']}")
    print(f"  Rejects:         {report['rejects']}")
    print(f"  Reject Rate:     {report['reject_rate']}%")
    if report["violations"]:
        print("\n  beta REJECTS:")
        for v in report["violations"]:
            print(f"    {v['session_id']}: {v['task'][:50]}...")
            print(f"      Expected: {v['expected']} → Got: {v['actually_read']} | {v['phase2_verdict']}")

    # Step 3: 蓝图读取分布
    print("\n[3/3] Blueprint Read Distribution:")
    dist = summary["events_by_blueprint"]
    for bpid in sorted(dist, key=lambda x: -dist[x]):
        bar = "█" * dist[bpid]
        print(f"  {bpid}: {dist[bpid]:>2}  {bar}")

    # 输出完整 report JSON
    report_path = REPO_ROOT / "data" / "telemetry" / "session-simulator-report.json"
    full_report = {
        "phase": "P2_hard_compliance",
        "g6_active": True,
        "summary": summary,
        "compliance": report,
    }
    tmp_path = f"{report_path}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(full_report, fh, ensure_ascii=False, indent=2)
        os.replace(tmp_path, report_path)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
    print(f"\nFull report → {report_path}")

    exit_code = 1 if report.get("rejects") else 0

    if args.jsonl:
        severity = "HIGH" if exit_code else "INFO"
        print(
            json.dumps(
                {
                    "severity": severity,
                    "check_id": "SESSION-SIM",
                    "rejects": report.get("rejects"),
                    "passes": report.get("passes"),
                    "reject_rate": report.get("reject_rate"),
                },
                ensure_ascii=False,
            )
        )

    if args.warn_only:
        return EXIT_PASS
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
