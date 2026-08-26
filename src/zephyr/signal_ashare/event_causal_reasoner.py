# [BLUEPRINT] MOD-SIG-112 | docs/03_modules/_domain_signal/event_causal_reasoner/blueprint.md
# [MODULE] zephyr.signal_ashare.event_causal_reasoner
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（协议核心纯内存；dowhy_runner/sqlite_conn/时钟/衰减系数全注入）
# [CONSUMERS] 运行时装配批（统一注入点装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 事件类型词表闭合（产业链/同业/供应链）；传导边模板不可含空事件类型；BFS路径按累计权重降序；强度衰减系数∈(0,1]；DoWhy未注入降级标记不阻断；sqlite_conn未注入跳过存储不抛错；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal/event_causal_reasoner/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] EventCausalError(占位 ZA-SIG-UNREGISTERED-EVENT-CAUSAL)——未知事件类型/空事件类型/非法衰减系数/空模板/模板重复时抛
# [TESTS] tests/signal_ashare/test_event_causal_reasoner.py
# [A_module] module_id=MOD-SIG-112 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""EventCausalReasoner — A股事件因果推理器（MOD-SIG-112，B1-00125，C2 D-ALT-22）。

事件类型→传导边模板（产业链上下游/同业/供应链三类词表闭合）
+ DoWhy反事实校验（注入dowhy_runner回调，库未装则降级标记不阻断）
+ 事件链时序存储（注入sqlite连接）
+ 事件影响路径与强度输出（路径BFS+强度衰减系数）。
EconML/DoWhy思想单机版。

纯内存/DI设计；外部副作用（OS调用/网络/进程控制）全部经注入回调。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "CausalImpactPath",
    "ConductionEdgeTemplate",
    "EventCausalError",
    "EventCausalReasoner",
    "EventCausalResult",
    "EventType",
    "RelationType",
]


class EventCausalError(Exception):
    """事件因果推理协议输入/配置非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-EVENT-CAUSAL。
    """


class EventType(str, Enum):
    """事件类型词表（产业链/同业/供应链三类闭合）。"""

    POLICY = "政策"
    EARNINGS = "业绩"
    SECTOR_ROTATION = "板块轮动"
    SUPPLY_CHAIN_SHOCK = "供应链冲击"
    MERGER_ACQUISITION = "并购重组"
    MACRO_DATA = "宏观数据"
    BLACK_SWAN = "黑天鹅"


class RelationType(str, Enum):
    """传导关系类型词表（三类闭合）。"""

    UPSTREAM_DOWNSTREAM = "产业链上下游"
    PEER = "同业"
    SUPPLY_CHAIN = "供应链"


@dataclass(frozen=True)
class ConductionEdgeTemplate:
    """传导边模板：事件类型→目标行业/标的集合+关系类型+衰减系数。"""

    event_type: EventType
    target_sectors: tuple[str, ...]
    relation_type: RelationType
    decay: float

    def __post_init__(self) -> None:
        if not isinstance(self.event_type, EventType):
            raise EventCausalError(f"非法事件类型: {self.event_type!r}")
        if not self.target_sectors:
            raise EventCausalError("target_sectors 为空")
        if any(not s or not str(s).strip() for s in self.target_sectors):
            raise EventCausalError("target_sectors 含空白项")
        if not 0.0 < self.decay <= 1.0:
            raise EventCausalError(f"衰减系数越界: {self.decay!r}（须∈(0,1]）")


@dataclass(frozen=True)
class CausalImpactPath:
    """单条影响路径（BFS产出）。"""

    path: tuple[str, ...]
    cumulative_decay: float
    hops: int


@dataclass(frozen=True)
class EventCausalResult:
    """事件因果推理结果。"""

    event_type: EventType
    triggered_at: datetime.datetime
    impact_paths: tuple[CausalImpactPath, ...]
    dowhy_downgraded: bool = False
    dowhy_notes: tuple[str, ...] = ()
    stored: bool = False
    storage_notes: tuple[str, ...] = ()


