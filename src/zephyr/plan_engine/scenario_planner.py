# [BLUEPRINT] MOD-PLAN-005 | 待统筹登记（44号 §4 M3-③ 多情景方案+§9.11 竞价三细节）
# [MODULE] zephyr.plan_engine.scenario_planner
# [DOMAIN] D_PLAN
# [DEPENDENCIES] zephyr.plan_engine.overnight_boundary_reviser(OvernightRevision); zephyr.plan_engine.tomorrow_boundary_planner(TomorrowBoundary); zephyr.plan_engine.premarket_constraint_loader(SCENARIO_LIST); zephyr.data.ch_reader（默认 CH 读取通道）; zephyr.data.table_registry（表名解析）
# [CONSUMERS] MOD-PLAN-002(premarket_constraint_loader 9:25 竞价匹配的上游修正源); prediction_log 落库（M4-②，后续波次接）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 竞价仅作验证信号不作下单通道（40号决策⑧ MVP 不碰集合竞价，本模块零下单路径）; fail-open 不阻塞主流程; auction_book 缺数据=竞价验证段 degraded 不影响 9:00 三情景段; 9 情景语义与 MOD-PLAN-002 SCENARIO_LIST 对齐; 输出纯 dataclass JSON 可序列化
# [MODIFY-GUARD] blueprint.md
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单通道异常→该段降级(None/缺省值)+trace 留痕; 整体不抛异常（仅 trade_date 非法抛 ValueError）
# [TESTS] tests/plan_engine/test_scenario_planner.py
# [A_module] module_id=MOD-PLAN-005 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

ScenarioPlanner — 盘前多情景方案+竞价三细节 (MOD-PLAN-005)

44号 §4 M3-③ 落码：盘前"多情景方案整机"。MOD-PLAN-002 只"加载昨夜边界+9:25 竞价
匹配 9 情景"，缺"今日三情景操作预案"输出与 auction_book（1.46M 行已采集）的消费
接入——本模块补该缺口，两段式：

    - 9:00 三情景预案：输入 OvernightRevision.final_shift（MOD-PLAN-004 隔夜修正）
      +昨日边界 TomorrowBoundary（MOD-PLAN-001 产出，调用方注入）→ 高开/平开/低开
      三套参数化预案（加仓上限/禁加仓价位/减仓触发/动作清单，按档位映射缩放）。
    - 9:25 竞价验证+二次匹配：消费 auction_book 五档快照算竞价三细节（§9.11），
      复用 9 情景（SCENARIO_LIST 语义对齐 MOD-PLAN-002）二次匹配，输出最终情景
      确认/降信。auction_book 缺数据→本段 degraded，不影响 9:00 三情景段。

竞价三细节（§9.11 设计真源，消费 auction_book）：
    - D1 虚拟开盘价偏离 = (9:25 虚拟匹配价-昨收)/昨收（成交额加权的全市场聚合），
      与 M3-① gap_adj 方向交叉验证：背离→降信半个修正幅度（§9.6 末段）。
    - D2 匹配量放大 = 竞价成交量/5 日竞价均量 ≥1.2× 且方向一致→确认；
      量缩（<1.0×）→降信半档。
    - D3 撤单识别（9:20 分界，9:20 后不可撤单）：fake_ratio = 9:20 撤单量/
      9:15-9:20 峰值委托量（委托量=五档买卖委托合计，撤单量=峰值-9:20 后首快照
      委托量的口径代理）；>0.6→竞价方向信号作废（虚假申报，主力诱多/诱空）。
    - 昨日涨停竞价溢价 = 昨涨停股（kline_daily ⋈ stk_limit 收盘≥涨停价）今日
      竞价均涨幅——打板情绪开盘验证注记（联动 §9.7 反核/溢价名单留后续波次）。

档位映射（44号 §9.5/§9.6）：final_shift=-1 保守×0.5 / -0.5 偏守×0.8（半档-20%）/
0 正常×1.0 / +0.5 偏多×1.2（半档+20%）/ +1 进攻×1.2（封顶 firm 单票 8% 由消费方执行）。

不做什么：不直接改 TomorrowBoundary/ConstraintState（消费方负责应用）/
         不做方向点预测（90号 §7 只画栏杆不算命）/不参与集合竞价下单（40号决策⑧）。

依据: 44_premarket_intraday_decision_upgrade §4 M3-③ + §9.6 末段 + §9.11；40号 §2.9 决策⑧
SSoT: depgraph MOD-PLAN-005（待统筹登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: trade_date + OvernightRevision(final_shift/gap_adj) + TomorrowBoundary(可选注入) + auction_book/kline_daily/stk_limit
# 特征: 三情景参数化预案 / deviation(D1) / volume_ratio(D2) / fake_ratio(D3) / yesterday_limit_premium
# 算法: 9:00 三情景生成 → 9:25 竞价三细节验证 → 9 情景二次匹配 + 确认/降信/作废
# 输出: ScenarioPlan（纯 frozen dataclass，JSON 可序列化，供 prediction_log 落库）

