# [BLUEPRINT] MOD-SIG-079 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-20 行）
# [MODULE] zephyr.signal_ashare.sector_volume_anomaly
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] c1_market.kline_sector_880（只读，period='1d' 板块成交额）
# [CONSUMERS] （候选：情绪页市场宽度「量能异动」卡、板块页量能排序）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 偏离度=当日成交额/前 N 日均值−1（当日点不进均值，PIT 严格）；五档标签封闭（显著放量/温和放量/正常/温和缩量/显著缩量）；历史 <min_history / 当日缺量 / 均值=0 → 该板块跳过 notes 留痕不硬编；z-score 在 std=0 时出 None；单腿异常降级不炸；输入校验 fail-closed；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-20 行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] trade_date/series_map 非法→ValueError（fail-closed）；查询异常/客户端不可得→降级 notes 留痕不抛
# [TESTS] tests/signal_ashare/test_sector_volume_anomaly.py
# [A_module] module_id=MOD-SIG-079 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-SIG-079 — 板块量能异动检测（GAP-F-20，情绪页「量能异动」卡后端）。

板块成交额 vs N 日均值偏离度（MVP）：
- **数据源**：c1_market.kline_sector_880（period='1d'，880xxx 板块日 K，
  amount 成交额字段在码）。
- **口径**：deviation = amount_T / mean(amount 前 N 个交易日) − 1
  （当日点不进均值，PIT 严格）；z-score 在 std>0 时附带。
- **五档标签**（初拍阈值待实盘标定）：≥+100% 显著放量 / ≥+30% 温和放量 /
  其间正常 / ≤−30% 温和缩量 / ≤−50% 显著缩量。
- **观测层消费**，不接交易；板块跳过原因全部 notes 留痕。

# [ALGO_FLOW]
# 层: 输入
# - id: I1 板块成交额序列 dict[code → SectorAmountSeries]（(date, amount) 升序）
# - id: I2 trade_date（PIT 上限）
# 层: 算法
# - id: A1 当日量 vs 前 N 日均值偏离度 + z-score
# - id: A2 五档标签 + 偏离降序榜
# 层: 输出
# - id: O1 VolumeAnomalyReport（items + label_counts + notes）
# [/ALGO_FLOW]
#
# 边:
# I1,I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
import statistics
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Final, Mapping

logger = logging.getLogger(__name__)

__all__: Final = [
    "LABEL_MILD_SHRINK",
    "LABEL_MILD_SPIKE",
    "LABEL_NORMAL",
    "LABEL_SPIKE",
    "LABEL_STRONG_SHRINK",
    "SectorAmountSeries",
    "VolumeAnomalyConfig",
    "VolumeAnomalyItem",
    "VolumeAnomalyReport",
    "detect_volume_anomaly",
    "run_sector_volume_anomaly",
]

#: 五档标签（封闭集合）
LABEL_SPIKE: Final[str] = "显著放量"
LABEL_MILD_SPIKE: Final[str] = "温和放量"
LABEL_NORMAL: Final[str] = "正常"
LABEL_MILD_SHRINK: Final[str] = "温和缩量"
LABEL_STRONG_SHRINK: Final[str] = "显著缩量"

#: 板块日 K（kline_sector_880，period='1d'；窗口=trade_date 前 ma_window×2 自然日缓冲）
SQL_SECTOR_DAILY_AMOUNT: Final = """
SELECT sector_code, sector_name, trade_date, amount
FROM c1_market.kline_sector_880
WHERE period = %(period)s AND trade_date >= %(start)s AND trade_date <= %(end)s
ORDER BY sector_code, trade_date
"""


