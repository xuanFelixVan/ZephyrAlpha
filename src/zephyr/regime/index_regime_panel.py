# [BLUEPRINT] MOD-REGIME-008 | 待统筹登记（architecture_review_2026_08_module_upgrade_audit §11.5 IDX-01）
# [MODULE] zephyr.regime.index_regime_panel
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; sklearn(RobustScaler,可选); zephyr.data.ch_reader; zephyr.data.table_registry; zephyr.regime.core.regime_detector; zephyr.regime.regime_feature_builder; zephyr.regime.features.market_features; zephyr.regime.features.trend_features; zephyr.regime.features.regime_data_loader
# [CONSUMERS] IDX-02(Dashboard 四指数状态卡，随前端批落地)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 只输出regime概率分布与强弱排序,严禁输出点位/方向预测(90号§7铁律:点预测52-53%天花板+T+1兑现悖论); 每卡probabilitiesΣ=1.0且键集=REGIME_STATES(7态); 单指数缺数据该卡degraded不炸面板; 全指数缺数据面板级degraded; PIT严格(detect(t)只用≤t-1特征,与MOD-REGIME-002 blueprint §6.1一致); 4套配置非4套模型(同一RegimeDetector类+同一hmm_params+同一6特征族)
# [MODIFY-GUARD] none
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] IndexRegimePanelError(非法配置/SQL加载层异常被调用方要求上抛时); 数据缺失/拟合失败不抛错→卡片degraded降级
# [TESTS] tests/regime/test_index_regime_panel.py
# [A_module] module_id=MOD-REGIME-008 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #architecture_review_2026_08_module_upgrade_audit §11.3裁定一(1引擎×4代理) #§11.5 IDX-01 #92_phase2_business_construction_order §7.9 #MOD-REGIME-001 #MOD-REGIME-002
"""MOD-REGIME-008 IndexRegimePanel — 四指数 regime 面板（1 引擎 × 4 代理）。

设计真源（architecture_review_2026_08_module_upgrade_audit §11.3 裁定一）：
  四指数**不建 4 个独立预测模型**，建"1 引擎 × 4 代理"的 regime 面板：
  同一 HMM 框架（RegimeDetector 类 + 同一 hmm_params + 同一 6 特征族）按 4 个
  代理指数（000300 沪深300 / 000001 上证指数 / 399006 创业板指 / 000688 科创50）
  分别出 regime 概率分布 + 四指数强弱排序 + 背离警示（黄白线/权重掩护，消费 44 号
  M1-② distortion 结果或自算简版）。90 号 §7 铁律：点预测 52-53% 天花板 + T+1
  兑现悖论——本模块**只输出概率分布与排序，严禁输出点位/方向预测**。

耦合度实证与实现路径裁定（2026-08-22，读本模块施工前实证）：
  - RegimeFeatureBuilder 的 000300 **未写死**：market_proxy/cross_asset_indices/
    breadth_index 均为构造注入点，单指数耦合度低；
  - 但其数据层直连模块级 ch_reader.query（无 client 注入点），且 build_features()
    为全区间回测级构建——与面板"as-of 单日 + ch_client 可注入"的形态不合；
  - 故裁定**轻适配层路径**：数据加载由本模块自控（ch_client 注入，SQL 常量 +
    TableRegistry 真源表名），特征计算**逐函数复用** MOD-REGIME-002 的 6 个
    production 特征函数（realized_vol_pct / hurst_dfa / kalman_slope /
    cross_asset_corr / ad_ratio / volume_anomaly，公式零分叉），HMM 引擎复用
    RegimeDetector 本体（fit/detect 公共接口，零侵入）。

特征口径（与 MOD-REGIME-002 §3 同族，列序钉死 = FEATURE_NAMES）：
  F1 realized_vol_pct / F5 volume_anomaly / F2a hurst_dfa / F2b kalman_slope
    —— 用**各代理指数自身** close/volume（单指数特异维度）；
  F3 cross_asset_corr（三大指数 60 日相关）/ F4 ad_ratio（399106 涨跌家数）
    —— 市场共享环境维度，四代理同值（与"1 引擎"语义一致：同一市场环境，
    不同指数载体）。

降级纪律（观测层不炸面板）：
  - 某指数 K 线缺失 / 样本不足 / HMM 拟合失败 → 该卡 degraded=True +
    degrade_reason，probabilities 退化为引擎降级语义的无信息先验
    （r1-r4 各 1/4、r10-r12 为 0，Σ=1，与 RegimeDetector §7.4 降级输出同构）；
  - 全部指数缺数据 → 面板级 degraded=True，strength_ranking 为空；
  - 配置非法（如 proxies 为空）→ 抛 IndexRegimePanelError（配置错误 fail-fast）。

PIT 铁律：detect(as_of) 只用 ≤ as_of-1 的特征（features.shift(1)，与
MOD-REGIME-002 build_shrinkage_schedule 同款）；强弱排序用 ≤ as_of 的**已实现**
收益/波动（盘后事实，非预测）。

输出：IndexRegimePanel（frozen dataclass，to_dict/to_json 可 JSON 序列化），
供 IDX-02 Dashboard 四指数状态卡消费（观测层，不接交易，B-007 零风险）。

依据: architecture_review_2026_08_module_upgrade_audit §11.3/§11.5 /
92_phase2_business_construction_order §7.9 / 90号 §7（点预测铁律）
SSoT: depgraph MOD-REGIME-008
Version: 0.1.0
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import asdict, dataclass, field, replace
from typing import Any, Callable, Mapping

import numpy as np
import pandas as pd

from zephyr.data import ch_reader
from zephyr.data.table_registry import get_registry
from zephyr.regime.core.regime_detector import (
    HMM_STATES,
    OVERLAY_STATES,
    REGIME_STATES,
    RegimeDetector,
)
from zephyr.regime.features.market_features import (
    ad_ratio,
    cross_asset_corr,
    realized_vol_pct,
    volume_anomaly,
)
from zephyr.regime.features.regime_data_loader import parse_tsv
from zephyr.regime.features.trend_features import hurst_dfa, kalman_slope
from zephyr.regime.regime_feature_builder import FEATURE_NAMES, RegimeFeatureBuilder

try:
    from sklearn.preprocessing import RobustScaler
except ImportError:  # pragma: no cover
    RobustScaler = None  # type: ignore[assignment,misc]

try:
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # noqa: BLE001  # pragma: no cover
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)


class IndexRegimePanelError(ZephyrBaseError):
    """四指数 regime 面板错误（非法配置等 fail-fast 场景）。

    数据缺失/HMM 拟合失败不抛错——走卡片 degraded 降级（观测层不炸面板）。
    错误码待统筹登记（本期不写注册表 yaml，同 MOD-REGIME-007 先例）。
    """


# ──────────────────────────────────────────────────────────────────────────────
# 4 代理配置（config 化：4 套配置非 4 套模型——同一 RegimeDetector 类 + 同一 hmm_params）
# ──────────────────────────────────────────────────────────────────────────────

# 四代理指数（IDX-01 钉死：000300/000001/399006/000688），插入序即面板卡序
INDEX_PROXIES: dict[str, str] = {
    "000300": "沪深300",
    "000001": "上证指数",
    "399006": "创业板指",
    "000688": "科创50",
}

# F3 跨资产相关性指数（市场共享环境维度，与 MOD-REGIME-002 默认一致）
_DEFAULT_CROSS_ASSET: tuple[str, ...] = ("000300", "000905", "399006")
# F4 涨跌家数源（399106 深证综指，市场共享环境维度）
_DEFAULT_BREADTH = "399106"

# 指数 K 线查询（NO-BARE-SQL gate 豁免：_SQL_ 前缀常量；表名经 TableRegistry 真源解析）
_SQL_INDEX_KLINE = (
    "SELECT trade_date, symbol, open, high, low, close, volume, "
    "advance_count, decline_count "
    "FROM {table} FINAL "
    "WHERE symbol IN ({symbols}) "
    "AND trade_date >= toDate('{start}') "
    "AND trade_date <= toDate('{end}') "
    "ORDER BY symbol, trade_date"
)

# HMM 特征滚动窗口（F2a/F2b，与 MOD-REGIME-002 钉死值一致）
_TREND_WINDOW = 200
# detect trailing 窗口最小行数（与 MOD-REGIME-002 build_shrinkage_schedule 同款阈值）
_MIN_DETECT_ROWS = 10


@dataclass(frozen=True)
class IndexProxyConfig:
    """单代理指数配置（一套配置 ≠ 一套模型：引擎/特征族/超参全共享）。

    Attributes:
        code: 指数代码（kline_index.symbol）。
        name: 中文名（面板展示）。
        cross_asset_indices: F3 跨资产相关性指数集（市场共享维度，默认与
            MOD-REGIME-002 一致）。
        breadth_index: F4 涨跌家数源（市场共享维度，默认 399106）。
        enabled: 是否纳入面板（False 时该代理不出卡）。
    """

    code: str
    name: str
    cross_asset_indices: tuple[str, ...] = _DEFAULT_CROSS_ASSET
    breadth_index: str = _DEFAULT_BREADTH
    enabled: bool = True


def _default_proxies() -> tuple[IndexProxyConfig, ...]:
    """默认 4 代理（IDX-01 钉死清单，插入序 = INDEX_PROXIES 声明序）。"""
    return tuple(IndexProxyConfig(code=code, name=name) for code, name in INDEX_PROXIES.items())


@dataclass(frozen=True)
class IndexRegimePanelConfig:
    """面板计算配置。

    Attributes:
        proxies: 代理指数配置集（默认 IDX-01 四代理）。
        train_years: HMM 训练窗口年数（as_of 回看，与 MOD-REGIME-002 walk-forward
            单季训练窗同款）。
        detect_window: detect 时 trailing 特征窗口（给 HMM 序列上下文）。
        min_train_samples: 训练矩阵最小行数（dropna 后，与 MOD-REGIME-002 ≥100 同族）。
        data_load_start: K 线加载起始日（需覆盖 train_years + 特征 warmup ~270 日）。
        hmm_params: HMM 超参（4 代理共享同一份；None=RegimeDetector 默认 4 态）。
        rank_window: 强弱排序的近期收益/波动窗口（交易日数）。
        standardize_features: 是否 RobustScaler 标准化（PIT：scaler 只见训练窗口）。
        enable_simple_divergence: 是否自算简版权重掩护背离（指数涨但跌家数>涨家数）。
            m1_distortion 注入与本开关独立——注入结果总会转为警示，本开关控制自算。
    """

    proxies: tuple[IndexProxyConfig, ...] = field(default_factory=_default_proxies)
    train_years: int = 5
    detect_window: int = 60
    min_train_samples: int = 100
    data_load_start: str = "2010-01-01"
    hmm_params: dict[str, Any] | None = None
    rank_window: int = 20
    standardize_features: bool = True
    enable_simple_divergence: bool = True


# ──────────────────────────────────────────────────────────────────────────────
# 面板输出契约（frozen dataclass，JSON 可序列化）
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DivergenceAlert:
    """背离警示（黄白线剪刀差/权重掩护）。

    kind:
      - "m1_distortion_guard"        — M1-②a 护盘假象（注入）
      - "m1_distortion_weight_cover" — M1-②b 权重掩护（注入）
      - "m1_distortion"              — M1-② 失真（注入，无细分字段时）
      - "weight_cover_simple"        — 自算简版：指数涨但跌家数>涨家数
    """

    kind: str
    index_code: str | None  # None = 市场级（M1-② 注入）；自算简版 = 触发指数代码
    trade_date: str
    detail: str  # 中文描述（可审计、可直接上卡）
    severity: str = "warn"


@dataclass(frozen=True)
class IndexRegimeCard:
    """单指数 regime 卡（面板的一格）。

    probabilities 契约：键集 = REGIME_STATES（r1-r4 + r10-r12 共 7 态），Σ=1.0；
    degraded 卡为无信息先验（r1-r4 各 1/4、r10-r12 为 0，与 RegimeDetector §7.4
    降级输出同构）——**只表达状态概率分布，不是点位/方向预测**。

    Attributes:
        code/name: 指数代码/中文名。
        trade_date: 该卡数据截止交易日（该指数在库 ≤ 面板日的最后交易日）。
        probabilities: 7 态 regime 概率分布（Σ=1）。
        dominant_regime: max(P) 对应态（degraded 时为并列首态，无语义）。
        confidence: max(P) 值。
        recent_return: 近 rank_window 日累计对数收益（≤ as_of 已实现事实）。
        volatility: 近 rank_window 日日收益 std × √252（年化）。
        strength_score: 强弱分 = recent_return / (volatility + ε)（收益/波动调整）。
        rank: 强弱排序位次（1=最强；degraded/无数据卡为 None）。
        degraded: 该卡是否降级（缺数据/样本不足/加载失败）。
        degrade_reason: 降级原因（中文，None=未降级）。
        hmm_degraded: HMM 拟合失败降级标记（特征足但 fit 失败，概率为均匀先验）。
    """

    code: str
    name: str
    trade_date: str | None
    probabilities: dict[str, float]
    dominant_regime: str
    confidence: float
    recent_return: float | None
    volatility: float | None
    strength_score: float | None
    rank: int | None
    degraded: bool
    degrade_reason: str | None
    hmm_degraded: bool = False


@dataclass(frozen=True)
class IndexRegimePanel:
    """四指数 regime 面板（IDX-01 输出契约，frozen，JSON 可序列化）。

    Attributes:
        trade_date: 面板交易日（入参 as-of；None 入参时 = 各卡在库最新日的最大者，
            全缺时为加载截止日）。
        cards: 四指数卡（顺序 = config.proxies 声明序）。
        strength_ranking: 强弱排序（指数代码降序，最强在前；仅含非 degraded 且
            strength_score 有效的卡）。
        divergence_alerts: 背离警示（M1-② 注入 + 自算简版）。
        degraded: 面板级降级标记（True = 全部指数卡均 degraded）。
    """

    trade_date: str
    cards: tuple[IndexRegimeCard, ...]
    strength_ranking: tuple[str, ...]
    divergence_alerts: tuple[DivergenceAlert, ...]
    degraded: bool
    schema_version: str = "1.0"

    def to_dict(self) -> dict[str, Any]:
        """转纯 dict（tuple 递归转 list），供 JSON 序列化/前端消费。"""
        return asdict(self)

    def to_json(self) -> str:
        """转 JSON 字符串（ensure_ascii=False 保中文）。"""
        return json.dumps(self.to_dict(), ensure_ascii=False)


# ──────────────────────────────────────────────────────────────────────────────
# 引擎入口
# ──────────────────────────────────────────────────────────────────────────────


def compute_index_regime_panel(
    trade_date: str | None = None,
    ch_client: Callable[[str], str] | Any | None = None,
    config: IndexRegimePanelConfig | None = None,
    *,
    m1_distortion: Any = None,
) -> IndexRegimePanel:
    """计算四指数 regime 面板（1 引擎 × 4 代理）。

    流程：加载 4 代理 + F3/F4 共享指数日 K → 每代理按同一 6 特征族构建特征
    （PIT shift(1)）→ 同一 RegimeDetector 框架各 fit/detect → 7 态概率分布卡
    → 强弱排序（近期收益/波动调整）→ 背离警示（M1-② 注入 + 自算简版）。

    Args:
        trade_date: 面板 as-of 日（"YYYY-MM-DD"），None = 各指数在库最新交易日。
        ch_client: ClickHouse 查询注入（callable: sql → TSV 字符串，或带
            .query(sql) 方法的对象）；None = zephyr.data.ch_reader.query。
        config: 面板配置（None = 默认 IDX-01 四代理配置）。
        m1_distortion: 可选 M1-② 失真检测结果注入
            （market_sentiment_analyzer.DistortionDetectionResult 或同名字段 dict；
            distortion_flag=True 时转背离警示，index_code=None 市场级）。

    Returns:
        IndexRegimePanel（frozen，to_dict/to_json 可序列化）。

    Raises:
        IndexRegimePanelError: 配置非法（proxies 空/参数越界）——fail-fast。
            数据缺失/查询失败/HMM 拟合失败**不抛错**，走卡片/面板 degraded。
    """
    cfg = config or IndexRegimePanelConfig()
    _validate_config(cfg)
    query_fn = _resolve_query_fn(ch_client)

    end = trade_date or pd.Timestamp.now().strftime("%Y-%m-%d")
    index_df = _load_index_kline(query_fn, cfg, end)

    cards = tuple(
        _compute_card(proxy, index_df, cfg, trade_date)
        for proxy in cfg.proxies
        if proxy.enabled
    )

    # 强弱排序：非 degraded 且 strength_score 有效的卡按 score 降序
    ranked = sorted(
        (c for c in cards if not c.degraded and c.strength_score is not None),
        key=lambda c: c.strength_score,  # type: ignore[arg-type]
        reverse=True,
    )
    rank_of = {c.code: i + 1 for i, c in enumerate(ranked)}
    cards = tuple(replace(c, rank=rank_of.get(c.code)) for c in cards)
    strength_ranking = tuple(c.code for c in ranked)

    alerts = _build_divergence_alerts(cards, index_df, cfg, m1_distortion)

    panel_trade_date = trade_date or max(
        (c.trade_date for c in cards if c.trade_date), default=end
    )
    panel_degraded = bool(cards) and all(c.degraded for c in cards)
    panel = IndexRegimePanel(
        trade_date=panel_trade_date,
        cards=cards,
        strength_ranking=strength_ranking,
        divergence_alerts=alerts,
        degraded=panel_degraded,
    )
    _logger.info(
        "四指数 regime 面板: date=%s, 卡=%d (degraded=%d), 排序=%s, 警示=%d",
        panel.trade_date,
        len(cards),
        sum(1 for c in cards if c.degraded),
        list(strength_ranking),
        len(alerts),
    )
    return panel


# ──────────────────────────────────────────────────────────────────────────────
# 私有：配置校验 / 查询注入 / 数据加载
# ──────────────────────────────────────────────────────────────────────────────


def _validate_config(cfg: IndexRegimePanelConfig) -> None:
    """配置 fail-fast 校验（数据问题不在这里——走 degraded）。"""
    if not cfg.proxies:
        raise IndexRegimePanelError("proxies 为空——面板至少需 1 个代理指数")
    if not any(p.enabled for p in cfg.proxies):
        raise IndexRegimePanelError("全部代理 enabled=False——面板无卡可出")
    if cfg.train_years < 1:
        raise IndexRegimePanelError(f"train_years 需 ≥1，实际 {cfg.train_years}")
    if cfg.detect_window < _MIN_DETECT_ROWS:
        raise IndexRegimePanelError(f"detect_window 需 ≥{_MIN_DETECT_ROWS}，实际 {cfg.detect_window}")
    if cfg.min_train_samples < 1:
        raise IndexRegimePanelError(f"min_train_samples 需 ≥1，实际 {cfg.min_train_samples}")
    if cfg.rank_window < 2:
        raise IndexRegimePanelError(f"rank_window 需 ≥2，实际 {cfg.rank_window}")


def _resolve_query_fn(ch_client: Callable[[str], str] | Any | None) -> Callable[[str], str]:
    """把 ch_client 归一为 query callable（sql → TSV）；None → ch_reader.query。"""
    if ch_client is None:
        return ch_reader.query
    if callable(ch_client):
        return ch_client
    query = getattr(ch_client, "query", None)
    if callable(query):
        return query
    raise IndexRegimePanelError(
        f"ch_client 形态非法（需 callable 或带 .query 方法）: {type(ch_client).__name__}"
    )


def _load_index_kline(
    query_fn: Callable[[str], str],
    cfg: IndexRegimePanelConfig,
    end: str,
) -> pd.DataFrame | None:
    """加载 4 代理 + F3/F4 共享指数日 K（MultiIndex(symbol, trade_date)）。

    查询失败/无行 → None（调用方走全卡 degraded，不炸面板）。
    表名经 TableRegistry 真源解析（fail-closed，禁硬编码表名）。
    """
    symbols = sorted(
        {p.code for p in cfg.proxies if p.enabled}
        | {s for p in cfg.proxies if p.enabled for s in p.cross_asset_indices}
        | {p.breadth_index for p in cfg.proxies if p.enabled}
    )
    syms_str = ", ".join(f"'{s}'" for s in symbols)
    try:
        table = get_registry().table("market_index_kline")
    except Exception as exc:  # noqa: BLE001 — 注册表不可用 → 全卡 degraded
        _logger.warning("market_index_kline 表名解析失败（注册表不可用）: %s", exc)
        return None
    sql = _SQL_INDEX_KLINE.format(table=table, symbols=syms_str, start=cfg.data_load_start, end=end)
    try:
        tsv = query_fn(sql)
    except Exception as exc:  # noqa: BLE001 — 查询失败 → 全卡 degraded
        _logger.warning("index_kline 查询失败（全卡 degraded）: %s", exc)
        return None
    rows = parse_tsv(tsv, ncols=9)
    if not rows:
        _logger.warning("index_kline 查询为空: symbols=%s, [%s, %s]", symbols, cfg.data_load_start, end)
        return None
    cols = ["trade_date", "symbol", "open", "high", "low", "close", "volume", "advance_count", "decline_count"]
    df = pd.DataFrame(rows, columns=cols)
    df["trade_date"] = pd.to_datetime(df["trade_date"])
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["advance_count"] = pd.to_numeric(df["advance_count"], errors="coerce").fillna(0)
    df["decline_count"] = pd.to_numeric(df["decline_count"], errors="coerce").fillna(0)
    return df.set_index(["symbol", "trade_date"]).sort_index()


# ──────────────────────────────────────────────────────────────────────────────
# 私有：单代理卡片计算（特征 → HMM → 概率 + 强弱分）
# ──────────────────────────────────────────────────────────────────────────────


def _uniform_probabilities() -> dict[str, float]:
    """无信息先验（与 RegimeDetector §7.4 降级输出同构）：r1-r4 各 1/4，r10-r12 为 0。"""
    n = len(HMM_STATES)
    probs = {s: 1.0 / n for s in HMM_STATES}
    probs.update({s: 0.0 for s in OVERLAY_STATES})
    return probs


def _degraded_card(proxy: IndexProxyConfig, reason: str, as_of: str | None = None) -> IndexRegimeCard:
    """构造 degraded 卡（概率=无信息先验，Σ=1 契约保持，不炸面板）。"""
    probs = _uniform_probabilities()
    return IndexRegimeCard(
        code=proxy.code,
        name=proxy.name,
        trade_date=as_of,
        probabilities=probs,
        dominant_regime=max(probs, key=lambda k: probs[k]),
        confidence=max(probs.values()),
        recent_return=None,
        volatility=None,
        strength_score=None,
        rank=None,
        degraded=True,
        degrade_reason=reason,
        hmm_degraded=False,
    )


def _compute_card(
    proxy: IndexProxyConfig,
    index_df: pd.DataFrame | None,
    cfg: IndexRegimePanelConfig,
    trade_date: str | None,
) -> IndexRegimeCard:
    """单代理卡：6 特征（PIT shift）→ RegimeDetector fit/detect → 7 态概率 + 强弱分。"""
    if index_df is None:
        return _degraded_card(proxy, "index_kline 数据加载失败/为空", as_of=trade_date)
    try:
        kline = index_df.xs(proxy.code, level="symbol")
    except KeyError:
        return _degraded_card(proxy, f"指数 {proxy.code} 无 K 线数据", as_of=trade_date)
    if trade_date is not None:
        kline = kline.loc[:trade_date]
    if kline.empty:
        return _degraded_card(proxy, f"指数 {proxy.code} 在 ≤{trade_date} 无 K 线数据", as_of=trade_date)

    as_of_ts = kline.index.max()
    as_of = as_of_ts.strftime("%Y-%m-%d")

    # ── 6 特征（逐函数复用 MOD-REGIME-002 production 特征函数，PIT 在 detect 前 shift）
    try:
        features = _build_proxy_features(proxy, index_df, kline, as_of_ts)
    except Exception as exc:  # noqa: BLE001 — 特征构建失败 → 该卡 degraded
        _logger.warning("指数 %s 特征构建失败: %s", proxy.code, exc)
        return _degraded_card(proxy, f"特征构建失败: {exc}", as_of=as_of)

    # PIT 铁律：detect(as_of) 只用 ≤ as_of-1 特征（与 MOD-REGIME-002 同款 shift(1)）
    features_shifted = features.shift(1)

    # ── 训练窗口（as_of 回看 train_years，dropna 去 warmup）
    train_start = (as_of_ts - pd.DateOffset(years=cfg.train_years)).strftime("%Y-%m-%d")
    train = features_shifted.loc[train_start:as_of].dropna()
    if len(train) < cfg.min_train_samples:
        return _degraded_card(
            proxy,
            f"训练样本不足: [{train_start}, {as_of}] 仅 {len(train)} 行（需 ≥{cfg.min_train_samples}）",
            as_of=as_of,
        )
    X_train = np.nan_to_num(train[list(FEATURE_NAMES)].to_numpy(dtype=float), nan=0.0, posinf=0.0, neginf=0.0)

    # ── scaler（PIT：只 fit 训练窗口）
    scaler = None
    if cfg.standardize_features and RobustScaler is not None:
        try:
            scaler = RobustScaler().fit(X_train)
        except Exception as exc:  # noqa: BLE001 — scaler 失败降级不标准化
            _logger.warning("指数 %s RobustScaler 拟合失败，降级不标准化: %s", proxy.code, exc)
            scaler = None

    # ── HMM 引擎（同一 RegimeDetector 框架 + 同一 hmm_params；shrinkage 与观测层无关，关闭）
    detector = RegimeDetector(hmm_params=cfg.hmm_params, shrinkage_enabled=False)
    hmm_degraded = False
    try:
        detector.fit({"X": scaler.transform(X_train) if scaler is not None else X_train, "lengths": None})
    except Exception as exc:  # noqa: BLE001 — 拟合失败 → detect 自动降级均匀分布（§7.4）
        _logger.warning("指数 %s HMM 拟合失败，概率降级为均匀先验: %s", proxy.code, exc)
        hmm_degraded = True

    # ── detect 窗口（trailing detect_window，PIT 已 shift）
    window = features_shifted.loc[:as_of].iloc[-cfg.detect_window :]
    if len(window) < _MIN_DETECT_ROWS or window.dropna().empty:
        return _degraded_card(proxy, f"detect 窗口不足（{len(window)} 行）", as_of=as_of)
    X_detect = np.nan_to_num(window[list(FEATURE_NAMES)].to_numpy(dtype=float), nan=0.0, posinf=0.0, neginf=0.0)
    if scaler is not None:
        X_detect = scaler.transform(X_detect)
    try:
        probs, _shrinkage = detector.detect(
            {"X": X_detect},
            overlay_signals={},  # 观测层：纯 HMM 概率分布，不接 overlay 转换
            risk_signal_inputs={"params": {1: 1.0}, "opportunity": {}},  # risk=1.0 不干预
        )
    except Exception as exc:  # noqa: BLE001 — detect 异常 → 该卡 degraded
        _logger.warning("指数 %s detect 异常: %s", proxy.code, exc)
        return _degraded_card(proxy, f"detect 异常: {exc}", as_of=as_of)

    # ── 强弱分（≤ as_of 已实现收益/波动，盘后事实，非预测）
    recent_return, volatility, strength_score = _compute_strength(kline["close"].astype(float), cfg.rank_window)

    return IndexRegimeCard(
        code=proxy.code,
        name=proxy.name,
        trade_date=as_of,
        probabilities=dict(probs.probabilities),
        dominant_regime=probs.dominant_regime,
        confidence=float(probs.confidence),
        recent_return=recent_return,
        volatility=volatility,
        strength_score=strength_score,
        rank=None,  # 由面板组装层回填
        degraded=False,
        degrade_reason=None,
        hmm_degraded=hmm_degraded,
    )


def _build_proxy_features(
    proxy: IndexProxyConfig,
    index_df: pd.DataFrame,
    kline: pd.DataFrame,
    as_of: pd.Timestamp,
) -> pd.DataFrame:
    """按单指数序列构建 6 特征（列序 = FEATURE_NAMES，与 MOD-REGIME-002 钉死一致）。

    F1/F2a/F2b/F5 用**该代理指数自身** close/volume；F3/F4 为市场共享环境维度
    （cross_asset_indices 两两相关 + breadth_index 涨跌家数），四代理同值。
    """
    proxy_close = kline["close"].astype(float)
    proxy_volume = kline["volume"].astype(float)

    # F1 实现波动率分位 / F5 量能异动（该指数）
    f1 = realized_vol_pct(proxy_close)
    f5 = volume_anomaly(proxy_volume)
    # F2a Hurst / F2b Kalman（该指数，rolling 200——复用 builder 的滚动应用器）
    f2a = RegimeFeatureBuilder._rolling_apply(proxy_close, hurst_dfa, window=_TREND_WINDOW)
    f2b = RegimeFeatureBuilder._rolling_apply(proxy_close, kalman_slope, window=_TREND_WINDOW)

    # F3 跨资产相关性（市场共享：cross_asset_indices 两两 60 日相关均值）
    available = [s for s in proxy.cross_asset_indices if s in index_df.index.get_level_values(0)]
    if available:
        cross_close = index_df.loc[available]["close"].unstack("symbol")
        cross_returns = np.log(cross_close / cross_close.shift(1))
        f3 = cross_asset_corr(cross_returns, window=60)
    else:  # 共享指数全缺 → F3 全 NaN（训练 dropna 处理）
        f3 = pd.Series(np.nan, index=proxy_close.index)

    # F4 涨跌家数比（市场共享：breadth_index adv/dec，对齐到该指数交易日）
    try:
        br = index_df.xs(proxy.breadth_index, level="symbol")
        adv = br["advance_count"].reindex(proxy_close.index).fillna(0.0)
        dec = br["decline_count"].reindex(proxy_close.index).fillna(0.0)
    except KeyError:
        adv = pd.Series(0.0, index=proxy_close.index)
        dec = pd.Series(0.0, index=proxy_close.index)
    f4 = ad_ratio(adv, dec)

    features = pd.DataFrame(
        {
            "realized_vol_pct": f1,
            "hurst_dfa": f2a,
            "kalman_slope": f2b,
            "cross_asset_corr": f3,
            "ad_ratio": f4,
            "volume_anomaly": f5,
        }
    )
    return features.loc[:as_of].sort_index()


def _compute_strength(close: pd.Series, rank_window: int) -> tuple[float | None, float | None, float | None]:
    """强弱分：近 rank_window 日累计对数收益 / 年化波动（收益/波动调整，类 Sharpe）。

    用 ≤ as_of 的已实现收盘（盘后事实，非预测）。有效收益不足 2 个 → 全 None。
    """
    window_close = close.dropna().iloc[-(rank_window + 1) :]
    if len(window_close) < 3:
        return None, None, None
    rets = np.log(window_close / window_close.shift(1)).dropna()
    if len(rets) < 2:
        return None, None, None
    recent_return = float(rets.sum())
    volatility = float(rets.std(ddof=0) * math.sqrt(252))
    strength_score = recent_return / (volatility + 1e-6)
    return recent_return, volatility, strength_score


# ──────────────────────────────────────────────────────────────────────────────
# 私有：背离警示（M1-② 注入 + 自算简版）
# ──────────────────────────────────────────────────────────────────────────────


def _extract_field(obj: Any, key: str) -> Any:
    """从 dataclass 对象或 dict 提取字段（M1-② 注入形态兼容层）。"""
    if obj is None:
        return None
    if isinstance(obj, Mapping):
        return obj.get(key)
    return getattr(obj, key, None)


def _build_divergence_alerts(
    cards: tuple[IndexRegimeCard, ...],
    index_df: pd.DataFrame | None,
    cfg: IndexRegimePanelConfig,
    m1_distortion: Any,
) -> tuple[DivergenceAlert, ...]:
    """背离警示汇总：M1-② 注入（市场级）+ 自算简版（逐指数权重掩护）。"""
    alerts: list[DivergenceAlert] = []

    # ── 路径 1：M1-② distortion 注入（优先证据源，市场级 index_code=None）
    if m1_distortion is not None:
        flag = _extract_field(m1_distortion, "distortion_flag")
        panel_date = max((c.trade_date for c in cards if c.trade_date), default="")
        if flag:
            guard_illusion = bool(_extract_field(m1_distortion, "guard_illusion"))
            weight_cover = bool(_extract_field(m1_distortion, "weight_cover"))
            if guard_illusion:
                guard_ratio = _extract_field(m1_distortion, "guard_ratio")
                alerts.append(
                    DivergenceAlert(
                        kind="m1_distortion_guard",
                        index_code=None,
                        trade_date=panel_date,
                        detail=f"M1-②a 护盘假象：权重股贡献占比 guard_ratio={_fmt(guard_ratio)} 且上涨家数占比过低",
                    )
                )
            if weight_cover:
                spread = _extract_field(m1_distortion, "spread_current")
                spread_z = _extract_field(m1_distortion, "spread_zscore")
                alerts.append(
                    DivergenceAlert(
                        kind="m1_distortion_weight_cover",
                        index_code=None,
                        trade_date=panel_date,
                        detail=f"M1-②b 权重掩护：黄白线剪刀差 spread={_fmt(spread)}（z={_fmt(spread_z)}）超阈且走扩",
                    )
                )
            if not guard_illusion and not weight_cover:
                alerts.append(
                    DivergenceAlert(
                        kind="m1_distortion",
                        index_code=None,
                        trade_date=panel_date,
                        detail="M1-② 市场失真标记触发（distortion_flag=True，无细分字段）",
                    )
                )

    # ── 路径 2：自算简版（指数涨但跌家数>涨家数 → 权重掩护，逐指数）
    if cfg.enable_simple_divergence and index_df is not None:
        alerts.extend(_simple_divergence(cards, index_df, cfg))

    return tuple(alerts)


def _simple_divergence(
    cards: tuple[IndexRegimeCard, ...],
    index_df: pd.DataFrame,
    cfg: IndexRegimePanelConfig,
) -> list[DivergenceAlert]:
    """自算简版权重掩护：指数当日涨 但 全市场跌家数>涨家数（399106 广度）。

    广度缺失/断更（adv=dec=0）时跳过不误报。仅对非 degraded 卡评估。
    """
    out: list[DivergenceAlert] = []
    breadth_by_proxy = {p.code: p.breadth_index for p in cfg.proxies}
    for card in cards:
        if card.degraded or card.trade_date is None:
            continue
        breadth_code = breadth_by_proxy.get(card.code, _DEFAULT_BREADTH)
        try:
            br = index_df.xs(breadth_code, level="symbol")
        except KeyError:
            continue
        try:
            kline = index_df.xs(card.code, level="symbol")
        except KeyError:
            continue
        day = pd.Timestamp(card.trade_date)
        if day not in br.index:
            continue
        adv = float(br.loc[day, "advance_count"])
        dec = float(br.loc[day, "decline_count"])
        if adv == 0.0 and dec == 0.0:  # 广度断更（399106 近期缺数据填 0）→ 不误报
            continue
        closes = kline["close"].astype(float).loc[:day].dropna()
        if len(closes) < 2:
            continue
        day_ret = float(closes.iloc[-1] / closes.iloc[-2] - 1.0)
        if day_ret > 0.0 and dec > adv:
            out.append(
                DivergenceAlert(
                    kind="weight_cover_simple",
                    index_code=card.code,
                    trade_date=card.trade_date,
                    detail=(
                        f"{card.name}（{card.code}）当日涨 {day_ret:+.2%}，"
                        f"但跌家数 {int(dec)} > 涨家数 {int(adv)}——权重掩护简版背离"
                    ),
                )
            )
    return out


def _fmt(v: Any) -> str:
    """数值格式化（None 安全，供警示 detail）。"""
    if v is None:
        return "N/A"
    try:
        return f"{float(v):.3f}"
    except (TypeError, ValueError):
        return str(v)


__all__ = [
    "INDEX_PROXIES",
    "IndexProxyConfig",
    "IndexRegimePanelConfig",
    "IndexRegimeCard",
    "IndexRegimePanel",
    "DivergenceAlert",
    "IndexRegimePanelError",
    "compute_index_regime_panel",
]