"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Final

from zephyr.plan_engine.overnight_boundary_reviser import (
    OvernightBoundaryReviser,
    OvernightRevision,
)
from zephyr.plan_engine.premarket_constraint_loader import SCENARIO_LIST
from zephyr.plan_engine.tomorrow_boundary_planner import TomorrowBoundary

log = logging.getLogger(__name__)

# ── 常量（44号 §9.11/§9.6 参数默认值，全部可经 ScenarioPlannerConfig 覆盖）──

OPEN_THRESHOLD: Final = 0.02  # 高/低开判定阈值 ±2%（与 MOD-PLAN-002._match_scenario 对齐语义）
VOLUME_CONFIRM_RATIO: Final = 1.2  # D2 放量确认阈值：竞价量/5日均量 ≥1.2×（§9.11/§9.6 末段）
VOLUME_SHRINK_RATIO: Final = 1.0  # D2 量缩阈值：<1.0× → 降信半档
FAKE_RATIO_VOID: Final = 0.6  # D3 虚假申报作废阈值：fake_ratio >0.6 → 竞价方向信号作废
HISTORY_DAYS: Final = 5  # D2 竞价均量窗口（5 日）
HISTORY_WINDOW_CALENDAR_DAYS: Final = 15  # 历史取数窗口（自然日，覆盖≥5 交易日）
GAP_SIGNIFICANT: Final = 0.005  # 背离判定的 gap_adj 显著性下限（半档阈值，|gap| 不足不判背离）

AUCTION_START: Final = "09:15"  # 集合竞价开始（自由申报期，可撤单）
CANCEL_DEADLINE: Final = "09:20"  # 撤单分界（9:20 后不可撤单，40号决策⑧ 交易规则表）
AUCTION_END: Final = "09:25"  # 集合竞价撮合时点（虚拟匹配价定格）

BASE_MAX_ADD_POSITION: Final = 0.30  # boundary 缺省时的加仓上限基线（MOD-PLAN-001 默认口径）

# 档位映射（44号 §9.5 保守/进攻 + §9.6 ±半档=加仓上限±20%）：shift → (档位名, 加仓上限缩放)
SHIFT_STANCE: Final = {
    -1.0: ("CONSERVATIVE", 0.5),  # 保守整档（§9.5：加仓上限×0.5）
    -0.5: ("DEFENSIVE", 0.8),  # 偏守半档（§9.6：-20%）
    0.0: ("NORMAL", 1.0),  # 正常
    0.5: ("OFFENSIVE", 1.2),  # 偏多半档（§9.6：+20%）
    1.0: ("AGGRESSIVE", 1.2),  # 进攻整档（§9.5：×1.2，封顶 firm 单票 8% 由消费方执行）
}

# 五档委托量合计表达式（auction_book 买卖五档量求和，D3 委托量口径）
_BOOK_VOL_EXPR: Final = (
    "toFloat64(bid_volume1)+toFloat64(bid_volume2)+toFloat64(bid_volume3)"
    "+toFloat64(bid_volume4)+toFloat64(bid_volume5)"
    "+toFloat64(ask_volume1)+toFloat64(ask_volume2)+toFloat64(ask_volume3)"
    "+toFloat64(ask_volume4)+toFloat64(ask_volume5)"
)

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀，与 ch_reader/overnight_boundary_reviser 同约定）
# 今日竞价末快照（9:25 虚拟匹配价/累计竞价量/成交额，按标的 argMax 取末 tick）
_SQL_AUCTION_FINAL_SNAPSHOT = (
    "SELECT symbol, symbol_canonical, "
    "argMax(toFloat64(last_price), timestamp) AS match_price, "
    "argMax(toFloat64(pre_close), timestamp) AS pre_close, "
    "argMax(toFloat64(volume), timestamp) AS match_vol, "
    "argMax(toFloat64(amount), timestamp) AS match_amt "
    "FROM {table} FINAL WHERE trade_date = toDate('{trade_date}') GROUP BY symbol"
)
# D3 撤单识别：9:15-9:20 峰值委托量 vs 9:20 后首快照委托量（9:20 后不可撤单=真实委托）
_SQL_AUCTION_BOOK_SERIES = (
    "SELECT symbol, "
    "maxIf({book_vol}, timestamp < toDateTime64('{deadline}', 3, 'Asia/Shanghai')) AS peak_vol, "
    "argMinIf({book_vol}, timestamp, timestamp >= toDateTime64('{deadline}', 3, 'Asia/Shanghai')) AS vol_after, "
    "countIf(timestamp < toDateTime64('{deadline}', 3, 'Asia/Shanghai')) AS n_pre, "
    "countIf(timestamp >= toDateTime64('{deadline}', 3, 'Asia/Shanghai')) AS n_after "
    "FROM {table} FINAL WHERE trade_date = toDate('{trade_date}') GROUP BY symbol"
)
# 历史竞价量（D2 分母）：过去 N 自然日窗口内按 (日,标的) 取末 tick 累计竞价量，Python 侧按日聚合
_SQL_AUCTION_HISTORY_VOL = (
    "SELECT trade_date, symbol, argMax(toFloat64(volume), timestamp) AS v "
    "FROM {table} FINAL "
    "WHERE trade_date < toDate('{trade_date}') AND trade_date >= toDate('{win_start}') "
    "GROUP BY trade_date, symbol ORDER BY trade_date DESC"
)
# 昨日涨停名单：kline_daily ⋈ stk_limit（USING 无别名写法，inject_final 注入 FINAL 后语法仍合法，
# 与 akshare_provider #198/overnight_boundary_reviser 同约定）；收盘≥涨停价-0.001（四舍五入容差）
_SQL_LIMIT_UP_SYMBOLS = (
    "SELECT symbol_canonical FROM {kline_table} INNER JOIN {stk_table} "
    "USING (symbol_canonical, trade_date) "
    "WHERE trade_date = toDate('{prev_date}') AND limit_up IS NOT NULL "
    "AND toFloat64(close) >= toFloat64(limit_up) - 0.001"
)


