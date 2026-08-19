# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-03
# [MODULE] zephyr.factor.core.evaluation.backtest
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.table_registry; zephyr.factor.factor_base; zephyr.factor.core.evaluation.metrics
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——ch_reader注入FINAL保证去重；前向收益shift(-horizon)仅用于回测评估不用于实盘信号；仅用trade_date做截面对齐禁止用ingested_at
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH查询失败->返回空DataFrame(同ch_reader); 因子未注册->KeyError向上抛; 数据不足->EvaluationResult字段为0
# [TESTS] tests/factor/test_evaluation_backtest.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: symbol 列表 + factor_id + 评估日期区间（evaluate_factor 入参）
# I2: market_kline_daily 历史长表（ch_reader 注入 FINAL 保 PIT 去重，含 adj_factor 列）
# F1: _adjusted_close_panel 复权价面板（close×adj_factor，NULL/0/负回退 1.0，#197：除权日前向收益不再误判腰斩）
# A1: 数据加载+面板组装（长表→宽表，trade_date 截面对齐禁 ingested_at）
# A2: 逐标的 FactorBase.compute 因子值调度
# A3: _compute_forward_returns 前向收益（复权价 shift(-horizon)，仅回测评估不实盘）
# A4: metrics 纯函数汇总（IC/IR/OOS/分组收益）
# O1: EvaluationResult（IC/IR 等评估指标；数据不足字段为 0）
# [/ALGO_FLOW]
"""D-FACTOR-03 因子评估回测运行器——端到端因子评估。

封装 ch_reader 数据访问 + metrics 纯函数计算，实现：
加载数据 → 逐标的计算因子值 → 组装面板 → 计算 IC/IR/OOS → 返回 EvaluationResult。

职责边界：
- 数据加载（ch_reader.query，自动注入 FINAL 保证 PIT 去重）
- 面板组装（长表 → 宽表面板）
- 因子计算调度（逐标的调用 FactorBase.compute）
- 评估指标汇总（调用 metrics.* 纯函数）

INV-004 PIT 铁律落实：
- ch_reader 对 ReplacingMergeTree 自动注入 FINAL，去重后查询
- 前向收益 shift(-horizon) 仅用于回测评估，不参与实盘信号生成
- 不使用 ingested_at（可能引入未来函数），仅用 trade_date 做截面对齐
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from io import StringIO
from typing import Sequence

import pandas as pd

from zephyr.data import ch_reader
from zephyr.data.table_registry import get_registry
from zephyr.factor.core.evaluation.metrics import (
    check_overfitting,
    compute_ic_series,
    compute_ir,
    compute_oos_positive_rate,
)
from zephyr.factor.factor_base import FactorRegistry

log = logging.getLogger(__name__)

# 表名真源：business_data_categories.yaml via table_registry（裁定 #ARCH-CH-024）
_TBL_KLINE_DAILY = get_registry().table("market_kline_daily")

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀）
# ch_reader.query() 自动注入 FINAL（ReplacingMergeTree 去重），故 final 占位留空
_SQL_LOAD_HISTORY = (
    "SELECT trade_date, symbol, open, high, low, close, volume, amount, adj_factor "
    "FROM {tbl}{final} "
    "WHERE symbol IN ({symbols}) "
    "AND trade_date >= toDate('{start}') AND trade_date <= toDate('{end}') "
    "ORDER BY symbol, trade_date"
)

# TSV 列顺序（ClickHouse SELECT 返回无表头，按 SELECT 顺序映射）
_HISTORY_COLUMNS = [
    "trade_date",
    "symbol",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
    "adj_factor",
]


@dataclass(frozen=True)
class EvaluationResult:
    """因子评估结果容器。

    Attributes:
        factor_id: 因子ID
        ic_mean: IC 均值（样本内）
        ic_std: IC 标准差
        ir: 信息比率 = ic_mean / ic_std
        oos_positive_rate: 样本外 IC 正率
        is_overfitted: 是否判定过拟合（OOS_IC/IS_IC < 阈值）
        sample_size: 评估截面数（IC 序列长度）
    """

    factor_id: str
    ic_mean: float
    ic_std: float
    ir: float
    oos_positive_rate: float
    is_overfitted: bool
    sample_size: int


def _escape_symbol(symbol: str) -> str:
    """转义标的代码中的单引号，防 SQL 注入。"""
    return str(symbol).replace("'", "\\'")


def _strip_symbol_suffix(symbol: str) -> str:
    """去除 symbol 的交易所后缀，返回纯数字代码（600519.SH → 600519）。

    kline_daily.symbol 存储纯数字代码，调用方传入契约格式（600519.SH）时
    需先去后缀再查 DB。幂等：纯数字 symbol 原样返回。
    裁定#ARCH-SYMBOL-NORMALIZE-001（2026-07-25）：与 producer 对齐。
    """
    if not symbol:
        return symbol
    s = str(symbol).strip()
    return s.split(".")[0]


def _format_symbols(symbols: Sequence[str]) -> str:
    """格式化标的列表为 SQL IN 子句内容（'a','b','c'）。

    自动去除交易所后缀（600519.SH → 600519），匹配 kline_daily 纯数字存储。
    """
    escaped = [_escape_symbol(_strip_symbol_suffix(s)) for s in symbols if s]
    return ",".join(f"'{s}'" for s in escaped)


def _tsv_to_dataframe(tsv: str) -> pd.DataFrame:
    """解析 ch_reader 返回的 TSV 为 DataFrame（TSV 无表头，按列顺序映射）。

    symbol 列强制为 str（避免 "000001" 被解析为整数 1，丢失前导零）。
    ClickHouse Nullable 列的 NULL 在 TSV 中为 \\N，通过 na_values 转为 NaN。
    """
    if not tsv or not tsv.strip():
        return pd.DataFrame()
    df = pd.read_csv(
        StringIO(tsv),
        sep="\t",
        header=None,
        names=_HISTORY_COLUMNS,
        dtype={"symbol": str},
        na_values=["\\N"],
    )
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df


def load_history(symbols: Sequence[str], start: str, end: str) -> pd.DataFrame:
    """从 ClickHouse 加载历史日 K 行情。

    Args:
        symbols: 标的代码列表（如 ['600519.SH', '000001.SZ']）
        start: 起始日期 'YYYY-MM-DD'
        end: 结束日期 'YYYY-MM-DD'

    Returns:
        DataFrame，index=(symbol, trade_date) MultiIndex，
        columns=open/high/low/close/volume/amount/adj_factor。空结果返回空 DataFrame。
    """
    if not symbols:
        return pd.DataFrame()
    sql = _SQL_LOAD_HISTORY.format(
        tbl=_TBL_KLINE_DAILY,
        final="",
        symbols=_format_symbols(symbols),
        start=start,
        end=end,
    )
    df = _tsv_to_dataframe(ch_reader.query(sql))
    if df.empty:
        return df
    # 防御性去重：ReplacingMergeTree 即使注入 FINAL，极端情况下仍可能返回
    # 同一 (symbol, trade_date) 多行（版本未合并/并发写入）。此处兜底去重，
    # 避免下游 _compute_factor_panel 的 reindex 触发
    # "cannot reindex on an axis with duplicate labels"。
    df = df.drop_duplicates(subset=["symbol", "trade_date"], keep="last")
    df = df.set_index(["symbol", "trade_date"])
    return df.sort_index()


def _compute_factor_panel(factor_cls: type, history: pd.DataFrame) -> pd.DataFrame:
    """逐标的计算因子值，组装面板 (index=date, columns=symbol)。"""
    factor = factor_cls()
    values: dict[str, pd.Series] = {}
    for symbol, group in history.groupby(level="symbol"):
        values[str(symbol)] = factor.compute(group.droplevel("symbol"))
    if not values:
        return pd.DataFrame()
    return pd.DataFrame(values)


def _adjusted_close_panel(history: pd.DataFrame) -> pd.DataFrame:
    """构建复权收盘价面板 (index=trade_date, columns=symbol)。

    tracker #197：前向收益必须按复权价（adj_close = close × adj_factor）计算，
    否则除权日（如 10送10 价格腰斩）会被计为 -50% 真实亏损，系统性偏差 IC/IR。

    口径纪律——同行自洽乘法：仅保证同一行 close 与 adj_factor 自洽相乘。
    kline_daily.adj_factor 已知混存 QMT dr / 新浪 hfq 两口径（遗留 #209②，
    登记为 P2 后续治理），本函数不做口径归一。

    防御：adj_factor 为 NULL（ClickHouse Nullable，TSV \\N）或 <= 0（无效因子，
    裁定#ARCH-ADJFACTOR-NULL-001：0 视为 None）时回退 1.0，该行退化为不复权价
    （对齐 baostock 主口径：不复权写入 adj_factor=1），避免 NaN 污染收益面板。
    """
    adj = history["adj_factor"]
    # NaN > 0 为 False → NULL 与 0/负值一并被 where 替换为 1.0
    adj = adj.where(adj > 0, 1.0)
    return (history["close"] * adj).unstack(level="symbol")


def _compute_forward_returns(price_panel: pd.DataFrame, horizon: int) -> pd.DataFrame:
    """前向收益 = price.shift(-horizon) / price - 1。

    tracker #197：调用方须传入复权价面板（见 _adjusted_close_panel），
    传 raw close 会把除权日价格跳变计为真实盈亏。本函数只做位移比值纯计算。
    """
    return price_panel.shift(-horizon) / price_panel - 1


def _build_result(factor_id: str, ic_series: pd.Series, oos_ratio: float) -> EvaluationResult:
    """从 IC 序列构建评估结果。"""
    if ic_series.empty:
        return EvaluationResult(factor_id, 0.0, 0.0, 0.0, 0.0, True, 0)
    ic_mean = float(ic_series.mean())
    ic_std = float(ic_series.std(ddof=0))
    ir = compute_ir(ic_series)
    oos_rate = compute_oos_positive_rate(ic_series, oos_ratio)
    oos_count = max(1, int(len(ic_series) * oos_ratio))
    oos_ic_mean = float(ic_series.iloc[-oos_count:].mean())
    overfit = check_overfitting(ic_mean, oos_ic_mean)
    return EvaluationResult(factor_id, ic_mean, ic_std, ir, oos_rate, overfit, len(ic_series))


def evaluate_factor(
    factor_id: str,
    symbols: Sequence[str],
    start: str,
    end: str,
    horizon: int = 5,
    oos_ratio: float = 0.3,
) -> EvaluationResult:
    """端到端因子评估：加载数据 → 计算因子值 → 计算 IC/IR/OOS → 返回结果。

    Args:
        factor_id: 已注册的因子ID（FactorRegistry.get 查询）
        symbols: 评估标的池
        start: 回测起始日期 'YYYY-MM-DD'
        end: 回测结束日期 'YYYY-MM-DD'
        horizon: 前向收益周期（交易日），默认 5
        oos_ratio: 样本外比例，默认 0.3

    Returns:
        EvaluationResult。数据不足时各指标为 0，is_overfitted=True。

    Raises:
        KeyError: factor_id 未在 FactorRegistry 注册
    """
    factor_cls = FactorRegistry.get(factor_id)
    history = load_history(symbols, start, end)
    if history.empty:
        log.warning("evaluate_factor: 历史数据为空 factor=%s", factor_id)
        return _build_result(factor_id, pd.Series(), oos_ratio)
    factor_panel = _compute_factor_panel(factor_cls, history)
    # tracker #197：前向收益按复权价面板计算（close × adj_factor），
    # 修复除权日 raw close 腰斩被计为 -50% 真实亏损导致的 IC/IR 系统性偏差
    adj_close_panel = _adjusted_close_panel(history)
    return_panel = _compute_forward_returns(adj_close_panel, horizon)
    # 丢弃前向收益全 NaN 的尾部截面（无未来数据，避免注入 0 IC 噪声）
    return_panel = return_panel.dropna(how="all")
    ic_series = compute_ic_series(factor_panel, return_panel, horizon)
    return _build_result(factor_id, ic_series, oos_ratio)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def tsv_to_dataframe(tsv) -> pd.DataFrame:
    """公共接口：tsv_to_dataframe（Stage 4 公共化）。"""
    return _tsv_to_dataframe(tsv)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def format_symbols(symbols) -> str:
    """公共接口：format_symbols（Stage 4 公共化）。"""
    return _format_symbols(symbols)


# ── Stage 4 公共化（2026-07-30）：public wrapper for D_PORTFOLIO_CORE StrategyRunner ──
def compute_factor_panel(factor_cls: type, history: pd.DataFrame) -> pd.DataFrame:
    """公共接口：逐标的计算因子值并组装 (date×symbol) 面板。

    供 D_PORTFOLIO_CORE StrategyRunner 复用（裁定：策略层直连因子评估运行器，
    跳过已坏的 AlphaSignalPipeline）。包裹私有 _compute_factor_panel，行为不变。

    Args:
        factor_cls: FactorBase 子类（已 @FactorRegistry.register 注册）
        history: load_history() 返回的 MultiIndex(symbol, trade_date) DataFrame，
                 columns 至少含 close（动量类因子需要）

    Returns:
        DataFrame(index=trade_date, columns=symbol)，值为因子截面得分。
        空输入返回空 DataFrame。
    """
    return _compute_factor_panel(factor_cls, history)
