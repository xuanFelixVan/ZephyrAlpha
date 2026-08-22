# [BLUEPRINT] MOD-DATA-061 | 待统筹登记（blueprint 未建，真源=架构审查报告 §11.5 SEC-02 行 + 92号清单 §7.6）
# [MODULE] zephyr.data.sector_intraday_aggregator
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.table_registry; c1_market.sector_snapshot（只读）; zephyr.data.ch_writer（默认客户端延迟加载，可注入旁路）
# [CONSUMERS] （MVP 阶段无——调度挂接点预留 44号 M1-④ 盘中调度回路载体（波5 注册任务）；候选消费方：SEC-01 板块盘后报告器、Dashboard D-02 板块全景页、SEC-05 主线候选榜盘中修正）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 纯函数聚合（aggregate_sector_intraday 无 I/O 无副作用，同输入同输出）；本模块不注册调度任务（M1-④ 载体职责）；资金腿口径=成交额增量代理（sector_snapshot 无主力净流入字段，22号 §3.1⑥ 实证裁定；880xxx 板块指数 inside/outside 为指数自身合成报价 tick 计数，2026-08-22 实证近恒 0-4，不作资金流主口径）；市场统计指数（880001-880009）默认剔除出板块榜；PIT（只读 ≤ 查询时点快照）；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/92_phase2_business_construction_order.md §7.6
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入为空/全部非法→degraded=True 空榜不炸；单板块仅 1 条快照→窗口增量为 0/速度 None 不炸（notes 留痕）；CH 查询异常/客户端不可用→load_latest_snapshots 返回 []+log（不抛，对齐 ch_reader 降级语义）；timestamp 无法解析的记录跳过不炸
# [TESTS] tests/zephyr/data/test_sector_intraday_aggregator.py
# [A_module] module_id=MOD-DATA-061 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-DATA-061 — 盘中板块实时聚合器（SEC-02，92号清单 §7.6；架构审查报告 §11.5 SEC-02 行）。

sector_snapshot 30s 轮询字段（582 板块，amount/inside/outside/涨跌家数/涨速）
→ 板块资金榜/涨跌家数结构/涨速榜/新开板清单，18-30s 刷新级纯函数聚合器。

四件输出（SectorIntradayBoard）：
  1. 资金榜（inflow_top）：窗口成交额增量降序——盘中资金活跃度代理。
     口径裁定：sector_snapshot 18 采集字段无主力净流入类字段（22号 spec §3.1⑥
     "snapshot 链路不含资金流字段"实证），盘后真净流入=money_flow×sector_constituent
     聚合（SEC-01 范围，非本模块）；880xxx 板块指数 inside/outside 实证为指数自身
     合成报价 tick 计数（2026-08-22 直查 880806.SH 全日近恒 0-4），不能作资金流
     主口径——行内保留 net_active_buy 估算字段（内外盘差×均价×100）供 881xxx/
     个股聚合等未来数据源前向兼容，默认不参与排名。
  2. 涨跌家数结构（breadth）：全市场板块合计 up/down 家数+涨跌比+结构变化量
     （窗口首尾快照差），板块级 latest up_home/down_home 逐行可下钻。
  3. 涨速榜（speed_top）：最新 zangsu 降序（通达信涨速=近 N 分钟涨幅%，
     Decimal(10,3) 采集口径），附窗口涨速变化量。
  4. 新开板清单（new_open_boards）：本刷新周期新晋入榜（资金榜∪涨速榜）而
     上一周期未入榜的板块代码——"开板"在此=板块新晋浮出水面进入监控榜
     （对照上一刷新周期），非个股涨停开板（sector_snapshot 无个股腿，个股
     开板监控属 44号 M1-④ 全市场分钟快照口径）。

调度挂接点（本模块不注册任务，载体=44号 M1-④ 盘中调度回路，波5 接线）：
    回路每 18-30s：snaps = load_latest_snapshots(minutes=5)
                   board = aggregate_sector_intraday(snaps, previous_board=上轮 board)
    previous_board 参数即挂接契约——新开板对照基线由回路逐轮持有。