def _parse_tsv(tsv: str, ncols: int) -> list[list[str]]:
    """把 ch_reader.query 返回的 TSV 字符串解析成行列表（ncols 不足跳过该行）。"""
    if not tsv or not tsv.strip():
        return []
    rows: list[list[str]] = []
    for line in tsv.strip().split("\n"):
        vals = line.rstrip("\r").split("\t")
        if len(vals) >= ncols:
            rows.append(vals)
    return rows


def _safe_float(v: Any) -> float | None:
    """安全转 float；失败/NaN/Inf 返回 None（区别于 0.0，供降级判定）。"""
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def _snap_shift(shift: float) -> float:
    """final_shift 吸附到五档集合 {-1,-0.5,0,+0.5,+1}（非预期值就近吸附+截断）。"""
    return max(-1.0, min(1.0, round(shift * 2) / 2))


# ── 配置契约（44号 §9.11/§9.6 参数 config 化，默认值取设计真源口径）──


@dataclass(frozen=True)
class ScenarioPlannerConfig:
    """盘前多情景方案配置（全参数可调，默认值=44号设计真源口径）。"""

    open_threshold: float = OPEN_THRESHOLD  # 高/低开判定阈值（与 MOD-PLAN-002 ±2% 对齐）
    volume_confirm_ratio: float = VOLUME_CONFIRM_RATIO  # D2 放量确认阈值 1.2×
    volume_shrink_ratio: float = VOLUME_SHRINK_RATIO  # D2 量缩阈值 1.0×
    fake_ratio_void: float = FAKE_RATIO_VOID  # D3 虚假申报作废阈值 0.6
    history_days: int = HISTORY_DAYS  # D2 竞价均量窗口（5 日）
    history_window_calendar_days: int = HISTORY_WINDOW_CALENDAR_DAYS
    gap_significant: float = GAP_SIGNIFICANT  # 背离判定 gap_adj 显著性下限
    cancel_deadline: str = CANCEL_DEADLINE  # 撤单分界时刻（9:20）
    base_max_add_position: float = BASE_MAX_ADD_POSITION  # boundary 缺省基线


DEFAULT_CONFIG: Final = ScenarioPlannerConfig()


# ── 输出契约（供 prediction_log 落库 + MOD-PLAN-002 消费）──


@dataclass(frozen=True)
class ScenarioActionPlan:
    """单情景操作预案（9:00 产出，高开/平开/低开三选一被激活）。

    参数化边界与动作清单：加仓上限（final_shift 档位缩放）/禁加仓价位/减仓触发价/
    必出止盈价（boundary 注入时给绝对价位，缺省 None=仅相对参数）+ 中文动作清单。
    """

    name: str  # HIGH_OPEN / FLAT_OPEN / LOW_OPEN
    open_pct_min: float | None  # 触发开盘涨幅下界（含，None=无下界）
    open_pct_max: float | None  # 触发开盘涨幅上界（不含，None=无上界）
    stance: str  # 档位（CONSERVATIVE/DEFENSIVE/NORMAL/OFFENSIVE/AGGRESSIVE）
    final_shift: float  # 隔夜修正档位（-1/-0.5/0/+0.5/+1）
    max_add_position: float  # 修正后加仓上限（基线×档位缩放）
    no_add_price: float | None  # 禁加仓价位（防追高）
    reduce_trigger_price: float | None  # 减仓触发价（箱体下沿）
    must_exit_price: float | None  # 必出止盈价位
    actions: list[str]  # 动作清单（中文，含数值留痕）


