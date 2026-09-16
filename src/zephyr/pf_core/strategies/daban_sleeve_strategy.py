# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md
# [MODULE] zephyr.pf_core.strategies.daban_sleeve_strategy
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.governance.strategies.strategy_base; zephyr.shared.contracts.selection_result; zephyr.signal_ashare.screening.short_term_stock_selector; zephyr.signal_ashare.limit_up.youzi_relay_emotion_engine; zephyr.signal_ashare.quant_short_term_strength_engine; zephyr.signal_ashare.strategy_signal.dual_engine_fusion_decision_engine; datetime（封板时刻合成）; pandas（权重面板构建，函数内 lazy）; zephyr.infrastructure.database_service（持久化负载只读通道，函数内 lazy，宪法 §9.1）; zephyr.data.trading_calendar（前一交易日真源，lazy）; zephyr.ex_core.daban_load_producer（LOAD_INSERT_COLUMNS 列序真源，lazy）; schemas.categories.market.market_daban_engine_load（表名真源，lazy）
# [CONSUMERS] zephyr.pf_core.strategies（lazy re-export）; lane A framework_composer（经 build_weight_panel_for_dates 消费本策略产 daban-sleeve 权重面板）; zephyr.ex_core.daban_load_producer（产负载行经注入的 load_source 送入本策略 PIT 真读）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] canonical 输出=权重 dict[str,float]（对齐 StrategyBase）；权重和<=1.0（归一化后 max_single 截顶只减不增）；仅做多；6类决策优先级权重表与 21号 §3.6 L304-317 一致；本模块 MUST 只被 import 一次（@StrategyRegistry.register 对重复 strategy_id 直接 raise，双注册陷阱见 strategies/__init__.py）；PIT 真读铁律：决策日 T 只消费 trade_date<T（前一交易日）的负载行（load_source.fetch_load 承载 shift(1)，禁未来函数）；输入缺失禁静默零负载：PIT 读空必须 logger.warning 显式 skipped 该日，非静默返回全零；负载行→引擎 payload 由本策略拥有（row_to_engine_payload），不喂 selector 资格门（其机构输入非本事件源可产，喂默认将致 overall<45→"回避"系统性清零）；**产而不消铁律**：无注入 load_source 时本策略 MUST 默认经 DatabaseService 真读 c1_market.daban_engine_load（生产者持久化行零消费者=P0）；PIT 双保险=SQL 谓词 trade_date<as_of + 代码级逐行剔除 day>=as_of（读源/假源越权回未来行亦不可见）；回退到更早事件日分区须发**恰好一条** WARNING 点名回退（禁静默陈旧消费，对齐 wyckoff_engine 禁静默零值纪律）；开关 use_persisted_load=False 关闭持久化消费=逐决策日回落既有 fail-closed 分支（不新建"空但自信"的候选集）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空 universe/空 signals->返回空 dict（不抛异常）；payload 缺负载/引擎降级/决策"中性"/final_score<=0->剔除该标的不抛异常；build_weight_panel_for_dates：load_source 某决策日返回空行->logger.warning+该日全零（显式 skipped，非静默）；负载行缺/非法 symbol->剔除该行不抛；默认持久化读源：as_of 非日期->ValueError 抛给调用方（禁裸串入 SQL），读库异常->logger.warning 降级空行（该日走同一 skipped 分支，不抛不崩决策链）
# [TESTS] tests/pf_core/test_daban_sleeve_strategy.py; tests/pf_core/test_daban_sleeve_strategy_load.py
# [A_module] module_id=MOD-L05-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: pf_core
# category: strategy_implementation
# status: active
# created: "2026-08-21"
# ---

