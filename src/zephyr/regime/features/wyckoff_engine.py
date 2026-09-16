# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §4.12 Phase2c
# [MODULE] zephyr.regime.features.wyckoff_engine
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] MOD-REGIME-002(OverlaySignalsConstructor消费s2_wyckoff_score→S2 confirm)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] score∈[0,100]; 无结构=0(平时不干预); PIT严格(只用历史事件,ffill传播已发生阶段); PIT由调用方shift(1); 2026-09-16 WYF-3 起 _DIMENSION_STATUS=falsified ⇒ wyckoff_score 显式恒 0+一次性告警(禁静默恒零); SC 量能腿口径由 sc_vol_mode 承载(默认 vol_z=历史路径零改变, 固定基准量纲候选经 v2 协议预注册)
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] —
# [TESTS] tests/regime/test_wyckoff_engine.py; tests/regime/validation/test_wyckoff_walkforward.py  # 后者=WYF-3 新阈值路径+证伪路径
# [A_module] module_id=MOD-REGIME-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #10_regime_detector_spec §4.12 #MOD-REGIME-002 #Phase2c
"""
Wyckoff 吸筹 FSM 6 阶段识别 + 评分（MOD-REGIME-002 Phase 2c）。

把 OHLCV + 量能 z-score 映射成 Wyckoff 吸筹理论的 6 阶段事件 + 累加评分（0-100），
供 OverlaySignalsConstructor 组装 s2_wyckoff_score 维度喂 RegimeDetector S2 confirm。

Wyckoff 吸筹理论（10_regime_detector_spec §4.12.2）：
    PS(初步支撑) → SC(抛售高潮) → AR(自动反弹) → ST(二次测试)
    → Spring(震仓) → Test/SOS(强势信号)

每个阶段一旦出现，向后填充"已发生"（cummax 传播），加权累加：
    PS=10 / SC=30 / AR=15 / ST=20 / Spring=40 / Test=20（总分135，cap 100）

设计原则：
  - **PIT 铁律**：事件标记用 rolling+shift（严格历史）；sc_low/ar_high 用
    where(events).ffill() 传播（只用已发生事件的价位，不引入未来信息）。
    调用方 _precompute 末尾统一 shift(1) 再做最终 PIT 隔离。
  - **无结构 = 0**：无任何阶段出现 → score=0 → S2 confirm 不触发（C1 不退化前提）。
  - **Spring 是关键转折**（设计意图）：Spring 出现（+40）→ 累计至少 60+（过 S2 confirm 门槛 60）。
    WYF-3 实证：000300 2005-01-04..2026-09-15 共 5272 交易日，生产判据下
    PS/SC/AR/ST/Spring/Test 触发日 = 280/4/0/0/0/0，链从未闭合 → score 最大 40，
    门槛 60 结构性不可达（AR/ST/Spring/Test 合计 95 分权重从未计入）。
  - **当前维度状态 = falsified（WYF-3 裁定，2026-09-16）**：`wyckoff_score` 显式恒 0 +
    一次性 WARNING 披露，`wyckoff_dimension_status()` 供面板/审计读取。判据本身经
    walk-forward 重校无任何可用样本外信息量，详见
    docs/_working/wyf3/wyf3_recalibration_report.md（v1 证伪）与
    docs/_working/wyf3/wyf3_v2_rerun_report.md（v2 重跑触发条件第 1 条执行=证伪加厚，
    裁定#285）。
    阈值真源 `WyckoffParams` 保持原值不动（证伪的是判据，不是某个数字）。
    SC 量能腿口径经 `sc_vol_mode` 可切换（默认 "vol_z"=历史路径零改变；固定基准候选
    已被 v2 协议证伪，保留为可复算能力供后续复议，非生产推荐值）。

依据: 10_regime_detector_spec v1.3.1 §4.12.2 / Phase 2c 计划 §任务3
Version: 0.1.0

# [ALGO_FLOW] external: docs/03_modules/_domain_regime/algo_flow/wyckoff_engine.yaml
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Final

import numpy as np
import pandas as pd

__all__ = [
    "DEFAULT_WYCKOFF_PARAMS",
    "WyckoffParams",
    "detect_wyckoff_events",
    "sc_volume_leg",
    "wyckoff_dimension_status",
    "wyckoff_score",
    "wyckoff_score_from_events",
]

_logger = logging.getLogger(__name__)

# Wyckoff 6 阶段权重（10_regime_detector_spec §4.12.2）——真源在 WyckoffParams.stage_weights
_STAGE_WEIGHTS: Final[dict[str, float]] = {
    "ps": 10.0,
    "sc": 30.0,
    "ar": 15.0,
    "st": 20.0,
    "spring": 40.0,
    "test": 20.0,
}


@dataclass(frozen=True)
class WyckoffParams:
    """wyckoff 维度全部可调阈值的**单一真源**（WYF-3 落地，禁散落魔法数）。

    设计：默认值 == 2026-09-15 WYF-1 修复后的生产常数，故不传参时逐日行为与
    修复后基线完全一致（向后兼容）。校准期以 `replace(DEFAULT_WYCKOFF_PARAMS,
    **grid_point)` 构造候选，生产采纳=改本类默认值 + 注释指向裁定编号。

    每项标注：语义 / 现值来源 / 是否经样本外校验。
    `window`（PS 的 low 滚动窗 + 函数入参）刻意不入本类——它由调用方
    `overlay_features.s2_wyckoff_score(..., window=60)` 位置参数控制，属 API 契约。
    """

    # ── PS 初步支撑 ──
    ps_vol_z: float = 1.0            # 放量异动下限（严格 >）
    # ── SC 抛售高潮 ──
    sc_vol_mode: str = "vol_z"       # SC 量能腿口径："vol_z"(历史/生产现役) | "vol_ratio"(量比)
                                     # | "vol_epct"(expanding 历史分位) | "vol_qratio"(固定分位基准比)
                                     # ——WYF-3 v2 特征工程（裁定#271 重跑触发条件第 1 条执行），
                                     # 默认 vol_z ⇒ 不传参时逐日行为与历史完全一致（向后兼容铁律）
    sc_vol_z: float = 2.0            # mode=vol_z：恐慌巨量下限（严格 >）
    sc_vol_ratio: float = 2.0        # mode=vol_ratio：V/SMA(V,W_b) 下限（严格 >）
    sc_vol_epct: float = 0.98        # mode=vol_epct：expanding 历史分位下限（严格 >）
    sc_vol_qratio: float = 1.2       # mode=vol_qratio：V/EXP_QUANTILE(V,0.95) 下限（严格 >）
    sc_vol_baseline_window: int = 60   # mode=vol_ratio 的均量基准窗 W_b（v2 网格 {20,60}）
    sc_vol_expanding_min_periods: int = 260  # mode=vol_epct/vol_qratio 的 expanding 预热下限
                                             # （=WARMUP_TRADE_DAYS；不满窗=NaN=不触发，PIT 首日边界防泄漏）
    sc_pct: float = -0.04            # 单日跌幅下限（严格 <）
    sc_window: int | None = None     # 收盘新低回看窗；None=沿用函数 window 入参（现值口径）
    # ── AR 自动反弹（两道门，可独立摘除做消融）──
    ar_sc_window: int = 10           # SC 后回看窗
    ar_pct: float = 0.01             # 门①：反弹幅度下限（严格 >）
    ar_breakout_window: int = 10     # 门②：high 创 N 日新高
    ar_require_pct: bool = True      # 门①开关
    ar_require_breakout: bool = True  # 门②开关
    ar_vol_window: int = 10          # ST/Spring 缩量基准窗（已发生 AR 日均量）
    # ── ST 二次测试 ──
    st_sc_window: int | None = None  # SC 回看窗；None=与 AR 共用 ar_sc_window（现值口径）
    st_band: float = 0.02            # sc_low 回踩带宽 ±2%
    st_shrink: float = 0.7           # 缩量系数（< AR 均量×系数，严格 <）
    # ── Spring 震仓 ──
    spring_shrink: float = 0.8       # 缩量系数
    # ── Test/SOS 强势信号 ──
    test_spring_window: int = 20     # Spring 后回看窗
    test_vol_window: int = 20        # 放量基准窗
    test_vol_ratio: float = 1.0      # 放量系数（> 均量×系数，严格 >）
    # ── 评分与门槛语义（WYF-3 新增轴：cummax 永久粘滞 vs 有限记忆窗）──
    stage_weights: dict[str, float] = field(default_factory=lambda: dict(_STAGE_WEIGHTS))
    memory_window: int | None = None  # None=永久已发生（legacy cummax 粘滞）；N=只计近 N 日内出现
    score_cap: float = 100.0
    # S2 confirm 门槛**声明值**：权威真源=regime_detector.TRANSITION_CONFIG["S2"]
    # ["stages"]["confirm"]["keys_or_gte"]["wyckoff"]。本字段只供校准/报告对齐，
    # 引擎自身不做门槛判定；两者不一致须以 TRANSITION_CONFIG 为准并登记裁定。
    s2_confirm_gate: float = 60.0

    def resolved_sc_window(self, window: int) -> int:
        return self.sc_window if self.sc_window is not None else window

    def resolved_st_window(self) -> int:
        return self.st_sc_window if self.st_sc_window is not None else self.ar_sc_window

    def to_dict(self) -> dict[str, Any]:
        """可 hash 的纯数据视图（预注册 hash / JSON 落盘用）。"""
        d = {k: v for k, v in self.__dict__.items() if k != "stage_weights"}
        d["stage_weights"] = dict(self.stage_weights)
        return d


DEFAULT_WYCKOFF_PARAMS: Final[WyckoffParams] = WyckoffParams()

# ── 阈值别名（单一真源=上面的 WyckoffParams 默认值；保留旧名供既有测试/审计读取，
#    禁止在此另写字面值——任何值变化只改 WyckoffParams 默认值）─────────────
_P = DEFAULT_WYCKOFF_PARAMS
_PS_VOL_Z: Final[float] = _P.ps_vol_z
_SC_VOL_Z: Final[float] = _P.sc_vol_z
_SC_PCT: Final[float] = _P.sc_pct
_AR_SC_RECENT_WIN: Final[int] = _P.ar_sc_window
_AR_PCT: Final[float] = _P.ar_pct
_AR_BREAKOUT_WIN: Final[int] = _P.ar_breakout_window
_ST_BAND: Final[float] = _P.st_band
_ST_SHRINK: Final[float] = _P.st_shrink
_SPRING_SHRINK: Final[float] = _P.spring_shrink
_TEST_SPRING_RECENT_WIN: Final[int] = _P.test_spring_window
_TEST_VOL_RATIO: Final[float] = _P.test_vol_ratio


# ── WYF-3 维度可用性披露（禁静默恒零）────────────────────────────────────
# 校准结论落点。status="enabled" 时维度按 params 正常出分；status="falsified"
# 时引擎**显式**返回全 0 并在首次调用告警（不是"算了但没人知道恒 0"）。
# 真值表与终态由 WYF-3 walk-forward 重校报告给出（见 _DIMENSION_STATUS["evidence"]）。
#
# 2026-09-16 Lane F 终态=**falsified**（Owner 令"所有设计态全线施工/不留待裁"，覆盖裁定#257⑦
# 的 P2 降级）。要点：
#   · 证伪的是"六阶段判据本身"，不是某个阈值。故 DEFAULT_WYCKOFF_PARAMS **保持原值**
#     （=2026-09-15 WYF-1 修复后基线，仍由 tests/regime/test_wyckoff_engine.py 锁死），
#     以免"改个数"被误读成"修好了"。
#   · 现网行为零改变：全路径 21.7 年（5272 交易日）实算 score 最大 40 < 门槛 60，
#     score≥60 天数=0，即本维度今日对 S2 confirm 的贡献**本来就是 0**。本次只是把
#     "巧合的恒零"升级为"声明的恒零 + 告警"。
#   · 边界：`overlay_features.s2_wyckoff_score` 的 MVP 回退支（缺 high/low/vol/pct/vol_z
#     时 TR 收窄+中上部 → 可达 70）不经本引擎，**不受本状态影响**（该支不是 Wyckoff 量，
#     且同样未经样本外验证，已登记为遗留风险）。
_DIMENSION_STATUS: dict[str, Any] = {
    "status": "falsified",        # "enabled" | "falsified"
    "reason": (
        "WYF-3 walk-forward 重校（000300 2005-01-04..2026-09-15，5 折 expanding + 2025-01-02.."
        "2026-09-15 纯净留存段）：生产判据下 PS/SC/AR/ST/Spring/Test 触发日 = 280/4/0/0/0/0，"
        "score 最大 40，10 个训练与评估段达门天数全为 0（维度恒零）；预注册网格内可使链闭合的"
        "松弛判据虽训练段拟合良好（平均 excess20=+4.03%），样本外池化 6 事件 excess20=-4.62%、"
        "命中率劣于基线 17.7pp、0/5 折为正、合并 t=-0.10、WFE=-1.25、3/5 折恒零、1/5 折误爆"
        "（on_share 29.3%），纯净留存段 max_score=45 仍不达门。另：cummax 永久粘滞使 on_share"
        "只取两端（见 latch_dichotomy：生产事件集 + 门槛降到 40 ⇒ 单次 2018 事件即永久在线"
        "1927 日=36.6%），故不存在任何阈值向量能同时避免恒零与误爆——问题在判据而非门限。"
        "【v2 加厚 2026-09-16】裁定#271 重跑触发条件第 1 条已执行：SC 量能腿换固定基准量纲"
        "三族候选（量比/expanding 历史分位/固定分位基准比）×204 预注册网格点 0 合格"
        "（新腿臂最好 5 日 vs 下限 10；级联死，验证段/折叠未评）。钝化根因加深一层：恐慌日"
        "本身对任何基准都不再量能异常（2015-08-24 单日 -8.75%：量比@20=1.009、历史分位=0.945、"
        "分位基准比=0.905）——第一波放量永久抬高一切基准，第二波与后样本全部失明。"
        "详见 evidence 报告 §钝化段对照与 §失败模式。"
    ),
    "evidence": "docs/_working/wyf3/wyf3_v2_rerun_report.md",
    "evidence_v1": "docs/_working/wyf3/wyf3_recalibration_report.md",
    "params_source": "DEFAULT_WYCKOFF_PARAMS",
    # 重跑触发条件（证伪不是永久真理；下列任一发生必须重跑管线并复议本状态）
    "recheck_when": (
        "SC 量能腿由滚动 volume_anomaly z 换成固定基准量纲（钝化根因，见报告 §5.3）；"
        "或六阶段判据/权重/memory_window 语义任一改动；或 TRANSITION_CONFIG S2 confirm "
        "keys_or_gte 的 wyckoff 门槛变动；或指数标的/量纲口径变动（H1-P0 未复权治本后）。"
    ),
    # 触发执行台账（重跑不是无限循环：已执行的触发记录其结论，防重复立项）
    "recheck_log": (
        "触发1（固定基准量纲）2026-09-16 已执行=证伪加厚：协议 v2 预注册 204 点 0 合格"
        "（裁定#285）；触发2/3/4 仍未执行。"
    ),
    "ruling": "裁定#271（证伪置零）+ 裁定#285（v2 触发1执行：证伪加厚，维度维持置零）",
}
_status_warned = False


def wyckoff_dimension_status() -> dict[str, Any]:
    """返回 wyckoff 维度可用性披露快照（供面板/报告/审计读取，只读语义）。"""
    return dict(_DIMENSION_STATUS)


def _set_dimension_status(status: str, reason: str = "", evidence: str = "") -> None:
    """校准/测试通道改状态（生产代码不调用；测试用以后置证伪披露）。"""
    global _status_warned
    _DIMENSION_STATUS["status"] = status
    _DIMENSION_STATUS["reason"] = reason
    _DIMENSION_STATUS["evidence"] = evidence
    _status_warned = False


def _falsified_zero_index(index: pd.Index) -> pd.Series:
    """证伪态：显式返回恒 0 并一次性告警披露（禁静默）。"""
    global _status_warned
    if not _status_warned:
        _status_warned = True
        _logger.warning(
            "WYF-3 证伪披露：wyckoff 维度样本外无可用信息量，score 显式置零"
            "（S2 confirm 该析取腿等价不存在，非静默恒零）。reason=%s evidence=%s",
            _DIMENSION_STATUS["reason"],
            _DIMENSION_STATUS["evidence"],
        )
    return pd.Series(0.0, index=index)


# ── SC 量能腿口径表（WYF-3 v2：mode → WyckoffParams 阈值字段名）────────────
# 单一真源仍是 WyckoffParams 默认值；本表只登记"哪个口径读哪个字段"，禁另写字面值。
_SC_VOL_MODE_TO_THRESHOLD: Final[dict[str, str]] = {
    "vol_z": "sc_vol_z",
    "vol_ratio": "sc_vol_ratio",
    "vol_epct": "sc_vol_epct",
    "vol_qratio": "sc_vol_qratio",
}


def sc_volume_leg(volume: pd.Series, params: WyckoffParams | None = None) -> pd.Series:
    """SC 量能腿取值序列（固定基准量纲候选，WYF-3 v2 协议 §3 构造式）。

    全部口径只用 ≤T 数据（PIT 严格）：
      - vol_ratio：V(T)/SMA(V,W_b)(T)，rolling 向后含 T，min_periods=W_b（不满窗=NaN）；
      - vol_epct：V(T) 在 V(1..T) expanding 历史中的分位（rank pct），min_periods=N；
      - vol_qratio：V(T)/EXP_QUANTILE(V,0.95)(T)，同 expanding 预热。
    基准为 0（如长期无量）→ NaN → 与阈值比较恒 False（无量纲语义：无基准不触发，
    禁 inf 假触发）。停牌日 V=0 → 取值 0 → 不触发（放量腿的零量语义）。

    mode="vol_z" 时抛 ValueError：该腿由调用方传入的 vol_z 序列承载（生产口径单一
    真源是 RegimeFeatureBuilder F5，引擎内重算即制造第二实现=漂移温床）。

    供 detect_wyckoff_events 内部与校准管线（钝化段新旧腿对照表）使用。
    """
    p = params or DEFAULT_WYCKOFF_PARAMS
    v = volume.astype(float).fillna(0.0)
    if p.sc_vol_mode == "vol_ratio":
        base = v.rolling(p.sc_vol_baseline_window, min_periods=p.sc_vol_baseline_window).mean()
        return v / base.replace(0.0, np.nan)
    if p.sc_vol_mode == "vol_epct":
        return v.expanding(min_periods=p.sc_vol_expanding_min_periods).rank(pct=True)
    if p.sc_vol_mode == "vol_qratio":
        q95 = v.expanding(min_periods=p.sc_vol_expanding_min_periods).quantile(0.95)
        return v / q95.replace(0.0, np.nan)
    msg = (
        f"sc_vol_mode={p.sc_vol_mode!r} 无固定基准构造式；vol_z 腿由调用方传入序列承载，"
        "禁引擎内重算（生产同款口径单一真源）"
    )
    raise ValueError(msg)


def detect_wyckoff_events(
    close: pd.Series,
    high: pd.Series,
    low: pd.Series,
    volume: pd.Series,
    pct_change: pd.Series,
    vol_z: pd.Series,
    window: int = 60,
    *,
    params: WyckoffParams | None = None,
) -> pd.DataFrame:
    """识别 Wyckoff 6 阶段事件点，返回 DataFrame[ps,sc,ar,st,spring,test]（0/1 flag）。

    事件标记一律"向后 rolling（含当日）+ ffill 已发生事件"，PIT 由调用方 shift(1) 二次保证。
    全部阈值来自 `params`（单一真源 WyckoffParams），默认值=生产现值 → 逐日行为与
    WYF-1 修复后基线完全一致。

    Parameters
    ----------
    close, high, low : OHLC 序列（市场代理）。
    volume : 成交量序列。
    pct_change : 日涨跌幅序列（close.pct_change()）。
    vol_z : 量能异动 z-score（volume_anomaly，复用 HMM F5，20 日滚窗）。SC 量能腿
        sc_vol_mode="vol_z"（默认）时即 SC 第一腿；其余 mode 下 SC 腿改由 volume
        现算固定基准量纲（sc_volume_leg），本参数仍供 PS 腿使用。
    window : PS 的 low 滚动窗，亦是 SC 收盘新低窗的缺省来源（params.sc_window=None 时）。
    params : 阈值集（None=DEFAULT_WYCKOFF_PARAMS）。校准期由网格构造候选实例。

    Returns
    -------
    pd.DataFrame，index 同 close，列 [ps, sc, ar, st, spring, test]，值 0.0/1.0。
    """
    p = params or DEFAULT_WYCKOFF_PARAMS
    events = pd.DataFrame(index=close.index)
    c = close.ffill()
    h = high.ffill()
    l = low.ffill()
    v = volume.fillna(0.0)
    pct = pct_change.fillna(0.0)
    z = vol_z.fillna(0.0)

    rolling_min = l.rolling(window).min()
    # WYF-1 Bug1 修复：SC 判定必须用收盘价自身的滚动新低（c<=low 滚动低点数学上不可达）
    close_rolling_min = c.rolling(p.resolved_sc_window(window)).min()

    # ── PS 初步支撑：下跌中放量但不再创新低 ──
    # vol_z>1（放量）& low>rolling_min.shift(1)（不再创新低）& pct<0（下跌趋势中）
    not_new_low = l > rolling_min.shift(1)
    events["ps"] = ((p.ps_vol_z < z) & not_new_low & (pct < 0)).astype(float)

    # ── SC 抛售高潮：巨量暴跌 + 收盘创滚动新低 ──
    # 量能腿口径可切换（WYF-3 v2，sc_vol_mode 承载）：默认 vol_z=历史路径逐位一致；
    # 固定基准口径（vol_ratio/vol_epct/vol_qratio）由 volume 现算（PIT 安全见
    # sc_volume_leg）。不满窗/无基准=NaN → 与阈值比较恒 False（预热日不触发）。
    if p.sc_vol_mode == "vol_z":
        sc_vol_leg = z
    else:
        sc_vol_leg = sc_volume_leg(v, p)  # v=volume.fillna(0)，与引擎内口径一致
    sc_vol_threshold = getattr(p, _SC_VOL_MODE_TO_THRESHOLD[p.sc_vol_mode])
    sc_condition = (sc_vol_leg > sc_vol_threshold) & (pct < p.sc_pct) & (c <= close_rolling_min + 1e-8)
    events["sc"] = sc_condition.astype(float)

    # ── AR 自动反弹：SC 后近窗内、两道门（反弹幅度 / high 创新高）──
    # 门①②可独立摘除（ar_require_*）——WYF-3 网格对两道门分别做消融与扫描
    sc_recent = events["sc"].rolling(p.ar_sc_window).max() > 0
    ar_legs = pd.Series(True, index=close.index)
    if p.ar_require_pct:
        ar_legs &= pct > p.ar_pct
    if p.ar_require_breakout:
        ar_legs &= h >= h.rolling(p.ar_breakout_window).max()
    events["ar"] = (sc_recent & ar_legs).astype(float)

    # SC 低点 forward fill（只用已发生的 SC 事件的 low，PIT 安全）
    sc_low = l.where(events["sc"] > 0).ffill()
    # AR 后的均量（AR 事件日的 volume 滚动均值，缩量判定基准）
    # WYF-1 Bug2 修复：AR 事件稀疏，裸 rolling(10) 的 min_periods=10 导致恒 NaN；
    # ffill 传播已发生事件 + min_periods=1（ffill 已保证 PIT 安全——只传播已发生阶段）
    ar_vol_avg = v.where(events["ar"] > 0).ffill().rolling(p.ar_vol_window, min_periods=1).mean()
    # AR 高点 forward fill（只用已发生的 AR 事件的 high）
    ar_high = h.where(events["ar"] > 0).ffill()

    # ── ST 二次测试：回落至 SC 区域 + 缩量 + 近期有 SC ──
    # ST 的 SC 回看窗默认与 AR 共用（params.st_sc_window=None 保持现值口径）
    st_sc_recent = events["sc"].rolling(p.resolved_st_window()).max() > 0
    in_sc_zone = (l <= sc_low * (1.0 + p.st_band)) & (l >= sc_low * (1.0 - p.st_band))
    shrink_vol = v < (ar_vol_avg * p.st_shrink)
    events["st"] = (in_sc_zone & shrink_vol & st_sc_recent).astype(float)

    # ── Spring 震仓：跌破 sc_low 但收回 + 缩量 ──
    broke_sc = l < sc_low
    recovered = c > sc_low
    spring_shrink = v < (ar_vol_avg * p.spring_shrink)
    events["spring"] = (broke_sc & recovered & spring_shrink).astype(float)

    # ── Test/SOS 强势信号：Spring 后上突 AR 高点 + 放量 ──
    spring_recent = events["spring"].rolling(p.test_spring_window).max() > 0
    vol_expanding = v > (v.rolling(p.test_vol_window).mean() * p.test_vol_ratio)
    events["test"] = (spring_recent & (c > ar_high) & vol_expanding).astype(float)

    return events.fillna(0.0)


def wyckoff_stage_occurrence(
    events: pd.DataFrame,
    *,
    memory_window: int | None = None,
) -> pd.DataFrame:
    """事件点 → "阶段已发生"矩阵（0/1），PIT 安全。

    memory_window=None：legacy 语义——阶段一旦出现，**永久**算已发生（cummax 粘滞）。
    memory_window=N：只承认近 N 个交易日（含当日）内出现过的阶段（rolling max），
    使评分具备时间局部性（S2 是一次性转换，永久在线=噪声；参 capitulation
    "rolling max 致状态粘滞 → 衰减加权"的同族治本，见 WYF-3 报告 §结构证明）。
    """
    cols = [c for c in _STAGE_WEIGHTS if c in events.columns]
    if memory_window is None:
        return events[cols].cummax()
    return events[cols].rolling(int(memory_window), min_periods=1).max()


def wyckoff_score_from_events(
    events: pd.DataFrame,
    params: WyckoffParams | None = None,
) -> pd.Series:
    """事件矩阵 → 评分序列（0-100，cap 后）。**评分尾段唯一真源**。

    生产 `wyckoff_score` 与校准管线 `wyckoff_walkforward.score_from_events` 共用本函数
    （RULE-SSOT：判据与算分不得两处实现，否则"诊断版绿了、生产版死的"结构性复发）。

    刻意**不受** `_DIMENSION_STATUS` 影响：证伪披露关的是"生产出口"，不是研究能力；
    若这里也被门掉，则报告 §recheck_when 触发的重跑将无法出分（自毒化）。
    """
    p = params or DEFAULT_WYCKOFF_PARAMS
    occurred = wyckoff_stage_occurrence(events, memory_window=p.memory_window)
    score = pd.Series(0.0, index=events.index)
    for stage, weight in p.stage_weights.items():
        if stage in occurred.columns:
            score += occurred[stage] * weight
    # cap（默认 100：实际最高 135，但 score 维度 ∈ [0,100] INVARIANTS）
    return score.clip(upper=p.score_cap).fillna(0.0)


def wyckoff_score(
    close: pd.Series,
    high: pd.Series,
    low: pd.Series,
    volume: pd.Series,
    pct_change: pd.Series,
    vol_z: pd.Series,
    window: int = 60,
    *,
    params: WyckoffParams | None = None,
) -> pd.Series:
    """Wyckoff 吸筹评分 → 0-100（累加已出现阶段分数，cap 100）。

    每个阶段一旦出现（默认永久记忆，params.memory_window 可改为有限窗），加权累加。
    默认权重映射（对齐 S2 confirm 门槛 wyckoff>=60）：
      Spring 出现（PS+SC+AR+ST+Spring ≥ 60）→ 至少 60+（过 confirm 门槛）
      SC+AR+ST 完整（无 Spring，+65）→ 65（过门槛）
      仅 PS+SC（+40）→ 40（未达门槛）
      仅 PS（+10）→ 10
      无任何阶段 → 0

    证伪态（WYF-3 终态，当前即为此态）：`wyckoff_dimension_status()["status"]=="falsified"`
    时本函数**显式**返回恒 0 并一次性 log.warning 披露，不走"算了但没人知道恒零"。
    要绕过该出口做研究，用 `wyckoff_score_from_events`。

    Parameters
    ----------
    同 detect_wyckoff_events。

    Returns
    -------
    pd.Series，值 ∈ [0, 100]。
    """
    if _DIMENSION_STATUS["status"] == "falsified":
        return _falsified_zero_index(close.index)
    p = params or DEFAULT_WYCKOFF_PARAMS
    events = detect_wyckoff_events(close, high, low, volume, pct_change, vol_z, window, params=p)
    return wyckoff_score_from_events(events, p)