@dataclass(frozen=True)
class AuctionVerification:
    """竞价三细节验证结果（9:25 产出，§9.11）。

    auction_book 缺数据/查询异常 → 全字段 None + status 留痕（degraded），
    不影响 9:00 三情景段（fail-open 铁律）。
    """

    deviation: float | None  # D1 虚拟开盘价偏离（成交额加权，(9:25 匹配价-昨收)/昨收）
    volume_ratio: float | None  # D2 竞价成交量/5 日竞价均量
    fake_ratio: float | None  # D3 撤单比（9:20 撤单量/9:15-9:20 峰值委托量）
    yesterday_limit_premium: float | None  # 昨日涨停竞价溢价（昨涨停股竞价均涨幅）
    direction: str | None  # 竞价方向桶 UP/DOWN/FLAT（deviation 对 ±open_threshold）
    direction_consistent: bool | None  # 与 gap_adj 方向一致性（None=无 gap_adj 基准）
    confirmed: bool  # 放量≥1.2× 且方向一致 → 确认
    volume_shrink: bool  # 量缩（<1.0×）→ 降信半档
    direction_void: bool  # fake_ratio>0.6 → 竞价方向信号作废（虚假申报）
    status: str  # ok / degraded:no_data / degraded:no_history / error:...
    detail: dict[str, Any] = field(default_factory=dict)  # 样本数/峰值委托量等留痕


@dataclass(frozen=True)
class ScenarioPlan:
    """今日三情景操作预案+竞价验证总产出（MOD-PLAN-005 输出契约，JSON 可序列化）。"""

    date: str  # 交易日（ISO）
    three_scenarios: list[ScenarioActionPlan]  # 9:00 三情景预案（HIGH/FLAT/LOW 顺序固定）
    auction_verification: AuctionVerification | None  # 9:25 竞价验证（None=未执行）
    final_scenario: str  # 最终情景（9 情景之一，SCENARIO_LIST 语义）
    confidence_scale: float  # 信度缩放（1.0 确认 / 0.5 降信半档 / 0.25 双降信）
    degraded: bool  # 任一段降级留痕（竞价验证段降级不影响三情景段）
    reasons: list[str]  # 决策理由链（留痕）
    trace: dict[str, Any]  # 通道状态留痕

    def to_dict(self) -> dict[str, Any]:
        """JSON 可序列化字典（prediction_log 落库契约）。"""
        return asdict(self)


# ── 盘前多情景方案器 ──


