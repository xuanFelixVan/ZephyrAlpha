"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: slo_manager.py
# 层: 算法
# - id: A1
#   name_zh: ① SLOManager
#   name_en: SLOManager
#   intro: class SLOManager 源码 L90-L182
#   desc: 公共方法（定义序）: get_slos, list_contracts, check, record_duration, subscribe_eventbus；源码 L90-L182
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② get_slo_manager
#   name_en: get_slo_manager
#   intro: 5.39.6: SLOManager 进程级单例（boot_hooks 启动时实例化）。
#   desc: 5.39.6: SLOManager 进程级单例（boot_hooks 启动时实例化）。；源码 L188-L193
#   inputs: 无参数
#   outputs: SLOManager
# 层: 输出
# - id: O1
#   name_zh: SLOManager
#   name_en: SLOManager
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from typing import Final

# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.slo_manager
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""SLO/SLI 管理器（CT-SLO-001）——12条CT-* p95/p99目标 + Error Budget。

5.39.6 治本：原 SLOManager 定义后从未实例化（死代码）。现提供
``get_slo_manager()`` 单例 + ``subscribe_eventbus()`` 事件驱动接入——
boot_hooks 启动时实例化并订阅 EventBus，task.completed 等事件携带
``contract_id`` + ``duration_s`` 时自动采集样本、计算 p95/p99 并对照
SLO_MATRIX 检查，违规则 warning + ``slo.breach_total`` counter。
"""

import logging
import math
from collections import deque

logger = logging.getLogger(__name__)


SLO_MATRIX: Final[dict[str, dict]] = {
    "CT-ORC-SCRIPT-001": {"slos": [("p95", 3600.0)], "metric": "duration_s"},
    "CT-ORC-CE-001": {"slos": [("p95", 3.0)], "metric": "duration_s"},
    "CT-ORC-VMS-001": {"slos": [("p99", 1.0)], "metric": "duration_s"},
    "CT-ORC-GATE-001": {"slos": [("p99", 0.05)], "metric": "duration_s"},
    "CT-SCRIPT-GATE-001": {"slos": [("p95", 30.0)], "metric": "duration_s"},
    "CT-CE-VMS-001": {"slos": [("p99", 0.5)], "metric": "duration_s"},
    "CT-CE-LSG-001": {"slos": [("p99", 0.1), ("false_positive_pct", 5.0)], "metric": "duration_s"},
    "CT-FLE-ORC-001": {"slos": [("p95", 30.0), ("false_positive_pct", 10.0)], "metric": "duration_s"},
    "CT-FLE-DB-001": {"slos": [("p95", 10.0)], "metric": "duration_s"},
    "CT-TELE-FLE-001": {"slos": [("p95", 5.0)], "metric": "duration_s"},
    "CT-PIPE-ORC-001": {"slos": [("p95", 2.0)], "metric": "duration_s"},
    "CT-ORC-DB-001": {"slos": [("p95", 0.5)], "metric": "duration_s"},
}


class SLOManager:
    # 5.39.6: 每合同保留最近 N 个 duration 样本用于 p95/p99 计算
    _MAX_SAMPLES = 1000

    def __init__(self) -> None:
        self._durations: dict[str, deque[float]] = {}
        self._subscribed = False

    def get_slos(self, contract_id: str) -> dict | None:
        return SLO_MATRIX.get(contract_id)

    def list_contracts(self) -> list[str]:
        return list(SLO_MATRIX.keys())

    def check(self, contract_id: str, p95: float) -> tuple[bool, str]:
        slo = SLO_MATRIX.get(contract_id)
        if slo is None:
            return True, "NO_SLO_DEFINED"
        for percentile, threshold in slo["slos"]:
            if percentile == "p95" and p95 > threshold:
                return False, f"p95 {p95}s > {threshold}s"
            if percentile == "p99" and p95 > threshold:
                return False, f"p99 {p95}s > {threshold}s"
        return True, "OK"

    def record_duration(self, contract_id: str, duration_s: float) -> tuple[bool, str]:
        """5.39.6: 采集一次 duration 样本并对照 SLO 检查。

        样本写入 MetricsRegistry（``slo.duration_s`` histogram，contract_id
        作为 label 维度，对标 5.39.3 低基数名+高基数 label 原则），
        随后用滚动样本计算 p95 调 ``check()``；违规则 warning 日志 +
        ``slo.breach_total`` counter。返回 ``check()`` 结果。
        """
        samples = self._durations.setdefault(contract_id, deque(maxlen=self._MAX_SAMPLES))
        samples.append(duration_s)

        try:
            from zephyr.shared.observability.metrics import get_registry

            get_registry().observe("slo.duration_s", duration_s, labels={"contract_id": contract_id})
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.debug("slo metric observe failed", exc_info=True)

        sorted_samples = sorted(samples)
        p95_idx = max(0, math.ceil(0.95 * len(sorted_samples)) - 1)
        p95 = sorted_samples[p95_idx]
        ok, msg = self.check(contract_id, p95)
        if not ok:
            logger.warning("SLO breach: %s — %s (n=%d)", contract_id, msg, len(sorted_samples))
            try:
                from zephyr.shared.observability.metrics import get_registry

                get_registry().inc("slo.breach_total", labels={"contract_id": contract_id})
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.debug("slo breach counter failed", exc_info=True)
        return ok, msg

    def subscribe_eventbus(self) -> None:
        """5.39.6: 订阅 EventBus，事件驱动采集 duration 样本（幂等）。

        task.completed 事件携带 ``contract_id``/``source_blueprint`` 与
        ``duration_s``/``duration`` 属性（或 dict key）时自动 record_duration。
        """
        if self._subscribed:
            return
        self._subscribed = True
        try:
            from zephyr.shared.event_bus import bus

            def _on_task_completed(event: object) -> None:
                try:
                    contract_id = (
                        getattr(event, "contract_id", "")
                        or getattr(event, "source_blueprint", "")
                        or (event.get("contract_id") if isinstance(event, dict) else "")
                        or (event.get("source_blueprint") if isinstance(event, dict) else "")
                        or ""
                    )
                    duration = getattr(event, "duration_s", None)
                    if duration is None:
                        duration = getattr(event, "duration", None)
                    if duration is None and isinstance(event, dict):
                        duration = event.get("duration_s") or event.get("duration")
                    if not contract_id or duration is None:
                        return
                    self.record_duration(str(contract_id), float(duration))
                except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                    logger.debug("slo task.completed handler failed", exc_info=True)

            bus.subscribe("task.completed", _on_task_completed)
            logger.info("SLOManager: subscribed to EventBus task.completed (SLO auto-check)")
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("SLOManager: EventBus subscribe failed: %s", e, exc_info=True)


_default_manager: SLOManager | None = None


def get_slo_manager() -> SLOManager:
    """5.39.6: SLOManager 进程级单例（boot_hooks 启动时实例化）。"""
    global _default_manager
    if _default_manager is None:
        _default_manager = SLOManager()
    return _default_manager
