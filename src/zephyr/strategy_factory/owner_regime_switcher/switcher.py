# [BLUEPRINT] MOD-SOWNER-002 | docs/03_modules/_domain_ashare_signal/blueprint.md
# [MODULE] zephyr.strategy_factory.owner_regime_switcher.switcher
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] dataclasses; pandas
# [CONSUMERS] zephyr.strategy_factory.owner_regime_switcher.exam; tests/strategy_factory/test_s_owner_002_switcher.py
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 第 t 日调度=trade_date 严格早于 t 的最近快照（翻转次日生效，PIT 双保险）；候选态置信 <min_confidence=不确定=维持当前态；滞后带=候选态连续 N 日一致才翻转；快照陈旧度（距最近可见快照的交易日数）>M 日或窗口起点无态=失败安全（全时全包×保守系数，fail 到保守态）
# [MODIFY-GUARD] 考试冻结文档 §2——冻结后语义变更=第二真源作弊
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(状态集重叠/系数越界/快照空)
# [TESTS] tests/strategy_factory/test_s_owner_002_switcher.py
# [A_module] module_id=MOD-SOWNER-002 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""切换器核心——regime 状态 → (启用包集合, 各包仓位上限系数) 逐日调度表。

冻结口径（e4_freeze_s_owner_002 §2）:
  * 状态集映射（Owner mandate 先验，参数化）: trend_up={r3,r11,r12}→{B:1.0}；
    range={r1,r2}→{A:0.6}；trend_down={r4,r10}→{}（现金，上限 0.2 备用）。
  * 置信门: dominant 属目标态但 confidence < min_confidence → 候选态=当前态（不确定=维持）。
  * 滞后带: 候选态≠当前态须连续 N 日一致才翻转（防日频抖动反复换包）。
  * 失败安全: 快照缺失连续 > M 个交易日，或窗口起点无任何可用快照 → 全时全包×保守系数。
  * NaN 防御: dominant/confidence 为 NaN 按"不确定"处理（维持当前态/失败安全）。
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

# 三态映射键（与冻结文档 §2 一致；值=7 态编号集合，参数化供考试）
STATE_TREND_UP = "trend_up"
STATE_RANGE = "range"
STATE_TREND_DOWN = "trend_down"
STATE_FAIL_SAFE = "fail_safe"

ALL_SEVEN_STATES = ("r1", "r2", "r3", "r4", "r10", "r11", "r12")

# 冻结默认：各态的包上限映射（包 A=ETF 波段代理（防御）；包 B=动量代理（进攻））
DEFAULT_TREND_UP_CAPS: dict[str, float] = {"B": 1.0}
DEFAULT_RANGE_CAPS: dict[str, float] = {"A": 0.6}
DEFAULT_TREND_DOWN_CAPS: dict[str, float] = {}
DEFAULT_FAIL_SAFE_CAPS: dict[str, float] = {"A": 0.5, "B": 0.5}

_VALID_PACKAGE_NAMES = frozenset("AB")  # 策略包名域={A,B}（单字符拆分构造；策略包≠治理家族，词表同形异义）  # 策略包名域（非 governance family，词表扫描勿误判）