【数据实证口径（2026-08-22 直查 c1_market.sector_snapshot，可信）】
- 表结构 DESCRIBE 实证：timestamp DateTime64(3,'Asia/Shanghai')、amount
  Decimal(18,2)、up_home/down_home UInt32、inside/outside UInt32、
  zangsu Decimal(10,3)、market_type LowCardinality(String)。
- 2026-08-20 全日 7020 行/468 板块（09:45→15:55）；08-21 2340 行（采集窗
  09:40→11:15 半日）。amount 累计语义实证单调不减（448 万→1888 万序列）。
- inside/outside 对 880xxx 板块指数近恒 0-4（指数合成报价 tick 计数），
  资金腿主口径由此裁定为成交额增量代理（见上）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 板块快照序列（sector_snapshot 30s 轮询/推送）
#   fields: sector_code/timestamp/now_price/last_close/amount/up_home/down_home/inside/outside/zangsu/average_price/market_type
# - id: I2
#   name: 上一刷新周期榜（previous_board，M1-④ 回路持有）
#   fields: inflow_top/speed_top 板块代码集合
# 层: 特征
# - id: F1
#   name_zh: 单板块窗口聚合
#   formula: pct_change=(now-last_close)/last_close; amount_delta=末值−首值(累计单调);
#     amount_velocity=amount_delta/窗口分钟; net_active_buy=Σ(Δoutside−Δinside)×均价×100(复位守卫);
#     up/down_home 末值与差量; zangsu 末值与差量
# - id: F2
#   name_zh: 全市场广度结构
#   formula: total_up=Σup_home; total_down=Σdown_home; ratio=up/max(down,1); 板块涨跌平计数; 结构变化=末−首合计差
# 层: 算法
# - id: A1
#   name_zh: 资金榜/涨速榜排名
#   desc: inflow_top=amount_delta 降序(并列 sector_code 升序); speed_top=zangsu 降序(>min_speed 过滤)
# - id: A2
#   name_zh: 新开板对照
#   desc: current=资金榜∪涨速榜代码集; new=current−previous_board 同口径集; 无基线→空集+notes
# 层: 输出
# - id: O1
#   name_zh: SectorIntradayBoard
#   intro: asof/n_sectors/inflow_top/speed_top/breadth/new_open_boards/rows/degraded/notes；frozen dataclass asdict JSON 可序列化
# [/ALGO_FLOW]
#
# 边:
# I1 --> F1
# I1 --> F2
# F1 --> A1
# I2,A1 --> A2
# A1,F2,A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Final

log = logging.getLogger(__name__)

__all__: Final = [
    "SectorBreadth",
    "SectorFlowRow",
    "SectorIntradayBoard",
    "SectorIntradayConfig",
    "aggregate_sector_intraday",
    "load_latest_snapshots",
]

# 表名真源：business_data_categories.yaml via table_registry（裁定 #ARCH-CH-024，
# 对齐 sector_ranking_engine/sector_snapshot_collector 同族模式）
from zephyr.data.table_registry import get_registry as _get_table_registry

_TBL_SECTOR_SNAPSHOT: Final = _get_table_registry().table("market_sector_snapshot_880")

# SQL 集中化（NO-BARE-SQL gate 豁免 SQL_ 前缀；参数化 %(name)s 禁 f-string 插值）
# 取最新交易日的最近 minutes 分钟窗口快照；ch_reader/ch_writer 通道自动注入 FINAL 去重
SQL_LATEST_SNAPSHOTS: Final = f"""
SELECT sector_code, timestamp, now_price, last_close, amount, up_home, down_home,
       inside, outside, zangsu, average_price, market_type, trade_date
FROM {_TBL_SECTOR_SNAPSHOT}
WHERE trade_date = (SELECT max(trade_date) FROM {_TBL_SECTOR_SNAPSHOT})
  AND timestamp >= (SELECT max(timestamp) FROM {_TBL_SECTOR_SNAPSHOT}) - INTERVAL %(minutes)s MINUTE
ORDER BY sector_code, timestamp
"""

