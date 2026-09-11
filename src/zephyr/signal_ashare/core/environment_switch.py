# [BLUEPRINT] MOD-SIG-138 | docs/03_modules/_domain_signal/environment_switch/blueprint.md
# [MODULE] zephyr.signal_ashare.core.environment_switch
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（纯函数查表核，零 IO；情绪六段状态与两市成交额由调用方注入）
# [CONSUMERS] TDM-E-L3-06（环境开关）；L3-07 策略专属链（链启停消费，待接线）；L3-07-1 打板链（首板筛选器启停，待接线）；C13 intraday_tomorrow_forecast（情绪档输入协同，待接线）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 查表静态可审计（六段状态×开关动作封闭表，蓝图 §2）; 两市成交额<8000 亿=首板筛选器停（节点真源，实证=地量首板次日溢价为负）; 冰点(capitulation)=短线链全停只留波段链; 疯狂(euphoria)=反向收紧 tighten=True; 未知状态/负值/NaN 成交额→EnvironmentSwitchInputError（fail-closed）; 同输入必同输出（frozen+纯函数）; 阈值与开关表=proposed 待实盘标定
# [MODIFY-GUARD] 地图节点 TDM-E-L3-06
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 状态不在六段封闭集/成交额<0 或非有限 → EnvironmentSwitchInputError（fail-closed）
# [TESTS] tests/signal_ashare/test_environment_switch.py
# [TTL] permanent
"""EnvironmentSwitch — 环境开关查表（MOD-SIG-138，TDM-E-L3-06，长城夜班 Owner 立项）。

节点语义（TDM-E-L3-06 algo_note 逐条对码）：
    环境开关查表：两市成交<8000 亿=首板筛选器停（实证数据：地量首板次日溢价为负）；
    情绪冰点=短线链全停只留波段链；极端高潮=反向收紧。开关表按 L1 六段状态查。

六段状态键=地图 state_matrix 列轴（capitulation/accumulation/ignition/expansion/
euphoria/distribution）；与 sentiment_cycle.SentimentPhase 五阶段的归并映射
（ignition/expansion↔主升 等）由调用方负责，本件只认六段封闭集。

晨审定性（st-tdm-review-20260911 §7.1）：STRATEGY_DEPLOYMENT_MATRIX（3 策略×5 阶段）
仅部分承载，"成交<8000 亿首板链停"类环境开关查无专件→立 C 类候选；Owner 2026-09-11
夜班令"除币圈外开工"立项本件。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Final

#: 两市成交额地量阈值（亿元，节点真源；实证=地量首板次日溢价为负）
LOW_TURNOVER_THRESHOLD_YI: Final = 8000.0

#: 六段封闭状态集（真源=地图 state_matrix 列轴）
SIX_STATES: Final[tuple[str, ...]] = (
    "capitulation",  # 绝望冰点
    "accumulation",  # 修复
    "ignition",  # 启动
    "expansion",  # 主升
    "euphoria",  # 疯狂高潮
    "distribution",  # 退潮
)


@dataclass(frozen=True)
class EnvironmentSwitches:
    """环境开关输出（frozen，JSON 可序列化经 to_dict）。

    开关语义：``*_on=False`` = 该链当日停；``tighten_risk=True`` = 反向收紧
    （极端高潮日反向压缩仓位上限/提高门槛，不等于停链）。
    """

    state: str  # 六段状态回显
    turnover_amount_yi: float  # 成交额回显（亿元）
    first_board_filter_on: bool  # 首板筛选器（打板链首板层）
    short_term_chain_on: bool  # 短线链（1-3 日情绪链）
    swing_chain_on: bool  # 波段链（5-20 日趋势链）
    tighten_risk: bool  # 反向收紧
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """全基本类型字典。"""
        return {
            "state": self.state,
            "turnover_amount_yi": self.turnover_amount_yi,
            "first_board_filter_on": self.first_board_filter_on,
            "short_term_chain_on": self.short_term_chain_on,
            "swing_chain_on": self.swing_chain_on,
            "tighten_risk": self.tighten_risk,
            "notes": list(self.notes),
        }


#: 六段→基准开关动作封闭表（proposed；地量/冰点/高潮三条硬规则叠加其上）
#: 列序：first_board / short_term / swing / tighten
_SWITCH_TABLE: Final[dict[str, tuple[bool, bool, bool, bool]]] = {
    "capitulation": (False, False, True, False),  # 冰点：短线链全停只留波段链
    "accumulation": (True, True, True, False),  # 修复：全开
    "ignition": (True, True, True, False),  # 启动：全开
    "expansion": (True, True, True, False),  # 主升：全开
    "euphoria": (True, True, True, True),  # 疯狂：全开+反向收紧
    "distribution": (False, False, True, False),  # 退潮：收短线留波段
}


class EnvironmentSwitchInputError(ValueError):
    """输入非法（状态不在六段封闭集/成交额负值或非有限）——fail-closed。"""


def evaluate_environment_switches(state: str, turnover_amount_yi: float) -> EnvironmentSwitches:
    """环境开关查表主入口：六段状态+两市成交额 → 当日各链启停。

    Args:
        state: L1 六段状态名（SIX_STATES 封闭集，大小写敏感）。
        turnover_amount_yi: 两市成交额（亿元，≥0）。

    Returns:
        EnvironmentSwitches（frozen）。

    Raises:
        EnvironmentSwitchInputError: 状态未知或成交额非法（fail-closed）。
    """
    if not isinstance(state, str) or state not in _SWITCH_TABLE:
        raise EnvironmentSwitchInputError(
            f"未知情绪状态: {state!r}（六段封闭集={list(SIX_STATES)}）"
        )
    turnover = float(turnover_amount_yi)
    if not math.isfinite(turnover) or turnover < 0.0:
        raise EnvironmentSwitchInputError(f"两市成交额非法: {turnover_amount_yi!r}")

    fb, st, sw, tighten = _SWITCH_TABLE[state]
    notes: list[str] = []
    if turnover < LOW_TURNOVER_THRESHOLD_YI:
        fb = False
        notes.append(
            f"两市成交 {turnover:.0f} 亿 < {LOW_TURNOVER_THRESHOLD_YI:.0f} 亿 → 首板筛选器停"
            "（实证：地量首板次日溢价为负）"
        )
    if state == "capitulation":
        notes.append("情绪冰点 → 短线链全停只留波段链")
    elif state == "euphoria":
        notes.append("极端高潮 → 反向收紧（压仓位上限/提门槛，不止链）")
    elif state == "distribution":
        notes.append("退潮期 → 收短线留波段")

    return EnvironmentSwitches(
        state=state,
        turnover_amount_yi=turnover,
        first_board_filter_on=fb,
        short_term_chain_on=st,
        swing_chain_on=sw,
        tighten_risk=tighten,
        notes=notes,
    )
