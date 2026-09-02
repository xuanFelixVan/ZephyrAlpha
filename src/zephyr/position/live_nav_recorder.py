# [BLUEPRINT] MOD-POS-023 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-29 行）
# [MODULE] zephyr.position.live_nav_recorder
# [DOMAIN] D_POSITION
# [DEPENDENCIES] （资产源协议注入：miniQMT broker 鸭型 get_positions→cash/total_market_value；CTR-P1-008 券商未接，当前=miniQMT 模拟净值源）
# [CONSUMERS] （候选：总览页净值图 vs 沪深300；落库表 DDL 草稿见 fragments——禁直建，Owner 窗口）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 总资产=现金+市值（miniQMT 模拟账户口径）；净值比=总资产/base_nav（首点 base_nav=None 自身为基准=1.0）；基准比=benchmark_close/benchmark_base（缺基准任一→None 降级不硬编）；曲线按 trade_date 升序归一；最大回撤≤0 口径取绝对值%；落库仅经 writer 注入（本模块不直连 DB）；输入校验 fail-closed；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-29 行
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] asset/trade_date/现金市值非法→ValueError（fail-closed）；资产源异常→ValueError（资产快照获取失败）；writer 异常→ValueError（净值落库失败）
# [TESTS] tests/position/test_live_nav_recorder.py
# [A_module] module_id=MOD-POS-023 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-POS-023 — 实盘净值曲线序列（GAP-F-29，总览页净值图后端）。

账户净值日频记录 + 曲线序列产出（vs 沪深300）：
- **资产源**：CTR-P1-008 券商通道未接——当前为 **miniQMT 模拟净值源**
  （SimulatedQmtAssetSource 适配 broker.get_positions() → cash/total_market_value
  鸭子类型，生产接线=ex_core.adapters.miniqmt_broker 同款查询）；接口注入位
  预留——任何返回 AssetSnapshot 的 source 均可替换（未来券商账户/手工录入）。
- **净值口径**：总资产=现金+市值（模拟账户无负债/融资，MVP 口径明文化）；
  nav_ratio=总资产/base_nav（首点自身为基准）；benchmark_ratio=基准收盘/
  基准基点（沪深300，缺基准数据→None 降级）。
- **曲线**：累计收益（首末 nav_ratio）、最大回撤（峰值回撤绝对值 %）、
  超额=净值区间收益−基准区间收益（首末皆有基准比率的点段）。
- **落库**：persist_nav_points 仅经 writer 注入（本模块不直连 DB）；
  目标表 c1_market.account_nav_daily DDL 草稿见
  .runtime/construction_20260823/fragments/GAP7_registry.yaml（禁直建，Owner 窗口）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1 AssetSnapshot（现金/市值；资产源适配产出）
# - id: I2 base_nav / benchmark_close / benchmark_base（基准注入位）
# 层: 算法
# - id: A1 日频 NavPoint（净值比/基准比）
# - id: A2 曲线组装（累计收益/最大回撤/超额）
# 层: 输出
# - id: O1 NavPoint / NavCurve（frozen dataclass，JSON 可序列化）
# [/ALGO_FLOW]
#
# 边:
# I1,I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Callable, Final, Sequence

logger = logging.getLogger(__name__)

__all__: Final = [
    "AssetSnapshot",
    "NavCurve",
    "NavPoint",
    "SimulatedQmtAssetSource",
    "build_nav_curve",
    "persist_nav_points",
    "record_daily_nav",
]


# ------------------------------------------------------------------
# 资产快照 / 净值点 / 曲线
# ------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AssetSnapshot:
    """账户资产快照（模拟账户口径：现金+市值，无负债腿）。"""

    cash: float
    market_value: float
    frozen_cash: float = 0.0  # 冻结资金（留痕，不入总资产——miniQMT cash 已含可用/冻结拆分口径待标定）


@dataclass(frozen=True, slots=True)
class NavPoint:
    """日频净值点（落库行形态）。"""

    trade_date: str
    total_asset: float
    cash: float
    market_value: float
    nav_ratio: float  # vs base_nav（首点=1.0）
    benchmark_close: float | None = None
    benchmark_ratio: float | None = None  # vs benchmark_base（缺→None）


@dataclass(frozen=True, slots=True)
class NavCurve:
    """净值曲线序列输出（总览页消费）。"""

    points: list[NavPoint] = field(default_factory=list)  # trade_date 升序
    latest_nav: float = 0.0
    cum_return_pct: float = 0.0  # 首末 nav_ratio 区间收益 %
    max_drawdown_pct: float = 0.0  # 峰值回撤绝对值 %（≥0）
    excess_vs_benchmark_pct: float | None = None  # 缺基准序列 → None
    degraded: bool = False
    notes: list[str] = field(default_factory=list)


# ------------------------------------------------------------------
# 资产源（接口注入位；当前=miniQMT 模拟净值源）
# ------------------------------------------------------------------


class SimulatedQmtAssetSource:
    """miniQMT 模拟账户资产源（broker 鸭子类型适配）。

    broker 协议：``get_positions()`` 返回含 ``cash`` / ``total_market_value``
    属性的对象（ex_core.adapters.miniqmt_broker PositionSnapshot 同形态）。
    本类不建连接——连接生命周期由调用方（通道管理器 MOD-EX-058）持有。
    """

    def __init__(self, broker: Any) -> None:
        self._broker = broker

    def fetch_asset(self) -> AssetSnapshot:
        """取资产快照；源异常 → ValueError（fail-closed，不出伪净值）。"""
        try:
            snap = self._broker.get_positions()
            cash = float(getattr(snap, "cash"))
            mv = float(getattr(snap, "total_market_value"))
        except Exception as exc:  # noqa: BLE001 — 源异常 fail-closed
            raise ValueError(f"资产快照获取失败: {exc!r}") from exc
        return AssetSnapshot(cash=cash, market_value=mv)


