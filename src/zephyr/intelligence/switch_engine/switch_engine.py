# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §l6_switch_engine
# [MODULE] zephyr.intelligence.switch_engine.switch_engine
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
# [DEPENDENCIES] zephyr.intelligence.switch_engine.switch_registry (SwitchRegistryStore/SwitchRegistryRecord);
#                zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] zephyr.ai_layer.switch_engine.tombstone_manager (seal 走 retired→tombstone 边);
#             zephyr.ai_layer.switch_engine.approval_router (promote approved_by 语义);
#             zephyr.ai_layer.switch_engine.revert_drill (EVENT_EDGES 回切分支+dry-run);
#             zephyr.ai_layer.switch_engine.rollout_tiers (规则对象状态线)
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 七态规范枚举定形（DESIGN §②-B 裁定留痕）：promote=一次性切换动作（事件），
#              promoted=动作后驻留态，拼写全稿统一；aborted=终态（Owner 重开=新 switch_id
#              新行，老行留档）；状态迁移唯一合法通道=EVENT_EDGES 白名单，表外迁移一律
#              拒绝（fail-closed）；T1-T6 触发器=纯函数机检（信号缺失=不触发，绝不编造）；
#              一键回切=单命令完成状态回拨+消费指针还原（champion_ref 回正），RTO≤1 交易日；
#              回切只改指针与状态，不删任何档案（A 退役不删观察期——墓碑制）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L6_ab_switch/DESIGN.md §②-B/§②-C/§④-S4
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 表外 (state,event) 迁移→SwitchTransitionError（附当前态+事件）；
#                  非法 approved_by/approved_by 缺失→ValueError（promote fail-closed）；
#                  revert 目标态不在该态合法出边→SwitchTransitionError；signals 非法键忽略
#                  （触发器只认预注册键，不猜）
# [TESTS] tests/intelligence/switch_engine/test_switch_engine.py（七态迁移全覆盖逐边/非法边
#         全枚举拒绝/回切单命令可逆 promoted→canary/T1-T6 机检逐条+信号缺失不触发/
#         promote 记录 promotion_record/aborted 终态无出边）
"""switch_engine — L6 七态状态机迁移器 + T1-T6 机检 + 一键回切执行器（S4 施工件）。

状态机=一张 DB 表（switch_registry）+一个迁移器（本模块），不建工作流引擎（DESIGN
自审闸过度工程检查 ②）。每态入边事件/进入判据/退出判据见 DESIGN §②-B 状态表；
本模块把"退出判据→向"编码为 EVENT_EDGES 白名单，"判据值"消费 config/switch_criteria.yaml
（经 criteria.freeze 冻结进行，判据自改=新 switch_id）。

回切语义（§②-C 表）：promoted 期回切→退 canary 或 aborted；canary 期回切→退 shadow
或 aborted；shadow 判据败→aborted。revert 单命令返回终态记录=可逆性验收锚。
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Final

from zephyr.intelligence.switch_engine.switch_registry import (
    SwitchRegistryRecord,
    SwitchRegistryStore,
)
from zephyr.shared.utils.time_utils import now_utc

INITIAL_STATE: Final[str] = "shadow"
TERMINAL_STATE: Final[str] = "aborted"

# (当前态, 事件) → 目标态。逐行对齐 DESIGN §②-B 状态表"退出判据（→向）"列。
EVENT_EDGES: Final[dict[tuple[str, str], str]] = {
    (INITIAL_STATE, "graduate"): "canary",               # 影子期判据全绿且满 min_months → canary
    (INITIAL_STATE, "abort"): TERMINAL_STATE,            # 判据败/好得反常未释疑 → aborted
    ("canary", "promote"): "promoted",                    # canary 期零事故满期 → promote 动作
    ("canary", "rollback_to_shadow"): INITIAL_STATE,      # 回切触发 → 退 shadow
    ("canary", "abort"): TERMINAL_STATE,
    ("promoted", "stabilize"): "champion",                # 切换满 1 体检窗无回切 → champion
    ("promoted", "rollback_to_canary"): "canary",         # 期内回切一键退回
    ("promoted", "abort"): TERMINAL_STATE,                # 回切且不可退回 canary
    ("champion", "supersede"): "retired",                 # 被下一代顶替 → retired（退位事件）
    ("champion", "degrade_revive_predecessor"): INITIAL_STATE,  # 自身劣化降级，前代走墓碑复检回 shadow
    ("retired", "seal"): "tombstone",                     # 观察窗满 → §②-D 封存规程
    ("retired", "revive"): INITIAL_STATE,                 # 观察窗内复活条件触发 → 回 shadow 重走对比
    ("tombstone", "revive"): INITIAL_STATE,               # 复活条件触发 → 回 shadow（复活≠直提）
}
# aborted 无出边：Owner 手递重开卡=新 switch_id 新行（open_switch），老行终态留档。

ROLLBACK_EDGE_BY_STATE: Final[dict[str, str]] = {
    "promoted": "rollback_to_canary",
    "canary": "rollback_to_shadow",
}
# revert 只许走回切/冻结语义事件，禁借道前进边（stabilize/promote 等）。
REVERT_EVENTS: Final[frozenset[str]] = frozenset(
    {"rollback_to_canary", "rollback_to_shadow", "abort"}
)

T1_KEY: Final[str] = "t1_correctness_incidents_min"
T2_KEY: Final[str] = "t2_disagreement_rate_max"
T3_PCT_KEY: Final[str] = "t3_perf_delta_pct_max"
T3_DAYS_KEY: Final[str] = "t3_consecutive_trading_days"
T4_PCT_KEY: Final[str] = "t4_cost_increase_pct_max"
T4_BENEFIT_KEY: Final[str] = "t4_requires_compensating_benefit"

ACTION_IMMEDIATE_ROLLBACK: Final[str] = "immediate_rollback"
ACTION_BLOCK_PROMOTION: Final[str] = "block_promotion"
ACTION_AUTO_ROLLBACK: Final[str] = "auto_rollback"
ACTION_ROLLBACK_REVIEW: Final[str] = "rollback_review"
ACTION_FREEZE_SWITCH: Final[str] = "freeze_switch"
ACTION_PAUSE_SHADOW: Final[str] = "pause_shadow"


class SwitchTransitionError(RuntimeError):
    """表外状态迁移（fail-closed：当前态+事件+合法出边全量随异常给出）。"""


CONSUMER_STATES: Final[frozenset[str]] = frozenset({"promoted", "champion"})


def active_ref(record: SwitchRegistryRecord) -> str:
    """消费指针（推导型，不落库）：生产消费方当前接哪一版。

    promoted/champion 态 → challenger_ref 已上岗为生效版；其余态 → champion_ref
    （影子/canary 期 B 输出仅供对比器，永不回流生产——三闸·消费闸）。revert 的
    "消费指针还原"即由状态回拨经本推导自然生效，无第二份可漂移指针落库。
    """
    return record.challenger_ref if record.state in CONSUMER_STATES else record.champion_ref


@dataclass(frozen=True)
class SwitchTriggerVerdict:
    """单个 T 触发器机检结论（signals 缺失=不触发，绝不编造）。"""

    trigger: str
    fired: bool
    action: str
    detail: str


def evaluate_triggers(
    signals: dict[str, Any], criteria: dict[str, Any], state: str
) -> list[SwitchTriggerVerdict]:
    """T1-T6 预注册触发器机检（纯函数；信号缺失视为未发生，不触发不抛）。"""
    verdicts: list[SwitchTriggerVerdict] = []

    def _num(key: str) -> float | None:
        value = signals.get(key)
        return float(value) if isinstance(value, (int, float)) else None

    incidents = _num("correctness_incidents")
    t1_min = float(criteria.get(T1_KEY, 1))
    verdicts.append(
        SwitchTriggerVerdict(
            "T1", incidents is not None and incidents >= t1_min,
            ACTION_IMMEDIATE_ROLLBACK,
            f"correctness_incidents={incidents} 阈={t1_min}（立即一键回切，B 冻结待查）",
        )
    )

    rate = _num("disagreement_rate")
    t2_max = criteria.get(T2_KEY)
    t2_fired = rate is not None and t2_max is not None and rate > float(t2_max)
    t2_action = ACTION_ROLLBACK_REVIEW if state in ("canary", "promoted") else ACTION_BLOCK_PROMOTION
    verdicts.append(
        SwitchTriggerVerdict("T2", t2_fired, t2_action, f"disagreement_rate={rate} 上界={t2_max}")
    )

    pct = _num("perf_median_delta_pct")
    days = _num("perf_degradation_days")
    t3_fired = (
        pct is not None and days is not None
        and pct > float(criteria.get(T3_PCT_KEY, 20))
        and days >= float(criteria.get(T3_DAYS_KEY, 5))
    )
    verdicts.append(
        SwitchTriggerVerdict("T3", t3_fired, ACTION_AUTO_ROLLBACK, f"delta={pct}% days={days}")
    )

    cost = _num("cost_increase_pct")
    benefit_claimed = bool(signals.get("compensating_benefit_claimed"))
    need_benefit = bool(criteria.get(T4_BENEFIT_KEY, True))
    t4_fired = cost is not None and cost > float(criteria.get(T4_PCT_KEY, 15)) and (
        need_benefit and not benefit_claimed
    )
    verdicts.append(
        SwitchTriggerVerdict("T4", t4_fired, ACTION_ROLLBACK_REVIEW, f"cost=+{cost}% 补偿主张={benefit_claimed}")
    )

    t5_fired = signals.get("anomalous_gain") is True
    verdicts.append(
        SwitchTriggerVerdict("T5", t5_fired, ACTION_FREEZE_SWITCH, "收益/指标异常放大 → L4 三查")
    )

    t6_fired = signals.get("quota_exceeded") is True
    verdicts.append(
        SwitchTriggerVerdict("T6", t6_fired, ACTION_PAUSE_SHADOW, "配额越限 → 暂停影子（非回切）")
    )
    return verdicts


class SwitchEngine:
    """状态机迁移器+promote/revert 动作执行器。判据冻结由调用方经 criteria.freeze 注入。"""

    def __init__(
        self,
        store: SwitchRegistryStore,
        *,
        clock: Callable[[], datetime] = now_utc,
    ) -> None:
        self.store = store
        self._clock = clock

    def open_switch(self, record: SwitchRegistryRecord) -> SwitchRegistryRecord:
        """开户：初始态恒 shadow（影子不下真决策是第一不变量）。

        state_history 开户起笔由 store.create 完成（seed=create 事件），本方法不再
        重复追加同态条目。
        """
        record = (
            SwitchRegistryRecord(**{**record.__dict__, "state": INITIAL_STATE})
            if record.state != INITIAL_STATE
            else record
        )
        self.store.ensure_schema()
        self.store.create(record, created_at=self._clock())
        return self.store.require(record.switch_id)

    def legal_targets(self, state: str) -> dict[str, str]:
        """给定当前态的合法出边 {事件: 目标态}（表外态返回空——含 aborted 终态）。"""
        return {
            event: target for (src, event), target in EVENT_EDGES.items() if src == state
        }

    def transition(self, switch_id: str, event: str, evidence_ref: str) -> SwitchRegistryRecord:
        """事件驱动迁移：白名单校验→落库。表外迁移抛 SwitchTransitionError。"""
        record = self.store.require(switch_id)
        targets = self.legal_targets(record.state)
        if event not in targets:
            raise SwitchTransitionError(
                f"表外迁移：state={record.state} event={event!r} "
                f"合法出边={targets or '无（终态）'}"
            )
        return self.store.update_state(
            switch_id, targets[event], evidence_ref, at=self._clock()
        )

    def promote(
        self, switch_id: str, *, approved_by: str, receipt_ref: str
    ) -> SwitchRegistryRecord:
        """promote 动作（canary→promoted 一次性切换事件）：审批语义由 S6 分流器裁定，
        本执行器只 fail-closed 校验 approved_by 枚举并留痕 promotion_record。"""
        if approved_by not in {"auto", "independent_review", "owner_one_click"}:
            raise ValueError(f"非法 approved_by={approved_by!r}")
        if not receipt_ref:
            raise ValueError("promote 缺 receipt_ref（拍板回执留痕不可空）")
        record = self.store.require(switch_id)
        if record.state != "canary":
            raise SwitchTransitionError(
                f"promote 仅可自 canary 执行，当前 state={record.state}"
            )
        promoted_at = self._clock().isoformat()
        return self.store.update_state(
            switch_id,
            "promoted",
            f"promote:{receipt_ref}",
            patches={"promotion_record": {
                "approved_by": approved_by, "receipt_ref": receipt_ref,
                "promoted_at": promoted_at,
            }},
            at=self._clock(),
        )

    def revert(self, switch_id: str, *, reason: str, target_state: str | None = None) -> SwitchRegistryRecord:
        """一键回切（单命令可逆）：状态回拨+消费指针还原（champion_ref 回正）。

        默认目标：promoted→canary、canary→shadow（ROLLBACK_EDGE_BY_STATE）；
        显式 target_state 须为该态合法出边（如 abort）。一次调用完成，无人工步骤。
        """
        record = self.store.require(switch_id)
        event = ROLLBACK_EDGE_BY_STATE.get(record.state)
        if target_state is not None:
            event = next(
                (
                    e for e, tgt in self.legal_targets(record.state).items()
                    if tgt == target_state and e in REVERT_EVENTS
                ),
                None,
            )
            if event is None:
                raise SwitchTransitionError(
                    f"revert 目标态非法：state={record.state} target={target_state}"
                )
        if event is None:
            raise SwitchTransitionError(f"当前态 {record.state} 无回切出边（影子前/终态）")
        reverted = self.store.update_state(
            switch_id,
            EVENT_EDGES[(record.state, event)],
            f"revert:{reason}",
            patches={"rollback": {
                "plan_ref": "zephyr.intelligence.switch_engine.SwitchEngine.revert",
                "executed_at": self._clock().isoformat(), "reason": reason,
            }},
            at=self._clock(),
        )
        # 消费指针还原：状态回退后 active_ref() 重新指向 champion_ref（消费闸），
        # 单命令完成（RTO≤1 交易日），无第二份可漂移指针。
        return reverted

    def revert_plan(self, switch_id: str) -> dict[str, Any]:
        """回切 dry-run 计划（S7 演练三查①消费：可执行且分支正确，不落任何状态变更）。"""
        record = self.store.require(switch_id)
        event = ROLLBACK_EDGE_BY_STATE.get(record.state)
        plan: dict[str, Any] = {
            "switch_id": switch_id,
            "from_state": record.state,
            "legal": event is not None,
            "event": event,
            "to_state": EVENT_EDGES.get((record.state, event)) if event else None,
        }
        return plan
