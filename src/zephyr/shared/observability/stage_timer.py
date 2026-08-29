# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.observability.stage_timer
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.observability.metrics
# [CONSUMERS] zephyr.data.tick_subscriber（CAND-OBS-001 试点）；后续各生产模块按契约接入
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 阶段名合法集白名单校验; observe 仅登记已 begin 的阶段; 同阶段重复 begin 以末次为准; 计时源 time.perf_counter 单调; 零第三方依赖
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非法阶段名/未 begin 即 end -> ValueError（fail-closed，契约命名漂移即阻断）
# [TESTS] tests/zephyr/shared/observability/test_stage_timer.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""stage_timer —— 分段延迟打点助手（CAND-OBS-001 打点契约 MVP 施工件）。

职责
----
消灭"手写 time.perf_counter() 计时样板"（tick_subscriber 4 段 stage 各重复一遍）。
契约口径（design_memos/observability_contract_todo.md §三/§五 MVP 转正）：
  - 指标命名 ``{module}_{stage}_duration_seconds``（histogram，Prometheus 命名约定）
  - 阶段拆分按层定制（本助手不规定阶段名集合，由调用模块按契约声明）
  - 底层落 ``MetricsRegistry.observe``（MOD-INF-016 现成底座，零新建采集引擎）

设计边界（MVP）：不做 Prometheus/Grafana 重基建部署；不做 trace_id 贯通（挂后续波次）；
不做跨进程聚合。只提供"单事务多阶段计时"这一个语义原语。

对标
----
对手系统（BalletHip）下单全链路 build→sign→post 三段式打点（契约文档 §2.1）——
本助手把"每阶段独立计时+独立 histogram"做成一行调用。

用法::

    from zephyr.shared.observability.stage_timer import StageTimer

    timer = StageTimer(module="tick_subscriber")
    timer.begin("ws_recv")
    # ... 接收 ...
    timer.end("ws_recv")      # → observe tick_subscriber_ws_recv_duration_seconds
    timer.begin("parse")
    # ... 解析 ...
    timer.end("parse")        # → observe tick_subscriber_parse_duration_seconds

异常即未 begin 的阶段被 end（计时语义断裂，fail-closed 阻断契约漂移）。
"""

from __future__ import annotations

import logging
import re
import time
from typing import Final

from zephyr.shared.observability.metrics import MetricsRegistry, get_registry

_logger = logging.getLogger(__name__)

__all__: Final = ["StageTimer"]

#: 阶段名合法字符集（snake_case 小写字母/数字/下划线——Prometheus 指标名片段）
_STAGE_NAME_RE: Final = re.compile(r"^[a-z][a-z0-9_]*$")

#: 指标名模板（契约命名规约）
_METRIC_TEMPLATE: Final = "{module}_{stage}_duration_seconds"


class StageTimer:
    """单事务多阶段分段计时器——契约命名的打点样板消除器。

    线程安全由底层 MetricsRegistry 保证（其 inc/observe 均持锁）；
    本类自身只在 begin/end 时读写实例字典（单事务单线程使用语义，
    跨线程共享同一实例非设计场景）。
    """

    def __init__(
        self,
        module: str,
        registry: MetricsRegistry | None = None,
    ) -> None:
        """初始化分段计时器。

        Args:
            module: 模块名（指标前缀，如 "tick_subscriber"）。
            registry: 指标注册表（None=全局单例 get_registry()，测试可注入隔离实例）。
        """
        if not module or not _STAGE_NAME_RE.match(module):
            raise ValueError(
                f"module 名非法（须 snake_case 小写开头）: {module!r}"
            )
        self._module = module
        self._registry = registry if registry is not None else get_registry()
        self._open_stages: dict[str, float] = {}  # stage → begin 时刻（perf_counter）

    def begin(self, stage: str) -> None:
        """开始一个阶段计时。同阶段重复 begin 以末次为准（重置语义）。"""
        if not _STAGE_NAME_RE.match(stage):
            raise ValueError(
                f"stage 名非法（须 snake_case 小写开头）: {stage!r}"
            )
        self._open_stages[stage] = time.perf_counter()

    def end(self, stage: str) -> float:
        """结束一个阶段并 observe 到契约指标，返回耗时秒数。

        Raises:
            ValueError: 阶段未 begin（计时语义断裂，fail-closed）。
        """
        if stage not in self._open_stages:
            raise ValueError(
                f"stage 未 begin 即 end（计时语义断裂）: {stage!r}"
            )
        t0 = self._open_stages.pop(stage)
        elapsed = time.perf_counter() - t0
        self._registry.observe(self._metric_name(stage), elapsed)
        return elapsed

    def measure(self, stage: str):
        """上下文管理器形态——with timer.measure("parse"): ... （等价 begin/end 对）。"""
        return _StageContext(self, stage)

    def _metric_name(self, stage: str) -> str:
        return _METRIC_TEMPLATE.format(module=self._module, stage=stage)

    @property
    def open_stages(self) -> tuple[str, ...]:
        """当前仍未 end 的阶段名（诊断用，防泄漏）。"""
        return tuple(self._open_stages)


class _StageContext:
    """StageTimer.measure 的上下文管理器实现（内部件）。"""

    def __init__(self, timer: StageTimer, stage: str) -> None:
        self._timer = timer
        self._stage = stage
        self.elapsed: float = 0.0

    def __enter__(self) -> "_StageContext":
        self._timer.begin(self._stage)
        return self

    def __exit__(self, *exc) -> None:
        self.elapsed = self._timer.end(self._stage)