#: load_latest_snapshots 返回 dict 的键序（与 SQL 列序一一对应）
_SNAPSHOT_KEYS: Final = (
    "sector_code",
    "timestamp",
    "now_price",
    "last_close",
    "amount",
    "up_home",
    "down_home",
    "inside",
    "outside",
    "zangsu",
    "average_price",
    "market_type",
    "trade_date",
)


# ------------------------------------------------------------------
# 配置与输出容器（frozen dataclass，asdict JSON 可序列化）
# ------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SectorIntradayConfig:
    """聚合阈值配置——默认值取自 92号清单 §7.6 + 2026-08-22 数据实证。"""

    inflow_top_n: int = 20  # 资金榜长度（窗口成交额增量降序）
    speed_top_n: int = 20  # 涨速榜长度（最新 zangsu 降序）
    min_speed: float = 0.0  # 入涨速榜最小涨速（严格大于；0=只留正涨速）
    min_amount_delta: float = 0.0  # 入资金榜最小成交增量（严格大于；0=剔除窗口零成交）
    lot_size: int = 100  # 内外盘手→股换算（net_active_buy 估算，前向兼容字段）
    market_index_prefixes: tuple[str, ...] = ("88000",)  # 市场统计指数剔除前缀（880001-880009）


@dataclass(frozen=True, slots=True)
class SectorFlowRow:
    """单板块窗口聚合行（资金/广度/涨速三维全量，榜单行与下钻行共用）。"""

    sector_code: str
    last_timestamp: str  # 最新快照时间戳 ISO
    n_snapshots: int  # 窗口内快照条数
    pct_change: float  # 最新涨跌幅（小数，0.02=2%；last_close≤0 → 0）
    amount: float  # 最新累计成交额（采集原始单位）
    amount_delta: float  # 窗口成交额增量（末−首，累计语义实证单调；负差按 0 截断）
    amount_velocity: float | None  # 成交额速度（增量/窗口分钟）；窗口<1 分钟 → None
    net_active_buy: float  # 净主动买入估算（内外盘差×均价×lot_size；880xxx 实证常态 ~0，前向兼容字段）
    up_home: int  # 最新上涨家数
    down_home: int  # 最新下跌家数
    up_home_delta: int  # 上涨家数窗口变化（末−首）
    down_home_delta: int  # 下跌家数窗口变化（末−首）
    zangsu: float  # 最新涨速（采集口径 Decimal(10,3)）
    zangsu_delta: float  # 涨速窗口变化（末−首）


@dataclass(frozen=True, slots=True)
class SectorBreadth:
    """涨跌家数结构（全市场板块合计 + 结构变化量）。"""

    total_up: int  # 全板块上涨家数合计（最新快照）
    total_down: int  # 全板块下跌家数合计（最新快照）
    up_down_ratio: float  # 涨跌比 = total_up / max(total_down, 1)
    sectors_up: int  # 上涨板块数（pct_change>0）
    sectors_down: int  # 下跌板块数（pct_change<0）
    sectors_flat: int  # 平盘板块数
    total_up_delta: int  # 上涨家数合计窗口变化（末−首，结构改善/恶化方向标）
    total_down_delta: int  # 下跌家数合计窗口变化


@dataclass(frozen=True, slots=True)
class SectorIntradayBoard:
    """盘中板块聚合榜输出契约（18-30s 刷新级，M1-④ 回路逐轮持有做新开板对照）。"""

    asof: str  # 全板块最新快照时间戳 ISO；空输入 → ""
    trade_date: str = ""  # 数据日 YYYY-MM-DD（记录含 trade_date 时取最新）
    n_sectors: int = 0  # 参与聚合的板块数（剔除市场统计指数后）
    inflow_top: list[SectorFlowRow] = field(default_factory=list)  # 资金榜（成交额增量代理口径）
    speed_top: list[SectorFlowRow] = field(default_factory=list)  # 涨速榜
    breadth: SectorBreadth = field(
        default_factory=lambda: SectorBreadth(0, 0, 0.0, 0, 0, 0, 0, 0)
    )
    new_open_boards: list[str] = field(default_factory=list)  # 新开板清单（新晋入榜，对照上一周期）
    rows: list[SectorFlowRow] = field(default_factory=list)  # 全量聚合行（下钻/再排名用）
    degraded: bool = False  # 输入为空/全部非法 → True（结果仅供观测不可用于决策）
    notes: list[str] = field(default_factory=list)  # 口径/降级留痕