"""
D_PORTFOLIO_CORE — 打板 sleeve 组装策略（CAND-SIG-012 晋升，P0-4① 施工）

组装 signal_ashare 四引擎（全部 production，直接 import 调用不重复造轮子）：
  - ShortTermStockSelector（BM-SEL-22，MOD-SIG-023）——资格门：降级/推荐"回避"→剔除
  - YouziRelayEmotionEngine（BM-SEL-23，MOD-SIG-033）——游资情绪 6 因子评分
  - QuantShortTermStrengthEngine（BM-SEL-24，MOD-SIG-034）——量化强度 6 维评级
  - DualEngineFusionDecisionEngine（BM-SEL-25，MOD-SIG-035）——双引擎融合 6 类决策

排序算法（21 号 §3.6 L304-317 施工补全）：
  final_score = fused_score × priority_weight(6类决策)，按 final_score 降序取 Top-N
  （打板 sleeve N≤10 容量硬约束），权重按 final_score 比例归一化到 ≤1.0。

urgency=immediate（盘中立即，21 号 L255-259 映射表：T 日盘中买入，T+1 卖出）。

SSoT: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.5/§3.6

# [ALGO_FLOW] external: docs/03_modules/_domain_portfolio_core/algo_flow/daban_sleeve_strategy.yaml
"""

from __future__ import annotations

import datetime as _dt
import logging
import re
from typing import Any, Callable, Final, Mapping, Sequence

from zephyr.governance.strategies.strategy_base import (
    StrategyBase,
    StrategyMeta,
    StrategyRegistry,
)
from zephyr.shared.contracts.selection_result import (
    URGENCY_IMMEDIATE,
    SelectionResult,
    SignalInput,
    TargetPosition,
)
from zephyr.signal_ashare.strategy_signal.dual_engine_fusion_decision_engine import (
    DualEngineFusionDecisionEngine,
    FusionDecisionInput,
)
from zephyr.signal_ashare.quant_short_term_strength_engine import (
    QuantShortTermStrengthEngine,
    QuantStrengthInput,
)
from zephyr.signal_ashare.screening.short_term_stock_selector import (
    ShortTermStockSelector,
    StockSelectionInput,
)
from zephyr.signal_ashare.limit_up.youzi_relay_emotion_engine import (
    YouziEmotionInput,
    YouziRelayEmotionEngine,
)

_logger = logging.getLogger(__name__)

# 6 类决策优先级权重（21 号 §3.6 L308-315 裁定表：final_score = fusion_score × priority_weight）
# P0 主升龙头 / P1 二进三 / P2 跟风 / P3 复苏 / P4 伪强 / P5 地天反包；"中性"→0 剔除
_DECISION_PRIORITY: dict[str, float] = {
    "主升龙头": 1.0,
    "二进三": 0.85,
    "跟风": 0.65,
    "复苏": 0.50,
    "伪强": 0.30,
    "地天反包": 0.20,
}

_EXCLUDE_RECOMMENDATIONS = ("回避",)  # BM-SEL-22 资格门：回避→剔除

# 负载行→引擎 payload 常量（消费契约归本策略拥有）
_MAIN_LINE_MIN_CONSEC: Final = 2  # 主线龙头代理口径：连板数≥2（fusion/quant is_main_line）
_TRADE_TIME_RE: Final[re.Pattern[str]] = re.compile(r"(\d{1,2}):(\d{2})(?::(\d{2}))?\s*$")

# 持久化负载消费（c1_market.daban_engine_load）——品类键与 DDL-as-Code CATEGORY_ID 同名；
# T-1 陈旧判定回溯窗（自然日，覆盖春节/国庆最长连休）
_LOAD_CATEGORY_ID: Final = "market_daban_engine_load"
_T1_LOOKBACK_NATURAL_DAYS: Final = 15


def _min_load_date() -> "_dt.date":
    """事件日下限哨兵真源=producer.MIN_EVENT_DATE（禁本地另写日期字面量）。

    CH 对空 Date 列取 max() 回 1970-01-01（或 0000-00-00），早于此一律判"无分区"，
    不得被误读成陈旧回退分区。
    """
    from zephyr.ex_core.daban_load_producer import MIN_EVENT_DATE

    return MIN_EVENT_DATE


def _plain_symbol(symbol: Any) -> str:
    """canonical/裸码 → 纯数字码（面板列与 universe 同源）；非法→空串。"""
    s = str(symbol or "").strip()
    if not s:
        return ""
    return s.split(".")[0] if "." in s else s


