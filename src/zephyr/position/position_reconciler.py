# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.position.position_reconciler
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] 无生产消费方（BRK-016 在册断点；事件入口=handle_execution_report，待 ex_core 终态事件扇出后由装配批挂接）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 持仓对账必须执行;P0-FATAL必须触发硬中断;事件触发:ExecutionReport到达时自动对账(禁止时间触发);**输入不可得即判不平(Fail-Closed)——缺键/None/非字典/双空无出处一律 status=input_unavailable, 禁把"没数据"说成"对平了"**
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/rollback/test_rollback_position_reconciler.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: "cron"在注释中，非实际cron调用

"""
Position Reconciler — v0.10.1 持仓对账: execution report+book record+counterparty三方对账。

事件触发机制：
  - 触发源: D_EXECUTION_CORE ExecutionReport 事件
  - 触发条件: 成交回报到达时自动触发 reconcile
  - 禁止时间触发（无 cron/Timer/sleep-loop/periodic）
  - 调用方通过 handle_execution_report 事件入口触发对账

Fail-Closed 契约（全流通战役 BRK-016 加严，2026-09-18）：
  本件此前的实现把"两侧都拿不到数据"和"两侧数据一致"返回同一个
  ``match=True`` —— 上游持仓源断供时，对账器会**静默判平**，与
  #ARCH-327（加固代码在 except 里空转而测试全绿）同型。现契约：

    ① 事件非 dict / 缺 internal_positions|external_positions 键 / 值为 None
       或非 dict           → status=input_unavailable, match=False
    ② 两侧均为空 dict 且无 positions_provenance（出处声明）
       → status=input_unavailable（空仓是合法态，但必须由调用方显式声明）
    ③ 真判平（两侧齐备且无差异）→ status=ok, match=True
    ④ 任何非 ok 态都可经 escalation_sink 触发硬中断（P0-FATAL）

  纯比较器 ``reconcile(internal, external)`` 语义不变（显式传双测=已声明），
  收紧只发生在**事件入口**——因为歧义（"拿不到"还是"真的空"）只在那里出现。

# [ALGO_FLOW] external: docs/03_modules/_domain_position/algo_flow/position_reconciler.yaml
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any, Final

_logger = logging.getLogger(__name__)

_RULE_ID_POSITION_MISMATCH = "POS-RECON-001"
#: 输入不可得的独立 rule_id——与"真差异"分开归因（否则运维无法区分"错"和"瞎"）
_RULE_ID_INPUT_UNAVAILABLE: Final[str] = "POS-RECON-002"

#: 事件必备键（缺一即判输入不可得，禁 .get(key, {}) 静默补空）
_REQUIRED_EVENT_KEYS: Final[tuple[str, str]] = (
    "internal_positions",
    "external_positions",
)
_PROVENANCE_KEY: Final[str] = "positions_provenance"

#: 对账结果状态
STATUS_OK: Final[str] = "ok"
STATUS_MISMATCH: Final[str] = "mismatch"
STATUS_INPUT_UNAVAILABLE: Final[str] = "input_unavailable"


class PositionReconciler:
    """持仓对账器——事件驱动（ExecutionReport到达时触发），输入不可得即判不平。"""

    def __init__(self, escalation_sink: Callable[[dict], None] | None = None) -> None:
        """初始化。

        Args:
            escalation_sink: 破闸回调（P0-FATAL 硬中断/告警的注入位）。
                None = 只计数并留 error 日志（**不静默**：日志级别 error）。
                回调异常一律吞不掉地转为 write 侧计数留痕，不打断对账主链。
        """
        self._positions: dict[str, dict] = {}
        self._escalation_sink = escalation_sink
        self.unavailable_count = 0
        self.mismatch_count = 0

    def reconcile(self, internal: dict, external: dict) -> dict:
        """对账核心逻辑——比较内部持仓与外部持仓差异

        Args:
            internal: 内部持仓字典 {symbol: quantity}
            external: 外部持仓字典 {symbol: quantity}

        Returns:
            dict with keys: match(bool), diffs(dict), count(int), rule_id(str)
        """
        diffs = {}
        all_keys = set(internal.keys()) | set(external.keys())
        for k in all_keys:
            i = internal.get(k, 0)
            e = external.get(k, 0)
            if i != e:
                diffs[k] = {"internal": i, "external": e, "diff": i - e}
        match = len(diffs) == 0
        result: dict[str, Any] = {
            "match": match,
            "diffs": diffs,
            "count": len(diffs),
            "status": STATUS_OK if match else STATUS_MISMATCH,
            "rule_id": None if match else _RULE_ID_POSITION_MISMATCH,
            "escalate": self.should_escalate(len(diffs)) if not match else False,
        }
        if not match:
            self.mismatch_count += 1
            _logger.warning(
                "Position reconciliation failed: %d diffs, rule_id=%s",
                len(diffs),
                _RULE_ID_POSITION_MISMATCH,
                extra={"context": {"diffs": diffs}},
            )
        return result

    def handle_execution_report(self, execution_report: dict) -> dict:
        """事件入口——ExecutionReport到达时触发对账

        事件触发源: D_EXECUTION_CORE ExecutionReport 事件
        禁止时间触发——仅通过事件调用此方法

        Args:
            execution_report: 执行回报字典，包含 internal/external 持仓

        Returns:
            reconcile 结果字典；输入不可得时为
            ``{match: False, status: "input_unavailable", rule_id: "POS-RECON-002",
            missing: [...], count: 0, diffs: {}, escalate: True}``
            ——**绝不返回 match=True**（Fail-Closed）。
        """
        missing = self._probe_event_payload(execution_report)
        if missing:
            return self._fail_closed(execution_report, missing)

        internal = execution_report["internal_positions"]
        external = execution_report["external_positions"]
        if not internal and not external and not execution_report.get(_PROVENANCE_KEY):
            # 双空且无出处声明 = 无法区分"真空仓"与"两侧都瞎了"→ 判不可得
            return self._fail_closed(execution_report, ["unproven_empty_positions"])

        _logger.info("Position reconcile triggered by ExecutionReport event")
        result = self.reconcile(internal, external)
        if result["escalate"]:
            self._escalate(result)
        return result

    @staticmethod
    def _probe_event_payload(event: Any) -> list[str]:
        """事件输入体检：返回缺失/非法项清单（空列表=输入齐备）。"""
        if not isinstance(event, dict):
            return ["event_not_mapping"]
        missing: list[str] = []
        for key in _REQUIRED_EVENT_KEYS:
            if key not in event:
                missing.append(key)
            elif not isinstance(event[key], dict):
                missing.append(f"{key}:not_mapping")
        return missing

    def _fail_closed(self, event: Any, missing: list[str]) -> dict:
        """输入不可得 → 判不平 + 计数 + error 日志 + 升级判定（禁静默放行）。"""
        self.unavailable_count += 1
        result: dict[str, Any] = {
            "match": False,
            "diffs": {},
            "count": 0,
            "status": STATUS_INPUT_UNAVAILABLE,
            "rule_id": _RULE_ID_INPUT_UNAVAILABLE,
            "missing": list(missing),
            "escalate": True,
        }
        _logger.error(
            "持仓对账输入不可得（禁判平）: rule_id=%s missing=%s event_keys=%s",
            _RULE_ID_INPUT_UNAVAILABLE,
            missing,
            sorted(event) if isinstance(event, dict) else type(event).__name__,
        )
        self._escalate(result)
        return result

    def _escalate(self, result: dict) -> None:
        """P0-FATAL 升级：有 sink 交出去（异常留痕不吞），无 sink 打 error 日志。"""
        if self._escalation_sink is None:
            _logger.error(
                "持仓对账需升级但未注入 escalation_sink（P0-FATAL 无人接）: rule_id=%s status=%s",
                result.get("rule_id"),
                result.get("status"),
            )
            return
        try:
            self._escalation_sink(result)
        except Exception as exc:  # noqa: BLE001 — 升级旁路异常禁打断对账，但必须 Fail-Loud
            _logger.error(
                "escalation_sink 抛异常（升级未生效，需人工介入）: %r", exc,
                extra={"context": {"rule_id": result.get("rule_id")}},
            )

    def should_escalate(self, diff_count: int, threshold: int = 3) -> bool:
        """判断是否需要升级（P0-FATAL 硬中断阈值）"""
        return diff_count >= threshold