# ------------------------------------------------------------------
# 内部辅助（纯函数）
# ------------------------------------------------------------------


def _to_float(v: object, default: float = 0.0) -> float:
    """安全转 float（Decimal/int/str 兼容；None/空串/非法 → default）。"""
    if v is None or v == "":
        return default
    try:
        return float(v)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return default


def _to_int(v: object, default: int = 0) -> int:
    """安全转 int（float 截断；None/空串/非法 → default）。"""
    if v is None or v == "":
        return default
    try:
        return int(float(v))  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return default


def _as_dt(v: object) -> datetime | None:
    """时间戳归一（datetime 原样；str 按 ISO 解析；非法 → None 由调用方跳过）。"""
    if isinstance(v, datetime):
        return v
    if isinstance(v, date):
        return datetime(v.year, v.month, v.day)
    if isinstance(v, str):
        try:
            return datetime.fromisoformat(v)
        except ValueError:
            return None
    return None


def _is_market_index(code: str, market_type: str, prefixes: tuple[str, ...]) -> bool:
    """市场统计指数判定（market_type=mkt_index 或代码前缀命中，双保险）。"""
    if market_type == "mkt_index":
        return True
    digits = code.split(".")[0]
    return any(digits.startswith(p) for p in prefixes)


def _normalize_snapshots(snapshots: Any) -> list[dict[str, Any]]:
    """输入归一为 dict 列表（list[dict] 原样；pandas DataFrame 经 to_dict('records') 转换，
    模块级不 import pandas——鸭子类型 has to_dict 即可）。"""
    if snapshots is None:
        return []
    if isinstance(snapshots, list):
        return [r for r in snapshots if isinstance(r, dict)]
    to_dict = getattr(snapshots, "to_dict", None)
    if callable(to_dict):
        records = to_dict("records")
        return [r for r in records if isinstance(r, dict)]
    raise TypeError(f"snapshots 类型不支持（须 list[dict] 或 DataFrame 鸭子类型）: {type(snapshots)!r}")


def _delta(cur: float, prev: float) -> float:
    """累计量差值（负差=计数器复位/口径跳变，回退取当前值；对齐采集器累计语义）。"""
    d = cur - prev
    return d if d >= 0 else cur


def _aggregate_sector(records: list[dict[str, Any]], cfg: SectorIntradayConfig) -> SectorFlowRow | None:
    """单板块快照序列 → 聚合行（records 须同 sector_code；按 timestamp 升序重排）。"""
    timed: list[tuple[datetime, dict[str, Any]]] = []
    for rec in records:
        ts = _as_dt(rec.get("timestamp"))
        if ts is not None:
            timed.append((ts, rec))
    if not timed:
        return None
    timed.sort(key=lambda x: x[0])

    first_ts, first = timed[0]
    last_ts, last = timed[-1]

    last_close = _to_float(last.get("last_close"))
    now_price = _to_float(last.get("now_price"))
    pct_change = (now_price - last_close) / last_close if last_close > 0 else 0.0

    amount_last = _to_float(last.get("amount"))
    amount_delta = max(0.0, amount_last - _to_float(first.get("amount")))

    window_minutes = (last_ts - first_ts).total_seconds() / 60.0
    amount_velocity = amount_delta / window_minutes if window_minutes > 0 else None

    # 净主动买入估算：逐对差分（复位守卫）×均价×手股换算。
    # 880xxx 板块指数实证 inside/outside 近恒 0-4（指数合成报价 tick），常态产出 ~0；
    # 保留本字段供 881xxx/个股聚合等未来有意义数据源前向兼容，默认不参与排名。
    net_active = 0.0
    for i in range(1, len(timed)):
        prev_rec, cur_rec = timed[i - 1][1], timed[i][1]
        d_out = _delta(_to_float(cur_rec.get("outside")), _to_float(prev_rec.get("outside")))
        d_in = _delta(_to_float(cur_rec.get("inside")), _to_float(prev_rec.get("inside")))
        price = _to_float(cur_rec.get("average_price")) or _to_float(cur_rec.get("now_price"))
        net_active += (d_out - d_in) * price * cfg.lot_size

    up_last = _to_int(last.get("up_home"))
    down_last = _to_int(last.get("down_home"))
    zangsu_last = _to_float(last.get("zangsu"))

    return SectorFlowRow(
        sector_code=str(last.get("sector_code") or first.get("sector_code") or ""),
        last_timestamp=last_ts.isoformat(),
        n_snapshots=len(timed),
        pct_change=round(pct_change, 6),
        amount=round(amount_last, 2),
        amount_delta=round(amount_delta, 2),
        amount_velocity=round(amount_velocity, 2) if amount_velocity is not None else None,
        net_active_buy=round(net_active, 2),
        up_home=up_last,
        down_home=down_last,
        up_home_delta=up_last - _to_int(first.get("up_home")),
        down_home_delta=down_last - _to_int(first.get("down_home")),
        zangsu=round(zangsu_last, 4),
        zangsu_delta=round(zangsu_last - _to_float(first.get("zangsu")), 4),
    )