def _seal_datetime(trade_date: Any, first_touch_time: Any) -> _dt.datetime | None:
    """事件日 + 首触时刻 HH:MM:SS → datetime（youzi seal_time 输入）；缺/非法→None。"""
    if first_touch_time is None:
        return None
    m = _TRADE_TIME_RE.search(str(first_touch_time))
    if not m:
        return None
    try:
        d = _dt.date.fromisoformat(str(trade_date)[:10])
    except (TypeError, ValueError):
        return None
    hh, mm = int(m.group(1)), int(m.group(2))
    ss = int(m.group(3) or 0)
    try:
        return _dt.datetime(d.year, d.month, d.day, hh, mm, ss)
    except ValueError:
        return None


def _maybe_positive(value: Any) -> float | None:
    """真实正有限数 → float；None/空/非数/NaN/inf/非正 → None（不喂引擎默认，禁拍假值）。"""
    if value is None:
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if f != f or f in (float("inf"), float("-inf")) or f <= 0:
        return None
    return f


# ---------------------------------------------------------------------------
# 持久化负载真读（c1_market.daban_engine_load → DatabaseService PIT）
# ——治"信号产而不消"P0：生产者已落表，本段是其上**默认**消费通道
# ---------------------------------------------------------------------------

# SQL 模板常量（NO-BARE-SQL gate 约定：_SQL_* 前缀集中，不散落裸 SQL）
_SQL_PERSISTED_MAX_EVENT_DATE: Final = (
    "SELECT max(trade_date) FROM {table} WHERE trade_date < toDate('{as_of}')"
)
_SQL_PERSISTED_ROWS_BY_DATE: Final = (
    "SELECT {columns} FROM {table} FINAL WHERE trade_date = toDate('{event_date}')"
)

#: 读通道注入位（duck：sql -> rows）；默认走 DatabaseService reader 角色
LoadRowReader = Callable[[str], Sequence[Any]]

_TRUTH_CACHE: dict[str, str] = {}


def _persisted_load_columns() -> tuple[str, ...]:
    """负载列序真源=daban_load_producer.LOAD_INSERT_COLUMNS（与 DDL INSERT_COLUMNS 同序）。"""
    from zephyr.ex_core.daban_load_producer import LOAD_INSERT_COLUMNS

    return LOAD_INSERT_COLUMNS


def _persisted_load_table() -> str:
    """表名真源=schemas DDL-as-Code（RULE-SSOT，禁本模块硬编码 "{db}.{table}"）。

    schemas/ 是仓根 DDL-as-Code 包（不在 src 包内），与 zephyr.pf_alloc.allocation_inputs
    同一先例：显式挂仓根到 sys.path 后 import，目的是不复制表结构常量（复制=两份真源）。
    """
    if "table" not in _TRUTH_CACHE:
        import sys

        try:
            from zephyr.shared.io.paths import REPO_ROOT as _ROOT

            root = str(_ROOT)
        except Exception:  # noqa: BLE001 — 仅路径解析降级（同 allocation_inputs 先例）
            from pathlib import Path as _P

            root = str(_P(__file__).resolve().parents[4])
        if root not in sys.path:
            sys.path.insert(0, root)
        from schemas.categories.market.market_daban_engine_load import (
            CATEGORY_ID,
            DATABASE,
            TABLE_NAME,
        )

        if CATEGORY_ID != _LOAD_CATEGORY_ID:
            raise RuntimeError(
                f"daban-sleeve: 负载品类漂移 DDL={CATEGORY_ID!r} != 本模块 {_LOAD_CATEGORY_ID!r}"
            )
        _TRUTH_CACHE["table"] = f"{DATABASE}.{TABLE_NAME}"
    return _TRUTH_CACHE["table"]


def _default_load_reader(sql: str) -> Sequence[Any]:
    """默认只读通道：DatabaseService reader 角色（宪法 §9.1 禁裸 duckdb/裸连接散落）。"""
    from zephyr.infrastructure.database_service import get_db_service

    conn = get_db_service().get_clickhouse_conn(role="reader")
    return conn.execute(sql)


