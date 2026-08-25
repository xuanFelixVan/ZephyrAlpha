# [BLUEPRINT] MOD-PLAN-019 | docs/03_modules/_domain_plan_engine/scenario_playbook/blueprint.md
# [MODULE] zephyr.plan_engine.scenario_playbook
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.premarket_constraint_loader(SCENARIO_LIST)
# [CONSUMERS] 运行时装配批（盘中状态/事件注入；复盘 review_sink 接 scenario_probability_model 更新）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 模板库9情景全覆盖(SCENARIO_LIST语义对齐MOD-PLAN-002); 多命中取risk_escalation最高(保守优先); 确认流PROPOSED→CONFIRMED→EXECUTED/REJECTED/EXPIRED非法迁移Fail-Closed; confirm必须携confirmed_by(人工在环留痕); 复盘Beta(1,1)平滑; review_sink异常不阻断如实记录; 纯函数判定核心不下单不写库
# [MODIFY-GUARD] tests/plan_engine/test_scenario_playbook.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PlaybookError(未登记错误码-申请中)
# [TESTS] tests/plan_engine/test_scenario_playbook.py
# [A_module] module_id=MOD-PLAN-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: 模板库(默认9情景/可注入覆盖) + market_state + active_scenario + events + bar_index
# A1: match(情景过滤→触发命中(常配或state∧event)→保守优先多命中取risk_escalation最高)
# A2: 确认流状态机(PROPOSED→CONFIRMED→EXECUTED; REJECTED/EXPIRED终态; 非法迁移拒绝)
# A3: settle(Beta(1,1)命中率平滑→review payload→review_sink回调)
# O1: PlaybookMatch / PlaybookConfirmation.status / settle payload
# [/ALGO_FLOW]
"""C-005 多情景对策——预案模板库 + 盘中实时匹配 + 执行确认流（MOD-PLAN-019）。

真源：construction_backlog_dig.tsv B1-00190（跨域元文档 §功能域模块·D-PORTFOLIO，
裁定=做 P1）+ CAND-PLAN-013。TSV 现状注记："情景规划器在，情景预案模板库与
盘中自动匹配触发未成体系"——本模块补该缺口，三段式：

  ① 预案模板库：PlaybookTemplate（情景 → 操作边界 OperationBoundary / 持仓动作
     HoldingAction / 风控升级 risk_escalation 0~2 + 触发条件 trigger_states/
     trigger_events + ttl_bars），默认库 9 情景全覆盖（SCENARIO_LIST 语义对齐
     MOD-PLAN-002，唯一真源直用不重造）。
  ② 盘中实时匹配：按 active_scenario 过滤模板 → 触发命中（常配模板无触发条件
     恒命中；触发型须 market_state∈trigger_states 且 events∩trigger_events
     非空）→ 多命中取 risk_escalation 最高者（保守优先，平手 template_id 升序）。
  ③ 执行确认流：PROPOSED →(人工 confirm, 必须 confirmed_by)→ CONFIRMED →
     EXECUTED；PROPOSED → REJECTED / EXPIRED（tick 超 ttl_bars）；非法迁移
     Fail-Closed（对齐 40号决策⑧ 人工在环）。

复盘闭环：settle(template_id, hit) → Beta(1,1) 平滑命中率 → review payload
经 review_sink 回调供 MOD-PLAN-017 scenario_probability_model 更新（装配批
接线）；sink 异常不阻断如实记录。

不做什么：不重生成盘前情景（MOD-PLAN-005 产出注入）、不直接写库、不下单
（只出对策建议与确认状态）。

SSoT: docs/03_modules/_domain_plan_engine/scenario_playbook/blueprint.md
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Final

from zephyr.plan_engine.premarket_constraint_loader import SCENARIO_LIST

__all__: Final = [
    "HoldingAction",
    "OperationBoundary",
    "PlaybookConfirmation",
    "PlaybookError",
    "PlaybookLibrary",
    "PlaybookMatch",
    "PlaybookStatus",
    "PlaybookTemplate",
    "default_library",
]

_log = logging.getLogger(__name__)


class PlaybookError(ValueError):
    """多情景对策错误（输入非法/状态机非法迁移）。"""

    error_code = "ZA-PLAN-0004"  # 2026-08-25 主代理正式登记（P1 R4W19）

    def __init__(self, *args: object, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code


class HoldingAction(str, Enum):
    """持仓动作枚举（对策建议，非下单指令）。"""

    HOLD = "HOLD"  # 持有不动
    ADD = "ADD"  # 加仓（受 operation_boundary 上限约束）
    REDUCE = "REDUCE"  # 减仓
    EXIT = "EXIT"  # 离场
    WATCH = "WATCH"  # 观察（暂不动作）


class PlaybookStatus(str, Enum):
    """确认流状态机。"""

    PROPOSED = "PROPOSED"
    CONFIRMED = "CONFIRMED"
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


@dataclass(frozen=True)
class OperationBoundary:
    """操作边界（模板参数，消费方应用，本模块不直接改约束状态）。

    Attributes:
        max_add_position: 加仓上限（相对仓位占比 ∈[0,1]）
        no_add_above_price: 禁加仓价位（None=不限）
        reduce_trigger_pct: 减仓触发跌幅（None=不设）
    """

    max_add_position: float = 0.0
    no_add_above_price: float | None = None
    reduce_trigger_pct: float | None = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.max_add_position <= 1.0:
            raise PlaybookError(f"max_add_position必须在[0,1], got {self.max_add_position}")
        if self.no_add_above_price is not None and self.no_add_above_price <= 0:
            raise PlaybookError(f"no_add_above_price必须>0, got {self.no_add_above_price}")
        if self.reduce_trigger_pct is not None and not 0.0 < self.reduce_trigger_pct <= 1.0:
            raise PlaybookError(f"reduce_trigger_pct必须在(0,1], got {self.reduce_trigger_pct}")


@dataclass(frozen=True)
class PlaybookTemplate:
    """情景对策模板（不可变）。

    Attributes:
        template_id: 模板唯一标识
        scenario: 适用情景（必须 ∈ SCENARIO_LIST，语义对齐 MOD-PLAN-002）
        operation_boundary: 操作边界
        holding_action: 持仓动作建议
        risk_escalation: 风控升级档位（0=常规 / 1=提级 / 2=紧急）
        trigger_states: 触发型市场状态集（空=常配模板）
        trigger_events: 触发型事件集（空=不依赖事件）
        ttl_bars: 确认流有效期（bar 数，>=1）
    """

    template_id: str
    scenario: str
    operation_boundary: OperationBoundary = field(default_factory=OperationBoundary)
    holding_action: HoldingAction = HoldingAction.WATCH
    risk_escalation: int = 0
    trigger_states: frozenset[str] = frozenset()
    trigger_events: frozenset[str] = frozenset()
    ttl_bars: int = 30

    def __post_init__(self) -> None:
        if not self.template_id:
            raise PlaybookError("template_id不能为空")
        if self.scenario not in SCENARIO_LIST:
            raise PlaybookError(f"scenario必须∈SCENARIO_LIST, got {self.scenario}")
        if self.risk_escalation not in (0, 1, 2):
            raise PlaybookError(f"risk_escalation必须∈(0,1,2), got {self.risk_escalation}")
        if self.ttl_bars < 1:
            raise PlaybookError(f"ttl_bars必须>=1, got {self.ttl_bars}")

    @property
    def is_standing(self) -> bool:
        """常配模板（无触发条件，恒命中）。"""
        return not self.trigger_states and not self.trigger_events


@dataclass(frozen=True)
class PlaybookMatch:
    """盘中匹配结果（不可变）。"""

    template: PlaybookTemplate
    matched_trigger: str  # "standing" | 命中触发描述
    proposed_at_bar: int


class PlaybookConfirmation:
    """执行确认流状态机（PROPOSED→CONFIRMED→EXECUTED / REJECTED / EXPIRED）。"""

    def __init__(self, match: PlaybookMatch) -> None:
        if not isinstance(match, PlaybookMatch):
            raise PlaybookError("match必须是PlaybookMatch")
        self._match = match
        self._status = PlaybookStatus.PROPOSED
        self._confirmed_by: str | None = None
        self._closed_bar: int | None = None

    @property
    def match(self) -> PlaybookMatch:
        return self._match

    @property
    def status(self) -> PlaybookStatus:
        return self._status

    @property
    def confirmed_by(self) -> str | None:
        return self._confirmed_by

    @property
    def closed_bar(self) -> int | None:
        return self._closed_bar

    def _ensure_open(self, action: str) -> None:
        if self._status is not PlaybookStatus.PROPOSED and self._status is not PlaybookStatus.CONFIRMED:
            raise PlaybookError(f"终态{self._status.value}不可{action}")
        if self._status is PlaybookStatus.CONFIRMED and action == "confirm":
            raise PlaybookError("重复confirm非法")

    def confirm(self, confirmed_by: str, bar_index: int) -> None:
        """人工确认（必须携操作者留痕，对齐 40号决策⑧ 人工在环）。"""
        if not confirmed_by:
            raise PlaybookError("confirm必须携confirmed_by（人工确认留痕）")
        self._ensure_open("confirm")
        if self._status is not PlaybookStatus.PROPOSED:
            raise PlaybookError(f"仅PROPOSED可confirm, 当前{self._status.value}")
        self._status = PlaybookStatus.CONFIRMED
        self._confirmed_by = confirmed_by

    def reject(self, bar_index: int) -> None:
        """人工否决（PROPOSED/CONFIRMED 均可否决到 REJECTED 终态）。"""
        self._ensure_open("reject")
        self._status = PlaybookStatus.REJECTED
        self._closed_bar = bar_index

    def mark_executed(self, bar_index: int) -> None:
        """标记已执行（仅 CONFIRMED 可执行）。"""
        if self._status is not PlaybookStatus.CONFIRMED:
            raise PlaybookError(f"仅CONFIRMED可mark_executed, 当前{self._status.value}")
        self._status = PlaybookStatus.EXECUTED
        self._closed_bar = bar_index

    def tick(self, bar_index: int) -> bool:
        """推进时钟：PROPOSED 超 ttl_bars → EXPIRED。返回本次是否转为 EXPIRED。"""
        if self._status is not PlaybookStatus.PROPOSED:
            return False
        if bar_index - self._match.proposed_at_bar > self._match.template.ttl_bars:
            self._status = PlaybookStatus.EXPIRED
            self._closed_bar = bar_index
            return True
        return False


class PlaybookLibrary:
    """预案模板库：匹配 + 复盘命中率统计（Beta(1,1) 平滑）。"""

    def __init__(self, templates: Sequence[PlaybookTemplate]) -> None:
        if not templates:
            raise PlaybookError("模板库不能为空")
        ids = [t.template_id for t in templates]
        if len(ids) != len(set(ids)):
            raise PlaybookError("template_id不得重复")
        self._templates: tuple[PlaybookTemplate, ...] = tuple(templates)
        self._by_id: dict[str, PlaybookTemplate] = {t.template_id: t for t in templates}
        # Beta(1,1) 先验：{template_id: [alpha, beta]}
        self._hits: dict[str, list[int]] = {t.template_id: [1, 1] for t in templates}

    @property
    def templates(self) -> tuple[PlaybookTemplate, ...]:
        return self._templates

    @property
    def scenarios(self) -> frozenset[str]:
        return frozenset(t.scenario for t in self._templates)

    def match(
        self,
        market_state: str,
        active_scenario: str,
        events: Sequence[str],
        bar_index: int,
    ) -> PlaybookMatch | None:
        """盘中实时匹配：情景过滤 → 触发命中 → 保守优先（risk_escalation 最高）。

        无命中返回 None（不臆造对策）；active_scenario 非法 Fail-Closed。
        """
        if active_scenario not in self.scenarios:
            raise PlaybookError(f"active_scenario未在模板库覆盖: {active_scenario}")
        if not market_state:
            raise PlaybookError("market_state不能为空")
        event_set = frozenset(events)
        hits: list[tuple[PlaybookTemplate, str]] = []
        for t in self._templates:
            if t.scenario != active_scenario:
                continue
            if t.is_standing:
                hits.append((t, "standing"))
            elif market_state in t.trigger_states and (
                not t.trigger_events or event_set & t.trigger_events
            ):
                hits.append((t, f"state:{market_state}"))
        if not hits:
            return None
        hits.sort(key=lambda h: (-h[0].risk_escalation, h[0].template_id))
        best, trigger = hits[0]
        return PlaybookMatch(template=best, matched_trigger=trigger, proposed_at_bar=bar_index)

    def settle(
        self,
        template_id: str,
        hit: bool,
        review_sink: Callable[[dict], None] | None = None,
    ) -> dict:
        """复盘回写：Beta(1,1) 平滑命中率 + review payload 经 sink 回调。

        sink 异常不阻断（如实记录）；template_id 未知 Fail-Closed。
        """
        if template_id not in self._by_id:
            raise PlaybookError(f"未知template_id: {template_id}")
        ab = self._hits[template_id]
        if hit:
            ab[0] += 1
        else:
            ab[1] += 1
        samples = ab[0] + ab[1] - 2  # 扣除 Beta(1,1) 先验
        payload = {
            "template_id": template_id,
            "scenario": self._by_id[template_id].scenario,
            "hit": bool(hit),
            "hit_rate": ab[0] / (ab[0] + ab[1]),
            "samples": samples,
        }
        if review_sink is not None:
            try:
                review_sink(payload)
            except Exception:  # noqa: BLE001 — sink 异常不阻断如实记录（装配批接线）
                _log.warning("review_sink 回调异常（不阻断）", exc_info=True)
        return payload


def default_library() -> PlaybookLibrary:
    """默认模板库：9 情景全覆盖（SCENARIO_LIST 语义对齐 MOD-PLAN-002）。

    档位哲学（44号 §9.5/§9.6 对齐）：真涨/假跌顺势加仓、假涨/真跌逆势减仓、
    洗盘观察；真跌情景风控升级最高（2=紧急）。
    """
    templates = (
        PlaybookTemplate(
            template_id="PB-HIGH-REAL-UP",
            scenario="HIGH_OPEN_REAL_UP",
            operation_boundary=OperationBoundary(max_add_position=0.30),
            holding_action=HoldingAction.ADD,
            risk_escalation=0,
            trigger_states=frozenset({"TREND_UP"}),
            trigger_events=frozenset({"VOLUME_CONFIRM"}),
        ),
        PlaybookTemplate(
            template_id="PB-HIGH-FAKE-UP",
            scenario="HIGH_OPEN_FAKE_UP",
            operation_boundary=OperationBoundary(max_add_position=0.0, reduce_trigger_pct=0.02),
            holding_action=HoldingAction.REDUCE,
            risk_escalation=1,
        ),
        PlaybookTemplate(
            template_id="PB-HIGH-WASH",
            scenario="HIGH_OPEN_WASH",
            operation_boundary=OperationBoundary(max_add_position=0.0),
            holding_action=HoldingAction.WATCH,
            risk_escalation=0,
        ),
        PlaybookTemplate(
            template_id="PB-LOW-REAL-DOWN",
            scenario="LOW_OPEN_REAL_DOWN",
            operation_boundary=OperationBoundary(max_add_position=0.0, reduce_trigger_pct=0.01),
            holding_action=HoldingAction.EXIT,
            risk_escalation=2,
        ),
        PlaybookTemplate(
            template_id="PB-LOW-FAKE-DOWN",
            scenario="LOW_OPEN_FAKE_DOWN",
            operation_boundary=OperationBoundary(max_add_position=0.20),
            holding_action=HoldingAction.ADD,
            risk_escalation=1,
            trigger_states=frozenset({"TREND_UP", "REVERSAL_UP"}),
            trigger_events=frozenset({"VOLUME_CONFIRM"}),
        ),
        PlaybookTemplate(
            template_id="PB-LOW-WASH",
            scenario="LOW_OPEN_WASH",
            operation_boundary=OperationBoundary(max_add_position=0.0),
            holding_action=HoldingAction.WATCH,
            risk_escalation=0,
        ),
        PlaybookTemplate(
            template_id="PB-FLAT-REAL-UP",
            scenario="FLAT_OPEN_REAL_UP",
            operation_boundary=OperationBoundary(max_add_position=0.15),
            holding_action=HoldingAction.ADD,
            risk_escalation=0,
            trigger_states=frozenset({"TREND_UP"}),
            trigger_events=frozenset({"VOLUME_CONFIRM"}),
        ),
        PlaybookTemplate(
            template_id="PB-FLAT-REAL-DOWN",
            scenario="FLAT_OPEN_REAL_DOWN",
            operation_boundary=OperationBoundary(max_add_position=0.0, reduce_trigger_pct=0.02),
            holding_action=HoldingAction.REDUCE,
            risk_escalation=1,
        ),
        PlaybookTemplate(
            template_id="PB-FLAT-WASH",
            scenario="FLAT_OPEN_WASH",
            operation_boundary=OperationBoundary(max_add_position=0.0),
            holding_action=HoldingAction.HOLD,
            risk_escalation=0,
        ),
    )
    return PlaybookLibrary(templates)