def _build_breadth(rows: list[SectorFlowRow]) -> SectorBreadth:
    """全量聚合行 → 涨跌家数结构（合计 + 变化量 + 板块涨跌平计数）。"""
    total_up = sum(r.up_home for r in rows)
    total_down = sum(r.down_home for r in rows)
    return SectorBreadth(
        total_up=total_up,
        total_down=total_down,
        up_down_ratio=round(total_up / max(total_down, 1), 4),
        sectors_up=sum(1 for r in rows if r.pct_change > 0),
        sectors_down=sum(1 for r in rows if r.pct_change < 0),
        sectors_flat=sum(1 for r in rows if r.pct_change == 0),
        total_up_delta=sum(r.up_home_delta for r in rows),
        total_down_delta=sum(r.down_home_delta for r in rows),
    )


def _watch_codes(board: SectorIntradayBoard) -> set[str]:
    """榜单监控代码集（资金榜 ∪ 涨速榜）——新开板对照口径。"""
    return {r.sector_code for r in board.inflow_top} | {r.sector_code for r in board.speed_top}


# ------------------------------------------------------------------
# 主接口
# ------------------------------------------------------------------


def aggregate_sector_intraday(
    snapshots: Any,
    previous_board: SectorIntradayBoard | None = None,
    config: SectorIntradayConfig | None = None,
) -> SectorIntradayBoard:
    """主入口：sector_snapshot 窗口快照序列 → 盘中板块聚合榜（纯函数，无 I/O）。

    Args:
        snapshots: list[dict]（键=sector_snapshot 列名）或 pandas DataFrame 鸭子类型；
            窗口建议 ≥2 倍轮询周期（默认调用方 load_latest_snapshots(minutes=5)）。
        previous_board: 上一刷新周期榜（M1-④ 回路逐轮持有）；None → 新开板清单为空
            并 notes 留痕（首轮聚合无对照基线）。
        config: 阈值配置（None 用默认 92号 §7.6 + 实证口径）。

    Returns:
        SectorIntradayBoard；输入为空/全部非法 → degraded=True 空榜不炸。
    """
    cfg = config or SectorIntradayConfig()
    notes: list[str] = []

    records = _normalize_snapshots(snapshots)
    if not records:
        return SectorIntradayBoard(asof="", degraded=True, notes=["输入快照序列为空"])

    # 按板块分组（剔除市场统计指数与缺代码/缺时间戳记录）
    by_sector: dict[str, list[dict[str, Any]]] = {}
    n_skipped = 0
    latest_td = ""
    for rec in records:
        code = str(rec.get("sector_code") or "")
        if not code:
            n_skipped += 1
            continue
        if _is_market_index(code, str(rec.get("market_type") or ""), cfg.market_index_prefixes):
            continue
        td = rec.get("trade_date")
        if td is not None:
            latest_td = max(latest_td, str(td)) if latest_td else str(td)
        by_sector.setdefault(code, []).append(rec)
    if n_skipped:
        notes.append(f"跳过缺 sector_code 记录 {n_skipped} 条")

    rows: list[SectorFlowRow] = []
    n_no_time = 0
    for code, recs in by_sector.items():
        row = _aggregate_sector(recs, cfg)
        if row is None:
            n_no_time += len(recs)
            continue
        rows.append(row)
    if n_no_time:
        notes.append(f"跳过 timestamp 无法解析记录 {n_no_time} 条")

    if not rows:
        return SectorIntradayBoard(asof="", trade_date=latest_td, degraded=True, notes=notes + ["无有效板块快照"])

    rows.sort(key=lambda r: r.sector_code)
    asof = max(r.last_timestamp for r in rows)

    # 资金榜：窗口成交额增量降序（并列 sector_code 升序保确定性）；零增量不入榜
    inflow = sorted(
        (r for r in rows if r.amount_delta > cfg.min_amount_delta),
        key=lambda r: (-r.amount_delta, r.sector_code),
    )[: cfg.inflow_top_n]
    # 涨速榜：最新涨速降序（>min_speed 过滤，默认只留正涨速）
    speed = sorted(
        (r for r in rows if r.zangsu > cfg.min_speed),
        key=lambda r: (-r.zangsu, r.sector_code),
    )[: cfg.speed_top_n]
    if all(r.n_snapshots == 1 for r in rows):
        notes.append("全部板块单快照：窗口增量/速度不可得，资金榜按零增量口径为空或极简")

    breadth = _build_breadth(rows)

    # 新开板清单：本周期入榜而上一周期未入榜（对照基线=M1-④ 回路逐轮持有的上轮榜）
    new_open: list[str] = []
    if previous_board is not None:
        current_watch = {r.sector_code for r in inflow} | {r.sector_code for r in speed}
        new_open = sorted(current_watch - _watch_codes(previous_board))
    else:
        notes.append("无 previous_board 对照基线（首轮聚合），新开板清单为空")

    return SectorIntradayBoard(
        asof=asof,
        trade_date=latest_td,
        n_sectors=len(rows),
        inflow_top=inflow,
        speed_top=speed,
        breadth=breadth,
        new_open_boards=new_open,
        rows=rows,
        degraded=False,
        notes=notes,
    )