def _coerce_decision_date(value: Any) -> _dt.date:
    """决策日归一为 date（拒非日期——禁裸串入 SQL）；date/datetime/'YYYY-MM-DD' 可容。"""
    if isinstance(value, _dt.datetime):
        return value.date()
    if isinstance(value, _dt.date):
        return value
    try:
        return _dt.date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"daban-sleeve: 决策日 {value!r} 非法（禁裸串入 SQL）") from exc


def _as_date(value: Any) -> _dt.date | None:
    """负载行 trade_date（driver 可能回 date/datetime/str）→ date；非法→None。"""
    if isinstance(value, _dt.datetime):
        return value.date()
    if isinstance(value, _dt.date):
        return value
    try:
        return _dt.date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None


def _previous_trading_day(as_of: _dt.date) -> _dt.date | None:
    """决策日 T 的前一交易日（真源 zephyr.data.trading_calendar，禁本模块自建日历）。

    取 [T-回溯窗, T-1] 内最后一个交易日；日历不可用/窗口内无交易日→None（不可判陈旧，
    调用方不据此告警，也不放宽 PIT——PIT 谓词恒 trade_date<T，与本函数解耦）。
    """
    try:
        from zephyr.data.trading_calendar import trading_days_in_range

        days = trading_days_in_range(
            as_of - _dt.timedelta(days=_T1_LOOKBACK_NATURAL_DAYS),
            as_of - _dt.timedelta(days=1),
        )
    except Exception as exc:  # noqa: BLE001 — 日历降级不阻断决策读（PIT 谓词不受影响）
        _logger.warning("daban-sleeve: 前一交易日解析异常（陈旧判定不可用，PIT 谓词不变）: %s", exc)
        return None
    return days[-1] if days else None


class _PersistedDabanLoadSource:
    """daban_engine_load 持久化负载的默认消费源（duck 同 DabanEngineLoadSource.fetch_load）。

    PIT：SQL 谓词 trade_date < as_of（决策日 T 只用前一交易日及更早）+ 代码级逐行复核
    （读源越权回未来行亦不可见）。分区缺失不猜——回退到更早事件日时发**恰好一条** WARNING
    点名回退目标；异常→降级空行，由策略侧走与"今日无负载行"同一 fail-closed 分支。
    """

    def __init__(self, reader: LoadRowReader | None = None) -> None:
        self._reader = _default_load_reader if reader is None else reader
        self._warned_fallbacks: set[tuple[str, str]] = set()

    def resolve_event_date(self, as_of_date: Any) -> _dt.date | None:
        """决策日前最近的事件日分区（trade_date<as_of 的 max）；无分区/异常→None。"""
        as_of = _coerce_decision_date(as_of_date)
        sql = _SQL_PERSISTED_MAX_EVENT_DATE.format(table=_persisted_load_table(), as_of=as_of.isoformat())
        try:
            rows = list(self._reader(sql))
        except Exception as exc:  # noqa: BLE001 — 读库异常降级空（策略侧 skipped 告警）
            _logger.warning("daban-sleeve: 负载事件日解析异常，该决策日降级空: %s", exc)
            return None
        if not rows or rows[0][0] is None:
            return None
        day = _as_date(rows[0][0])
        # PIT/空表双不靠读源自律：max() 回未来日/不可解析/CH 空表哨兵（1970-01-01 等）→ 无分区
        if day is None or day >= as_of or day < _min_load_date():
            return None
        return day

    def fetch_load(self, as_of_date: Any) -> list[dict[str, Any]]:
        """决策日 → 持久化负载行（list[dict]，键=LOAD_INSERT_COLUMNS）。"""
        as_of = _coerce_decision_date(as_of_date)
        event_date = self.resolve_event_date(as_of)
        if event_date is None:
            return []
        self._disclose_fallback(as_of, event_date)
        columns = _persisted_load_columns()
        sql = _SQL_PERSISTED_ROWS_BY_DATE.format(
            table=_persisted_load_table(),
            columns=", ".join(columns),
            event_date=event_date.isoformat(),
        )
        try:
            raw = list(self._reader(sql))
        except Exception as exc:  # noqa: BLE001 — 同上：分区读异常降级空行
            _logger.warning("daban-sleeve: 负载分区 %s 读取异常，降级空: %s", event_date, exc)
            return []
        rows: list[dict[str, Any]] = []
        for record in raw:
            if len(record) != len(columns):
                continue
            row = dict(zip(columns, record, strict=True))
            day = _as_date(row.get("trade_date"))
            if day is None or day >= as_of:  # PIT 代码级双保险（禁未来函数，不依赖 SQL 自律）
                continue
            row["trade_date"] = day.isoformat()
            rows.append(row)
        return rows

    def _disclose_fallback(self, as_of: _dt.date, event_date: _dt.date) -> None:
        """T-1 分区缺失而用了更早分区→恰好一条 WARNING 点名回退（禁静默陈旧消费）。"""
        expected = _previous_trading_day(as_of)
        if expected is None or event_date >= expected:
            return
        key = (as_of.isoformat(), event_date.isoformat())
        if key in self._warned_fallbacks:
            return
        self._warned_fallbacks.add(key)
        _logger.warning(
            "daban-sleeve: 决策日 %s 的 T-1 分区 %s 无负载——fallback 回退到更早事件日 %s"
            "（滞后 %d 天，点名披露非静默）",
            as_of,
            expected,
            event_date,
            (expected - event_date).days,
        )


