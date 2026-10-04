# [BLUEPRINT] MOD-GOV-CARDREVIEWAUTO | docs/01_policies_and_standards/sop/construction_sop/task_card_work_order_policy.md | §interface-2
# [MODULE] scripts.governance.card_review_automation
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.persistence.task_repo (TaskRepository/TaskNotFoundError，函数内延迟 import 保持核心可 mock)；stdlib argparse/json/sys/time
# [CONSUMERS] docs/01_policies_and_standards/sop/construction_sop/task_card_work_order_policy.md §interface-2 | 施工车道收尾（人工/车道确认后调 verify）| tests/governance/persistence/test_card_review_automation.py
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 任务卡工单制政策 v1.0 接口②自动化：对指定卡自动跑两轮 batch_review（轮数/轮间隔可配，轮内出现 issue 即提前停——连续零问题计数被脏轮打断后继续空跑无意义）；产出 verify 就绪度报告（schema=card_review_automation/v1）；恒不代盖章——本工具任何路径都不调 TaskRepository.verify()，盖章=人工/车道确认后的独立动作（立法 §2 禁裸 UPDATE，verify() 是唯一合法核销路径）；卡已 verification_status=verified 时 already_verified=True 且不再建议核销；卡不存在返回 ok=False + error=task_not_found 不抛穿 CLI
# [MODIFY-GUARD] 报告 schema 字段增删必须同步 tests/governance/persistence/test_card_review_automation.py 的形态断言；stamped 字段恒 False，禁止改为从 repo 读
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] rc=0 核销就绪（或已盖章）；rc=1 未就绪（含提前停）；rc=2 卡不存在/用法错误；rounds 非法抛 ValueError；--json 输出机器可读报告，人读模式打印 conclusion
# [TESTS] tests/governance/persistence/test_card_review_automation.py
# [A_module] module_id=MOD-GOV-CARDREVIEWAUTO | layer=module | stability=stable | safety=L | ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  合法 manual CLI：车道收尾按需跑两轮预审+就绪报告，非常驻自动运行器
# create-guard-not-dup: 本模块是任务卡工单制政策接口②的唯一两轮预审自动化器（batch_review 循环调度+verify 就绪报告+禁代盖章语义），非 task_repo 审查引擎/收尾校验 gate 的第二实现——CREATE-GUARD 命中词仅时间性措辞（batch review rounds / verify report）
"""card_review_automation.py — 任务卡两轮预审自动化（任务卡工单制政策 v1.0 接口②）

立法锚点
--------
docs/01_policies_and_standards/sop/construction_sop/task_card_work_order_policy.md §interface-2：

- 验收 = ``TaskRepository.batch_review`` 连续 2 轮 0 问题（``get_review_status().review_complete``）。
- 核销 = ``TaskRepository.verify()``（唯一合法路径，禁裸 UPDATE），前置=审查完成。
- 本工具只把"两轮预审"机械化并出具就绪报告；**盖章（verify）仍人工/车道确认后调用**。

用法
----
::

    python scripts/governance/card_review_automation.py --task-id SRC-123 \\
        [--rounds 2] [--interval-seconds 0] [--reviewer card_law_automation] \\
        [--session-id <sid>] [--db-path <path>] [--json]

退出码：0=核销就绪（或已盖章）；1=未就绪；2=卡不存在/用法错误。

报告 schema（card_review_automation/v1）::

    {schema, task_id, ok, rounds_requested, rounds_run, rounds_passed, early_stopped,
     review_status, verification_status, already_verified, verify_ready, stamped, conclusion}
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any, Callable

SCHEMA_VERSION = "card_review_automation/v1"

DEFAULT_ROUNDS = 2  # 对齐 task_repo.CIRCULAR_ACCEPTANCE_ROUNDS（连续 2 轮 0 问题）
MAX_ROUNDS = 10
DEFAULT_REVIEWER = "card_law_automation"

_REQUIRED_REPORT_KEYS = (
    "schema",
    "task_id",
    "ok",
    "rounds_requested",
    "rounds_run",
    "rounds_passed",
    "early_stopped",
    "review_status",
    "verification_status",
    "already_verified",
    "verify_ready",
    "stamped",
    "conclusion",
)

__all__ = ["SCHEMA_VERSION", "DEFAULT_ROUNDS", "run_card_review_automation", "main"]


def _not_found_report(task_id: str) -> dict[str, Any]:
    """任务卡不存在时的错误报告（不抛穿 CLI，rc=2）。"""
    return {
        "schema": SCHEMA_VERSION,
        "task_id": task_id,
        "ok": False,
        "error": "task_not_found",
        "stamped": False,
        "conclusion": f"任务卡 {task_id} 不存在：先建卡（create_and_ready）再跑预审。",
    }


def run_card_review_automation(
    repo: Any,
    task_id: str,
    *,
    rounds: int = DEFAULT_ROUNDS,
    interval_seconds: float = 0.0,
    reviewer: str = DEFAULT_REVIEWER,
    session_id: str | None = None,
    sleep: Callable[[float], None] | None = None,
) -> dict[str, Any]:
    """对指定任务卡自动跑 ``rounds`` 轮 batch_review 并汇总 verify 就绪度报告。

    参数
    ----
    repo:
        TaskRepository（或同型 mock：需 batch_review/get_review_status/get）。
    task_id:
        任务卡 ID。
    rounds:
        预审轮数（默认 2，对齐 CIRCULAR_ACCEPTANCE_ROUNDS；<1 或 >MAX_ROUNDS 抛 ValueError）。
    interval_seconds:
        轮间隔秒数（经 ``sleep`` 注入触发，仅轮与轮之间，不首尾多睡）。
    reviewer / session_id:
        透传给 batch_review 的审计字段。
    sleep:
        睡眠函数注入点（默认 time.sleep；测试注入 mock 断言调用时序）。

    返回
    ----
    dict
        schema=card_review_automation/v1 的就绪度报告（字段见模块 docstring）。
        恒不调用 ``repo.verify``——stamped 恒 False（立法 §2 禁代盖章）。
        卡不存在（TaskNotFoundError）返回 ok=False + error=task_not_found。
    """
    if not isinstance(rounds, int) or isinstance(rounds, bool) or rounds < 1 or rounds > MAX_ROUNDS:
        raise ValueError(f"rounds 必须在 1..{MAX_ROUNDS}，收到 {rounds!r}")
    from zephyr.governance.persistence.task_repo import TaskNotFoundError

    _sleep = sleep if sleep is not None else time.sleep
    try:
        card = repo.get(task_id)
    except TaskNotFoundError:
        return _not_found_report(task_id)
    if card is None:
        return _not_found_report(task_id)

    report: dict[str, Any] = {
        "schema": SCHEMA_VERSION,
        "task_id": task_id,
        "ok": True,
        "rounds_requested": rounds,
        "rounds_run": 0,
        "rounds_passed": 0,
        "early_stopped": False,
        "review_status": {},
        "verification_status": "",
        "already_verified": False,
        "verify_ready": False,
        "stamped": False,
        "conclusion": "",
    }

    for round_index in range(rounds):
        if round_index > 0 and interval_seconds > 0:
            _sleep(interval_seconds)
        result = repo.batch_review(task_id, reviewer=reviewer, session_id=session_id)
        report["rounds_run"] += 1
        if result.get("passed", False):
            report["rounds_passed"] += 1
        else:
            # 轮内出现 issue 即提前停：连续零问题计数被脏轮打断，继续空跑无意义
            report["early_stopped"] = True
            break

    report["review_status"] = repo.get_review_status(task_id)
    fresh_card = repo.get(task_id)
    verification_status = str(getattr(fresh_card, "verification_status", "") or "")
    report["verification_status"] = verification_status
    already_verified = verification_status == "verified"
    report["already_verified"] = already_verified
    review_complete = bool(report["review_status"].get("review_complete", False))
    report["verify_ready"] = review_complete and not already_verified

    if already_verified:
        report["conclusion"] = "卡已 verified（已盖章）：无需重复核销。"
    elif report["verify_ready"]:
        report["conclusion"] = (
            f"两轮预审通过（连续零问题={report['review_status'].get('consecutive_zero', 0)}）："
            f"verify 就绪——请人工/车道确认后调用 TaskRepository.verify('{task_id}') 核销（本工具不代盖章）。"
        )
    elif report["early_stopped"]:
        report["conclusion"] = f"第 {report['rounds_run']} 轮预审发现问题，已提前停：先整改建卡/产物后重跑本工具。"
    else:
        report["conclusion"] = f"预审 {report['rounds_run']} 轮完成但连续零问题不足 2 轮：verify 前置未满足，禁止核销。"
    return report


def _print_human(report: dict[str, Any]) -> None:
    print(f"[card_review_automation] {report['task_id']}: {report['conclusion']}")
    rs = report.get("review_status") or {}
    print(
        f"  rounds_run={report.get('rounds_run')} rounds_passed={report.get('rounds_passed')}"
        f" early_stopped={report.get('early_stopped')}"
        f" consecutive_zero={rs.get('consecutive_zero', 0)}/2"
    )
    print(
        f"  verification_status={report.get('verification_status') or 'unknown'}"
        f" already_verified={report.get('already_verified')} verify_ready={report.get('verify_ready')}"
        f" stamped={report.get('stamped')}"
    )


def main(argv: list[str] | None = None) -> int:
    """CLI 入口：解析参数 → 跑两轮预审 → 输出报告；退出码见模块 docstring。"""
    parser = argparse.ArgumentParser(
        prog="card_review_automation",
        description="任务卡两轮预审自动化（接口②）：自动跑 batch_review + verify 就绪度报告；恒不代盖章。",
    )
    parser.add_argument("--task-id", required=True, help="任务卡 ID（NAMESPACE-SEQ）")
    parser.add_argument("--rounds", type=int, default=DEFAULT_ROUNDS, help=f"预审轮数（默认 {DEFAULT_ROUNDS}）")
    parser.add_argument("--interval-seconds", type=float, default=0.0, help="轮间隔秒数（默认 0）")
    parser.add_argument("--reviewer", default=DEFAULT_REVIEWER, help=f"审查者标识（默认 {DEFAULT_REVIEWER}）")
    parser.add_argument("--session-id", default=None, help="会话 ID（审计字段）")
    parser.add_argument("--db-path", default=None, help="SQLite 路径（默认 DB_PATH；测试/隔离用）")
    parser.add_argument("--json", action="store_true", help="机器可读 JSON 输出")
    args = parser.parse_args(argv)

    from zephyr.governance.persistence.task_repo import TaskRepository

    repo = TaskRepository(db_path=args.db_path) if args.db_path else TaskRepository()
    try:
        report = run_card_review_automation(
            repo,
            args.task_id,
            rounds=args.rounds,
            interval_seconds=args.interval_seconds,
            reviewer=args.reviewer,
            session_id=args.session_id,
        )
    except ValueError as exc:
        print(f"USAGE-ERROR: {exc}", file=sys.stderr)
        return 2
    finally:
        repo.close()

    if args.json:
        missing = [k for k in _REQUIRED_REPORT_KEYS if k not in report and k != "error"]
        if missing and report.get("ok", False):
            print(f"INTERNAL-ERROR: 报告缺字段 {missing}", file=sys.stderr)
            return 2
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_human(report)

    if not report.get("ok", False):
        return 2
    return 0 if (report.get("verify_ready") or report.get("already_verified")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