def load_latest_snapshots(ch_client: Any | None = None, minutes: int = 5) -> list[dict[str, Any]]:
    """便捷入口：读 sector_snapshot 最新交易日最近 minutes 分钟快照 → dict 列表。

    Args:
        ch_client: clickhouse-driver 鸭子类型（execute(sql, params) -> list[tuple]）；
            None 时延迟取 ch_writer.get_client()，不可得 → 返回 []+log（不抛，
            对齐 ch_reader 失败静默降级语义）。
        minutes: 回看窗口分钟数（默认 5，覆盖 ≥2 个 30s 轮询周期+推送乱序）。

    Returns:
        dict 列表（键=_SNAPSHOT_KEYS 列名）；查询异常/无数据 → []。
    """
    if minutes <= 0:
        raise ValueError(f"minutes 须为正整数: {minutes!r}")

    client = ch_client if ch_client is not None else _default_client()
    if client is None:
        log.warning("ch_client 未注入且默认客户端不可用，load_latest_snapshots 返回空")
        return []
    try:
        rows = client.execute(SQL_LATEST_SNAPSHOTS, {"minutes": minutes})
    except Exception as e:  # noqa: BLE001 — 数据层异常一律降级不炸
        log.warning("sector_snapshot 窗口查询失败: %r", e)
        return []
    if not rows:
        return []
    return [dict(zip(_SNAPSHOT_KEYS, row, strict=True)) for row in rows]


def _default_client() -> Any | None:
    """延迟加载默认 CH 客户端（不可用时返回 None，由调用方转降级）。"""
    try:
        from zephyr.data.ch_writer import get_client

        return get_client()
    except Exception:  # noqa: BLE001 — 连接/依赖问题一律降级
        log.warning("ch_writer 默认客户端不可用", exc_info=True)
        return None