# ------------------------------------------------------------------
# 配置 / 输入 / 输出
# ------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class VolumeAnomalyConfig:
    """量能异动配置（初拍阈值，待实盘标定）。"""

    ma_window: int = 20  # N 日均值窗（交易日）
    min_history: int = 5  # 历史最小样本（不足跳过）
    spike_threshold: float = 1.0  # ≥+100% 显著放量
    mild_threshold: float = 0.3  # ≥+30% 温和放量
    shrink_mild: float = -0.3  # ≤−30% 温和缩量
    shrink_spike: float = -0.5  # ≤−50% 显著缩量
    top_n: int = 20  # 榜单条数上限
    sector_period: str = "1d"


@dataclass(frozen=True, slots=True)
class SectorAmountSeries:
    """单板块成交额序列（(trade_date, amount) 升序）。"""

    sector_code: str
    sector_name: str
    points: tuple[tuple[str, float], ...]


@dataclass(frozen=True, slots=True)
class VolumeAnomalyItem:
    """单板块量能异动条目。"""

    sector_code: str
    sector_name: str
    amount_today: float
    ma_n: float
    deviation_pct: float  # 偏离度 %（(amount/ma−1)×100）
    zscore: float | None  # std=0 → None
    label: str  # 五档封闭


@dataclass(frozen=True, slots=True)
class VolumeAnomalyReport:
    """量能异动检测输出（观测层消费，不接交易）。"""

    date: str
    items: list[VolumeAnomalyItem] = field(default_factory=list)  # 偏离降序
    label_counts: dict[str, int] = field(default_factory=dict)
    total_sectors: int = 0  # 入评板块总数（含被跳过的）
    degraded: bool = False
    notes: list[str] = field(default_factory=list)


# ------------------------------------------------------------------
# 纯函数核
# ------------------------------------------------------------------


def _classify(deviation: float, cfg: VolumeAnomalyConfig) -> str:
    if deviation >= cfg.spike_threshold:
        return LABEL_SPIKE
    if deviation >= cfg.mild_threshold:
        return LABEL_MILD_SPIKE
    if deviation <= cfg.shrink_spike:
        return LABEL_STRONG_SHRINK
    if deviation <= cfg.shrink_mild:
        return LABEL_MILD_SHRINK
    return LABEL_NORMAL


def detect_volume_anomaly(
    series_map: Mapping[str, SectorAmountSeries],
    trade_date: str,
    config: VolumeAnomalyConfig | None = None,
) -> VolumeAnomalyReport:
    """量能异动主核（纯函数，不触库）。

    Args:
        series_map: {sector_code: SectorAmountSeries}（(date, amount) 升序）。
        trade_date: 数据日（YYYY-MM-DD，PIT 上限，fail-closed）。
        config: 配置（None 用默认）。

    Returns:
        VolumeAnomalyReport；全板块被跳过 → degraded。

    Raises:
        ValueError: trade_date 非法 / series_map 元素类型非法（fail-closed）。
    """
    if not isinstance(trade_date, str):
        raise ValueError(f"trade_date 非法（须 YYYY-MM-DD 字符串）: {trade_date!r}")
    try:
        date.fromisoformat(trade_date)
    except ValueError as exc:
        raise ValueError(f"trade_date 非真实日期: {trade_date!r}") from exc
    cfg = config or VolumeAnomalyConfig()
    notes: list[str] = []
    items: list[VolumeAnomalyItem] = []
    for code, series in series_map.items():
        if not isinstance(series, SectorAmountSeries):
            raise ValueError(f"series_map 元素非法（须 SectorAmountSeries）: {type(series).__name__}")
        past = [(d, a) for d, a in series.points if d <= trade_date]
        today_pts = [a for d, a in past if d == trade_date]
        if not today_pts:
            notes.append(f"{code} 当日成交额缺失，跳过")
            continue
        amount_today = float(today_pts[-1])
        hist = [float(a) for d, a in past if d < trade_date][-cfg.ma_window :]
        if len(hist) < cfg.min_history:
            notes.append(f"{code} 历史不足（{len(hist)}<{cfg.min_history}），跳过")
            continue
        ma = sum(hist) / len(hist)
        if ma <= 0:
            notes.append(f"{code} N 日均值为 0，偏离度不适用，跳过")
            continue
        deviation = amount_today / ma - 1.0
        z: float | None = None
        if len(hist) >= 2:
            std = statistics.stdev(hist)
            if std > 0:
                z = round((amount_today - ma) / std, 4)
        items.append(
            VolumeAnomalyItem(
                sector_code=series.sector_code,
                sector_name=series.sector_name,
                amount_today=round(amount_today, 2),
                ma_n=round(ma, 2),
                deviation_pct=round(deviation * 100.0, 2),
                zscore=z,
                label=_classify(deviation, cfg),
            )
        )
    items.sort(key=lambda i: (-i.deviation_pct, i.sector_code))
    label_counts: dict[str, int] = {}
    for i in items:
        label_counts[i.label] = label_counts.get(i.label, 0) + 1
    total = len(series_map)
    capped = items[: cfg.top_n]
    if len(items) > cfg.top_n:
        notes.append(f"榜单截断 top_n={cfg.top_n}（全量 {len(items)} 板块）")
    return VolumeAnomalyReport(
        date=trade_date,
        items=capped,
        label_counts=label_counts,
        total_sectors=total,
        degraded=not items,
        notes=notes,
    )


