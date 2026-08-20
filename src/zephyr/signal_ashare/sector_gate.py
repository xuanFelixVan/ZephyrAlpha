# [BLUEPRINT] MOD-SIG-026 supplement | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/22_sector_rotation_spec.md §3.1⑩⑪
# [MODULE] zephyr.signal_ashare.sector_gate
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS] (待 G05 选股引擎漏斗准入层 / RRG 象限过滤层)
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] signal_weight ∈ [0,1]; 先 gate 后 weight; 纯函数无副作用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知水温档位 → ValueError
# [TESTS] tests/signal_ashare/test_sector_gate.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: water_temp(水温 5 档, regime/情绪周期上游判定, 本模块只响应不判定)
# I2: sector_code + score(个股强度 0-1, G05 多因子综合分) + top_sectors(当日 Top 热门板块集)
# I3: rotation_state(§3.1⑨ 5 状态, RISK_ON 档 CONSENSUS_CLIMAX 双重抑制用)
# A1: water_temp_response(5 档 → signal_weight/gate_thresholds/rrg_filter 三类输出)
# A2: admission_gate(核心热门直通 CORE_HOT / 次优≥level2 SECONDARY / 超强≥level3 WILDCARD / 其余 BLOCKED)
# A3: apply_rrg_filter(ALL / IMPROVING_ONLY / LEADING_ONLY / NONE 象限过滤)
# O1: WaterTempResponse + (gate_pass, gate_level) + rrg 放行布尔
# [/ALGO_FLOW]
"""三级放行门槛 + 水温→板块信号响应映射（22 号 spec §3.1⑩⑪）。

⑩ 准入 gate v2.1（先 gate 后 weight）：板块一日游（Top3 次日重合率 14.8%）
下降低阈值（v2.0 0.70/0.90 → v2.1 0.60/0.80），对非热门启动板块好股票留
放行通道；核心热门直通 / 次优板块+个股强度≥0.60 / 超强个股通配≥0.80。

⑪ 水温 5 档响应（本模块不判水温，水温归 regime 10 号/情绪周期 28 号）：
NEUTRAL 全权重 / RISK_ON ×0.5 / PANIC_REPAIR 仅改善象限+阈值放宽 /
RISK_OFF 仅领先象限+阈值收紧 / CRASH 全拦截。RISK_ON 叠加 5 状态
CONSENSUS_CLIMAX 时 signal_weight 再 ×0.5（双重抑制过热追高）。

边界：仓位比例（100/50/50/30/0%）归 regime/firm 层（30 号 §2.2 MOD-POS-021），
本模块只输出板块信号响应。阈值 v2.1 初拟待 G05 回测验证（spec §6 待裁定）。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# ------------------------------------------------------------------
# 常量（22 号 spec §3.1⑩⑪ v2.1 阈值，待 G05 回测校准）
# ------------------------------------------------------------------

GATE_CORE_HOT = "CORE_HOT"
GATE_SECONDARY = "SECONDARY"
GATE_WILDCARD = "WILDCARD"
GATE_BLOCKED = "BLOCKED"

RRG_FILTER_ALL = "ALL"
RRG_FILTER_IMPROVING_ONLY = "IMPROVING_ONLY"
RRG_FILTER_LEADING_ONLY = "LEADING_ONLY"
RRG_FILTER_NONE = "NONE"


class WaterTemp(str, Enum):
    """水温 5 档（上游 regime 12 态 + 情绪周期 5 阶段桥接，本模块不判定）"""

    NEUTRAL = "NEUTRAL"
    RISK_ON = "RISK_ON"
    PANIC_REPAIR = "PANIC_REPAIR"
    RISK_OFF = "RISK_OFF"
    CRASH = "CRASH"


@dataclass(frozen=True)
class GateThresholds:
    """三级放行门槛动态阈值（level2=次优板块+个股强度 / level3=超强个股通配）"""

    level2: float = 0.60
    level3: float = 0.80


@dataclass(frozen=True)
class WaterTempResponse:
    """水温 → 板块信号响应（signal_weight / gate_thresholds / rrg_filter）"""

    signal_weight: float
    gate_thresholds: GateThresholds
    rrg_filter: str


#: 水温 5 档 → 响应基表（§3.1⑪ 算法表）
_WATER_TEMP_TABLE: dict[WaterTemp, WaterTempResponse] = {
    WaterTemp.NEUTRAL: WaterTempResponse(1.0, GateThresholds(0.60, 0.80), RRG_FILTER_ALL),
    WaterTemp.RISK_ON: WaterTempResponse(0.5, GateThresholds(0.60, 0.80), RRG_FILTER_ALL),
    WaterTemp.PANIC_REPAIR: WaterTempResponse(0.5, GateThresholds(0.50, 0.70), RRG_FILTER_IMPROVING_ONLY),
    WaterTemp.RISK_OFF: WaterTempResponse(0.3, GateThresholds(0.80, 0.90), RRG_FILTER_LEADING_ONLY),
    WaterTemp.CRASH: WaterTempResponse(0.0, GateThresholds(1.01, 1.01), RRG_FILTER_NONE),
}


def water_temp_response(
    water_temp: WaterTemp | str,
    *,
    consensus_climax: bool = False,
) -> WaterTempResponse:
    """水温 → 板块信号响应映射（5 档 → 3 类可执行调整）。

    Args:
        water_temp: 水温档位（regime/情绪周期上游输入）。
        consensus_climax: 当日 5 状态 = CONSENSUS_CLIMAX（仅 RISK_ON 档生效，
            signal_weight 进一步 ×0.5，即 0.5×0.5=0.25 双重抑制过热追高）。

    Raises:
        ValueError: 未知水温档位。
    """
    try:
        temp = WaterTemp(water_temp)
    except ValueError as exc:
        raise ValueError(f"未知水温档位: {water_temp!r}") from exc
    base = _WATER_TEMP_TABLE[temp]
    weight = base.signal_weight
    if temp == WaterTemp.RISK_ON and consensus_climax:
        weight *= 0.5
    return WaterTempResponse(weight, base.gate_thresholds, base.rrg_filter)


def admission_gate(
    sector_code: str,
    score: float,
    top_sectors: set[str] | frozenset[str],
    thresholds: GateThresholds | None = None,
    *,
    retained_sectors: set[str] | frozenset[str] | None = None,
) -> tuple[bool, str]:
    """三级放行门槛（准入 gate v2.1，先 gate 后 weight）。

    Args:
        sector_code: 个股所属板块代码。
        score: 个股强度分 ∈ [0,1]（G05 多因子综合分，非本模块定义）。
        top_sectors: 当日 Top 热门板块集合（级别1 直通）。
        thresholds: 动态阈值（默认 v2.1 标准 0.60/0.80；
            水温联动时传 water_temp_response().gate_thresholds）。
        retained_sectors: 保留板块集（次优板块归属判定）；None 时退化为
            spec §3.1⑩ 伪代码简化版（级别2 仅按个股强度单条件判定）。

    Returns:
        (gate_pass, gate_level)：CORE_HOT 核心热门直通 / SECONDARY 次优板块+强度 /
        WILDCARD 超强个股通配（无视板块）/ BLOCKED 拦截。
    """
    th = thresholds or GateThresholds()
    if sector_code in top_sectors:
        return True, GATE_CORE_HOT
    if retained_sectors is None:
        if th.level2 <= score < th.level3:
            return True, GATE_SECONDARY
    elif sector_code in retained_sectors and score >= th.level2:
        return True, GATE_SECONDARY
    if score >= th.level3:
        return True, GATE_WILDCARD
    return False, GATE_BLOCKED


def apply_rrg_filter(quadrant: str, rrg_filter: str) -> bool:
    """RRG 象限过滤层（水温联动：PANIC_REPAIR 仅改善 / RISK_OFF 仅领先 / CRASH 全拦截）。

    Args:
        quadrant: RRG 象限（LEADING/WEAKENING/LAGGING/IMPROVING）。
        rrg_filter: water_temp_response().rrg_filter。

    Returns:
        True=该象限板块信号放行；False=信号 weight=0。
    """
    if rrg_filter == RRG_FILTER_ALL:
        return True
    if rrg_filter == RRG_FILTER_IMPROVING_ONLY:
        return quadrant == "IMPROVING"
    if rrg_filter == RRG_FILTER_LEADING_ONLY:
        return quadrant == "LEADING"
    return False  # RRG_FILTER_NONE