def _resolve_load_source(load_source: Any, use_persisted_load: bool, reader: LoadRowReader | None) -> Any:
    """负载源择路：注入源优先（测试/自定义）→ 开关开=持久化默认源 → 开关关=None（无消费）。"""
    if load_source is not None:
        return load_source
    if not use_persisted_load:
        _logger.warning(
            "daban-sleeve: 持久化负载消费开关关闭（use_persisted_load=False 且无注入源）"
            "——全部决策日回落 fail-closed skipped 分支，不产任何候选",
        )
        return None
    return _PersistedDabanLoadSource(reader=reader)


@StrategyRegistry.register
class DabanSleeveStrategy(StrategyBase):
    """打板 sleeve 组装策略——双引擎融合评分 × 6 类决策优先级取 Top-N。

    signals 负载约定（dict[str, dict]，键=标的代码）：
        {
          "600519": {
            "selector": {StockSelectionInput 字段（不含 symbol）, 可选——缺省跳过资格门},
            "youzi": {YouziEmotionInput 字段},
            "quant": {QuantStrengthInput 字段},
            "fusion_context": {FusionDecisionInput 上下文字段（连板数/主线/涨跌幅/风险分）, 可选},
          },
        }

    用法：
        strategy = DabanSleeveStrategy()
        weights = strategy.generate_target_weights(universe, signals, {"top_n": 10, "max_single": 0.15})
        result = strategy.select(SignalInput(...))  # → SelectionResult(urgency=immediate)

        # 决策日面板：默认经 DatabaseService 真读持久化负载表 c1_market.daban_engine_load
        panel = strategy.build_weight_panel_for_dates(dates, universe)
        panel = strategy.build_weight_panel_for_dates(dates, universe, load_source=my_source)   # 注入优先
        panel = strategy.build_weight_panel_for_dates(dates, universe, use_persisted_load=False)  # 关消费
    """

    meta = StrategyMeta(
        strategy_id="daban-sleeve",
        name="打板sleeve组装策略",
        description="组装短线选股/游资情绪/量化强度/双引擎融合四引擎，融合评分×6类决策优先级取Top-N，urgency=immediate",
        strategy_type="equity_long_only",
        version="1.0.0",
        author="zephyr-agent",
        factor_dependencies=[],
        tags=["daban", "sleeve", "dual_engine_fusion", "a_share", "limit_up"],
        supported_markets=["a_share"],
        battle_map_ref="BM-SEL-23-C",   # 作战地图：选股·情绪周期策略映射（production，涨停板情绪周期）
    )

    _URGENCY = URGENCY_IMMEDIATE

    def __init__(
        self,
        selector: Any | None = None,
        youzi_engine: Any | None = None,
        quant_engine: Any | None = None,
        fusion_engine: Any | None = None,
    ) -> None:
        # 依赖注入：默认真实四引擎（production），测试注入 fake 隔离（不打网络/DB）
        self._selector = selector or ShortTermStockSelector()
        self._youzi = youzi_engine or YouziRelayEmotionEngine()
        self._quant = quant_engine or QuantShortTermStrengthEngine()
        self._fusion = fusion_engine or DualEngineFusionDecisionEngine()

    def generate_target_weights(
        self,
        universe: list[str] | None = None,
        signals: dict[str, Any] | None = None,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, float]:
        """四引擎逐标的评分，final_score 降序取 Top-N 按比例归一化。

        Args:
            universe: 候选标的列表（涨停标的+连板梯队，漏斗①产出）。
            signals: {symbol: 引擎输入负载}，形态见类 docstring。
            constraints: {"top_n": int=10（打板容量硬约束 N≤10）, "max_single": float=0.15}

        Returns:
            {symbol: weight}，权重和 <= 1.0。空输入/无有效评分返回 {}。
        """
        if not universe or not signals:
            _logger.debug(
                "daban-sleeve: 空 universe/signals，返回空权重 (universe=%d signals=%d)",
                len(universe or []),
                len(signals or {}),
            )
            return {}

        cons = constraints or {}
        top_n = min(int(cons.get("top_n", 10)), 10)  # 21 号 §3.6：打板 sleeve N≤10 容量硬约束
        max_single = float(cons.get("max_single", 0.15))

        scored: list[tuple[str, float]] = []
        for sym in universe:
            payload = signals.get(sym)
            if not isinstance(payload, dict):
                continue
            score = self._score_symbol(sym, payload)
            if score > 0:
                scored.append((sym, score))

        if not scored:
            _logger.debug("daban-sleeve: 无有效融合评分，返回空权重")
            return {}

        scored.sort(key=lambda x: x[1], reverse=True)
        picks = scored[:top_n]
        total = sum(s for _, s in picks)
        if total <= 0:
            return {}

        # 比例归一化（和=1.0）后 max_single 截顶——截顶只减不增，权重和 ≤1.0 不变量成立
        weights = {sym: min(s / total, max_single) for sym, s in picks}

        _logger.info(
            "daban-sleeve: 选出 %d 只（top_n=%d, max_single=%.4f, 权重和=%.4f）",
            len(weights),
            top_n,
            max_single,
            sum(weights.values()),
        )
        return weights

    def _score_symbol(self, symbol: str, payload: dict[str, Any]) -> float:
        """单标的四引擎流水线：资格门 → 游资/量化评分 → 融合决策 × 优先级权重。"""
        # ① BM-SEL-22 资格门（可选负载）：降级或"回避"→剔除
        selector_fields = payload.get("selector")
        if isinstance(selector_fields, dict):
            sel_res = self._selector.analyze(StockSelectionInput(symbol=symbol, **selector_fields))
            if sel_res.is_degraded or sel_res.recommendation in _EXCLUDE_RECOMMENDATIONS:
                return 0.0

        # ②③ BM-SEL-23/24 双引擎评分
        youzi_res = self._youzi.analyze(YouziEmotionInput(**payload.get("youzi", {})))
        quant_res = self._quant.analyze(QuantStrengthInput(**payload.get("quant", {})))

        # ④ BM-SEL-25 融合决策（降级传播契约：上游降级→融合降级→剔除）
        fusion_res = self._fusion.analyze(
            FusionDecisionInput(
                youzi_result=youzi_res,
                quant_result=quant_res,
                **payload.get("fusion_context", {}),
            )
        )
        if fusion_res.is_degraded:
            return 0.0

        priority = _DECISION_PRIORITY.get(str(fusion_res.decision), 0.0)
        if priority <= 0:
            return 0.0
        return float(fusion_res.fused_score) * priority

    # ------------------------------------------------------------------
    # 负载真读（PIT，经注入 load_source）——daban 四引擎应用层批产消费面
    # ------------------------------------------------------------------

    @staticmethod
    def row_to_engine_payload(row: Mapping[str, Any]) -> dict[str, Any]:
        """daban_engine_load 负载行 → 四引擎 payload（youzi/quant/fusion_context）。

        可产字段真实映射；不可产字段**省略**（交引擎 dataclass 中性默认，禁拍假值冒充）。
        **不产 selector 门**：其机构评分输入（target_price/fundamental/float_cap/corr 等）
        非打板事件源可产，喂默认会使 overall<45→"回避"系统性清零整条 sleeve（挖矿 LUE-1
        实证），故按策略契约省略 selector 键（资格门可选、缺省即跳过）。
        is_main_line 为消费侧代理口径（连板数≥2），非真源主线判定，已在注释留痕。
        """
        consec = int(row.get("consec_limit") or 0)
        open_board = row.get("open_board_count")
        seal_amount = row.get("seal_amount")
        cap_raw = row.get("float_market_cap")
        pct = row.get("stock_change_pct")
        mkt_pct = row.get("market_change_pct")
        breadth = row.get("market_breadth_ratio")
        is_main = consec >= _MAIN_LINE_MIN_CONSEC

        youzi: dict[str, Any] = {
            "consecutive_limit_ups": consec,
            "seal_amount": float(seal_amount) if seal_amount is not None else 0.0,
            "open_board_count": int(open_board) if open_board is not None else 0,
            "seal_time": _seal_datetime(row.get("trade_date"), row.get("first_touch_time")),
            "sector_limit_up_count": int(row.get("sector_limit_up_count") or 0),
            "market_limit_up_count": int(row.get("market_limit_up_count") or 0),
            "market_breadth_ratio": float(breadth) if breadth is not None else 0.5,
        }
        quant: dict[str, Any] = {
            "stock_change_pct": float(pct) if pct is not None else 0.0,
            "market_change_pct": float(mkt_pct) if mkt_pct is not None else 0.0,
            "consecutive_limit_ups": consec,
            "is_main_line": is_main,
        }
        # 流通市值为挖矿 LUE-1 实证可产真字段（stock_indicator.circ_mv 折元）——仅在真实
        # 正数时喂入，解锁 youzi 封单质量（seal_amount/cap 封流比 20 分因子）与 quant 资金
        # 分母；缺/非正则不喂，交引擎 0.0 中性默认（封单质量诚实记 "流通市值为0"，禁拍假值）。
        cap = _maybe_positive(cap_raw)
        if cap is not None:
            youzi["float_market_cap"] = cap
            quant["float_market_cap"] = cap
        fusion_context: dict[str, Any] = {
            "consecutive_limit_ups": consec,
            "is_main_line": is_main,
            "stock_change_pct": float(pct) if pct is not None else 0.0,
            "market_change_pct": float(mkt_pct) if mkt_pct is not None else 0.0,
        }
        return {"youzi": youzi, "quant": quant, "fusion_context": fusion_context}

    @classmethod
    def build_signals_from_load(cls, load_rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        """负载行序列 → signals（{纯数字码: 四引擎 payload}）；非法/缺 symbol 行剔除。"""
        signals: dict[str, Any] = {}
        for row in load_rows:
            plain = _plain_symbol(row.get("symbol"))
            if not plain:
                continue
            signals[plain] = cls.row_to_engine_payload(row)
        return signals

    def build_weight_panel_for_dates(
        self,
        dates: Sequence[Any],
        universe: Sequence[str],
        *,
        load_source: Any = None,
        top_n: int = 10,
        max_single: float = 0.15,
        use_persisted_load: bool = True,
        load_reader: LoadRowReader | None = None,
    ):
        """逐决策日 PIT 读负载 → 四引擎评分 → date×symbol 权重面板（供 composer 路由消费）。

        负载源三态（`_resolve_load_source` 择路）：
          1. 注入 load_source → 原样使用（测试/自定义源，行为与既往一致）；
          2. 无注入 + use_persisted_load=True（**出厂默认**）→ 本策略自建
             `_PersistedDabanLoadSource`，经 DatabaseService reader 角色真读持久化表
             c1_market.daban_engine_load（生产者落表自此有默认消费者，治"产而不消"）；
          3. 无注入 + use_persisted_load=False → 无源，逐决策日回落下方"零行"分支。

        每个决策日 T：source.fetch_load(T)（只回 trade_date<T 的最新事件日分区，
        shift(1) 防未来函数；未来日期分区在 SQL 谓词与代码级双重过滤下永不可见）
        → 负载行→signals→generate_target_weights→面板行。
        **禁静默零负载**：某日无 PIT 负载行→logger.warning 显式 skipped（该日全零=现金日，
        引擎沿用持仓），与 event_sentiment_adapter.build_event_weight_panel 契约同构。

        Args:
            dates: 决策日序列（date/datetime.str，通常 load_history 面板 index）。
            universe: 候选标的（面板列，纯数字码或 canonical 自动归一）。
            load_source: 负载源（duck：fetch_load(date)->list[dict]）；None=按开关走
                持久化默认源（生产通道），非 None 时优先于开关。
            top_n / max_single: 透传策略 constraints（打板 N≤10 容量硬约束）。
            use_persisted_load: 持久化负载消费开关（默认 True；False 且无注入源=不消费）。
            load_reader: 默认持久化源的读通道注入位（sql->rows，None=DatabaseService reader）。

        Returns:
            pandas.DataFrame（index=DatetimeIndex 决策日，columns=universe 纯码，dtype float）。
        """
        import pandas as pd

        source = _resolve_load_source(load_source, use_persisted_load, load_reader)
        idx = pd.DatetimeIndex(pd.to_datetime([d if not isinstance(d, str) else d for d in dates]))
        cols = [_plain_symbol(s) for s in universe]
        cols = [c for c in cols if c]
        panel = pd.DataFrame(0.0, index=idx, columns=cols)
        uni_set = set(cols)

        for d in idx:
            rows = source.fetch_load(d.date()) if source is not None else []
            if not rows:
                _logger.warning(
                    "daban-sleeve: 决策日 %s 无 PIT 负载行（事件表未产/当日空）——显式 skipped，非静默零权重",
                    d.date(),
                )
                continue
            payload = self.build_signals_from_load(rows)
            tradable = [s for s in payload if s in uni_set]
            if not tradable:
                continue
            weights = self.generate_target_weights(
                tradable,
                {s: payload[s] for s in tradable},
                {"top_n": top_n, "max_single": max_single},
            )
            for sym, w in weights.items():
                panel.loc[d, sym] = w

        return panel.fillna(0.0)

    def select(self, signal_input: SignalInput) -> SelectionResult:
        """21 号 §3.5 标准接口：SignalInput → SelectionResult（urgency=immediate）。

        SignalInput.signals 元素约定：dict 且含 "symbol" 键，其余键为引擎输入负载。
        """
        signals_map: dict[str, Any] = {}
        for s in signal_input.signals:
            if isinstance(s, dict) and "symbol" in s:
                signals_map[str(s["symbol"])] = {k: v for k, v in s.items() if k != "symbol"}
        constraints = {"regime_budget": signal_input.regime_budget, **signal_input.metadata}
        weights = self.generate_target_weights(list(signal_input.universe), signals_map, constraints)
        portfolio = [
            TargetPosition(
                symbol=sym,
                target_weight=w,
                signal_source=self.meta.strategy_id,
                urgency=self._URGENCY,
            )
            for sym, w in weights.items()
        ]
        return SelectionResult(
            target_portfolio=portfolio,
            signals=list(signal_input.signals),
            confidence=self._placeholder_confidence(weights),
            metadata={
                "sleeve": "daban",
                "urgency": self._URGENCY,
                "confidence_note": "占位算法（21号§6待裁定-5）：入选标的权重和，非定稿置信度",
            },
        )

    @staticmethod
    def _placeholder_confidence(weights: dict[str, float]) -> float:
        """占位置信度（21 号 §6 待裁定-5：算法未定，先用权重和 ∈[0,1] 占位）。"""
        if not weights:
            return 0.0
        return min(1.0, sum(weights.values()))


__all__: Final = ["DabanSleeveStrategy"]