# ------------------------------------------------------------------
# 主入口（薄加载层，ch_client 注入可 mock）
# ------------------------------------------------------------------


def _normalize_dt(trade_date: str | date | datetime) -> date:
    if isinstance(trade_date, datetime):
        return trade_date.date()
    if isinstance(trade_date, date):
        return trade_date
    return datetime.strptime(str(trade_date), "%Y-%m-%d").date()


def _default_client() -> Any | None:
    try:
        from zephyr.data.ch_writer import get_client

        return get_client()
    except Exception:  # noqa: BLE001 — 连接/依赖问题一律降级
        logger.warning("ch_writer 默认客户端不可用，量能异动检测降级", exc_info=True)
        return None


def run_sector_volume_anomaly(
    trade_date: str | date | datetime,
    ch_client: Any | None = None,
    config: VolumeAnomalyConfig | None = None,
) -> VolumeAnomalyReport:
    """主入口：板块量能异动检测（日频）。

    Args:
        trade_date: 数据日（PIT 上限）。
        ch_client: clickhouse-driver 鸭子类型；None 延迟取默认客户端。
        config: 配置（None 用默认；ma_window 决定加载窗口=2×N 自然日缓冲）。

    Returns:
        VolumeAnomalyReport；查询异常/客户端不可得 → degraded notes 留痕。
    """
    cfg = config or VolumeAnomalyConfig()
    current = _normalize_dt(trade_date)  # ValueError fail-closed
    date_str = current.isoformat()
    client = ch_client if ch_client is not None else _default_client()
    if client is None:
        return VolumeAnomalyReport(date=date_str, degraded=True, notes=["CH 客户端不可得，量能异动检测整体降级"])
    start = current - timedelta(days=max(cfg.ma_window * 2, cfg.min_history * 2))
    try:
        rows = client.execute(
            SQL_SECTOR_DAILY_AMOUNT,
            {"period": cfg.sector_period, "start": start, "end": current},
        )
    except Exception as e:  # noqa: BLE001 — 查询腿降级
        return VolumeAnomalyReport(date=date_str, degraded=True, notes=[f"kline_sector_880 查询异常，整体降级: {e!r}"])
    series: dict[str, list[tuple[str, float]]] = {}
    names: dict[str, str] = {}
    for r in rows:
        code = str(r[0])
        names[code] = str(r[1])
        series.setdefault(code, []).append((str(r[2])[:10], float(r[3])))
    smap = {
        code: SectorAmountSeries(sector_code=code, sector_name=names.get(code, ""), points=tuple(pts))
        for code, pts in series.items()
    }
    return detect_volume_anomaly(smap, date_str, cfg)