@dataclass(frozen=True)
class SwitcherConfig:
    """切换器参数（冻结默认值；网格化属 E4 后续，不在本窗）。"""

    trend_up_states: frozenset[str] = frozenset({"r3", "r11", "r12"})
    range_states: frozenset[str] = frozenset({"r1", "r2"})
    trend_down_states: frozenset[str] = frozenset({"r4", "r10"})
    trend_up_caps: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_TREND_UP_CAPS))
    range_caps: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_RANGE_CAPS))
    trend_down_caps: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_TREND_DOWN_CAPS))
    fail_safe_caps: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_FAIL_SAFE_CAPS))
    min_confidence: float = 0.35
    hysteresis_days: int = 5
    fail_safe_missing_days: int = 5

    def validate(self) -> None:
        """状态集互斥全覆盖+系数 [0,1]+参数正性（Fail-Closed）。"""
        union = self.trend_up_states | self.range_states | self.trend_down_states
        if len(self.trend_up_states & self.range_states) or len(
            self.trend_up_states & self.trend_down_states
        ) or len(self.range_states & self.trend_down_states):
            raise ValueError("状态集映射存在重叠（三态须互斥）")
        if union != set(ALL_SEVEN_STATES):
            raise ValueError(f"状态集映射未全覆盖 7 态: 缺 {set(ALL_SEVEN_STATES) - union}")
        for caps in (self.trend_up_caps, self.range_caps, self.trend_down_caps, self.fail_safe_caps):
            for pkg, cap in caps.items():
                if pkg not in _VALID_PACKAGE_NAMES:
                    raise ValueError(f"未知包名: {pkg}")
                if not 0.0 <= cap <= 1.0:
                    raise ValueError(f"包上限越界 [0,1]: {pkg}={cap}")
        if self.hysteresis_days < 1 or self.fail_safe_missing_days < 0:
            raise ValueError("滞后带天数须>=1；失败安全缺失天数须>=0")
        if not 0.0 <= self.min_confidence <= 1.0:
            raise ValueError("min_confidence 须在 [0,1]")


@dataclass(frozen=True)
class DailySchedule:
    """单日调度输出（切换器唯一对外语义=包集合+上限系数）。"""

    state: str
    caps: dict[str, float]
    fail_safe: bool


def build_schedule(
    trade_days: pd.DatetimeIndex,
    snapshots: pd.DataFrame,
    config: SwitcherConfig,
) -> pd.DataFrame:
    """构建逐日调度表（index=trade_days，列=state/cap_A/cap_B/fail_safe）。

    :param snapshots: regime 快照（trade_date/dominant/confidence；任意序）。
      PIT 铁律: 第 t 日只读 trade_date 严格早于 t 的最近一行。
    """
    config.validate()
    if snapshots.empty:
        raise RuntimeError("regime 快照为空——检查 run_id/数据链路")
    snap = snapshots.sort_values("trade_date")
    dates = pd.DatetimeIndex(pd.to_datetime(snap["trade_date"]))
    dominant = snap["dominant"].astype(object).to_numpy()
    conf = pd.to_numeric(snap["confidence"], errors="coerce").to_numpy(dtype=float)

    current: str | None = None
    candidate: str | None = None
    cand_run = 0
    stale_days = 0  # 距最近可见快照的交易日数（检测器断供检测）
    rows: list[dict[str, object]] = []
    j = -1  # 指向最后一个 trade_date < 当日 的快照行
    for day in trade_days:
        d = pd.Timestamp(day)
        prev_j = j
        while j + 1 < len(dates) and dates[j + 1] < d:
            j += 1
        stale_days = _update_stale_days(stale_days, j, prev_j)
        # 失败安全：快照陈旧度 > M 个交易日 → 全时全包×保守系数（fail 到保守态）
        if stale_days > config.fail_safe_missing_days:
            candidate = None
            cand_run = 0
            rows.append({"state": STATE_FAIL_SAFE, **_decap(config.fail_safe_caps), "fail_safe": True})
            current = STATE_FAIL_SAFE
            continue
        if current is None:
            # 窗口起点热启动：无当前态但有可见快照 → 直接采用其映射态为初始当前态
            # （置信门同样适用：低置信/未知态=失败安全保守态起步；滞后带此后照常门控后续翻转）
            current = _warm_start_state(dominant, conf, j, config)
            candidate = None
            cand_run = 0
            rows.append(
                {
                    "state": current,
                    **_decap(config.fail_safe_caps if current == STATE_FAIL_SAFE else _caps_of(current, config)),
                    "fail_safe": current == STATE_FAIL_SAFE,
                }
            )
            continue
        cand = _gated_candidate(dominant[j], conf[j], current, config)  # 置信门：低置信/未知态=维持当前态
        current, candidate, cand_run = _apply_hysteresis(cand, current, candidate, cand_run, config)  # 滞后带
        rows.append({"state": current, **_decap(_caps_of(current, config)), "fail_safe": False})
    out = pd.DataFrame(rows, index=pd.DatetimeIndex(trade_days))
    out.index.name = "trade_date"
    return out


