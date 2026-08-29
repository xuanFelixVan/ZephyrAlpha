# [BLUEPRINT] MOD-EX-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] zephyr.ex_core.daban_pit_safety
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib; zephyr.ex_core.daban_signal_decision; zephyr.ex_core.daban_exit_decision; zephyr.data.calendar（from_db_session 延迟导入）
# [CONSUMERS] （首批回测接线前暂无）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 龙虎榜 T 日盘后 17:00 公布→T 日盘中决策只能用 T-1 及之前（trade_date<as_of_date 硬断言）; next_day_auction data_date<=decision_date; 未知数据源不断言
# [MODIFY-GUARD] 24_daban_strategy_detail.md §3.13 缺失#5（v1.9.2，必须修复）/ §3.14 缺失#10（v1.9.3）
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PIT 违规→AssertionError（Fail-Closed，宁停不错）
# [TESTS] tests/ex_core/test_daban_pit_safety.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: symbol + as_of_date + db_session（鸭子类型 execute(sql,params).fetchall()，行需 .trade_date 属性+可 dict()）
# I2: DabanPITBacktestFramework 注入 data_loader(source,date)->dict / trading_days(start,end) / next_trading_day(date)
# I3: from_db_session 装配真实依赖——db_session+symbol→get_dragon_tiger_pit；zephyr.data.trading_calendar→XSHG 真日历；其余数据源 source_loaders 显式注入
# F1: get_dragon_tiger_pit——latest=T-1 查询 + 逐行 PIT 断言
# F2: assert_pit——按 PIT_RULES 对 dragon_tiger/next_day_auction 硬断言
# F3: run_backtest——加载+PIT 断言→pre_validate 门控→情绪周期定位→classify_decision_v192→次日出场→汇总
# O1: 龙虎榜行列表 / run_backtest 汇总 dict(trades/total/by_decision)
# [/ALGO_FLOW]
"""打板 PIT 安全族（24_daban_strategy_detail §3.13#5 + §3.14#10 施工）。

缺失#5 get_dragon_tiger_pit（首批实盘前必须修复）：龙虎榜 T 日盘后 17:00
公布，T 日盘中决策只能用 T-1 日及之前龙虎榜（INV-004 铁律）——T 日盘中用
T 日龙虎榜=未来函数=回测虚高+实盘失效。查询边界 + 逐行 PIT 断言双保险。

缺失#10 DabanPITBacktestFramework：全数据源 PIT 断言规则表 + assert_pit
+ run_backtest 注入式主循环（pre_validate→classify→next_day_exit 决策链
完整可用）。波 2a 补 from_db_session 真实依赖装配——交易日历接
zephyr.data.trading_calendar（XSHG 真日历，与 c1_market.trade_calendar 同源
语义），dragon_tiger 数据源接 get_dragon_tiger_pit；emotion_cycle_score/
echelon_data/next_day_auction 三数据源 ex_core 无既有查询函数，由
source_loaders 显式注入（DB 落库接线属数据层工程，未注入加载时显式报错）。

理论背书：北大 Jiang & Li 理性预期模型——打板 alpha 来自信息未完全纳入，
回测必须严格 PIT 否则虚高（PIT 违规=虚高 alpha）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Callable

from zephyr.ex_core.daban_exit_decision import NextDayExitDecision
from zephyr.ex_core.daban_signal_decision import (
    classify_decision_v192,
    pre_validate_daban_signal,
)

__all__ = [
    "get_dragon_tiger_pit",
    "DabanPITBacktestFramework",
]


def get_dragon_tiger_pit(symbol: str, as_of_date: date, db_session) -> list[dict]:
    """龙虎榜PIT安全查询（v1.9.2 补，as_of_date 边界断言）。

    龙虎榜盘后17:00公布，T日盘中决策若用T日龙虎榜=未来函数=回测虚高+实盘失效，
    只能用T-1日及之前龙虎榜。db_session 为鸭子类型（execute(sql, params).fetchall()，
    行对象需有 .trade_date 属性且可 dict()）；具体 DB 接线由调用方负责。
    """
    latest_available = as_of_date - timedelta(days=1)
    rows = db_session.execute(
        "SELECT * FROM dragon_tiger WHERE symbol = :symbol AND trade_date <= :latest ORDER BY trade_date DESC LIMIT 5",  # noqa: bare-sql  存量参数化查询/动态标识符，format重排伪新增（§5.160.2集中化专项另列）
        {"symbol": symbol, "latest": latest_available},
    ).fetchall()
    for row in rows:  # PIT断言
        assert row.trade_date < as_of_date, (
            f"PIT VIOLATION: dragon_tiger trade_date={row.trade_date} >= as_of_date={as_of_date}"
        )
    return [dict(row) for row in rows]


@dataclass
class DabanPITBacktestFramework:
    """打板 PIT 安全回测框架（v1.9.3 补，全数据源 PIT 断言，扩展 §3.13#5 到全数据源）。

    PIT_RULES + assert_pit + run_backtest 注入式主循环完整实现；依赖注入两条路径：
    ① from_db_session 真实装配（XSHG 真日历 + get_dragon_tiger_pit）；
    ② 构造器直注 data_loader/trading_days/next_trading_day（测试/自定义数据源）。
    """

    data_loader: Callable[[str, date], dict] = field(
        default=None
    )  # (source, date) -> 数据 dict（须含 'date' 键供 PIT 断言）
    trading_days: Callable[[date, date], list] = field(default=None)  # (start, end) -> 交易日列表
    next_trading_day: Callable[[date], date] = field(default=None)  # date -> 次一交易日

    @classmethod
    def from_db_session(cls, db_session, symbol: str, source_loaders: dict | None = None) -> DabanPITBacktestFramework:
        """真实依赖装配（波 2a 注入）：最小回测路径可直接跑通。

        - trading_days/next_trading_day：统一经 zephyr.data.calendar 包取 A 股日历
          （94号 §4.1/#261 注入式改造；ASHareCalendar 委托 XSHG 真日历，与
          c1_market.trade_calendar 同源语义，延迟导入防循环依赖）；
        - dragon_tiger 数据源：接 get_dragon_tiger_pit（§3.13#5，latest=T-1 边界+逐行断言）；
        - 其余数据源（emotion_cycle_score/echelon_data/next_day_auction）：ex_core 无既有
          查询函数，由 source_loaders {source: callable(source, date)->dict} 显式注入，
          未注入的数据源加载时 RuntimeError（Fail-Closed 显式报错，不静默造数）。
        """
        # 94号 §4.1/#261：日历消费统一经 data.calendar 包（ASHareCalendar 委托
        # trading_calendar 真源，行为零变化；后续币侧装配改注入 crypto 日历即可）
        from zephyr.data.calendar import get_market_calendar

        calendar = get_market_calendar("ashare")

        loaders = dict(source_loaders or {})

        def _next_trading_day(d: date) -> date:
            cur = d + timedelta(days=1)
            while not calendar.is_trading_day(cur):
                cur += timedelta(days=1)
            return cur

        def data_loader(source: str, d: date) -> dict:
            if source == "dragon_tiger":
                rows = get_dragon_tiger_pit(symbol, d, db_session)
                latest = max((r["trade_date"] for r in rows), default=d - timedelta(days=1))
                return {"date": latest, "rows": rows}
            loader = loaders.get(source)
            if loader is None:
                raise RuntimeError(
                    "数据源未注入 source_loaders（该源无既有查询函数，需调用方提供）",
                    {"source": source},
                )
            return loader(source, d)

        return cls(data_loader=data_loader, trading_days=calendar.trading_days_in_range, next_trading_day=_next_trading_day)

    PIT_RULES = {
        "dragon_tiger": {"publish_time": "T日17:00", "available_for": "T+1日盘中"},  # §3.13#5
        "emotion_cycle_score": {"publish_time": "实时计算", "available_for": "T日盘中"},  # 当日实时可用
        "echelon_data": {"publish_time": "实时", "available_for": "T日盘中"},  # 连板梯队实时
        "seal_data": {"publish_time": "实时", "available_for": "T日盘中"},  # 封单实时
        "next_day_auction": {"publish_time": "T+1日9:25", "available_for": "T+1日9:25后"},  # 次日竞价
        "news_sentiment": {"publish_time": "实时", "available_for": "T日盘中"},  # 新闻实时
    }

    @staticmethod
    def assert_pit(data_source: str, data_date: date, decision_date: date) -> None:
        """PIT 断言（v1.9.3 补，全数据源）。未知数据源不断言（未登记规则不拦）。"""
        rule = DabanPITBacktestFramework.PIT_RULES.get(data_source)
        if not rule:
            return
        if data_source == "dragon_tiger":  # 龙虎榜：决策日只能用 T-1 日及之前
            assert data_date < decision_date, f"PIT VIOLATION: dragon_tiger {data_date} >= decision {decision_date}"
        if data_source == "next_day_auction":  # 次日竞价：决策日 T+1 只能用 T+1 日 9:25 后数据
            assert data_date <= decision_date, f"PIT VIOLATION: next_day_auction {data_date} > decision {decision_date}"

    def run_backtest(self, strategy_config: dict, start: date, end: date) -> dict:
        """PIT 安全回测主循环（v1.9.3 补，注入式）。

        决策链：①数据加载+PIT 断言 → ②前置质量评估（§3.14#8）→ ③情绪周期定位
        → ④双引擎 7 类决策（§3.13#3）→ ⑤次日出场（§3.13#1）→ 汇总。
        退潮期仅 pre_val['pass'] is True（≥70 分）放行，CONDITIONAL 不放行（spec 语义）。
        """
        if not (self.data_loader and self.trading_days and self.next_trading_day):
            raise RuntimeError(
                "DabanPITBacktestFramework 未注入 data_loader/trading_days/next_trading_day"
                "（真实装配走 from_db_session，测试/自定义走构造器直注）"
            )
        results = []
        for decision_date in self.trading_days(start, end):
            dragon_tiger = self.data_loader("dragon_tiger", decision_date)  # ① 数据加载+PIT 断言
            self.assert_pit("dragon_tiger", dragon_tiger["date"], decision_date)
            emotion = self.data_loader("emotion_cycle_score", decision_date)
            echelon = self.data_loader("echelon_data", decision_date)
            pre_val = pre_validate_daban_signal(  # ② 前置质量评估（§3.14 缺失#8）
                echelon["health"], echelon["height"], echelon["sector_resonance"], echelon["follow_count"]
            )
            if not pre_val["pass"]:
                continue
            phase = emotion["phase"]  # ③ 情绪周期定位（§3.2）
            if (
                phase in ("退潮",) and pre_val["pass"] is not True
            ):  # spec 原意：退潮期仅满分级（pass is True）放行，CONDITIONAL 不放行
                continue
            decision = classify_decision_v192(emotion["score"], echelon["tech_score"], phase)  # ④ 双引擎决策（§3.5）
            if decision not in ("BOARD", "CONTINUE"):
                continue
            next_day = self.next_trading_day(decision_date)  # ⑤ 次日出场（§3.13#1）
            auction = self.data_loader("next_day_auction", next_day)
            self.assert_pit("next_day_auction", auction["date"], next_day)
            exit_dec = NextDayExitDecision().decide({"cost_basis": echelon["price"]}, auction, emotion, holding_days=1)
            results.append({"date": decision_date, "decision": decision, "exit": exit_dec})
        return self._summarize(results)

    @staticmethod
    def _summarize(results: list) -> dict:
        """回测结果汇总（骨架级：计数+决策分布；盈亏核算待数据层接线后补全）。"""
        by_decision: dict = {}
        for r in results:
            by_decision[r["decision"]] = by_decision.get(r["decision"], 0) + 1
        return {"total": len(results), "by_decision": by_decision, "trades": results}