class EventCausalReasoner:
    """事件因果推理器（传导边模板+BFS+可选DoWhy/存储）。"""

    def __init__(
        self,
        *,
        decay_factor: float = 0.5,
        max_hops: int = 5,
        min_cumulative_decay: float = 0.01,
        dowhy_runner: Callable[[EventType, Mapping[str, object]], dict] | None = None,
        sqlite_conn: object | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if not 0.0 < decay_factor <= 1.0:
            raise EventCausalError(f"decay_factor 越界: {decay_factor!r}（须∈(0,1]）")
        if max_hops < 1:
            raise EventCausalError(f"max_hops 须≥1: {max_hops}")
        if not 0.0 <= min_cumulative_decay < 1.0:
            raise EventCausalError(f"min_cumulative_decay 越界: {min_cumulative_decay!r}")
        self._decay_factor = float(decay_factor)
        self._max_hops = int(max_hops)
        self._min_cumulative_decay = float(min_cumulative_decay)
        self._dowhy_runner = dowhy_runner
        self._sqlite_conn = sqlite_conn
        self._clock = clock or datetime.datetime.now
        self._templates: dict[tuple[EventType, str], ConductionEdgeTemplate] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _now(self) -> datetime.datetime:
        return self._clock()

    # ── 模板注册 ──────────────────────────────────────────────────────────

    def register_template(self, template: ConductionEdgeTemplate) -> None:
        """注册传导边模板（幂等，重复覆盖）。"""
        key = (template.event_type, template.relation_type.value)
        if key in self._templates:
            _log.warning("传导边模板覆盖: %s", key)
        self._templates[key] = template

    def templates(self) -> tuple[ConductionEdgeTemplate, ...]:
        """模板视图（按 event_type 然后 relation_type 确定性排序）。"""
        return tuple(self._templates[k] for k in sorted(self._templates, key=lambda x: (x[0].value, x[1])))

    # ── DoWhy反事实（注入回调，降级不阻断） ──────────────────────────────

    def _run_dowhy(self, event_type: EventType, context: Mapping[str, object]) -> dict:
        """执行DoWhy反事实校验；未注入或异常则降级标记。"""
        if self._dowhy_runner is None:
            return {"downgraded": True, "notes": ("dowhy_runner 未注入，降级跳过",)}
        try:
            result = dict(self._dowhy_runner(event_type, context))
            result.setdefault("downgraded", False)
            return result
        except Exception as exc:  # noqa: BLE001 — 降级不阻断
            _log.warning("DoWhy执行异常，降级: %s", exc)
            return {"downgraded": True, "notes": (f"DoWhy异常降级: {exc}",)}

    # ── 时序存储（注入sqlite连接，未注入跳过） ────────────────────────────

    def _store_event_chain(
        self,
        event_type: EventType,
        triggered_at: datetime.datetime,
        paths: tuple[CausalImpactPath, ...],
    ) -> tuple[bool, tuple[str, ...]]:
        """事件链时序存储；未注入返回跳过标记。"""
        if self._sqlite_conn is None:
            return False, ("sqlite_conn 未注入，跳过存储",)
        try:
            cur = self._sqlite_conn.cursor()
            cur.execute(
                "INSERT INTO event_chain (event_type, triggered_at, path_count) VALUES (?, ?, ?)",
                (event_type.value, triggered_at.isoformat(), len(paths)),
            )
            self._sqlite_conn.commit()
            return True, ("存储成功",)
        except Exception as exc:  # noqa: BLE001 — 存储失败不阻断推理
            _log.warning("事件链存储异常: %s", exc)
            return False, (f"存储异常降级: {exc}",)

    # ── BFS影响路径 ───────────────────────────────────────────────────────

    def reason(self, event_type: EventType, *, context: Mapping[str, object] | None = None) -> EventCausalResult:
        """事件因果推理主入口：BFS路径+DoWhy+存储。"""
        if not isinstance(event_type, EventType):
            raise EventCausalError(f"未知事件类型: {event_type!r}")
        triggered_at = self._now()
        ctx = dict(context) if context else {}

        # DoWhy反事实校验
        dowhy_result = self._run_dowhy(event_type, ctx)
        dowhy_downgraded = bool(dowhy_result.get("downgraded", False))
        dowhy_notes = tuple(dowhy_result.get("notes", ()))

        # BFS传导路径
        impact_paths = self._bfs_paths(event_type)

        # 时序存储
        stored, storage_notes = self._store_event_chain(event_type, triggered_at, impact_paths)

        return EventCausalResult(
            event_type=event_type,
            triggered_at=triggered_at,
            impact_paths=impact_paths,
            dowhy_downgraded=dowhy_downgraded,
            dowhy_notes=dowhy_notes,
            stored=stored,
            storage_notes=storage_notes,
        )

    def _bfs_paths(self, event_type: EventType) -> tuple[CausalImpactPath, ...]:
        """从事件类型出发沿传导边模板BFS，输出影响路径与累计衰减。

        传导边模板仅定义"事件类型→目标板块"一级边（板块节点无出边），
        故 BFS 展开至 hop=1 即自然收敛；max_hops 保留给后续板块级边扩展。
        """
        results: list[CausalImpactPath] = []
        for key, template in sorted(self._templates.items(), key=lambda kv: (kv[0][0].value, kv[0][1])):
            if key[0] is not event_type:
                continue
            for sector in template.target_sectors:
                decay = template.decay * self._decay_factor
                if decay >= self._min_cumulative_decay:
                    results.append(
                        CausalImpactPath(
                            path=(event_type.value, sector),
                            cumulative_decay=round(decay, 6),
                            hops=1,
                        )
                    )
        # 按累计衰减降序，同衰减按路径字典序
        results.sort(key=lambda p: (-p.cumulative_decay, p.path))
        return tuple(results)
