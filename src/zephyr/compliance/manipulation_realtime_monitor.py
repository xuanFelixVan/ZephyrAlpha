# [BLUEPRINT] MOD-CMP-018 | 待统筹登记（blueprint 未建，真源=43_compliance_discipline.md §7.2/§7.3/§10）
# [MODULE] zephyr.compliance.manipulation_realtime_monitor
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] zephyr.compliance.trading_compliance_detector(检测规则唯一真源, 零重实现); zephyr.compliance.manipulation_stream_driver(30min 窗口塑形复用); zephyr.compliance.compliance_log; zephyr.data.symbol_normalizer.normalizer(TRAE-082 符号归一); zephyr.infrastructure.h1_redis_hot.h1_redis_schema(tick key SSoT); zephyr.shared.contracts.enums.order_enums; zephyr.ex_core.order_manager(TYPE_CHECKING 预接线)
# [CONSUMERS] zephyr.ex_core.order_manager(可选注入 manipulation_monitor——C-002 闸抛转 is_frozen; 委托/成交事件回调消费); 盘中流编排(attach_order_manager 装配)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 检测规则唯一真源=TradingComplianceDetector(本层只做流接线/窗口供给/告警冻结分发, 零规则重实现); 事件驱动零定时器(委托/成交事件喂入, tick 快照事件时刻懒拉); 检测失效/数据缺失→降级跳过不误判(43号§7.3 防误伤); 命中→告警+compliance_log 证据+冻结判定, 阻断执行走 C-002 既有合规闸抛转(本层不接任何下单/撤单执行路径); 冻结须人工复解释放(release_freeze 留痕)
# [MODIFY-GUARD] 43_compliance_discipline.md §7.2/§7.3/§10（A8 盘中实时流驱动批）
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无新增错误类（事件非法由 ManipulationStreamDriver.InvalidStreamEventError(ZA-CMP-0011) 承载；阻断抛转 OrderManager.ComplianceGateBlockError(ZA-EX-0011)）
# [TESTS] tests/compliance/test_manipulation_realtime_monitor.py
# [A_module] module_id=MOD-CMP-018 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: 委托事件流(OrderManager 订单事件回调: 报单/撤单) + 成交事件流(fill 回调) + tick 行情流(Redis tick 缓存, tick_subscriber CP-01 通道懒拉)
# F1: on_order_placed/on_order_cancelled/on_trade——喂 ManipulationStreamDriver(同一 detector 实例)→拉抬打压短窗评估→30min/5min 双窗 trim→命中分发
# F2: attach_order_manager(om)——register_order_event_callback+register_fill_callback 挂接, Order/Fill→合规记录映射(市价单 price=0 照喂, 关联账户标记经 counterparty_resolver)
# F3: RedisTickMarketProvider——tick:{symbol}:latest 懒读: minute_avg_volume=累计量/已交易分钟(Spoofing 前提), market_window=5min 滚动观测价变+量差(拉抬打压前提); 缺失/异常→降级(0.0/None)
# A1: _dispatch——命中一律 logging.error 告警+MANIPULATION_REALTIME_ALERT 落 compliance_log+冻结标的(线程安全)
# O1: is_frozen/frozen_symbols(阻断判定, C-002 既有闸抛转 ComplianceGateBlockError) + release_freeze(人工复解释放, MANIPULATION_FREEZE_RELEASE 留痕)
# [/ALGO_FLOW]
"""



D_COMPLIANCE — 盘中操纵 4 类检测实时流驱动接线层（43 号 §7.2/§7.3，A8 批）。

43 号 §10 边界："Spoofing/Layering/WashTrade 需订单/成交历史，由盘中实时流以
同一 detector 实例驱动，不在 Pre-Trade 链范围"。本模块即实时流驱动接线：
  1. **委托/成交流**：attach_order_manager 挂接 OrderManager 订单事件与 fill
     回调（进程内事件总线），Order/Fill 映射为合规记录喂 ManipulationStreamDriver；
  2. **tick 行情流**：RedisTickMarketProvider 懒读 tick_subscriber 的 Redis
     tick 缓存（CP-01 通道，事件时刻拉取，无轮询定时器），供给 Spoofing 分钟
     均量与拉抬打压 5min 短窗价变/市场量；
  3. **检出分发**：命中一律 告警（logging.error）+ compliance_log 证据
     （MANIPULATION_REALTIME_ALERT；逐命中 MANIPULATION_VERDICT 由 detector
     落，唯一真源）+ 冻结标的判定（is_frozen）。

阻断边界（43 号 §7.3 处置语义的工程映射）：本层只产出阻断**判定**——执行动
作走既有合规闸抛转（OrderManager C-002 `_check_compliance_gates` 消费
is_frozen → ComplianceGateBlockError 拒发新申报），本层不接任何真实下单/
撤单执行路径，不新建执行通道。冻结须人工复核后 release_freeze 释放（留痕）。
尾盘操纵/大额成交已由 C-004 Pre-Trade 链逐单覆盖（43 号 §10），不在本层重复。

检测口径（唯一真源=TradingComplianceDetector/ComplianceThresholds）：
  | 类型      | 实时流口径                                                     |
  |----------|---------------------------------------------------------------|
  | Spoofing | 30min 窗内大额(>分钟均量20%)快撤(≤10s) ≥3 次（分钟均量=tick 累计量/已交易分钟）|
  | Layering | 同侧 ≥3 档时间序单调梯度序列且撤单率 >80%（driver run 预筛）        |
  | WashTrade| 自成交零容忍（counterparty_resolver 关联账户标记命中本方）          |
  | 拉抬打压  | 5min 短窗价变 ≥3% 且我方成交量占窗内市场量 >30%（我方量=成交事件累计）|

降级语义（防误伤，43 号 §7.3）：分钟均量缺失/≤0 → Spoofing 跳过；tick 缺失或
冷启动观测不足 → 拉抬打压跳过；counterparty_resolver 缺失 → WashTrade 仅
守"两侧同账户"显式标记，不对正常成交误判。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: redis_conn 参数
#   fields: 参数 redis_conn（无注解）
#   code: manipulation_realtime_monitor.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: manipulation_realtime_monitor.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: mono 参数
#   fields: 参数 mono（无注解）
#   code: manipulation_realtime_monitor.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: window_seconds 参数
#   fields: 参数 window_seconds（无注解）
#   code: manipulation_realtime_monitor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① RedisTickMarketProvider
#   name_en: RedisTickMarketProvider
#   intro: tick 行情流供给——懒读 tick_subscriber 的 Redis tick 缓存（CP-01 通道）。
#   desc: tick 行情流供给——懒读 tick_subscriber 的 Redis tick 缓存（CP-01 通道）。 事件驱动零定时器：仅在监测器评估时刻（委托/成交事件）拉取 t…；公共方法（定义序）: minute_…
#   inputs: redis_conn clock mono window_seconds
#   outputs: 返回值
# - id: A2
#   name_zh: ② ManipulationRealtimeMonitor
#   name_en: ManipulationRealtimeMonitor
#   intro: 盘中操纵 4 类检测实时监测器（事件驱动，同一 detector 实例驱动）。
#   desc: 盘中操纵 4 类检测实时监测器（事件驱动，同一 detector 实例驱动）。 Args: detector: TradingComplianceDetector 实例（None…；公共方法（定义序）: attach_…
#   inputs: detector minute_volume_provider market_window_provider logger own_acc…
#   outputs: 返回值
#   （注：A2 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: RedisTickMarketProvider, ManipulationRealtimeMonitor
#   downstream: zephyr.ex_core.order_manager(可选注入 manipulation_monitor——C-002 闸抛转 is_frozen; 委托…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Final

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.compliance.manipulation_stream_driver import ManipulationStreamDriver
from zephyr.compliance.trading_compliance_detector import (
    ComplianceOrderRecord,
    ComplianceTradeRecord,
    ManipulationVerdict,
    TradingComplianceDetector,
)
from zephyr.data.symbol_normalizer.normalizer import normalize_symbol, to_canonical
from zephyr.infrastructure.h1_redis_hot.h1_redis_schema import tick_latest_key
from zephyr.shared.contracts.enums.order_enums import OrderStatus

if TYPE_CHECKING:
    from zephyr.ex_core.order_manager import OrderManager
    from zephyr.shared.contracts.fill import Fill
    from zephyr.shared.contracts.order import Order

_logger = logging.getLogger(__name__)

__all__: Final = [
    "ManipulationRealtimeMonitor",
    "MarketWindow",
    "RedisTickMarketProvider",
]

#: 实时告警事件类型（逐命中证据=detector 侧 MANIPULATION_VERDICT，本事件承载分发/冻结语义）
_EVENT_REALTIME_ALERT: Final = "MANIPULATION_REALTIME_ALERT"
#: 冻结释放事件类型（人工复核后释放，审计留痕）
_EVENT_FREEZE_RELEASE: Final = "MANIPULATION_FREEZE_RELEASE"
#: 事件 source 字段（与模块名一致，审计可溯）
_SOURCE: Final = "manipulation_realtime_monitor"
#: 拉抬打压短窗（秒）——对齐 C-004 price_change_5min_pct 的 5min 口径
_RAMP_WINDOW_S: Final = 300.0
#: 对手方占位（未知且非本方时两侧必须相异，防 WashTrade 误判）
_MARKET_BUYER: Final = "MARKET_BUYER"
_MARKET_SELLER: Final = "MARKET_SELLER"
#: A 股连续竞价时段（分钟数，MVP 常量；09:30-11:30 / 13:00-15:00）
_SESSION_OPEN_MIN: Final = 9 * 60 + 30
_SESSION_MID_CLOSE_MIN: Final = 11 * 60 + 30
_SESSION_MID_OPEN_MIN: Final = 13 * 60
_SESSION_CLOSE_MIN: Final = 15 * 60


@dataclass(frozen=True)
class MarketWindow:
    """拉抬打压短窗市场快照（5min 价变 + 窗内市场成交量）。

    Attributes:
        price_change_pct: 短窗价格变动（小数，带符号）。
        window_volume: 短窗市场成交量（tick 累计量差分）。
    """

    price_change_pct: float
    window_volume: float


class RedisTickMarketProvider:
    """tick 行情流供给——懒读 tick_subscriber 的 Redis tick 缓存（CP-01 通道）。

    事件驱动零定时器：仅在监测器评估时刻（委托/成交事件）拉取 tick 快照，
    同时累计 5min 滚动观测窗（价变/量差分）。全部读取失败/数据缺失降级
    返回 0.0/None（检测跳过不误判），本类契约永不抛异常。

    Args:
        redis_conn: redis 连接（decode_responses=True，duck-typed hgetall）。
        clock: 墙钟注入（测试用；None=datetime.now 本地时区，对齐 tick 本地时间）。
        mono: 单调钟注入（测试用；None=time.monotonic，仅用于观测窗 trim）。
        window_seconds: 拉抬打压短窗秒数（默认 300s=5min）。
    """

    def __init__(
        self,
        redis_conn: object,
        *,
        clock: Callable[[], datetime] | None = None,
        mono: Callable[[], float] | None = None,
        window_seconds: float = _RAMP_WINDOW_S,
    ) -> None:
        self._redis = redis_conn
        self._clock = clock or datetime.now
        self._mono = mono or time.monotonic
        self._window_s = window_seconds
        # symbol -> 观测窗 deque[(mono_ts, price, cum_volume)]
        self._obs: dict[str, deque[tuple[float, float, float]]] = {}

    def minute_avg_volume(self, symbol: str) -> float:
        """分钟均量=当日累计成交量/已交易分钟数（Spoofing 前提；缺失→0.0 降级）。"""
        tick = self._read_tick(symbol)
        if tick is None:
            return 0.0
        _, cum_volume = tick
        elapsed = self._elapsed_trading_minutes(self._clock())
        if elapsed <= 0 or cum_volume <= 0:
            return 0.0
        return cum_volume / elapsed

    def market_window(self, symbol: str) -> MarketWindow | None:
        """5min 滚动观测窗（拉抬打压前提；冷启动/缺数据→None 降级跳过）。"""
        tick = self._read_tick(symbol)
        if tick is None:
            return None
        price, cum_volume = tick
        now = self._mono()
        obs = self._obs.setdefault(symbol, deque())
        obs.append((now, price, cum_volume))
        cutoff = now - self._window_s
        while obs and obs[0][0] < cutoff:
            obs.popleft()
        if len(obs) < 2:
            return None
        old_ts, old_price, old_volume = obs[0]
        if old_price <= 0 or now <= old_ts:
            return None
        return MarketWindow(
            price_change_pct=price / old_price - 1,
            window_volume=max(0.0, cum_volume - old_volume),
        )

    def _read_tick(self, symbol: str) -> tuple[float, float] | None:
        """读 tick:{symbol}:latest → (price, 累计成交量)；任何失败→None。"""
        bare, exchange = normalize_symbol(symbol)
        if not bare or exchange is None:
            _logger.debug("tick 供给：symbol 无法归一（降级跳过）: %r", symbol)
            return None
        try:
            raw = self._redis.hgetall(tick_latest_key(to_canonical(bare, exchange)))  # type: ignore[attr-defined]
            if not raw:
                return None
            price = float(raw.get("price", 0))
            volume = float(raw.get("volume", 0))
        except Exception:  # noqa: BLE001 — Redis 故障/脏数据一律降级（契约：永不抛）
            _logger.debug("tick 供给读取失败（降级跳过）: %s", symbol, exc_info=True)
            return None
        if price <= 0:
            return None
        return price, volume

    @staticmethod
    def _elapsed_trading_minutes(now: datetime) -> float:
        """已交易分钟数（连续竞价时段口径；非时段内钳到边界）。"""
        hm = now.hour * 60 + now.minute + now.second / 60.0
        if hm < _SESSION_OPEN_MIN:
            return 0.0
        if hm <= _SESSION_MID_CLOSE_MIN:
            return hm - _SESSION_OPEN_MIN
        if hm < _SESSION_MID_OPEN_MIN:
            return float(_SESSION_MID_CLOSE_MIN - _SESSION_OPEN_MIN)
        if hm <= _SESSION_CLOSE_MIN:
            return float(_SESSION_MID_CLOSE_MIN - _SESSION_OPEN_MIN) + (hm - _SESSION_MID_OPEN_MIN)
        return float((_SESSION_MID_CLOSE_MIN - _SESSION_OPEN_MIN) + (_SESSION_CLOSE_MIN - _SESSION_MID_OPEN_MIN))


class ManipulationRealtimeMonitor:
    """盘中操纵 4 类检测实时监测器（事件驱动，同一 detector 实例驱动）。

    Args:
        detector: TradingComplianceDetector 实例（None=自建默认阈值实例）。
            检测规则/阈值/逐命中落日志全归 detector（唯一真源）。
        minute_volume_provider: callable(symbol) -> float 分钟均量供给
            （Spoofing 前提；None=Spoofing 跳过降级）。
        market_window_provider: callable(symbol) -> MarketWindow | None 短窗
            市场快照供给（拉抬打压前提；None/返回 None=跳过降级）。
        logger: ComplianceLogger（告警/释放事件落库；None=复用 detector 的
            logger，保证与逐命中证据同一证据链文件）。
        own_account: 本方账户标记（WashTrade 自成交判定锚点）。
        counterparty_resolver: callable(Fill) -> str | None 对手方账户解析
            （券商回报含对手方账户时注入；返回 ==own_account 即自成交命中）。
        ramp_window_s: 拉抬打压我方成交统计窗（秒，默认 300s 对齐短窗口径）。
    """

    def __init__(
        self,
        detector: TradingComplianceDetector | None = None,
        *,
        minute_volume_provider: Callable[[str], float] | None = None,
        market_window_provider: Callable[[str], MarketWindow | None] | None = None,
        logger: ComplianceLogger | None = None,
        own_account: str = "OWN_ACCOUNT",
        counterparty_resolver: Callable[[Fill], str | None] | None = None,
        ramp_window_s: float = _RAMP_WINDOW_S,
    ) -> None:
        self._detector = detector or TradingComplianceDetector(logger=logger)
        self._logger = logger or self._detector.logger
        self._driver = ManipulationStreamDriver(self._detector, minute_volume_provider=minute_volume_provider)
        self._market_window_provider = market_window_provider
        self._own_account = own_account
        self._counterparty_resolver = counterparty_resolver
        self._ramp_window_s = ramp_window_s
        self._order_manager: OrderManager | None = None
        self._freeze_lock = threading.Lock()
        # 事件串行化锁：OrderManager 回调可并发触发（策略线程报单/撤单 + broker 回调
        # 线程成交），driver 窗口与我方成交窗均非线程安全——入口统一串行（低频系统零竞争开销）
        self._event_lock = threading.Lock()
        # symbol -> 首命中冻结 verdict（留证；重复命中告警照发、冻结不覆盖首证）
        self._frozen: dict[str, ManipulationVerdict] = {}
        # symbol -> 我方成交窗 deque[(traded_at, qty)]（拉抬打压我方量统计）
        self._our_fills: dict[str, deque[tuple[datetime, float]]] = {}

    # ── 流挂接 ──

    def attach_order_manager(self, order_manager: OrderManager) -> None:
        """挂接 OrderManager 委托/成交事件流（进程内事件总线）。

        注册订单事件回调（报单/撤单）与 fill 回调（成交）——被动观察，
        不接任何下单/撤单执行路径（43 号 §10 边界）。
        """
        self._order_manager = order_manager
        order_manager.register_order_event_callback(self._on_order_event)
        order_manager.register_fill_callback(self._on_fill)

    # ── 事件喂入（公开入口，驱动/测试/装配共用） ──

    def on_order_placed(self, record: ComplianceOrderRecord) -> list[ManipulationVerdict]:
        """报单事件：入 driver 窗口评估 + 拉抬打压评估 + 命中分发。"""
        with self._event_lock:
            verdicts = self._driver.on_order_placed(record)
            verdicts.extend(self._evaluate_ramp(record.symbol))
            self._trim_windows(record.placed_at)
            return self._dispatch(record.symbol, verdicts)

    def on_order_cancelled(
        self,
        symbol: str,
        order_id: str,
        cancelled_at: datetime,
    ) -> list[ManipulationVerdict]:
        """撤单事件：driver 标记撤单重评估 + 拉抬打压评估 + 命中分发。"""
        with self._event_lock:
            verdicts = self._driver.on_order_cancelled(symbol, order_id, cancelled_at)
            verdicts.extend(self._evaluate_ramp(symbol))
            self._trim_windows(cancelled_at)
            return self._dispatch(symbol, verdicts)

    def on_trade(self, trade: ComplianceTradeRecord) -> list[ManipulationVerdict]:
        """成交事件：WashTrade 即时检测 + 我方量入窗 + 拉抬打压评估 + 分发。"""
        with self._event_lock:
            verdicts = self._driver.on_trade(trade)
            fills = self._our_fills.setdefault(trade.symbol, deque())
            fills.append((trade.traded_at, trade.qty))
            cutoff = trade.traded_at.timestamp() - self._ramp_window_s
            while fills and fills[0][0].timestamp() < cutoff:
                fills.popleft()
            verdicts.extend(self._evaluate_ramp(trade.symbol))
            self._trim_windows(trade.traded_at)
            return self._dispatch(trade.symbol, verdicts)

    # ── 阻断判定（C-002 既有合规闸抛转消费） ──

    def is_frozen(self, symbol: str) -> bool:
        """标的是否已被操纵命中冻结（阻断判定，OrderManager C-002 闸消费）。"""
        with self._freeze_lock:
            return symbol in self._frozen

    @property
    def frozen_symbols(self) -> tuple[str, ...]:
        """当前冻结标的集合（观测用，确定性排序）。"""
        with self._freeze_lock:
            return tuple(sorted(self._frozen))

    def release_freeze(self, symbol: str, operator: str) -> bool:
        """人工复核后释放冻结（释放事件落 compliance_log 留痕）。"""
        with self._freeze_lock:
            verdict = self._frozen.pop(symbol, None)
        if verdict is None:
            return False
        self._logger.log(
            _EVENT_FREEZE_RELEASE,
            _SOURCE,
            {
                "symbol": symbol,
                "operator": operator,
                "released_mtype": verdict.mtype.value,
                "released_detail": verdict.detail,
            },
        )
        _logger.warning("盘中操纵冻结释放: symbol=%s operator=%s mtype=%s", symbol, operator, verdict.mtype.value)
        return True

    # ── OrderManager 回调适配（Order/Fill → 合规记录映射） ──

    def _on_order_event(self, order: Order) -> None:
        """订单事件回调：SUBMITTED=报单 / CANCELLED=撤单（其余状态忽略）。"""
        if order.status is OrderStatus.SUBMITTED:
            record = ComplianceOrderRecord(
                order_id=order.order_id,
                symbol=order.symbol,
                side=order.side.value,
                price=float(order.limit_price or 0),
                qty=float(order.quantity),
                placed_at=order.updated_at or order.created_at or datetime.now(UTC),
            )
            self.on_order_placed(record)
        elif order.status is OrderStatus.CANCELLED:
            self.on_order_cancelled(order.symbol, order.order_id, order.updated_at or datetime.now(UTC))

    def _on_fill(self, fill: Fill) -> None:
        """成交回调：Fill+本方订单方向 → 合规成交记录（关联账户标记判定）。"""
        order = self._order_manager.get_order(fill.order_id) if self._order_manager is not None else None
        counterparty = self._counterparty_resolver(fill) if self._counterparty_resolver is not None else None
        if counterparty is not None and counterparty == self._own_account:
            # 自成交撮合结果（43 号 §7.3 关联账户标记命中本方）→ 两侧同账户
            buyer = seller = self._own_account
        elif order is not None and order.side.value == "BUY":
            buyer, seller = self._own_account, counterparty or _MARKET_SELLER
        elif order is not None and order.side.value == "SELL":
            buyer, seller = counterparty or _MARKET_BUYER, self._own_account
        else:
            buyer, seller = _MARKET_BUYER, _MARKET_SELLER
        trade = ComplianceTradeRecord(
            symbol=fill.symbol,
            price=float(fill.fill_price),
            qty=float(fill.filled_quantity),
            traded_at=fill.fill_timestamp,
            buyer_account=buyer,
            seller_account=seller,
        )
        self.on_trade(trade)

    # ── 拉抬打压评估（规则唯一真源=detector.check_ramp_dump） ──

    def _evaluate_ramp(self, symbol: str) -> list[ManipulationVerdict]:
        """拉抬打压：5min 短窗价变 + 我方成交占比（缺数据/零市场量降级跳过）。"""
        if self._market_window_provider is None:
            return []
        window = self._market_window_provider(symbol)
        if window is None or window.window_volume <= 0:
            return []
        our_volume = sum(qty for _, qty in self._our_fills.get(symbol, ()))
        if our_volume <= 0:
            return []
        verdict = self._detector.check_ramp_dump(window.price_change_pct, our_volume / window.window_volume)
        return [verdict] if verdict is not None else []

    # ── 命中分发（告警 + 证据 + 冻结判定） ──

    def _dispatch(self, symbol: str, verdicts: list[ManipulationVerdict]) -> list[ManipulationVerdict]:
        for verdict in verdicts:
            _logger.error(
                "盘中操纵命中[%s]: symbol=%s action=%s detail=%s —— 冻结该标的，告警人工介入",
                verdict.mtype.value,
                symbol,
                verdict.action.value,
                verdict.detail,
            )
            with self._freeze_lock:
                self._frozen.setdefault(symbol, verdict)
            self._logger.log(
                _EVENT_REALTIME_ALERT,
                _SOURCE,
                {
                    "symbol": symbol,
                    "mtype": verdict.mtype.value,
                    "action": verdict.action.value,
                    "detail": verdict.detail,
                    "frozen": True,
                },
            )
        return verdicts

    def _trim_windows(self, at: datetime) -> None:
        """30min 滚动窗口修剪（口径=detector.thresholds.spoof_repeat_window_s SSoT）。"""
        self._driver.trim_before(at - timedelta(seconds=self._detector.thresholds.spoof_repeat_window_s))