# ------------------------------------------------------------------
# 纯函数核
# ------------------------------------------------------------------


def _validate_date_str(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} 非法（须 YYYY-MM-DD 字符串）: {value!r}")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} 非真实日期: {value!r}") from exc
    return value


def record_daily_nav(
    asset: AssetSnapshot,
    trade_date: str | date | datetime,
    base_nav: float | None = None,
    benchmark_close: float | None = None,
    benchmark_base: float | None = None,
) -> NavPoint:
    """日频净值点计算（纯函数）。

    Args:
        asset: 资产快照（fail-closed；现金/市值须 ≥0 实数）。
        trade_date: 交易日（YYYY-MM-DD，fail-closed）。
        base_nav: 净值基准（首点 None → 自身为基准 nav_ratio=1.0）。
        benchmark_close/benchmark_base: 基准收盘/基点（缺任一 → benchmark_ratio=None）。

    Returns:
        NavPoint。

    Raises:
        ValueError: 输入非法（fail-closed）。
    """
    if not isinstance(asset, AssetSnapshot):
        raise ValueError(f"asset 非法（须 AssetSnapshot）: {type(asset).__name__}")
    if isinstance(trade_date, datetime):
        v_date = trade_date.date().isoformat()
    elif isinstance(trade_date, date):
        v_date = trade_date.isoformat()
    else:
        v_date = _validate_date_str(trade_date, "trade_date")
    for name, val in (("cash", asset.cash), ("market_value", asset.market_value)):
        if isinstance(val, bool) or not isinstance(val, (int, float)) or float(val) < 0:
            raise ValueError(f"cash/market_value 非法（须 ≥0 实数）: {name}={val!r}")
    total = float(asset.cash) + float(asset.market_value)
    base = total if base_nav is None else float(base_nav)
    if base <= 0:
        raise ValueError(f"base_nav 非法（须为正）: {base_nav!r}")
    bench_ratio: float | None = None
    if benchmark_close is not None and benchmark_base is not None and float(benchmark_base) > 0:
        bench_ratio = round(float(benchmark_close) / float(benchmark_base), 6)
    return NavPoint(
        trade_date=v_date,
        total_asset=round(total, 2),
        cash=round(float(asset.cash), 2),
        market_value=round(float(asset.market_value), 2),
        nav_ratio=round(total / base, 6),
        benchmark_close=None if benchmark_close is None else float(benchmark_close),
        benchmark_ratio=bench_ratio,
    )


def build_nav_curve(points: Sequence[NavPoint]) -> NavCurve:
    """净值曲线组装（纯函数；输入乱序 → 按 trade_date 升序归一）。

    Args:
        points: NavPoint 序列（空 → degraded）。

    Returns:
        NavCurve（累计收益/最大回撤/超额）。
    """
    pts = sorted(points, key=lambda p: p.trade_date)
    if not pts:
        return NavCurve(degraded=True, notes=["空净值序列，曲线整体降级"])
    cum_ret = (pts[-1].nav_ratio / pts[0].nav_ratio - 1.0) * 100.0 if pts[0].nav_ratio > 0 else 0.0
    peak = pts[0].nav_ratio
    max_dd = 0.0
    for p in pts:
        peak = max(peak, p.nav_ratio)
        if peak > 0:
            max_dd = min(max_dd, p.nav_ratio / peak - 1.0)
    excess: float | None = None
    bench_pts = [p for p in pts if p.benchmark_ratio is not None]
    if len(bench_pts) >= 2 and bench_pts[0].benchmark_ratio and bench_pts[0].benchmark_ratio > 0:
        bench_ret = (bench_pts[-1].benchmark_ratio / bench_pts[0].benchmark_ratio - 1.0) * 100.0  # type: ignore[operator]
        nav_ret_span = (
            (bench_pts[-1].nav_ratio / bench_pts[0].nav_ratio - 1.0) * 100.0 if bench_pts[0].nav_ratio > 0 else 0.0
        )
        excess = round(nav_ret_span - bench_ret, 4)
    notes: list[str] = []
    if excess is None:
        notes.append("基准序列不足（<2 个有效基准点），超额不出")
    return NavCurve(
        points=list(pts),
        latest_nav=pts[-1].total_asset,
        cum_return_pct=round(cum_ret, 4),
        max_drawdown_pct=round(abs(max_dd) * 100.0, 4),
        excess_vs_benchmark_pct=excess,
        degraded=False,
        notes=notes,
    )


def persist_nav_points(
    points: Sequence[NavPoint],
    writer: Callable[[list[NavPoint]], int],
) -> int:
    """净值落库（writer 注入；本模块不直连 DB，空序列跳过）。

    Args:
        points: 待落库净值点（trade_date 升序归一后传入 writer）。
        writer: 落库函数（NavPoint 列表 → 写入行数；生产接线=CH writer，
            目标表 c1_market.account_nav_daily DDL 草稿见 fragments）。

    Returns:
        写入行数。

    Raises:
        ValueError: writer 异常（净值落库失败，fail-closed）。
    """
    pts = sorted(points, key=lambda p: p.trade_date)
    if not pts:
        return 0
    try:
        return int(writer(list(pts)))
    except Exception as exc:  # noqa: BLE001 — 落库异常 fail-closed
        raise ValueError(f"净值落库失败: {exc!r}") from exc
