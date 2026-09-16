# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.matching_engine
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.portfolio; zephyr.backtest.core.matching_logic; zephyr.backtest.core.cost_model_calibration（滑点/冲击标定真源：冲击腿 per-tier η/β/σ + 口径开关）; zephyr.data.ch_reader（StkLimitProvider lazy import）; zephyr.data.implementations.akshare_provider（_limit_pct_of lazy import，涨跌幅切片单一真源）; zephyr.execution_simulation.almgren_chriss_impact_model（冲击成本 lazy import，P0-2）
# [CONSUMERS] zephyr.backtest.implementations.vectorized_engine; zephyr.backtest.implementations.event_driven_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] A股约束: T+1/涨跌停/停牌/100股整数倍; 委托MatchingLogic保证回测=实盘一致性; 涨跌停价三级解析链=stk_limit表PIT行→limit_pct_of切片规则（ST经st_stock_list最近可得快照）→板块前缀推断（无日期兜底），禁再造第四份口径（#ARCH-DATA-020）
#              INV-COST-LEGS(#23 H2): 执行成本两腿互斥可加——滑点腿（尺寸无关，价差+逆向
#              选择）唯一在 MatchingLogic 按 ADV 五分位解析，本引擎只透传「当日成交额」
#              不重算；冲击腿（尺寸相关，走单位移）唯一在本引擎 _apply_impact_to_books
#              按同层标定 η/β/σ 计价（IMPACT_GAMMA_RATIO=0 已裁定永久项不再另计，
#              否则同段位移计费两次）。引擎侧禁出现任何档位 bps/η 字面量（第二真源）。
#              INV-UNIT-001(车道K 2026-09-16): volumes 入参口径=「股」且与 prices 同复权空间
#              （由 load_history→market_units 出口一次性归一），本引擎禁再乘 100/禁再乘因子；
#              参与率与冲击的分子分母必须同源同纲（订单股数 ÷ 当日成交股数）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] MatchingError
# [TESTS] tests/backtest/test_matching_engine.py, tests/backtest/test_cost_model_wiring.py
# [A_module] module_id=MOD-BT-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""回测撮合引擎模块（v1.1.0 重构：委托 MatchingLogic 保证回测=实盘一致性）

职责:
  - 根据目标权重生成买卖订单（回测专用 orchestrator）
  - 委托 MatchingLogic 执行纯函数式撮合（回测=实盘一致性核心）
  - 应用A股约束: 100股整数倍/涨跌停/停牌
  - 将 MatchingFill 转换为 BacktestFill（加 date 字段）

v1.1.0 重构要点:
  - 移除重复的 MatchingConfig（ARCH-034 CLASS-UNIQUENESS 违规）-> 从 matching_logic 导入并 re-export
  - 移除重复的 _apply_slippage / _calc_commission -> 委托给 MatchingLogic
  - 新增 generate_fills_with_order_book() 支持5档盘口撮合（Level 4 撮合）
  - 新增 generate_fills_with_tick() 支持 Tick级5档撮合（做T专用）
  - 新增 match_order/match_limit_order/match_tick_order 单笔撮合入口

约束:
  - 撮合行为与 D_EX_CORE MiniQmtBroker 完全一致（共用同一份 MatchingLogic）
  - 涨跌停: 价格触及涨跌停板时不成交（价源三级解析链，见 _limit_bounds docstring；
    stk_limit 表 PIT 行优先，缺行走 _limit_pct_of 日期切片规则，#ARCH-DATA-020）
  - 停牌: 无数据时跳过
  - T+1: 由 Portfolio 负责（matching_engine 只生成 fills）
  - 成交量量纲（P0-1 车道K 2026-09-16，INV-UNIT-001）: `volumes` 入参口径**唯一**
    为「股」，且与 `prices` 同处一个复权空间。源头 `c1_market.kline_daily.volume`
    按 data_source **混存**两纲——`''` 主进料 94.6% 行为「手」(1手=100股)、
    `tushare`/`Baostock` 5.4% 行为「股」（表 schema 注释「成交量(股)」只对 5.4%
    成立）；归一在消费端边界 `zephyr.factor.core.evaluation.backtest.load_history`
    经 `zephyr.shared.utils.market_units.normalize_market_panel` 逐行自洽探测一次
    完成，本引擎**不再乘 100、不再乘复权因子**（散乘即双重缩放，参与率/冲击/换手
    全错）。参与率 = 订单股数 ÷ 当日成交股数，与价格量纲无关（同纲缩放不变）。
  - 绝对价语义（涨跌停）与价格缩放（P0-2 车道K）: 引擎价可以是"窗口末锚定复权价"
    （逐标的乘子 k≈1，最大失真见 MarketPanelReport），此时 stk_limit 表内**原始
    绝对价**与引擎价不同纲——_limit_bounds 按除权参考价自洽性检测后改走
    收益空间等价式（prev_close×(1±pct)），保证缩放不改变封板判定（见其 docstring）。

SSoT: docs/03_modules/_domain_backtest/blueprint.md §3.2 §5.1 §16.7

# [ALGO_FLOW] external: docs/03_modules/_domain_backtest/algo_flow/matching_engine.yaml
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, replace
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Callable, Iterable, Optional

from zephyr.backtest.core import cost_model_calibration as cost_cal
from zephyr.backtest.core.matching_logic import (
    MatchingConfig,
    MatchingFill,
    MatchingLogic,
    MatchingLogicError,
    MatchOrderInput,
    OrderBookSnapshot,
    TickSnapshot,
)
from zephyr.backtest.core.portfolio import BacktestFill, Portfolio

_logger = logging.getLogger(__name__)


