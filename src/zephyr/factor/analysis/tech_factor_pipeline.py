# [BLUEPRINT] MOD-L02-031 | master_tc_night C75（CNS-01 指标宽表→因子值计算链接线）
# [MODULE] zephyr.factor.analysis.tech_factor_pipeline
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.indicator_reader; zephyr.factor.analysis.multifactor_synthesis; pandas(pip)
# [CONSUMERS] （候选：ex_core/signal_providers 因子源升级位；dashboard/分析入口快照面）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] PIT 铁律透传（indicator_reader：end>as_of 硬拒；预热 NaN 不前向填充）；列名白名单双校验（TechnicalIndicatorRegistry 注册面，拼错即 ValueError）；输入校验 fail-closed（空列集/非法 method 即拒）；合成经既有 synthesize() 单一入口（禁第二套合成算法）；本模块只建"读宽表→因子值→合成信号"计算链，不承诺 IC 证据——IC 证据须 CH 实弹跑批（消费诚实铁律：链可达≠证据在册，禁造假消费）
# [MODIFY-GUARD] master_tc_night/lanes/L6_factory/00_workbook.md C75 节
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（空列/白名单外列/非法 method，透传 indicator_reader 的 PIT/参数校验）
# [TESTS] tests/factor/test_tech_factor_pipeline.py
# [A_module] module_id=MOD-L02-031 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""TECH 因子计算链——指标宽表→因子值→合成信号（MOD-L02-031，CNS-01 接线件）。

CNS-01 处方（14_consumption_census §五）："为 FCT-TECH-061/062/070/071/077/083/085
等 TDM 已声明 TECH 因子建计算链（读指标宽表→因子值）"，验收=至少 3 条出 IC 证据。
实态（2026-10-07 复核）：indicator_reader（Handler 层）与 multifactor_synthesis
（合成层）各自在册且各有消费者（ex_core/signal_providers 消费合成层），但
**两层之间的"宽表→因子值"腿零代码**——L3 生产可达=0。

本模块即那条缺失的腿（最小消费面）：

    read_indicator（PIT 宽表读取）
      → build_tech_factor_values（宽表列 → factor_id→Series 面板）
      → synthesize（既有合成单一入口）
    = synthesize_tech_signal（分析入口一键链）

**消费诚实声明（禁造假消费）**：本链落码=计算路径可达（L3 前置）；
IC 证据验收（≥3 条 FCT-TECH 出 IC）须 CH 实弹跑批后回填 factor_registry
的 code_path/证据位——本模块 docstring 即登记位，跑批归 CH 复活后实弹批
（91_progress §③-5 同窗）。默认列集映射 FCT-TECH-062（乖离率族 bias_6/12/24）
+动量族（rsi_6/macd_hist），均为 TechnicalIndicatorRegistry 在册输出列。

依据: decision_map_campaign_20260924/14_consumption_census.md §五 CNS-01；
17_quantified_acceptance.md §CNS-01。
SSoT: depgraph node MOD-L02-031（随本批 apply_depgraph 登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: symbol + 指标列集 + 时间窗（PIT as_of 可选）
# 特征: 宽表列 DataFrame
# 算法: 列→Series 面板（drop 辅助列）→ synthesize 统一入口
# 输出: 因子值面板 / 合成信号 Series
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Final, Sequence

import pandas as pd

from zephyr.factor.analysis.multifactor_synthesis import synthesize
from zephyr.factor.indicator_reader import read_indicator

logger = logging.getLogger(__name__)

__all__: Final = [
    "DEFAULT_TECH_COLUMNS",
    "SYNTH_METHODS",
    "build_tech_factor_values",
    "synthesize_tech_signal",
]

# FCT-TECH 已声明链默认列集（全部在 TechnicalIndicatorRegistry 白名单；
# bias 族=FCT-TECH-062 乖离率族，rsi_6/macd_hist=动量族代表列）
DEFAULT_TECH_COLUMNS: Final = ("bias_6", "bias_12", "bias_24", "rsi_6", "macd_hist")

SYNTH_METHODS: Final = ("equal_weight", "ic_weighted", "regression")

_AUX_COLS: Final = ("trade_date", "trade_time", "symbol", "period")


def build_tech_factor_values(
    symbol: str,
    columns: Sequence[str] = DEFAULT_TECH_COLUMNS,
    start: str | date | datetime | None = None,
    end: str | date | datetime | None = None,
    as_of: str | date | datetime | None = None,
    period: str = "daily",
) -> dict[str, pd.Series]:
    """指标宽表列 → factor_id→Series 因子值面板（CNS-01 缺失腿）。

    Args:
        symbol: 裸码（透传 indicator_reader）。
        columns: 指标输出列子集（白名单双校验；默认 FCT-TECH 声明链）。
        start/end/as_of/period: 透传 indicator_reader（PIT 硬拒语义不变）。

    Returns:
        dict：列名 → pd.Series（去 NaN 后的因子值序列；空表→空 dict）。

    Raises:
        ValueError: 空列集 / 白名单外列（透传 read_indicator）。
    """
    cols = tuple(columns)
    if not cols:
        raise ValueError("columns 不能为空（fail-closed）")
    df = read_indicator(symbol=symbol, period=period, columns=list(cols), start=start, end=end, as_of=as_of)
    if df.empty:
        logger.info("build_tech_factor_values: %s 空返回（宽表无数据/预热期）", symbol)
        return {}
    panel: dict[str, pd.Series] = {}
    for c in cols:
        if c not in df.columns:
            raise ValueError(f"宽表返回缺列 {c!r}（读层与白名单漂移，fail-closed）")
        s = df[c].dropna()
        if not s.empty:
            panel[c] = s
    logger.info("build_tech_factor_values: %s %d/%d 列非空", symbol, len(panel), len(cols))
    return panel


def synthesize_tech_signal(
    symbol: str,
    columns: Sequence[str] = DEFAULT_TECH_COLUMNS,
    method: str | None = None,
    start: str | date | datetime | None = None,
    end: str | date | datetime | None = None,
    as_of: str | date | datetime | None = None,
    period: str = "daily",
    **synth_kwargs,
) -> pd.Series:
    """一键链：宽表→因子值→合成信号（分析入口；合成经既有 synthesize 单一入口）。

    Args:
        method: equal_weight/ic_weighted/regression；None=配置默认（透传 synthesize）。
        **synth_kwargs: 方法特定参数（ic_weights/forward_returns）。

    Returns:
        合成信号 Series（链上任一环空→空 Series，不造信号）。

    Raises:
        ValueError: 非法 method / 白名单外列（fail-closed）。
    """
    if method is not None and method not in SYNTH_METHODS:
        raise ValueError(f"非法 method: {method}（可选 {SYNTH_METHODS}）")
    panel = build_tech_factor_values(symbol=symbol, columns=columns, start=start, end=end, as_of=as_of, period=period)
    if not panel:
        return pd.Series(dtype=float)
    signal = synthesize(panel, method=method, **synth_kwargs)
    logger.info("synthesize_tech_signal: %s method=%s → %d 点", symbol, method, len(signal))
    return signal