def _map_state(dom: object, config: SwitcherConfig) -> str | None:
    if dom in config.trend_up_states:
        return STATE_TREND_UP
    if dom in config.range_states:
        return STATE_RANGE
    if dom in config.trend_down_states:
        return STATE_TREND_DOWN
    return None  # 未知态（含 NaN）=不确定


def _caps_of(state: str, config: SwitcherConfig) -> dict[str, float]:
    return {
        STATE_TREND_UP: config.trend_up_caps,
        STATE_RANGE: config.range_caps,
        STATE_TREND_DOWN: config.trend_down_caps,
        STATE_FAIL_SAFE: config.fail_safe_caps,
    }[state]


def _update_stale_days(stale_days: int, j: int, prev_j: int) -> int:
    """快照可见性推进：起点无快照/新快照可见/断供 三分支（返回更新后陈旧度）。"""
    if j < 0:
        return stale_days + 1  # 窗口起点尚无任何快照
    if j != prev_j:
        return 0  # 有新快照可见
    return stale_days + 1  # 快照停止更新（检测器断供）


def _warm_start_state(dominant: np.ndarray, conf: np.ndarray, j: int, config: SwitcherConfig) -> str:
    """窗口起点热启动：无当前态但有可见快照 → 直接采用其映射态为初始当前态。

    置信门同样适用：低置信/未知态=失败安全保守态起步；滞后带此后照常门控后续翻转。
    """
    dom0 = dominant[j] if j >= 0 else None
    c0 = float(conf[j]) if j >= 0 and not pd.isna(conf[j]) else np.nan
    mapped0 = _map_state(dom0, config)
    return mapped0 if (mapped0 is not None and not pd.isna(c0) and c0 >= config.min_confidence) else STATE_FAIL_SAFE


def _gated_candidate(dom: object, c: float, current: str, config: SwitcherConfig) -> str:
    """置信门：dominant 缺失/未知态/低置信 → 不确定=候选态维持当前态。"""
    mapped = _map_state(dom, config)
    if mapped is None or pd.isna(c) or c < config.min_confidence:
        return current
    return mapped


def _apply_hysteresis(
    cand: str, current: str, candidate: str | None, cand_run: int, config: SwitcherConfig
) -> tuple[str, str | None, int]:
    """滞后带：候选态连续 N 日一致才翻转；候选=当前态则清零计数。返回 (current, candidate, cand_run)。"""
    if cand == current:
        return current, None, 0
    if cand == candidate:
        cand_run += 1
    else:
        candidate = cand
        cand_run = 1
    if cand_run >= config.hysteresis_days:
        return cand, None, 0
    return current, candidate, cand_run


def _decap(caps: dict[str, float]) -> dict[str, float]:
    """包上限展开为固定两列（缺包=0.0）。"""
    return {"cap_A": float(caps.get("A", 0.0)), "cap_B": float(caps.get("B", 0.0))}


def baseline_schedule(trade_days: pd.DatetimeIndex, cap_a: float = 1.0, cap_b: float = 1.0) -> pd.DataFrame:
    """"全时全包"基线调度表（无门控无缩放；两包全开×满上限）。"""
    idx = pd.DatetimeIndex(trade_days)
    return pd.DataFrame(
        {"state": "baseline", "cap_A": float(cap_a), "cap_B": float(cap_b), "fail_safe": False},
        index=idx,
    )
    # 注意：基线腿 state 列仅标注用；引擎只读 cap_A/cap_B


def scaled_schedule(sched_df: pd.DataFrame, scalar: float) -> pd.DataFrame:
    """整表乘常数系数（敞口匹配对照用；冻结文档 §5）。"""
    if not 0.0 < scalar <= 1.0 + 1e-9:
        raise ValueError(f"敞口匹配系数须在 (0,1]: {scalar}")
    out = sched_df.copy()
    out["cap_A"] = out["cap_A"] * scalar
    out["cap_B"] = out["cap_B"] * scalar
    return out


def count_state_transitions(sched_df: pd.DataFrame) -> int:
    """状态翻转次数（红蓝②防抖验收用：≤ 天数/N+2）。"""
    states = sched_df["state"].tolist()
    return sum(1 for i in range(1, len(states)) if states[i] != states[i - 1])