class MatchingError(Exception):
    """撮合引擎错误（回测专用 orchestrator 错误，区分 MatchingLogicError 纯函数错误）"""

    error_code = "ZA-BT-0008"

    def __init__(self, *args, error_code: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


# 兼容性 sentinel: 用于从单一价格构造的合成1档盘口的虚拟深度
# （2026-09-14 P0-2 整改后仅作为"无成交量数据时的兜底深度"；data 含 volume 列时
#  由 LiquidityGuardConfig 施加参与率上限+冲击成本，虚拟无限深度不再无条件生效）
_SYNTHETIC_DEPTH = Decimal("99999999")

#: 判定"引擎价与 stk_limit 表绝对价同纲"的相对容差（车道 K P0-2，见 _limit_bounds）。
#: 取值依据：交易所取整噪声 ≤ 半分（≤0.05% @10元 级别股价），而逐标的复权锚点在
#: 一个回测窗内的漂移通常 ≥0.3%（一次最小量级的现金分红）；0.2% 落在两者之间。
#: 判据"误为不同纲"无害——回退式 prev_close×(1±pct) 在同纲时与表价数值等价；
#: 判据"误为同纲"仅当缩放漂移 <0.2% 时发生，其对封板判定的影响同量级（可忽略）。
_LIMIT_REF_TOL = Decimal("0.002")


@dataclass(frozen=True)
class LiquidityGuardConfig:
    """日频流动性约束配置（P0-2，2026-09-14 外部审查整改）。

    仅回测撮合 orchestrator（MatchingEngine）消费——MatchingLogic 纯函数与
    实盘 MiniQmtBroker 共享链路零改动（回测=实盘一致性不变，本配置只让回测
    供给面更保守）。

    Attributes:
        max_participation_rate: 单标的单日成交量参与率上限（0.10=成交 ≤ 当日量 10%）。
            买卖同限；买单向下取整手，卖单向下取整股（清仓允许零股）。
        impact_enabled: 是否按 Almgren-Chriss 冲击模型调整成交价
            （临时+永久冲击 bps，参与率越高越贵；复用 execution_simulation 真源，
            η/β/γ/σ 按该标的流动性层从 cost_model_calibration 取标定档，口径开关
            关闭时回到 legacy 默认档。冲击=尺寸相关腿，与滑点（尺寸无关腿）互斥相加）。
    """

    max_participation_rate: Decimal = Decimal("0.10")
    impact_enabled: bool = True


def _normalize_date(value: object) -> datetime.date | None:
    """归一化交易日（str/date/datetime/Timestamp → date；None/非法 → None）。

    generate_fills* 的 date 参数历史上是 object（str/date/pd.Timestamp 均有），
    涨跌停 PIT 解析需要 date 型；非法输入返回 None（调用方退回无日期兜底路径）。
    """
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    s = str(value).strip()[:10]
    try:
        return datetime.date.fromisoformat(s)
    except ValueError:
        return None


@dataclass(frozen=True)
class LimitInfo:
    """单标的单日涨跌停约束包（StkLimitProvider 产出，撮合判定消费）。

    Attributes:
        limit_up: 涨停价（stk_limit 表 PIT 行命中时给出；NULL=无涨跌幅限制期）
        limit_down: 跌停价（同上）
        limit_pct: 涨跌停幅度小数（表行 limit_pct 或规则切片兜底产出；None=未知/无限制）
        st_flag: ST/*ST 标记（表行 st_flag 或 st_stock_list 最近可得快照 PIT）
        from_table: True=stk_limit 表 PIT 行直用（价格精确，撮合不重算）；
                    False=规则切片兜底（引擎按 prev_close×(1±pct) ROUND_HALF_UP 重算）
    """

    limit_up: Optional[Decimal] = None
    limit_down: Optional[Decimal] = None
    limit_pct: Optional[Decimal] = None
    st_flag: bool = False
    from_table: bool = False


#: StkLimitProvider 协议：`(trade_date, symbols) -> {symbol: LimitInfo}`。
#: trade_date 已归一化为 date；symbols 为撮合当日标的的原始 symbol 形态。
LimitProvider = Callable[[datetime.date, Iterable[str]], dict]


def _daily_notional_map(
    order_books: dict[str, OrderBookSnapshot],
    volumes: dict[str, Decimal] | None,
) -> dict[str, Decimal]:
    """逐笔「当日成交额」（元）= 当日成交量(股) × 当日基准价 —— 两条成本腿的流动性输入。

    本引擎唯一可得的流动性信息就是 ``volumes``（INV-UNIT-001：口径=「股」，与 prices
    同复权空间），故成交额只能由它 ×当日价 得到。标定表的分层母体是 40 日 ADV，
    用当日成交额代入是 ``cost_model_calibration.liquidity_tier`` docstring 明确认可的
    单调近似（同一把尺子，误差只在层间抖动，不会反向）。

    volume 缺失/非正、或价格非正的标的不进表：**不虚构流动性**——缺项由
    ``MatchingLogic`` 侧回落到标定真源的无信息档（全市场名义加权实证 bps），
    绝不在引擎里另立一个档位查表（那会是第二真源）。
    """
    if not volumes:
        return {}
    out: dict[str, Decimal] = {}
    for symbol, ob in order_books.items():
        vol = volumes.get(symbol)
        if vol is None or ob is None or ob.last_price is None or ob.last_price <= 0:
            continue
        v = vol if isinstance(vol, Decimal) else Decimal(str(vol))
        if v <= 0:
            continue
        out[symbol] = v * ob.last_price
    return out


def _build_target_orders(
    engine: MatchingEngine,
    target_weights: dict[str, float],
    order_books: dict[str, OrderBookSnapshot],
    portfolio: Portfolio,
    total_nav: Decimal,
    prev_close: dict[str, Decimal] | None,
    tick_mode: bool,
    trade_date: datetime.date | None = None,
    limit_map: dict | None = None,
) -> list[dict]:
    orders: list[dict] = []
    for symbol, weight in target_weights.items():
        if weight <= 0:
            continue

        ob = order_books.get(symbol)
        if ob is None or ob.last_price <= 0:
            continue  # 停牌或无数据

        # 计算目标数量（100股整数倍）
        target_value = total_nav * Decimal(str(weight))
        target_qty = int(target_value / ob.last_price / engine._config.lot_size) * engine._config.lot_size

        # 当前持仓
        current_pos = portfolio.get_position(symbol)
        current_qty = current_pos.quantity if current_pos else Decimal("0")

        # 差额
        diff = Decimal(target_qty) - current_qty
        if diff > 0:
            # 涨停封板：买单拒成（2026-08-19 阶段2 改方向感知——原买卖对称
            # 阻断把涨停日可成交的卖单也一并锁死）
            if not tick_mode and prev_close and engine._is_limit_up(
                symbol, ob.last_price, prev_close.get(symbol), trade_date, limit_map
            ):
                continue
            orders.append({"side": "BUY", "symbol": symbol, "quantity": diff})
        elif diff < 0:
            # 跌停封板：卖单拒成；涨停日卖单可成交（排队买盘即时消化）
            if not tick_mode and prev_close and engine._is_limit_down(
                symbol, ob.last_price, prev_close.get(symbol), trade_date, limit_map
            ):
                continue
            orders.append({"side": "SELL", "symbol": symbol, "quantity": abs(diff)})

    # 目标权重语义补全（2026-08-19 AI-NIGHT-001 阶段2 红队实证 P0）：持仓但
    # 目标权重缺失/<=0 的标的目标仓位=0，必须生成清仓卖单——否则轮动策略
    # 跌出信号的持仓永久滞留（实证：A 轮出后 59900 股滞留，轮入标的买入因
    # 现金被占连续被拒），回测系统性偏离信号意图。停牌/跌停无法卖出时跳过。
    for symbol, pos in portfolio.positions.items():
        if pos.quantity <= 0:
            continue
        if target_weights.get(symbol, 0.0) > 0:
            continue  # 已在上方差额逻辑处理
        ob = order_books.get(symbol)
        if ob is None or ob.last_price <= 0:
            continue  # 停牌或无数据，无法卖出
        if not tick_mode and prev_close and engine._is_limit_down(
            symbol, ob.last_price, prev_close.get(symbol), trade_date, limit_map
        ):
            continue  # 跌停封板无法卖出（涨停日卖单可成交，不阻断清仓）
        orders.append({"side": "SELL", "symbol": symbol, "quantity": pos.quantity})
    return orders


class MatchingEngine:
    """回测撮合引擎（v1.1.0 重构：委托 MatchingLogic）

    根据目标权重生成买卖订单，委托 MatchingLogic 应用滑点和手续费，
    产出 BacktestFill 列表。

    撮合逻辑（委托 MatchingLogic）:
      1. 计算当前总 NAV（现金+市值）
      2. 对每个 symbol 计算目标持仓金额 = NAV * target_weight
      3. 计算目标数量 = floor(目标金额 / price / lot_size) * lot_size
      4. 差额 = 目标数量 - 当前持仓
      5. 先卖后买（避免现金不足）
      6. 委托 MatchingLogic.{match_market_order|match_limit_order|match_tick_order} 撮合
      7. MatchingFill -> BacktestFill（加 date 字段）

    A股约束（本引擎校验）:
      - 100股整数倍（买入）
      - 涨跌停不成交（有 prev_close 时检查）
      - 停牌不成交（无价格数据时跳过）
      - T+1 由 Portfolio 负责（matching_engine 只生成 fills）

    Usage（向后兼容，日线回测）:
        engine = MatchingEngine(config=MatchingConfig(...))
        fills = engine.generate_fills(
            target_weights={"000001.SZ": 0.5, "600000.SH": 0.5},
            prices={"000001.SZ": Decimal("10.5"), "600000.SH": Decimal("8.3")},
            portfolio=portfolio,
            date="2024-01-15",
        )

    Usage（v1.1.0 新增，5档盘口撮合）:
        fills = engine.generate_fills_with_order_book(
            target_weights={"000001.SZ": 0.5},
            order_books={"000001.SZ": order_book_snapshot},
            portfolio=portfolio,
            date="2024-01-15",
        )

    Usage（v1.1.0 新增，Tick级5档撮合做T）:
        fills = engine.generate_fills_with_tick(
            target_weights={"000001.SZ": 0.5},
            ticks={"000001.SZ": tick_snapshot},
            portfolio=portfolio,
            date="2024-01-15",
        )
    """

    def __init__(
        self,
        config: MatchingConfig | None = None,
        limit_provider: LimitProvider | None = None,
        liquidity_config: LiquidityGuardConfig | None = None,
    ):
        """初始化撮合引擎

        Args:
            config: 撮合配置（可选，默认使用 MatchingConfig 默认值，frozen 不可变）
            limit_provider: 涨跌停 PIT 提供器（可选，协议见 LimitProvider）。注入后
                撮合涨跌停价优先消费其 stk_limit 表 PIT 行（#ARCH-DATA-020）；
                None=纯规则兜底（日期切片仅由 provider 内部兜底覆盖 ST，
                无 provider 时主板 ST 历史约束按无 ST 口径处理——生产路径经
                vectorized_engine 默认注入 StkLimitProvider）。
            liquidity_config: 流动性约束（P0-2，可选）。None=不启用（单测/盘口路径
                保持原行为）；启用后 generate_fills 的 volumes 参数驱动成交量上限
                与 Almgren-Chriss 冲击成本，仅作用于日线合成盘口路径。
        """
        self._config = config or MatchingConfig()
        self._logic = MatchingLogic(self._config)
        self._limit_provider = limit_provider
        self._liquidity_config = liquidity_config

    # ------------------------------------------------------------------
    # 批量撮合入口（回测主流程调用）
    # ------------------------------------------------------------------

    def generate_fills(
        self,
        target_weights: dict[str, float],
        prices: dict[str, Decimal],
        portfolio: Portfolio,
        date: object,
        prev_close: dict[str, Decimal] | None = None,
        volumes: dict[str, Decimal] | None = None,
    ) -> list[BacktestFill]:
        """根据目标权重生成成交记录（市价单，向后兼容接口）

        内部将单一价格构造成合成1档盘口，委托 MatchingLogic.match_market_order 撮合。
        撮合行为与原实现完全一致（BUY 按 price 成交，SELL 按 price 成交，应用滑点）。

        P0-2（2026-09-14 整改）：liquidity_config 启用且传入 volumes 时，先按
        max_participation_rate 收缩订单量（成交 ≤ 当日量上限），再按 Almgren-Chriss
        冲击模型调整盘口价（参与率越高冲击越大）——日频"无限流动性"失真治理。

        Args:
            target_weights: {symbol: weight} 目标权重（0.0-1.0, sum<=1.0）
            prices: {symbol: price} 当日价格
            portfolio: 当前持仓
            date: 当前日期
            prev_close: 前一日收盘价（可选，用于涨跌停检查）
            volumes: {symbol: volume} 当日成交量（可选，P0-2 流动性约束输入；
                None 或缺某标的时该标的不受限——无数据不虚构约束）。
                **口径契约（INV-UNIT-001）**：值必须是「股」，且与 `prices` 同处
                一个复权空间（两者都由 load_history 出口一次性归一）。直传源表
                `kline_daily.volume` 原始列会把参与率上限悄悄收紧 100 倍
                （94.6% 行是「手」）——车道 K P0-1 的病灶，勿再犯。
                同一个量还驱动**两条成本腿的分层**（#23 H2）：volume×当日价 = 该笔
                当日成交额，滑点腿据此落 ADV 五分位、冲击腿据此取该层标定 η/σ。
                不传 volumes 即无流动性信息，成本腿落标定真源的「无信息档」
                （滑点=全市场名义加权实证 bps，冲击=标定表成本上界层），不是回到 1bp。

        Returns:
            BacktestFill 列表（先卖后买排序）

        Raises:
            MatchingError: 参数无效
        """
        if not target_weights:
            return []

        if not prices:
            raise MatchingError("prices 不能为空")

        # 构造合成1档盘口 dict
        order_books: dict[str, OrderBookSnapshot] = {}
        for symbol, price in prices.items():
            if price is None or price <= 0:
                continue  # 停牌或无数据，跳过
            order_books[symbol] = self._synthetic_order_book(symbol, price)

        return self._generate_fills_from_order_books(
            target_weights=target_weights,
            order_books=order_books,
            portfolio=portfolio,
            date=date,
            prev_close=prev_close,
            tick_mode=False,
            volumes=volumes,
        )

    def generate_fills_with_order_book(
        self,
        target_weights: dict[str, float],
        order_books: dict[str, OrderBookSnapshot],
        portfolio: Portfolio,
        date: object,
        prev_close: dict[str, Decimal] | None = None,
    ) -> list[BacktestFill]:
        """根据目标权重 + 5档盘口生成成交记录（Level 4 撮合）

        v1.1.0 新增：使用真实5档盘口撮合，BUY 按 ask1 成交，SELL 按 bid1 成交。

        Args:
            target_weights: {symbol: weight} 目标权重
            order_books: {symbol: OrderBookSnapshot} 5档盘口快照
            portfolio: 当前持仓
            date: 当前日期
            prev_close: 前一日收盘价（可选，用于涨跌停检查）

        Returns:
            BacktestFill 列表（先卖后买排序）
        """
        if not target_weights:
            return []
        if not order_books:
            raise MatchingError("order_books 不能为空")

        return self._generate_fills_from_order_books(
            target_weights=target_weights,
            order_books=order_books,
            portfolio=portfolio,
            date=date,
            prev_close=prev_close,
            tick_mode=False,
        )

    def generate_fills_with_tick(
        self,
        target_weights: dict[str, float],
        ticks: dict[str, TickSnapshot],
        portfolio: Portfolio,
        date: object,
    ) -> list[BacktestFill]:
        """根据目标权重 + Tick快照生成成交记录（Tick级5档撮合，做T专用）

        v1.1.0 新增：基于 Tick 快照的5档逐档消化撮合。
        委托 MatchingLogic.match_tick_order，逐档消化 ask1->ask2->...->ask5（BUY）
        或 bid1->bid2->...->bid5（SELL），流动性约束为单档成交量上限=该档 vol。

        Args:
            target_weights: {symbol: weight} 目标权重
            ticks: {symbol: TickSnapshot} Tick快照（含5档盘口）
            portfolio: 当前持仓
            date: 当前日期

        Returns:
            BacktestFill 列表（先卖后买排序）
        """
        if not target_weights:
            return []
        if not ticks:
            raise MatchingError("ticks 不能为空")

        # 将 Tick 转换为 OrderBook，复用统一流程
        order_books: dict[str, OrderBookSnapshot] = {}
        for symbol, tick in ticks.items():
            if tick.last_price <= 0:
                continue  # 停牌
            order_books[symbol] = tick.to_order_book()

        return self._generate_fills_from_order_books(
            target_weights=target_weights,
            order_books=order_books,
            portfolio=portfolio,
            date=date,
            prev_close=None,  # Tick 模式不做涨跌停检查（Tick 内已含状态）
            tick_mode=True,
            ticks=ticks,
        )

    # ------------------------------------------------------------------
    # 单笔撮合入口（委托 MatchingLogic，供外部直接调用）
    # ------------------------------------------------------------------

    def match_order(
        self,
        order: MatchOrderInput,
        order_book: OrderBookSnapshot,
    ) -> MatchingFill:
        """撮合市价单（委托 MatchingLogic.match_market_order）

        Args:
            order: 委托订单（MARKET 类型）
            order_book: 5档盘口快照

        Returns:
            MatchingFill 成交结果
        """
        try:
            return self._logic.match_market_order(order, order_book)
        except MatchingLogicError as e:
            raise MatchingError(str(e)) from e

    def match_limit_order(
        self,
        order: MatchOrderInput,
        order_book: OrderBookSnapshot,
    ) -> MatchingFill:
        """撮合限价单（委托 MatchingLogic.match_limit_order）

        Args:
            order: 委托订单（LIMIT 类型，limit_price 必填）
            order_book: 5档盘口快照

        Returns:
            MatchingFill 成交结果（filled=False 表示未成交）
        """
        try:
            return self._logic.match_limit_order(order, order_book)
        except MatchingLogicError as e:
            raise MatchingError(str(e)) from e

    def match_tick_order(
        self,
        order: MatchOrderInput,
        tick: TickSnapshot,
    ) -> MatchingFill:
        """撮合Tick级订单（委托 MatchingLogic.match_tick_order，做T专用）

        逐档消化5档盘口，流动性约束为单档 vol。

        Args:
            order: 委托订单（TICK 类型）
            tick: Tick快照（含5档盘口）

        Returns:
            MatchingFill 成交结果（filled=False 表示未成交或部分成交）
        """
        try:
            return self._logic.match_tick_order(order, tick)
        except MatchingLogicError as e:
            raise MatchingError(str(e)) from e

    # ------------------------------------------------------------------
    # 属性
    # ------------------------------------------------------------------

    @property
    def config(self) -> MatchingConfig:
        """撮合配置（只读，frozen）"""
        return self._config

    @property
    def logic(self) -> MatchingLogic:
        """暴露内部 MatchingLogic 供 MiniQmtBroker 复用（回测=实盘一致性）"""
        return self._logic

    # ------------------------------------------------------------------
    # 私有辅助方法
    # ------------------------------------------------------------------

    def _generate_fills_from_order_books(
        self,
        target_weights: dict[str, float],
        order_books: dict[str, OrderBookSnapshot],
        portfolio: Portfolio,
        date: object,
        prev_close: dict[str, Decimal] | None = None,
        tick_mode: bool = False,
        ticks: dict[str, TickSnapshot] | None = None,
        volumes: dict[str, Decimal] | None = None,
    ) -> list[BacktestFill]:
        """统一批量撮合流程（内部共享方法）

        流程:
          1. 计算当前总 NAV
          2. 对每个 symbol 计算目标数量（100股整数倍）
          3. 计算差额（目标 - 当前持仓）
          3.5 P0-2 流动性约束（启用时）：成交量参与率上限收缩 + 冲击成本调价
              （冲击参数按 3.6 的流动性层从标定真源取档，非 DEFAULT_PARAMS）
          3.6 #23 H2 逐笔当日成交额解析（滑点腿与冲击腿共用的流动性输入）
          4. 先卖后买排序
          5. 委托 MatchingLogic 撮合（市价/限价/Tick）
          6. MatchingFill -> BacktestFill
        """
        # 计算当前总 NAV（用 last_price 汇总市值）
        prices_for_nav = {symbol: ob.last_price for symbol, ob in order_books.items()}
        total_nav = portfolio.total_nav(prices_for_nav)
        if total_nav <= 0:
            raise MatchingError(f"总 NAV 必须 > 0, got {total_nav}")

        # 涨跌停 PIT 预取（每次调用=一个回测日：一次批量查询，逐 symbol 查内存）。
        # tick_mode 不做涨跌停检查（prev_close=None），跳过预取防无谓触库。
        trade_date = _normalize_date(date)
        limit_map = None if tick_mode else self._prefetch_limit_map(trade_date, order_books.keys())

        # 计算目标持仓和差额
        orders: list[dict] = _build_target_orders(
            self,
            target_weights,
            order_books,
            portfolio,
            total_nav,
            prev_close,
            tick_mode,
            trade_date,
            limit_map,
        )

        # P0-2 流动性约束：成交量参与率上限收缩订单（先于冲击调价——参与率按
        # 收缩后的实际订单量计），再按 Almgren-Chriss 冲击调整合成盘口价格。
        # 仅日线合成盘口路径生效（tick_mode 的真实5档深度本身即是约束）。
        # 3.6 #23 H2：两条成本腿的流动性输入在此一次性解析成「逐笔当日成交额」，
        # 冲击腿（本引擎）、现金投影（sizing）与实际成交（MatchingLogic）必须消费
        # 同一个数——否则投影与成交口径分裂，满仓信号会因余量算错被拒单。
        notionals: dict[str, Decimal] = {} if tick_mode else _daily_notional_map(order_books, volumes)
        liquidity_on = (
            not tick_mode
            and volumes
            and self._liquidity_config is not None
        )
        if liquidity_on:
            orders = self._cap_orders_by_volume(orders, volumes or {})
            order_books = self._apply_impact_to_books(orders, order_books, volumes or {})

        # 先卖后买（避免现金不足）
        orders.sort(key=lambda o: 0 if o["side"] == "SELL" else 1)

        # 满仓归一化成本摩擦修复（2026-08-20 AI-NIGHT-001 包3.2 登记项#2）：
        # 目标 sizing 按 NAV×weight 换算不含交易成本余量，满仓（Σ=1）时买入
        # 总成本=成交额×(1+滑点)+佣金 必然超现金 → 整单被拒（每日重复 warning、
        # 回测偏离信号意图）。此处按"先卖后买"顺序投影现金，买单预计超支时
        # 收缩到可负担的最大整手；现金充足的非满仓场景逐位不变（零回归）。
        orders = self._clamp_buys_to_projected_cash(orders, order_books, portfolio, notionals)

        # 生成 fills
        fills: list[BacktestFill] = []
        for order_dict in orders:
            fill = self._match_order_dict(
                order_dict, order_books, tick_mode=tick_mode, ticks=ticks, notionals=notionals
            )
            # Tick 模式下部分成交（quantity>0 但 filled=False）也应当应用
            # 市价单/限价单完全成交才应用（filled=True）
            if fill is not None and (fill.filled or fill.filled_quantity > 0):
                fills.append(self._to_backtest_fill(fill, date))
        return fills

    def _clamp_buys_to_projected_cash(
        self,
        orders: list[dict],
        order_books: dict[str, OrderBookSnapshot],
        portfolio: Portfolio,
        notionals: dict[str, Decimal] | None = None,
    ) -> list[dict]:
        """按投影现金收缩买单至可负担的最大整手（满仓成本摩擦修复）

        逐单按"先卖后买"顺序投影现金：卖单按估算净回款累加，买单按估算总成本
        （成交额×(1+滑点)+max(佣金率佣金,最低佣金)+过户费，与 MatchingLogic 口径一致）
        扣减；买单预计超支时收缩数量到可负担整手，不足一手则丢弃。
        Portfolio._apply_buy 的现金非负检查仍是最终防线（本步骤只做 sizing 收缩）。
        （2026-08-21 费率口径统一 #233：估算含双向过户费 万0.1）

        口径纪律（#23 H2）：滑点 bps 不在本引擎取常数，而是逐标的经
        ``MatchingLogic.slippage_bps_for`` 按当日成交额解析——sizing 投影与实际成交
        共用同一真源同一优先级（含显式钉住口径），否则两者分裂会让满仓信号误拒。
        最低佣金按"每单 5 元地板"估（与 ``_calc_commission`` 同式）：它是小额单上的
        额外约束，不改动万0.854 这个费率本身。
        """
        notionals = notionals or {}
        rate = self._config.commission_rate
        min_comm = self._config.min_commission
        stamp = self._config.stamp_tax_rate
        transfer = self._config.transfer_fee_rate
        lot = self._config.lot_size

        def _slip(symbol: str) -> Decimal:
            return self._logic.slippage_bps_for(notionals.get(symbol)) / Decimal("10000")

        projected = portfolio.cash
        out: list[dict] = []
        for order in orders:
            ob = order_books.get(order["symbol"])
            slip = _slip(order["symbol"])
            if order["side"] == "SELL":
                base = self._side_base_price(ob, "SELL")
                exec_price = base * (1 - slip)
                gross = order["quantity"] * exec_price
                comm = max(gross * rate, min_comm) + gross * stamp + gross * transfer
                projected += gross - comm
                out.append(order)
                continue

            base = self._side_base_price(ob, "BUY")
            exec_price = base * (1 + slip)
            qty = order["quantity"]

            def _buy_cost(q: Decimal) -> Decimal:
                g = q * exec_price
                return g + max(g * rate, min_comm) + g * transfer

            if _buy_cost(qty) > projected:
                # 佣金率情形的可负担手数，再按最低佣金/滑点实际成本回校验递减
                qty = Decimal(int(projected / (exec_price * (1 + rate + transfer)) / lot) * lot)
                while qty > 0 and _buy_cost(qty) > projected:
                    qty -= lot
                if qty <= 0:
                    continue  # 现金不足一手，放弃该买单（无单可成）
                order = dict(order, quantity=qty)
            projected -= _buy_cost(qty)
            out.append(order)
        return out

    def _cap_orders_by_volume(
        self,
        orders: list[dict],
        volumes: dict[str, Decimal],
    ) -> list[dict]:
        """P0-2：按当日成交量参与率上限收缩订单量（买卖同限）。

        上限 = floor(volume × max_participation_rate)；买单向下取整手（A股买入
        整手约束），卖单向下取整股（清仓/卖出允许零股）。收缩后 ≤0 的订单丢弃；
        volume 缺失/非正的标的不受限（无数据不虚构约束）。

        量纲纪律（车道 K P0-1）：本方法是**纯比值**，对"订单量与日量同纲缩放"不变，
        因此它自身无法发现量纲错误——只有调用方守住 INV-UNIT-001（volume=股）
        上限才真的是 10%。传入「手」口径（源表 94.6% 行的真实量纲）时，有效上限
        会静默变成真实日量的 0.1%；探测与告警放在数据入口
        （`market_units.probe_volume_unit`），不在此处散乘 100 打补丁。
        """
        cap_rate = self._liquidity_config.max_participation_rate
        lot = Decimal(self._config.lot_size)
        out: list[dict] = []
        for order in orders:
            vol = volumes.get(order["symbol"])
            if vol is None or vol <= 0:
                out.append(order)
                continue
            cap_qty = vol * cap_rate
            if order["side"] == "BUY":
                capped = (cap_qty / lot).to_integral_value(rounding="ROUND_FLOOR") * lot
            else:
                capped = cap_qty.to_integral_value(rounding="ROUND_FLOOR")
            if capped <= 0:
                _logger.debug(
                    "P0-2 成交量上限: %s %s %s 股超当日参与率上限(%s%%×%s)，整单丢弃",
                    order["side"], order["symbol"], order["quantity"],
                    cap_rate, vol,
                )
                continue
            if capped < order["quantity"]:
                _logger.debug(
                    "P0-2 成交量上限: %s %s %s -> %s 股（≤当日量 %s×%s）",
                    order["side"], order["symbol"], order["quantity"], capped,
                    vol, cap_rate,
                )
                order = dict(order, quantity=capped)
            out.append(order)
        return out

    def _apply_impact_to_books(
        self,
        orders: list[dict],
        order_books: dict[str, OrderBookSnapshot],
        volumes: dict[str, Decimal],
    ) -> dict[str, OrderBookSnapshot]:
        """P0-2：按 Almgren-Chriss 冲击模型调整合成盘口成交价。

        每标的每日至多一笔订单（差额单/清仓单），按该笔实际订单量计参与率，
        冲击 bps（临时+永久，execution_simulation 真源）只加在同侧报价上：
        BUY 抬 ask1、SELL 压 bid1（冲击恒为不利方向）；last_price 不动——
        组合估值仍按市场价，冲击只影响成交。volume 缺失/非正的标的跳过。

        参数档（#23 H2-C 治本）：η/β/γ/σ 不再无条件消费 ``DEFAULT_PARAMS``
        （无出处默认档，与标定档的偏离倍数由 ``calibration.DEFAULT_PARAMS_REF`` 披露），而是
        按该标的流动性层从 ``cost_model_calibration`` 取标定档：层号由与滑点腿
        **同一个** ``_daily_notional_map``（当日成交额）解析，两腿共用一把尺子。
        两层含义必须分开看：
          - 冲击腿=尺寸相关（走单位移，随参与率增长）→ 本方法；
          - 滑点腿=尺寸无关（价差+逆向选择）→ MatchingLogic._apply_slippage。
        标定侧 ``IMPACT_GAMMA_RATIO=0`` 的裁定已把永久项折进临时项，故本方法计的是
        同一段位移的一次计费，与滑点腿互斥相加、不重叠（INV-COST-LEGS）。
        开关 ``calibration_enabled()`` 关时整条腿回到 legacy ``DEFAULT_PARAMS``，
        供台账 #23 H2 的 A/B 取证逐位复现接线前口径。

        参与率 p = 订单股数 ÷ 当日成交股数（分子分母同纲，INV-UNIT-001）。
        正常路径下 p ≤ max_participation_rate（上游 _cap_orders_by_volume 已收缩）；
        p 越出 [0,1] 说明 A-C 模型会抛"参与率越界"而被本函数兜住 → 该标的按无冲击
        成交（成本被系统性低估）。此时 MUST 告警点名"疑似量纲/参与率上限未生效"，
        不得静默旁路（车道 K 复验确认：现网该旁路并非 P0-1 的主通路，
        主通路是 100× 过严上限本身，但静默降级同样必须显式化）。
        """
        if self._liquidity_config is None or not self._liquidity_config.impact_enabled:
            return order_books
        try:
            from zephyr.execution_simulation.almgren_chriss_impact_model import (
                AlmgrenChrissImpactModel,
                ImpactParams,
            )
        except Exception as e:  # noqa: BLE001 — 冲击模型不可用时退化为仅成交量上限
            _logger.warning("AlmgrenChrissImpactModel 导入失败，冲击成本旁路: %s", e)
            return order_books

        calibrated = cost_cal.calibration_enabled()
        models: dict[int, Any] = getattr(self, "_impact_models", None)  # type: ignore[assignment]
        if models is None:
            models = self._impact_models = {}
        # 层参数是层常量（标定表静态），跨日复用安全；-1=legacy 档
        notionals = _daily_notional_map(order_books, volumes)

        def _model_for(symbol: str) -> AlmgrenChrissImpactModel:
            """该标的的冲击模型（按流动性层缓存）。

            层未知（本笔无成交额信息）且标定档生效时，落 **Q1_illiquid**：标定表里
            η·σ 随流动性单调递减，故 Q1 是表内成本上界——Fail-Closed 宁可高估，
            也不静默旁路成零冲击（档位数值只在标定件里，此处禁止复述）。
            """
            if not calibrated:
                key = -1
            else:
                notional = notionals.get(symbol)
                # 缺成交额时按最不流动层兜底（见 docstring）；不新设档位字面量表
                key = 0 if notional is None else cost_cal.liquidity_tier(float(notional))
                if notional is None:
                    _logger.debug(
                        "冲击腿无当日成交额信息（%s），按标定表成本上界层 Q1_illiquid 计价", symbol
                    )
            model = models.get(key)
            if model is None:
                if key < 0:
                    model = AlmgrenChrissImpactModel()  # legacy 口径（DEFAULT_PARAMS）
                else:
                    lvl = cost_cal.impact_level_for_tier(key)
                    model = AlmgrenChrissImpactModel(
                        params=ImpactParams(
                            eta=lvl.eta,
                            beta=lvl.beta,
                            gamma=lvl.gamma,
                            sigma=lvl.sigma,
                            permanent_exponent=lvl.permanent_exponent,
                        )
                    )
                models[key] = model
            return model

        adjusted = dict(order_books)
        for order in orders:
            symbol = order["symbol"]
            vol = volumes.get(symbol)
            ob = adjusted.get(symbol)
            if vol is None or vol <= 0 or ob is None or order["quantity"] <= 0:
                continue
            participation = float(order["quantity"]) / float(vol)
            if not 0.0 <= participation <= 1.0:
                _logger.warning(
                    "冲击报价参与率越界 p=%.3f（%s 订单 %s 股 / 当日量 %s），A-C 模型必抛错"
                    "→ 本标的按无冲击成交（成本低估）。疑似 INV-UNIT-001 违例："
                    "volumes 非「股」口径或 max_participation_rate 未生效，请核查数据入口",
                    participation,
                    symbol,
                    order["quantity"],
                    vol,
                )
            try:
                quote = _model_for(symbol).quote(float(order["quantity"]), float(vol))
            except Exception as e:  # noqa: BLE001 — 单标的冲击报价失败不炸整日撮合
                _logger.warning(
                    "冲击报价失败（%s p=%.3f），该标的按无冲击成交: %s", symbol, participation, e
                )
                continue
            shock = Decimal("1") + Decimal(str(quote.cost_bps)) / Decimal("10000")
            if order["side"] == "BUY":
                ask = (ob.ask_price[0] * shock,) + tuple(ob.ask_price[1:])
                adjusted[symbol] = replace(ob, ask_price=ask)
            else:
                bid = (ob.bid_price[0] / shock,) + tuple(ob.bid_price[1:])
                adjusted[symbol] = replace(ob, bid_price=bid)
        return adjusted

    @staticmethod
    def _side_base_price(ob: OrderBookSnapshot | None, side: str) -> Decimal:
        """取估算执行基准价：BUY 用 ask1、SELL 用 bid1，缺失回退 last_price。"""
        if ob is None:
            return Decimal("0")
        if side == "BUY":
            if ob.ask_price and ob.ask_price[0] > 0:
                return ob.ask_price[0]
        else:
            if ob.bid_price and ob.bid_price[0] > 0:
                return ob.bid_price[0]
        return ob.last_price

    def _match_order_dict(
        self,
        order_dict: dict,
        order_books: dict[str, OrderBookSnapshot],
        tick_mode: bool = False,
        ticks: dict[str, TickSnapshot] | None = None,
        notionals: dict[str, Decimal] | None = None,
    ) -> MatchingFill | None:
        """根据订单字典和盘口撮合，返回 MatchingFill

        Args:
            order_dict: {side, symbol, quantity}
            order_books: 盘口 dict
            tick_mode: True=Tick级5档撮合, False=市价单撮合
            ticks: Tick快照 dict（tick_mode=True 时必填）
            notionals: {symbol: 当日成交额(元)} 滑点分层输入（#23 H2-A；缺项=None=
                本笔无流动性信息，由标定真源落「无信息档」，引擎不自造档位）。
        """
        symbol = order_dict["symbol"]
        side = order_dict["side"]
        quantity = order_dict["quantity"]

        if quantity <= 0:
            return None

        order_input = MatchOrderInput(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type="TICK" if tick_mode else "MARKET",
            daily_notional_yuan=None if notionals is None else notionals.get(symbol),
        )

        try:
            if tick_mode and ticks is not None:
                tick = ticks.get(symbol)
                if tick is None:
                    return None
                return self._logic.match_tick_order(order_input, tick)
            else:
                ob = order_books.get(symbol)
                if ob is None:
                    return None
                return self._logic.match_market_order(order_input, ob)
        except MatchingLogicError:
            # 撮合失败（如盘口为空）视为未成交
            return None

    def _to_backtest_fill(self, fill: MatchingFill, date: object) -> BacktestFill:
        """将 MatchingFill 转换为 BacktestFill（加 date 字段）

        使用 filled_quantity（实际成交数量）而非 quantity（委托数量），
        以正确处理 Tick 级部分成交场景。
        """
        return BacktestFill(
            date=date,
            symbol=fill.symbol,
            side=fill.side,
            quantity=fill.filled_quantity,
            price=fill.price,
            commission=fill.commission,
            slippage_cost=fill.slippage_cost,
            decision_price=fill.decision_price,
            order_type=fill.order_type,
        )

    def _synthetic_order_book(self, symbol: str, price: Decimal) -> OrderBookSnapshot:
        """从单一价格构造合成1档盘口（日线回测兼容模式）

        用途: generate_fills() 接收单一价格时，构造1档盘口委托给 MatchingLogic。
        BUY 按 ask1=price 成交，SELL 按 bid1=price 成交，与原实现行为一致。
        虚拟深度设为大数（_SYNTHETIC_DEPTH）避免流动性约束触发。
        """
        return OrderBookSnapshot(
            symbol=symbol,
            ask_price=(price,),
            bid_price=(price,),
            ask_vol=(_SYNTHETIC_DEPTH,),
            bid_vol=(_SYNTHETIC_DEPTH,),
            last_price=price,
            timestamp=None,
        )

    def _prefetch_limit_map(
        self, trade_date: datetime.date | None, symbols: Iterable[str]
    ) -> dict | None:
        """按回测日批量预取涨跌停约束包（limit_provider 一次调用，结果内存直查）。

        provider 异常 fail-open（warn 一次 + 返回 {}，退回规则兜底）——回测撮合
        不因数据面故障中断；trade_date 非法/无 provider 返回 None（纯规则路径）。
        """
        if self._limit_provider is None or trade_date is None:
            return None
        try:
            return self._limit_provider(trade_date, list(symbols)) or {}
        except Exception as e:  # noqa: BLE001 — provider 故障降级不炸回测
            _logger.warning(
                "StkLimitProvider 预取失败（%s %s），退回规则兜底: %s",
                trade_date, list(symbols)[:5], e,
            )
            return {}

    def _fallback_limit_pct(
        self, symbol: str, trade_date: datetime.date | None, st_flag: bool
    ) -> Decimal | None:
        """规则切片兜底幅度：复用生成侧单一真源 _limit_pct_of（#ARCH-DATA-020）。

        trade_date=None（旧调用路径无日期）返回 None（调用方退板块前缀推断）；
        akshare_provider 导入失败/口径返回 None 均返回 None（保守回退链）。
        lazy import：撮合引擎不在模块级依赖 data.implementations（防环+轻导入）。
        """
        if trade_date is None:
            return None
        try:
            from zephyr.data.implementations.akshare_provider import AkshareIngestProvider

            pct = AkshareIngestProvider._limit_pct_of(symbol.split(".")[0], trade_date, st_flag)
        except Exception as e:  # noqa: BLE001 — 真源导入/查询故障退保守回退链
            _logger.warning("_limit_pct_of 切片真源调用失败（%s %s）: %s", symbol, trade_date, e)
            return None
        return None if pct is None else Decimal(str(pct))

    def _bounds_from_pct(self, prev_close: Decimal, pct: Decimal) -> tuple[Decimal, Decimal]:
        """按幅度在上限空间重算涨跌停价（ROUND_HALF_UP 到分，与生成侧同口径）。"""
        upper = (prev_close * (Decimal(1) + pct)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        lower = (prev_close * (Decimal(1) - pct)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return (upper, lower)

    def _limit_bounds(
        self,
        symbol: str,
        trade_date: datetime.date | None,
        prev_close: Decimal | None,
        limit_map: dict | None,
    ) -> tuple[Decimal, Decimal] | None:
        """单标的当日涨跌停价（三级解析链，#ARCH-DATA-020 重评条件②闭环）。

        链路（禁再造第四份口径）：
          1. stk_limit 表 PIT 行（from_table，limit_up/limit_down 精确价直用）；
             行在但 limit_*=NULL（新股无涨跌幅限制期）→ None（不封板）；
          2. 规则切片兜底：provider 兜底 limit_pct 或 AkshareIngestProvider._limit_pct_of
             （trade_date 切片，ST 由 provider 的 st_stock_list 最近可得快照），
             引擎按 prev_close×(1±pct) ROUND_HALF_UP 到分（与生成侧同口径）；
          3. 板块前缀推断 _infer_limit_pct（未知前缀保守回退，无日期无 ST）。
        prev_close 缺失/非正 → None（无基准不封板，保持既有行为）。

        缩放不变性（车道 K P0-2 配套修复，2026-09-16）：链路 1 的表内价是
        **交易所原始绝对价**，只有当引擎价序列与它同纲时才可直比。数据出口已把价格
        归一为"窗口末锚定复权价"（逐标的乘子 k，见 market_units），k≠1 时直比绝对价
        会把高分红/送转股误判为永久封板（例：10送10 复权后 k≈0.5，引擎价≈表跌停的一半
        → 所有卖单被拒）。判据用**除权参考价**自洽性：涨停=round(ref×(1+pct))、
        跌停=round(ref×(1−pct)) → 二者中点即 ref（仅含 ±半分的取整噪声），
        |prev_close/ref − 1| ≤ _LIMIT_REF_TOL 视为同纲、直用表价；否则改走链路 2 的
        等价式（表行自带 limit_pct 优先，缺 pct 时按 prev_close/ref 缩放表价）。

        等价性（为何缩放后走收益空间是**精确**的，不是近似）：复权价 P(t)=raw(t)×f(t)，
        除权日 f 跳变满足 f(T)/f(T−1)=raw_close(T−1)/ref ⇒ 引擎的
        prev_close=P(T−1)=ref×f(T)，于是 prev_close×(1±pct) 恰等于把交易所涨跌停价
        平移到本标的复权空间的结果——除权日与非除权日同式，封板判定不随缩放改变。
        唯一残余噪声是"复权价不再落在 0.01 网格上"带来的半分边界抖动
        （相对 10% 板幅 ≈0.05%，且仅在收盘贴板一分内可能翻转）。
        """
        if prev_close is None or prev_close <= 0:
            return None
        info = limit_map.get(symbol) if limit_map else None
        if info is not None and info.from_table:
            if info.limit_up is None or info.limit_down is None:
                return None  # 表行 limit_*=NULL：新股无涨跌幅限制期，不封板
            ref = (info.limit_up + info.limit_down) / Decimal(2)  # 除权参考价（交易所口径）
            same_caliber = ref > 0 and abs(prev_close / ref - Decimal(1)) <= _LIMIT_REF_TOL
            if same_caliber:
                return (info.limit_up, info.limit_down)  # 链路 1：同纲，表内精确价直用
            if info.limit_pct is not None:
                return self._bounds_from_pct(prev_close, info.limit_pct)  # 等价收益空间式
            if ref > 0:
                scale = prev_close / ref
                return (
                    (info.limit_up * scale).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                    (info.limit_down * scale).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                )
            _logger.warning(
                "涨跌停表行不可用（%s %s limit_up=%s limit_down=%s 且无 limit_pct），按不封板处理",
                symbol, trade_date, info.limit_up, info.limit_down,
            )
            return None
        st_flag = bool(info.st_flag) if info is not None else False
        pct: Decimal | None = None
        if info is not None and info.limit_pct is not None:
            pct = info.limit_pct
        else:
            pct = self._fallback_limit_pct(symbol, trade_date, st_flag)
        if pct is None:
            pct = self._infer_limit_pct(symbol)
        return self._bounds_from_pct(prev_close, pct)

    def _infer_limit_pct(self, symbol: str) -> Decimal:
        """按代码前缀推断板块涨跌停幅度（2026-08-19 AI-NIGHT-001 #211）。

        原实现全板块统一 ±10%（config.price_limit_pct），与宪章约束四不符：
        主板 ±10% / 科创板(68x) ±20% / 创业板(30x) ±20% / 北交所(4xx/8xx/92x) ±30%。
        本函数是涨跌停三级解析链的最后防线（#ARCH-DATA-020）：仅未知前缀
        （_limit_pct_of 返回 None 的异形代码）与无 trade_date 的旧调用路径生效；
        A 股股票的历史正确口径由 stk_limit 表 PIT 行 / _limit_pct_of 切片承载。
        """
        code = symbol.split(".")[0]
        if code.startswith(("68", "30")):
            return Decimal("0.20")
        if code.startswith(("4", "8", "92")):
            return Decimal("0.30")
        return self._config.price_limit_pct

    def _is_limit_up(
        self,
        symbol: str,
        price: Decimal,
        prev_close: Decimal | None,
        trade_date: datetime.date | None = None,
        limit_map: dict | None = None,
    ) -> bool:
        """是否涨停（封板价之上，买单拒成；卖单不受限）。

        涨跌停价取整口径与交易所一致：ROUND_HALF_UP 到分（非默认
        ROUND_HALF_EVEN），消除 x.xx5 边界 1 分差异；表 PIT 行命中时直接
        比对表价（stk_limit 生成侧已是同口径 ROUND_HALF_UP）。
        trade_date/limit_map 缺省时保持旧调用行为（板块前缀推断）。
        """
        bounds = self._limit_bounds(symbol, trade_date, prev_close, limit_map)
        return bounds is not None and price >= bounds[0]

    def _is_limit_down(
        self,
        symbol: str,
        price: Decimal,
        prev_close: Decimal | None,
        trade_date: datetime.date | None = None,
        limit_map: dict | None = None,
    ) -> bool:
        """是否跌停（封板价之下，卖单拒成；买单不受限）。

        取整口径同 _is_limit_up；参数缺省时保持旧调用行为。
        """
        bounds = self._limit_bounds(symbol, trade_date, prev_close, limit_map)
        return bounds is not None and price <= bounds[1]

    def _is_price_limit(
        self,
        symbol: str,
        price: Decimal,
        prev_close: Decimal | None,
        trade_date: datetime.date | None = None,
        limit_map: dict | None = None,
    ) -> bool:
        """检查是否涨跌停（三级解析链：stk_limit PIT 行 → 切片规则 → 前缀推断）

        Args:
            symbol: 标的代码
            price: 当前价格
            prev_close: 前一日收盘价
            trade_date: 交易日（涨跌停口径日期切片，缺省走旧推断路径）
            limit_map: 当日预取约束包（_prefetch_limit_map 产物，缺省走规则兜底）

        Returns:
            True=涨跌停（不成交）, False=正常
        """
        return self._is_limit_up(symbol, price, prev_close, trade_date, limit_map) or self._is_limit_down(
            symbol, price, prev_close, trade_date, limit_map
        )


class StkLimitProvider:
    """撮合涨跌停 PIT 提供器（c1_market.stk_limit 优先 + st_stock_list 快照兜底）。

    三级解析链的数据腿（#ARCH-DATA-020 重评条件②）：
      1. stk_limit 表单日 FINAL 查询（trade_date=当日，PIT strict）→ LimitInfo
         (from_table=True, limit_up/limit_down/limit_pct/st_flag=表行)；
      2. 表缺行（如 2026-07-06 前未回补历史/新股无行）→ st_stock_list 最近可得
         （≤T）快照取 st_flag → limit_pct 经生成侧单一真源 _limit_pct_of 按日切片
         （主板 ST 2026-07-06 起 10%、此前 5%；创业板 2020-08-24 切片同构）；
      3. CH 不可达/查询异常 → warn 一次后降级记忆（本实例不再重试），返回
         {}——撮合退回引擎内规则兜底（无 ST，fail-open 不炸回测）。

    使用：vectorized_engine 每次回测构造一个实例注入 MatchingEngine(limit_provider=)；
    撮合引擎按日批量调用本 provider（一次 SQL/回测日），不在逐 symbol 判定中触库。
    """

    #: stk_limit 单日行（inject_final 对 ReplacingMergeTree 注入 FINAL；
    #: symbol 列为 6 位裸码——撮合侧传 canonical 形态时须先取 split(".")[0]）
    _SQL_STK_LIMIT_DAY = (
        "SELECT symbol, limit_up, limit_down, limit_pct, st_flag "
        "FROM c1_market.stk_limit WHERE trade_date = '{d}' AND symbol IN ({symbols})"
    )
    #: ST 最近可得快照（≤T 口径 PIT 严格，与生成侧 _load_st_snapshots 同语义）
    _SQL_ST_SNAPSHOT_DAY = (
        "SELECT symbol FROM {st_table} WHERE trade_date = ("
        "SELECT max(trade_date) FROM {st_table} WHERE trade_date <= '{d}')"
    )

    def __init__(self) -> None:
        self._degraded = False
        self._st_cache: dict[datetime.date, set[str] | None] = {}

    def __call__(self, trade_date: datetime.date, symbols: Iterable[str]) -> dict:
        from zephyr.data import ch_reader as _chr

        out: dict = {}
        symbols = list(symbols)  # 可能被迭代两次（裸码集 + _canon 回映射），防生成器耗尽
        codes = {str(s or "").split(".")[0].zfill(6) for s in symbols if str(s or "").strip()}
        if not codes:
            return out
        sym_list = ",".join(f"'{c}'" for c in sorted(codes))
        tsv = _chr.query(_chr.inject_final(self._SQL_STK_LIMIT_DAY.format(d=trade_date.isoformat(), symbols=sym_list)))
        seen: set[str] = set()
        for line in (tsv or "").strip().split("\n"):
            parts = line.split("\t")
            if len(parts) != 5:
                continue
            code = parts[0].strip().zfill(6)
            seen.add(code)
            out[self._canon(code, symbols)] = LimitInfo(
                limit_up=_parse_tsv_decimal(parts[1]),
                limit_down=_parse_tsv_decimal(parts[2]),
                limit_pct=_parse_tsv_decimal(parts[3]),
                st_flag=parts[4].strip() == "1",
                from_table=True,
            )
        missing = [c for c in codes if c not in seen]
        if not missing:
            return out
        if self._degraded:
            return out
        st_set = self._st_flag_set(trade_date, _chr)
        if st_set is None:
            return out  # CH 不可达已降级（_st_flag_set 内置记忆）
        for code in missing:
            out[self._canon(code, symbols)] = LimitInfo(
                limit_pct=_fallback_pct(code, trade_date, code in st_set),
                st_flag=code in st_set,
                from_table=False,
            )
        return out

    @staticmethod
    def _canon(code: str, symbols: Iterable[str]) -> str:
        """把裸码映射回调用方传入的原始 symbol 形态（撮合侧按原 symbol 查内存）。"""
        for s in symbols:
            if str(s or "").split(".")[0].zfill(6) == code:
                return str(s)
        return code

    def _st_flag_set(self, trade_date: datetime.date, ch_reader_mod: object) -> set[str] | None:
        """trade_date 的 ST 代码集合（最近可得 ≤T 快照；None=CH 不可达降级）。"""
        if trade_date in self._st_cache:
            return self._st_cache[trade_date]
        try:
            from zephyr.data.table_registry import get_registry

            st_table = get_registry().table("market_st_stock_list")
        except Exception as e:  # noqa: BLE001 — registry 故障等同 CH 故障降级
            _logger.warning("st_stock_list 表名解析失败（ST 兜底降级）: %s", e)
            self._degraded = True
            return None
        sql = self._SQL_ST_SNAPSHOT_DAY.format(st_table=st_table, d=trade_date.isoformat())
        tsv = ch_reader_mod.query(ch_reader_mod.inject_final(sql))
        if not (tsv or "").strip():
            # 空结果：可能是 CH 不可达（query 故障静默空串）或该窗口确无快照——
            # 一律降级记忆（fail-open，撮合退规则兜底），warn 留痕
            _logger.warning("st_stock_list 快照查询为空（%s），ST 兜底降级为非 ST 口径", trade_date)
            self._st_cache[trade_date] = set()
            self._degraded = True
            return set()
        codes: set[str] = set()
        for line in tsv.strip().split("\n"):
            code = line.split("\t")[0].strip().split(".")[0].zfill(6)
            if code:
                codes.add(code)
        self._st_cache[trade_date] = codes
        return codes


def _parse_tsv_decimal(v: str) -> Decimal | None:
    """TSV 单元格 → Decimal（''/'\\N'/非法 → None，对应 CH NULL）。"""
    s = str(v or "").strip()
    if not s or s == "\\N":
        return None
    try:
        return Decimal(s)
    except Exception:  # noqa: BLE001 — 坏行按 NULL 处理
        return None


def _fallback_pct(code: str, trade_date: datetime.date, st_flag: bool) -> Decimal | None:
    """规则切片兜底幅度（provider 数据腿）：复用 _limit_pct_of 单一真源。

    返回 None 时撮合引擎自行退板块前缀推断（_infer_limit_pct）。
    """
    try:
        from zephyr.data.implementations.akshare_provider import AkshareIngestProvider

        pct = AkshareIngestProvider._limit_pct_of(code, trade_date, st_flag)
    except Exception as e:  # noqa: BLE001 — 真源故障退引擎回退链
        _logger.warning("_limit_pct_of 切片真源调用失败（%s %s）: %s", code, trade_date, e)
        return None
    return None if pct is None else Decimal(str(pct))


# MatchingConfig / MatchingFill / MatchOrderInput / OrderBookSnapshot / TickSnapshot
# 从 matching_logic re-export，保持 `from zephyr.backtest.core.matching_engine import MatchingConfig`
# 向后兼容（vectorized_engine 和 __init__.py 依赖此导入路径）
__all__ = [
    "MatchingEngine",
    "MatchingConfig",
    "MatchingError",
    "MatchingFill",
    "MatchOrderInput",
    "OrderBookSnapshot",
    "TickSnapshot",
    "LimitInfo",
    "LimitProvider",
    "StkLimitProvider",
    "LiquidityGuardConfig",
]
