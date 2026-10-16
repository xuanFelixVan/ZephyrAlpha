# [BLUEPRINT] MOD-DATA-ASMRT | docs/_working/infoaxis/00_ledger.md §4-P2 | 装配器共享运行时
# [MODULE] zephyr.data.assembly_runtime  # 事件钩子工厂（hook_factory 面）
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.shared.utils.time_utils（禁 datetime.now）；logging
# [CONSUMERS] pead_assembly/expectation_revision_assembler/equity_link_signals/
#   retail_comment_signals/goal_readiness_aggregator（五装配器的钩子/CLI 共享面——
#   CloneGuard extract 级合并处方：同构 maybe_emit/main 收敛单点，装配器只留 run_fn）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 纯共享工具零 IO；make_maybe_emit 工厂契约=宪法 §9.3 事件触发禁轮询+
#   永不反噬调度器（全捕获转 error 出声）+非唤醒点/失败零副作用；run_cli 契约=JSON
#   摘要打印+action==error 时 exit 1；tag 前缀日志归因
# [MODIFY-GUARD] tests/data/test_assembly_runtime.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 工厂返回的钩子永不抛（全捕获）；run_cli 异常上抛给调用方 CLI 层
# [TESTS] tests/data/test_assembly_runtime.py
# [TTL] permanent

"""事件钩子工厂（maybe_emit/run_cli 单点供给，五处装配流水线复用——st-infoaxis 收班克隆合并处方）。

真源：docs/_working/infoaxis/00_ledger.md §4（CloneGuard extract 级克隆阻断的治本：
同款钩子五份=克隆，收敛为工厂单点＋装配器薄委托）。
# [ALGO_FLOW]
# 层: 工厂闭包 → 唤醒过滤 → run → 摘要
# - make_maybe_emit(run_fn, wake_keys, tag): 返回 (task_id, success, **kw)->dict 钩子
# - run_cli(run_fn, argv, doc): --dry-run/--day 参数面 → JSON 打印 → exit code
# [/ALGO_FLOW]
"""

from __future__ import annotations

import argparse
import json
import logging
from collections.abc import Callable
from typing import Any, Final

__all__: Final = ["make_maybe_emit", "run_cli"]

log = logging.getLogger(__name__)


def make_maybe_emit(
    run_fn: Callable[..., dict[str, Any]],
    wake_keys: tuple[str, ...],
    tag: str,
) -> Callable[..., dict[str, Any]]:
    """调度器 task_completed 唤醒钩子工厂（宪法 §9.3 事件触发禁轮询；永不反噬）。

    契约（五装配器同款，l9/judgment 链先例）：非唤醒点/任务失败→skipped_wake_point
    零副作用；run 异常→error 出声绝不抛（钩子挂在调度器 SUCCESS 事件上，抛出=拖死采集链）。
    """
    prefix = f"[{tag}]"

    def maybe_emit(task_id: object = None, success: bool = True, **_kwargs: Any) -> dict[str, Any]:
        tid = str(task_id or "")
        if not success or not any(k in tid for k in wake_keys):
            return {"action": "skipped_wake_point"}
        try:
            res = run_fn()
            action = res.get("action", "error")
            if action == "error":
                log.warning("%s 读数未落地: %s", prefix, res.get("error", ""))
                return {"action": "error", "reason": res.get("error", "")}
            log.info("%s 已产出: %s", prefix, {k: v for k, v in res.items() if not str(k).startswith("tsv")})
            return {"action": action, **{k: v for k, v in res.items() if not str(k).startswith("tsv")}}
        except Exception as exc:  # noqa: BLE001 — 钩子永不反噬调度器，失败必须出声
            log.warning("%s 唤醒钩子异常（不影响后续链）: %s", prefix, exc, exc_info=True)
            return {"action": "error", "reason": str(exc)[:200]}

    return maybe_emit


def run_cli(run_fn: Callable[..., dict[str, Any]], argv: list[str] | None, doc: str) -> int:
    """装配器 CLI 共享面：--dry-run/--day → run_fn → JSON 摘要打印 → exit code。"""
    p = argparse.ArgumentParser(description=doc)  # noqa: m11-perm-manual-legitimate  工厂产 CLI 入口（装配器按需 runner 共享面；事件触发面由 make_maybe_emit 工厂承担=已注册订阅语义）
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--day", default=None)
    args = p.parse_args(argv)
    res = run_fn(day=args.day, dry_run=args.dry_run)
    print(json.dumps({k: v for k, v in res.items() if not str(k).startswith("tsv")}, ensure_ascii=False, default=str))
    if args.dry_run and res.get("tsv"):
        print(res["tsv"])
    return 0 if res.get("action") not in ("error",) else 1