class ScenarioPlanner:
    """盘前多情景方案器（MOD-PLAN-005）。

    数据经 ch_client 注入（测试 mock/离线）；未注入时走项目默认 CH 通道
    （zephyr.data.ch_reader.query）。竞价仅作验证信号不作下单通道（40号决策⑧）。
    """

    def __init__(
        self,
        ch_client: Callable[[str], str] | None = None,
        config: ScenarioPlannerConfig | None = None,
    ) -> None:
        self._config = config or DEFAULT_CONFIG
        self._ch = ch_client  # None → 查询时走 ch_reader.query（惰性解析，离线可导入）

    # ── 基础设施 ──────────────────────────────────────────────────────────

    @staticmethod
    def _table(category_id: str, fallback: str) -> str:
        """按 category_id 解析全限定表名；注册表不可用降级 fallback（fail-open）。"""
        try:
            from zephyr.data.table_registry import get_registry

            return get_registry().table(category_id)
        except Exception as exc:  # noqa: BLE001 — fail-open：表名解析失败不阻塞主流程
            log.warning("表名解析失败 %s，降级 %s: %s", category_id, fallback, exc)
            return fallback

    def _query(self, sql: str, channel: str, trace: dict[str, Any]) -> str:
        """执行 CH 查询（自动注入 FINAL）；异常→通道降级空串+留痕。"""
        try:
            if self._ch is not None:
                return self._ch(sql)
            from zephyr.data import ch_reader

            return ch_reader.query(sql)
        except Exception as exc:  # noqa: BLE001 — fail-open：单通道异常不炸整体
            log.warning("通道 %s 查询异常，降级跳过: %s", channel, exc)
            trace["channels"][channel] = f"error:{exc}"
            return ""

    # ── 9:00 三情景预案（44号 §4 M3-③）────────────────────────────────────

    def _build_three_scenarios(
        self,
        revision: OvernightRevision,
        boundary: TomorrowBoundary | None,
        reasons: list[str],
    ) -> list[ScenarioActionPlan]:
        """9:00 三情景操作预案：final_shift 档位映射 × 昨日边界参数化。

        final_shift 经 SHIFT_STANCE 映射档位缩放（§9.5/§9.6），作用于加仓上限；
        boundary 注入时给绝对价位（禁加仓/减仓触发/必出止盈），缺省 None 仅相对参数。
        """
        cfg = self._config
        shift = _snap_shift(revision.final_shift)
        stance, scale = SHIFT_STANCE[shift]
        base_add = boundary.max_add_position if boundary is not None else cfg.base_max_add_position
        max_add = round(base_add * scale, 4)
        no_add = boundary.no_add_price if boundary is not None else None
        reduce_trigger = boundary.box_lower if boundary is not None else None
        must_exit = boundary.must_exit_price if boundary is not None else None
        th = cfg.open_threshold

        reasons.append(
            f"final_shift={shift:+.1f} → {stance}档（加仓上限 {base_add:.0%}×{scale}={max_add:.0%}）"
            + ("（boundary 已注入）" if boundary is not None else "（boundary 缺省，价位字段 None）")
        )

        price_note = f"禁加仓价位 {no_add}" if no_add is not None else "禁加仓价位待 boundary 注入"
        reduce_note = (
            f"回落破减仓触发 {reduce_trigger} → 执行减仓"
            if reduce_trigger is not None
            else "减仓触发价待 boundary 注入"
        )
        exit_note = f"冲上沿必出止盈 {must_exit}（纪律）" if must_exit is not None else "必出止盈价待 boundary 注入"

        return [
            ScenarioActionPlan(
                name="HIGH_OPEN",
                open_pct_min=th,
                open_pct_max=None,
                stance=stance,
                final_shift=shift,
                max_add_position=max_add,
                no_add_price=no_add,
                reduce_trigger_price=reduce_trigger,
                must_exit_price=must_exit,
                actions=[
                    f"高开≥+{th:.0%} 激活：加仓上限 {max_add:.0%}（{stance}档）",
                    f"冲高至{price_note}，禁止追仓（防高开诱多）",
                    "竞价三细节验证：放量≥1.2×且方向一致→高开真涨按预案执行；量缩/方向背离→高开假涨不追仓",
                    "9:20 撤单比>0.6→竞价方向信号作废，按洗盘观望（虚假申报）",
                    reduce_note,
                ],
            ),
            ScenarioActionPlan(
                name="FLAT_OPEN",
                open_pct_min=-th,
                open_pct_max=th,
                stance=stance,
                final_shift=shift,
                max_add_position=max_add,
                no_add_price=no_add,
                reduce_trigger_price=reduce_trigger,
                must_exit_price=must_exit,
                actions=[
                    f"平开±{th:.0%} 激活：加仓上限 {max_add:.0%}（{stance}档），正常执行昨夜边界",
                    f"突破验证条件满足前不抢跑；{price_note}",
                    exit_note,
                    reduce_note,
                ],
            ),
            ScenarioActionPlan(
                name="LOW_OPEN",
                open_pct_min=None,
                open_pct_max=-th,
                stance=stance,
                final_shift=shift,
                max_add_position=max_add,
                no_add_price=no_add,
                reduce_trigger_price=reduce_trigger,
                must_exit_price=must_exit,
                actions=[
                    f"低开≤-{th:.0%} 激活：加仓上限 {max_add:.0%}（{stance}档），企稳前禁新开仓（防抄底接刀）",
                    "竞价假跌信号（方向背离向上+放量）→观察反核，不追卖",
                    "竞价三细节确认真跌（放量+方向一致向下）→从严执行减仓纪律",
                    reduce_note,
                ],
            ),
        ]

    # ── 竞价三细节（44号 §9.11，消费 auction_book）─────────────────────────

    def _load_final_snapshot(self, trade_date: str, trace: dict[str, Any]) -> dict[str, dict[str, Any]]:
        """今日竞价末快照：symbol_canonical → {match_price/pre_close/match_vol/match_amt}。"""
        table = self._table("market_auction_book", "c1_market.auction_book")
        tsv = self._query(
            _SQL_AUCTION_FINAL_SNAPSHOT.format(table=table, trade_date=trade_date),
            "auction_book",
            trace,
        )
        snap: dict[str, dict[str, Any]] = {}
        for sym, canon, mp, pc, vol, amt in _parse_tsv(tsv, 6):
            mp_f, pc_f = _safe_float(mp), _safe_float(pc)
            vol_f, amt_f = _safe_float(vol), _safe_float(amt)
            key = (canon or sym or "").strip()
            if not key:
                continue
            snap[key] = {
                "match_price": mp_f,
                "pre_close": pc_f,
                "match_vol": vol_f,
                "match_amt": amt_f,
            }
        return snap

    def _compute_deviation(self, snap: dict[str, dict[str, Any]]) -> tuple[float | None, float, int]:
        """D1 虚拟开盘价偏离：成交额加权 (9:25 匹配价-昨收)/昨收。

        返回 (deviation, today_total_vol, n_symbols)；无有效样本→(None, 0.0, 0)。
        """
        w_sum = 0.0
        dev_sum = 0.0
        total_vol = 0.0
        n = 0
        for row in snap.values():
            mp, pc = row["match_price"], row["pre_close"]
            vol = row["match_vol"] or 0.0
            total_vol += vol
            if mp is None or pc is None or pc <= 0 or mp <= 0:
                continue
            w = row["match_amt"] if row["match_amt"] and row["match_amt"] > 0 else 0.0
            if w <= 0:
                continue  # 无成交额=未匹配，不计入加权
            dev_sum += (mp - pc) / pc * w
            w_sum += w
            n += 1
        if w_sum <= 0:
            return None, total_vol, n
        return dev_sum / w_sum, total_vol, n

    def _compute_volume_ratio(
        self, trade_date: str, today_vol: float, trace: dict[str, Any]
    ) -> tuple[float | None, list[str]]:
        """D2 匹配量放大：今日竞价总量 / 5 日竞价均量。返回 (ratio, 历史日期留痕)。"""
        cfg = self._config
        d = datetime.date.fromisoformat(trade_date)
        win_start = (d - datetime.timedelta(days=cfg.history_window_calendar_days)).isoformat()
        table = self._table("market_auction_book", "c1_market.auction_book")
        tsv = self._query(
            _SQL_AUCTION_HISTORY_VOL.format(table=table, trade_date=trade_date, win_start=win_start),
            "auction_book_history",
            trace,
        )
        by_date: dict[str, float] = {}
        for dt, _sym, v in _parse_tsv(tsv, 3):
            v_f = _safe_float(v)
            if v_f is not None:
                by_date[dt] = by_date.get(dt, 0.0) + v_f
        dates = sorted(by_date, reverse=True)[: cfg.history_days]
        if not dates:
            return None, []
        avg = sum(by_date[x] for x in dates) / len(dates)
        if avg <= 0:
            return None, dates
        return today_vol / avg, dates

    def _compute_fake_ratio(self, trade_date: str, trace: dict[str, Any]) -> tuple[float | None, dict[str, Any]]:
        """D3 撤单识别（9:20 分界）：fake_ratio = 撤单量/9:15-9:20 峰值委托量。

        委托量=五档买卖委托合计；撤单量=峰值（9:15-9:20 可撤单期）-9:20 后首快照
        委托量（9:20 后不可撤单=真实委托留存）的口径代理。全市场按委托量加权聚合。
        快照不足（无 9:20 前/后样本）的标的剔除，防缺数据误判为全撤。
        """
        table = self._table("market_auction_book", "c1_market.auction_book")
        deadline = f"{trade_date} {self._config.cancel_deadline}:00"
        tsv = self._query(
            _SQL_AUCTION_BOOK_SERIES.format(
                table=table, deadline=deadline, book_vol=_BOOK_VOL_EXPR, trade_date=trade_date
            ),
            "auction_book_series",
            trace,
        )
        rows = _parse_tsv(tsv, 5)
        cancelled_sum = 0.0
        peak_sum = 0.0
        n_used = 0
        n_skipped = 0
        for _sym, peak, after, n_pre, n_after in rows:
            peak_f, after_f = _safe_float(peak), _safe_float(after)
            n_pre_f, n_after_f = _safe_float(n_pre), _safe_float(n_after)
            if not n_pre_f or not n_after_f or peak_f is None or peak_f <= 0 or after_f is None:
                n_skipped += 1
                continue
            cancelled_sum += max(0.0, peak_f - after_f)
            peak_sum += peak_f
            n_used += 1
        detail = {"symbols_used": n_used, "symbols_skipped": n_skipped, "peak_book_vol": peak_sum}
        if peak_sum <= 0:
            return None, detail
        return cancelled_sum / peak_sum, detail

    def _compute_limit_up_premium(
        self,
        trade_date: str,
        snap: dict[str, dict[str, Any]],
        hist_dates: list[str],
        trace: dict[str, Any],
    ) -> tuple[float | None, int]:
        """昨日涨停竞价溢价：昨涨停股（收盘≥涨停价）今日竞价均涨幅。

        昨日交易日取竞价历史窗口内最近一日（auction_book 有数据的最近历史日）；
        名单经 kline_daily ⋈ stk_limit（symbol_canonical universal 跨表 JOIN）。
        无名单/无匹配 → (None, 0)（该注记缺失不阻塞主流程）。
        """
        if not hist_dates:
            return None, 0
        prev_date = max(hist_dates)
        kline = self._table("market_kline_daily", "c1_market.kline_daily")
        stk = self._table("market_stk_limit", "c1_market.stk_limit")
        tsv = self._query(
            _SQL_LIMIT_UP_SYMBOLS.format(kline_table=kline, stk_table=stk, prev_date=prev_date),
            "limit_up_symbols",
            trace,
        )
        symbols = [r[0].strip() for r in _parse_tsv(tsv, 1) if r[0].strip()]
        if not symbols:
            return None, 0
        gains: list[float] = []
        for s in symbols:
            row = snap.get(s)
            if not row:
                continue
            mp, pc = row["match_price"], row["pre_close"]
            if mp is None or pc is None or pc <= 0 or mp <= 0:
                continue
            gains.append((mp - pc) / pc)
        if not gains:
            return None, len(symbols)
        return sum(gains) / len(gains), len(symbols)

    def _verify_auction(
        self,
        trade_date: str,
        revision: OvernightRevision,
        trace: dict[str, Any],
        reasons: list[str],
    ) -> AuctionVerification:
        """竞价三细节验证（9:25，§9.11）。auction_book 缺数据→degraded 不炸。"""
        cfg = self._config
        snap = self._load_final_snapshot(trade_date, trace)
        if not snap:
            trace["channels"].setdefault("auction_book", "skipped:no_data")
            reasons.append("auction_book 无今日数据，竞价验证段 degraded（不影响 9:00 三情景段）")
            return AuctionVerification(
                deviation=None,
                volume_ratio=None,
                fake_ratio=None,
                yesterday_limit_premium=None,
                direction=None,
                direction_consistent=None,
                confirmed=False,
                volume_shrink=False,
                direction_void=False,
                status="degraded:no_data",
            )
        trace["channels"]["auction_book"] = f"ok:{len(snap)}symbols"

        # D1 虚拟开盘价偏离
        deviation, today_vol, n_dev = self._compute_deviation(snap)
        # D2 匹配量放大
        volume_ratio, hist_dates = self._compute_volume_ratio(trade_date, today_vol, trace)
        # D3 撤单识别
        fake_ratio, fake_detail = self._compute_fake_ratio(trade_date, trace)
        # 昨日涨停竞价溢价
        premium, n_limit_up = self._compute_limit_up_premium(trade_date, snap, hist_dates, trace)

        # 方向桶（与 MOD-PLAN-002 ±2% 对齐）
        direction: str | None = None
        if deviation is not None:
            if deviation >= cfg.open_threshold:
                direction = "UP"
            elif deviation <= -cfg.open_threshold:
                direction = "DOWN"
            else:
                direction = "FLAT"

        # 与 gap_adj 方向交叉验证（§9.6 末段：|gap| 不足半档阈值不判背离）
        gap_adj = revision.gap_adj
        consistent: bool | None = None
        if deviation is not None and gap_adj is not None and abs(gap_adj) >= cfg.gap_significant:
            consistent = deviation * gap_adj > 0
            if not consistent:
                reasons.append(f"D1 方向背离：deviation={deviation:+.2%} vs gap_adj={gap_adj:+.2%} → 降信半个修正幅度")
        elif gap_adj is None:
            reasons.append("gap_adj 缺失（外盘通道无数据），方向一致性不验证")

        # D2 确认/量缩
        volume_shrink = volume_ratio is not None and volume_ratio < cfg.volume_shrink_ratio
        confirmed = (
            volume_ratio is not None
            and volume_ratio >= cfg.volume_confirm_ratio
            and (consistent is True or consistent is None)  # 无 gap_adj 基准时量能单边确认
        )
        if confirmed:
            reasons.append(f"D2 放量确认：竞价量/5日均量={volume_ratio:.2f}× ≥ {cfg.volume_confirm_ratio}×")
        elif volume_shrink:
            reasons.append(f"D2 量缩：{volume_ratio:.2f}× < {cfg.volume_shrink_ratio}× → 降信半档")
        elif volume_ratio is None:
            reasons.append("D2 历史竞价量缺失（5 日均量不可得），量能验证降级")

        # D3 虚假申报作废
        direction_void = fake_ratio is not None and fake_ratio > cfg.fake_ratio_void
        if direction_void:
            reasons.append(
                f"D3 虚假申报：fake_ratio={fake_ratio:.2f} > {cfg.fake_ratio_void} → 竞价方向信号作废（诱多/诱空）"
            )

        # 昨日涨停溢价注记（§9.11 联动 §9.7，本波次仅注记不门控）
        if premium is not None:
            reasons.append(f"昨日涨停竞价溢价={premium:+.2%}（{n_limit_up} 只昨涨停股，打板情绪开盘验证）")

        return AuctionVerification(
            deviation=deviation,
            volume_ratio=volume_ratio,
            fake_ratio=fake_ratio,
            yesterday_limit_premium=premium,
            direction=direction,
            direction_consistent=consistent,
            confirmed=confirmed,
            volume_shrink=volume_shrink,
            direction_void=direction_void,
            status="ok" if deviation is not None else "degraded:no_matched_amount",
            detail={"symbols": len(snap), "deviation_symbols": n_dev, "fake": fake_detail, "history_dates": hist_dates},
        )

    # ── 9:25 二次匹配修正（复用 9 情景，语义对齐 MOD-PLAN-002）────────────────

    def _rematch_scenario(
        self,
        verification: AuctionVerification,
        reasons: list[str],
    ) -> tuple[str, float]:
        """9:25 竞价实况二次匹配：三细节验证结论 → 最终情景确认/降信。

        桶由 D1 deviation 对 ±open_threshold 划分（HIGH/LOW/FLAT）；
        子型由验证结论选择：确认→REAL_* / 量缩或背离→FAKE_* / 撤单作废→*_WASH。
        返回 (final_scenario, confidence_scale)；scenario 保证 ∈ SCENARIO_LIST。
        """
        confidence = 1.0
        if verification.direction_consistent is False:
            confidence *= 0.5  # 背离 → 降信半个修正幅度（§9.6 末段）
        if verification.volume_shrink:
            confidence *= 0.5  # 量缩 → 降信半档（§9.11 D2）

        if verification.direction_void:
            # D3 作废：方向信号不可信 → 各桶 WASH 变体（观望）
            scenario = {"UP": "HIGH_OPEN_WASH", "DOWN": "LOW_OPEN_WASH"}.get(
                verification.direction or "", "FLAT_OPEN_WASH"
            )
            reasons.append(f"竞价方向作废 → {scenario}（不采信竞价方向）")
            return scenario, confidence

        if verification.direction == "UP":
            scenario = "HIGH_OPEN_REAL_UP" if verification.confirmed else "HIGH_OPEN_FAKE_UP"
        elif verification.direction == "DOWN":
            scenario = "LOW_OPEN_REAL_DOWN" if verification.confirmed else "LOW_OPEN_FAKE_DOWN"
        else:
            # FLAT 桶：放量确认时按 deviation 符号出方向子型，否则 WASH
            if verification.confirmed and verification.deviation is not None and verification.deviation > 0:
                scenario = "FLAT_OPEN_REAL_UP"
            elif verification.confirmed and verification.deviation is not None and verification.deviation < 0:
                scenario = "FLAT_OPEN_REAL_DOWN"
            else:
                scenario = "FLAT_OPEN_WASH"

        if scenario not in SCENARIO_LIST:  # 兜底：语义对齐 MOD-PLAN-002 9 情景常量
            scenario = "FLAT_OPEN_WASH"
        reasons.append(
            f"9:25 二次匹配 → {scenario}（confidence_scale={confidence}，confirmed={verification.confirmed}）"
        )
        return scenario, confidence

    # ── 主合成 ────────────────────────────────────────────────────────────

    def compute(
        self,
        trade_date: str | datetime.date,
        revision: OvernightRevision | None = None,
        boundary: TomorrowBoundary | None = None,
    ) -> ScenarioPlan:
        """计算今日三情景操作预案+竞价验证（两段式，任何单通道异常降级不炸整体）。

        Args:
            trade_date: 交易日（ISO 字符串或 date）。
            revision: 隔夜修正（MOD-PLAN-004 产出）；None 时用同一 ch_client 现算。
            boundary: 昨日边界（MOD-PLAN-001 产出，调用方注入）；None 时价位字段缺省。

        Returns:
            ScenarioPlan：三情景预案 + 竞价三细节验证 + 最终情景/信度 + 全程留痕。
        """
        if isinstance(trade_date, str):
            d = datetime.date.fromisoformat(trade_date)  # 非法日期抛 ValueError（ERROR_CONTRACT）
        else:
            d = trade_date
        iso = d.isoformat()
        trace: dict[str, Any] = {"channels": {}}
        reasons: list[str] = []

        # 隔夜修正（缺省现算，共用 ch_client 便于测试 mock）
        if revision is None:
            revision = OvernightBoundaryReviser(ch_client=self._ch).compute(iso)
            trace["channels"]["overnight_revision"] = "computed_inline"
        else:
            trace["channels"]["overnight_revision"] = "injected"

        # 段一：9:00 三情景预案（不依赖竞价数据）
        three = self._build_three_scenarios(revision, boundary, reasons)

        # 段二：9:25 竞价验证+二次匹配（auction_book 缺数据→degraded 不影响段一）
        verification = self._verify_auction(iso, revision, trace, reasons)
        degraded = verification.status != "ok" or boundary is None
        if verification.deviation is None:
            # 竞价数据缺失：与 MOD-PLAN-002 无竞价数据降级口径一致（FLAT_OPEN_WASH）
            final_scenario, confidence = "FLAT_OPEN_WASH", 1.0
            reasons.append("竞价验证段 degraded → final_scenario 缺省 FLAT_OPEN_WASH（与 MOD-PLAN-002 降级口径一致）")
        else:
            final_scenario, confidence = self._rematch_scenario(verification, reasons)

        return ScenarioPlan(
            date=iso,
            three_scenarios=three,
            auction_verification=verification,
            final_scenario=final_scenario,
            confidence_scale=confidence,
            degraded=degraded,
            reasons=reasons,
            trace=trace,
        )


# ── 主入口 ──


def compute_scenario_plan(
    trade_date: str | datetime.date,
    ch_client: Callable[[str], str] | None = None,
    config: ScenarioPlannerConfig | None = None,
    revision: OvernightRevision | None = None,
    boundary: TomorrowBoundary | None = None,
) -> ScenarioPlan:
    """盘前多情景方案主入口（MOD-PLAN-005）。

    Args:
        trade_date: 交易日（ISO 字符串或 date）。
        ch_client: CH 查询客户端（sql→TSV），可注入（测试 mock/离线）；
            None 时走项目默认 CH 通道（zephyr.data.ch_reader.query）。
        config: 参数配置（None=44号设计真源默认值）。
        revision: 隔夜修正注入位（None=经 OvernightBoundaryReviser 现算）。
        boundary: 昨日边界注入位（MOD-PLAN-001 产出；None 时价位字段缺省）。

    Returns:
        ScenarioPlan：纯 frozen dataclass，JSON 可序列化（供 prediction_log 落库）。
        竞价仅作验证信号不作下单通道（40号决策⑧）。
    """
    return ScenarioPlanner(ch_client=ch_client, config=config).compute(trade_date, revision=revision, boundary=boundary)
