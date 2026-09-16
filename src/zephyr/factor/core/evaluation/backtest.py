# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-03
# [MODULE] zephyr.factor.core.evaluation.backtest
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.table_registry; zephyr.factor.factor_base; zephyr.factor.core.evaluation.metrics; zephyr.shared.utils.market_units
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——ch_reader注入FINAL保证去重；前向收益shift(-horizon)仅用于回测评估不用于实盘信号；仅用trade_date做截面对齐禁止用ingested_at；
#              INV-UNIT-001(车道K 2026-09-16)：load_history 出口口径唯一真源=「volume 股 / 价格复权连续 / amount 元」，
#              量纲与复权只在出口归一一次（market_units），消费端禁再乘 100 或再乘因子
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH查询失败->返回空DataFrame(同ch_reader); 因子未注册->KeyError向上抛; 数据不足->EvaluationResult字段为0
# [TESTS] tests/factor/test_evaluation_backtest.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
D-FACTOR-03 因子评估回测运行器——端到端因子评估。

封装 ch_reader 数据访问 + metrics 纯函数计算，实现：
加载数据 → 逐标的计算因子值 → 组装面板 → 计算 IC/IR/OOS → 返回 EvaluationResult。

职责边界：
- 数据加载（ch_reader.query，自动注入 FINAL 保证 PIT 去重）
- **行情口径出口归一**（load_history 是全系统唯一的量纲/复权归一点——
  见 zephyr.shared.utils.market_units：volume 混存量纲逐行探测归一到股、
  价格改读后复权真值并按窗口末锚定；raw 价与原始 volume 保留在
  close_raw/open_raw/... 与 volume_lots 列，真实价语义（涨跌停价等）取 *_raw）
- 面板组装（长表 → 宽表面板）
- 因子计算调度（逐标的调用 FactorBase.compute）
- 评估指标汇总（调用 metrics.* 纯函数）

INV-004 PIT 铁律落实：
- ch_reader 对 ReplacingMergeTree 自动注入 FINAL，去重后查询
- 前向收益 shift(-horizon) 仅用于回测评估，不参与实盘信号生成
- 不使用 ingested_at（可能引入未来函数），仅用 trade_date 做截面对齐
- 复权锚点取**本窗已知**的末值（逐标的常数），不引入未来信息进入收益

# [ALGO_FLOW] external: docs/03_modules/_domain_factor/algo_flow/backtest.yaml
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
from zephyr.shared.utils.market_units import (
    MarketPanelReport,
    format_report,
    normalize_market_panel,
)

log = logging.getLogger(__name__)

# 表名真源：business_data_categories.yaml via table_registry（裁定 #ARCH-CH-024）
_TBL_KLINE_DAILY = get_registry().table("market_kline_daily")
# 后复权真值表（源 miniqmt/bdpan_hfq，任务 kline_daily_hfq_incremental）——复权唯一可用源
_TBL_KLINE_DAILY_HFQ = get_registry().table("market_kline_daily_hfq")

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀）
# ch_reader.query() 自动注入 FINAL（ReplacingMergeTree 去重），故 final 占位留空
_SQL_LOAD_HISTORY = (
    "SELECT trade_date, symbol, open, high, low, close, volume, amount, adj_factor "
    "FROM {tbl}{final} "
    "WHERE symbol IN ({symbols}) "
    "AND trade_date >= toDate('{start}') AND trade_date <= toDate('{end}') "
    "ORDER BY symbol, trade_date"
)

# 复权因子只需收盘价：adj_close/raw_close 给出逐日累计复权因子（同一标的比值即因子台阶）
_SQL_LOAD_ADJUSTED_CLOSE = (
    "SELECT trade_date, symbol, close "
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
_ADJUSTED_COLUMNS = ("trade_date", "symbol", "close")


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


def _parse_adjusted_close_tsv(tsv: str) -> pd.DataFrame:
    """解析后复权收盘价 TSV 为 MultiIndex(symbol, trade_date) 的 `close` 表。

    ch_reader 返回无表头 TSV，且调用方的 mock 可能把**其它列数**的行喂进来，
    故逐行做严格字段数校验（先例：`StkLimitProvider._SQL_STK_LIMIT_DAY` 解析环）。
    不匹配的行整行丢弃（宁可退化为"无复权源"——由调用方显式告警——也不把
    错位数据当复权真值用）。close<=0 / 非数值 / \\N 同样丢弃（后复权价为 0 无意义）。

    Returns:
        DataFrame(index=(symbol, trade_date), columns=[close])，无有效行时为空表。
    """
    rows: list[tuple[str, pd.Timestamp, float]] = []
    for line in (tsv or "").splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) != len(_ADJUSTED_COLUMNS):
            continue
        date_s, sym, close_s = parts[0].strip(), parts[1].strip(), parts[2].strip()
        if not sym or close_s in ("", "\\N", "NULL", "null"):
            continue
        try:
            close_v = float(close_s)
            date_v = pd.Timestamp(date_s)
        except ValueError:
            continue
        if close_v <= 0:
            continue
        rows.append((sym, date_v, close_v))
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows, columns=["symbol", "trade_date", "close"])
    df = df.drop_duplicates(subset=["symbol", "trade_date"], keep="last")
    return df.set_index(["symbol", "trade_date"]).sort_index()


def _load_adjusted_close(symbols: Sequence[str], start: str, end: str) -> pd.DataFrame | None:
    """读后复权收盘价（复权因子真值源）。无可用数据/查询失败 → None（调用方必告警）。

    为什么不用 `kline_daily.adj_factor`（tracker #197 原设计）：该列全史
    10,069,078 行中 `!= 1` 的行数 = 0（车道 K CH 只读实证，探针
    `.runtime/tmp/laneK_probe3.py`）——列从未回补，`close×adj_factor ≡ raw close`，
    #197 修正件自出生即惰性。`c1_market.adj_factor` 专表亦不可用：窗口后半段日行数
    由 ~7,000 塌到 9~21，且 2026-07 起多票因子被重定标（600036 6.4834→1.0274、
    000651 230.39→1.0505），跨重定标日相乘会注入 −68%~−84% 新幻影（#209② 根源）。
    """
    sql = _SQL_LOAD_ADJUSTED_CLOSE.format(
        tbl=_TBL_KLINE_DAILY_HFQ,
        final="",
        symbols=_format_symbols(symbols),
        start=start,
        end=end,
    )
    try:
        tsv = ch_reader.query(sql)
    except Exception as e:  # noqa: BLE001 — 复权源故障不得拖垮主链路，但必须显式告警
        log.warning(
            "后复权价查询失败（%s: %s），本窗退化为未复权价——除权日幻影缺口仍存在",
            type(e).__name__,
            e,
        )
        return None
    adj = _parse_adjusted_close_tsv(tsv)
    if adj.empty:
        return None
    return adj


def _log_panel_report(report: MarketPanelReport, context: str) -> None:
    """把归一披露件打成日志：任何口径风险必须**显式告警**，禁止静默算错。

    告警触发条件（任一）：量纲探测 suspect（多数行不可判定 或 归一后
    amount/(close×volume) 中位比越界 ±10%）、不可判定行需兜底、复权源缺失、
    存在完全无因子的标的。
    """
    line = format_report(report, context)
    v = report.volume
    problems: list[str] = []
    if v.suspect:
        problems.append("量纲自洽探测不通过（suspect）")
    if v.default_applied:
        problems.append(f"{v.default_applied} 行量纲不可判定，已按表声明口径（股）兜底")
    if not report.adjustment_enabled:
        problems.append("后复权因子源不可用，价格为**未复权原始价**（除权幻影未修）")
    elif report.unadjusted_symbols:
        problems.append(
            f"{report.unadjusted_symbols} 个标的（{report.unadjusted_rows} 行）无复权因子，"
            "该标的整窗退不复权"
        )
    if problems:
        log.warning("行情口径归一告警 %s：%s ｜ %s", context, "；".join(problems), line)
    else:
        log.info("行情口径归一 %s ｜ %s", context, line)


def load_history(
    symbols: Sequence[str],
    start: str,
    end: str,
    *,
    normalize_units: bool = True,
) -> pd.DataFrame:
    """从 ClickHouse 加载历史日 K 行情，并在**出口一次性**归一量纲与复权口径。

    Args:
        symbols: 标的代码列表（如 ['600519.SH', '000001.SZ']）
        start: 起始日期 'YYYY-MM-DD'
        end: 结束日期 'YYYY-MM-DD'
        normalize_units: 默认 True——出口口径为「volume=股 / 价格=复权连续 /
            amount=元」（INV-UNIT-001）。False 仅用于 A/B 复现修复前的 legacy
            原始口径（volume 手/股混存 + 未复权价），生产链路禁传。

    Returns:
        DataFrame，index=(symbol, trade_date) MultiIndex，
        columns=open/high/low/close/volume/amount/adj_factor（归一口径）
        + open_raw/high_raw/low_raw/close_raw（交易所原始价，真实价语义用）
        + volume_lots（源表原始混存量）。空结果返回空 DataFrame。
        `df.attrs[market_units.REPORT_ATTR]` 挂本次归一披露件。
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
    df = df.sort_index()
    if not normalize_units:
        log.warning("load_history(normalize_units=False)：绕过量纲/复权归一，仅用于 A/B 复验")
        return df
    adjusted = _load_adjusted_close(symbols, start, end)
    out, report = normalize_market_panel(df, adjusted=adjusted)
    _log_panel_report(report, f"load_history[{start}..{end}] {len(df)}行/{report.symbols}标的")
    return out


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

    车道 K（2026-09-16）口径变更：`load_history` 出口已把价格归一为**窗口末锚定的
    复权连续价**，`adj_factor` 重写为「本表 close 还原为后复权真值所需乘子」
    （逐标的常数 = 该标的窗口末 hfq/raw 比值）。于是
    `close × adj_factor ≡ kline_daily_hfq.close`（后复权真值），而逐标的常数在
    `P(t+1)/P(t)` 里抵消 → 前向收益与后复权口径**逐位相同**，除权幻影归零。
    当复权源不可用（退化为未复权路径）时，本函数的 `adj_factor` 就是源表原列直通
    （#197 原语义，实际恒 1，见 `_load_adjusted_close` 的为何改读 hfq 说明）。

    防御：adj_factor 为 NULL（ClickHouse Nullable，TSV \\N）或 <= 0（无效因子，
    裁定#ARCH-ADJFACTOR-NULL-001：0 视为 None）时回退 1.0，该行退化为不复权价，
    避免 NaN 污染收益面板。
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
