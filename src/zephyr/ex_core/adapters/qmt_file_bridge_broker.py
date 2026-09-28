# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
# [MODULE] zephyr.ex_core.adapters.qmt_file_bridge_broker
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.trading.trading_contracts.broker_interface; zephyr.ex_core.board_lot; zephyr.ex_core.price_cage; zephyr.governance.adapters.risk_validation_bridge; zephyr.shared.contracts.risk_limits; zephyr.shared.contracts.order; zephyr.shared.contracts.position; zephyr.shared.contracts.fill; zephyr.shared.utils.time_utils
# [CONSUMERS] zephyr.ex_core.order_manager
# [STARTUP] manual
# [MATURITY] draft
# [INVARIANTS] 文件状态机幂等(#SENDING→#DONE); 3秒轮询柜台同步; 双实例物理隔离(env=real/sim); sim 进桥前风控前置校验 fail-closed(R-H5E-1: 注入 risk_validator 即生效; env=real 保持现状不触校验——实盘账户启用=Owner 门裁定#338⑤); execution_report 生产端可选接线(attach_execution_report_producer, 同步线程每轮观察终态; 未接线=零行为变更, 断点E4); TRD-A10: 认领/撤单判定/check-then-act 全部在既有 self._lock 单临界区内完成(禁第二把锁), 客户端声称(#DONE/SENT/CONFIRMED)永不当作柜台收录, 柜台零收录超 phantom_grace_s→REJECTED+alert_sink+台账, 柜台导出缺失/超龄=禁判(不误杀活单), 撤单未获柜台凭证且龄<cancel_hold_s→False 不写行、超窗必放行; max_retry 死参数退役(全仓零消费者, 接线=重复下发即重复合同)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] QmtFileBridgeError
# [TESTS] tests/ex_core/adapters/test_qmt_file_bridge_broker.py
# [A_module] module_id=MOD-L06-001-QMTFB | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""QMT File Bridge Broker——大QMT文件桥执行器适配器

职责:
  - 实现 BrokerInterface 异步文件语义版本
  - HTTP 桥快路径（93 号备忘 §12）：submit_order 先 POST /order 直投沙箱 EXEC v16.4
    （实测中位 32ms ≈ miniqmt），失败自动降级文件桥（fail-open）
  - 通过指令CSV文件与沙箱内哑执行器(v14/v16)双向通信
  - submit_order 写入指令文件返回本地 order_id，broker_order_id 异步回填
  - 3秒轮询官方导出 CSV，同步柜台状态/成交/持仓
  - 双实例物理隔离：env="real"(实盘) / env="sim"(模拟)

约束:
  - HTTP 快路径 fail-open：连接拒绝/超时/非 200 一律降级文件桥（不抛异常不阻断）
  - 无实时连接，纯文件轮询（HTTP 路径只投单不读回报，回报统一走 ack 文件+柜台镜像）
  - 无实时盘口，预校验降级为无盘口模式
  - 算法单排队在 LocalOrderQueue，本类只负责单笔下发的文件写入
  - 柜台全量镜像由 CounterStateMirror 承担（单一职责，本类委托）

SSoT: docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
"""

from __future__ import annotations

import csv
import logging
import socket
import threading
from collections.abc import Callable
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Final

from zephyr.ex_core.board_lot import get_board_lot_rule
from zephyr.ex_core.price_cage import CageStatus, check_price_cage
from zephyr.governance.adapters.risk_validation_bridge import RiskValidationPort, RiskViolation
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order, OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.position import PositionSnapshot
from zephyr.shared.contracts.risk_limits import RiskLimits
from zephyr.shared.utils.time_utils import now_utc
from zephyr.trading.trading_contracts.broker_interface import BrokerInterface, FillCallback

_logger = logging.getLogger(__name__)


class QmtFileBridgeError(Exception):
    """QMT 文件桥错误"""

    error_code = "ZA-XC-QMTFB"


@dataclass
class FileBridgeInstruction:
    """文件桥指令行"""

    order_id: str
    action: str  # "order" | "cancel"
    symbol: str
    side: str  # "buy" | "sell"
    qty: int
    pricetype: str  # "latest" | "limit"
    price: float


@dataclass
class FileBridgeAck:
    """回执事件"""

    order_id: str
    status: str  # SENT | CONFIRMED | FAIL | CANCEL_SENT | RETRY
    detail: str


@dataclass
class CounterOrderRecord:
    """柜台委托记录"""

    remark: str
    sysid: str
    status: str
    symbol: str
    price: float
    qty: int
    filled_qty: int


# 柜台委托状态 → 本地 OrderStatus 映射
_COUNTER_STATUS_MAP: Final[dict[str, OrderStatus]] = {
    "已报": OrderStatus.SUBMITTED,
    "已报待撤": OrderStatus.SUBMITTED,
    "部成": OrderStatus.PARTIAL,
    "已成": OrderStatus.FILLED,
    "已撤": OrderStatus.CANCELLED,
    "废单": OrderStatus.REJECTED,
}

_ACTIVE_COUNTER_STATUSES: Final[tuple[str, ...]] = ("已报", "已报待撤", "部成")

# TRD-A10：终态口径唯一真源（旧写法在 :859/:904 各抄一份 inline 三元组，第三处再加必漂移）
_TERMINAL_STATUSES: Final[tuple[OrderStatus, ...]] = (
    OrderStatus.FILLED,
    OrderStatus.CANCELLED,
    OrderStatus.REJECTED,
)

# 回执/状态标记里"客户端声称已受理"但**不等于柜台收录**的状态（TRD-A10 缺陷①：
# 旧代码对这三类一个都不消费，订单因此永远停在 SUBMITTED=静默丢弃）
_CLAIM_ACK_STATUSES: Final[frozenset[str]] = frozenset({"SENT", "CONFIRMED", "CANCEL_SENT", "RETRY"})

# 柜台导出可信窗口：超过此龄期的 Order.csv 不能用来判"柜台零收录"（误杀防线）
_COUNTER_EXPORT_MAX_AGE_S: Final[float] = 60.0


class CounterStateMirror:
    """柜台全量镜像（2026-08-26 新增，2026-08-27 自 Broker 拆出）

    大脑必须知道 QMT 里所有状态，不只是本进程提交的订单：
    所有挂单（含手动/其他终端）、持仓（可用/冻结）、资金（可用/冻结）、当日成交。
    数据源：QMT 官方自动导出 Stock/*.csv（GBK）。
    """

    def __init__(self, stock_dir: Path):
        self._stock_dir = stock_dir
        self._orders: dict[str, dict] = {}  # remark -> {sysid, status, symbol, price, qty, filled_qty, side}
        self._positions: dict[str, dict] = {}  # bare_symbol -> {qty, available_qty, frozen_qty, cost, market_value}
        self._account: dict[str, Decimal] = {}  # {total, available, frozen, market_value}
        self._deals: list[dict] = []  # 当日成交（最新 100 条）
        self._processed_fill_ids: set[str] = set()

    # ── 查询接口 ──

    def get_orders(self) -> dict[str, dict]:
        return dict(self._orders)

    def get_positions(self) -> dict[str, dict]:
        return dict(self._positions)

    def get_account(self) -> dict[str, Decimal]:
        return dict(self._account)

    def get_deals(self) -> list[dict]:
        return list(self._deals)

    def available_cash(self) -> Decimal:
        return self._account.get("available", Decimal("0"))

    def available_qty(self, symbol: str) -> int:
        bare = symbol.split(".")[0]
        pos = self._positions.get(bare)
        return pos["available_qty"] if pos else 0

    def pending_count(self, symbol: str, side: str) -> int:
        bare = symbol.split(".")[0]
        return sum(1 for o in self._orders.values() if o["symbol"].split(".")[0] == bare and o["side"] == side)

    # ── 同步入口 ──

    def sync_all(self, order_cache: dict[str, Order], on_fill: Callable[[Fill], None]) -> None:
        """同步柜台全量状态：挂单/持仓/资金/成交

        Args:
            order_cache: 本进程订单缓存（用于回填 broker_order_id/推进状态）
            on_fill: 新成交回调（_processed_fill_ids 防重）
        """
        self._sync_orders(order_cache)
        self._sync_positions()
        self._sync_account()
        self._sync_deals(order_cache, on_fill)

    # ── 内部：分文件同步 ──

    def _sync_orders(self, order_cache: dict[str, Order]) -> None:
        order_file = self._stock_dir / "Order.csv"
        if not order_file.exists():
            return

        new_orders: dict[str, dict] = {}
        for row in _read_gbk_csv(order_file):
            if len(row) < 26:
                continue
            remark = row[9].strip()
            if remark == "投资备注" or not remark:  # 表头/空备注
                continue
            status_str = row[16].strip()
            sysid = row[15].strip()
            symbol = _normalize_symbol(row[11], row[10])
            side_str = row[25].strip()

            # 本进程订单：回填 broker_order_id + 状态推进（全状态，含终态）
            cached = order_cache.get(remark)
            if cached is not None:
                if sysid and not cached.broker_order_id:
                    cached.broker_order_id = sysid
                mapped = _COUNTER_STATUS_MAP.get(status_str)
                if mapped is not None and cached.status not in (
                    OrderStatus.FILLED,
                    OrderStatus.CANCELLED,
                    OrderStatus.REJECTED,
                ):
                    cached.status = mapped
                    cached.updated_at = now_utc()

            # 只保留活跃状态进镜像（已撤/已成/废单归档）
            if status_str not in _ACTIVE_COUNTER_STATUSES:
                continue
            new_orders[remark] = {
                "sysid": sysid,
                "status": status_str,
                "symbol": symbol,
                "price": _to_decimal(row[13]),
                "qty": _to_int(row[14]),
                "filled_qty": _to_int(row[17]),
                "side": "buy" if side_str == "买入" else "sell",
            }

        self._orders = new_orders

    def _sync_positions(self) -> None:
        pos_file = self._stock_dir / "PositionStatics.csv"
        if not pos_file.exists():
            return

        new_positions: dict[str, dict] = {}
        for row in _read_gbk_csv(pos_file):
            if len(row) < 19 or row[7] == "证券代码":
                continue
            qty = _to_int(row[9])
            if qty <= 0:
                continue
            symbol = _normalize_symbol(row[7], row[5])
            available = _to_int(row[15])
            new_positions[symbol.split(".")[0]] = {
                "qty": qty,
                "available_qty": available,
                "frozen_qty": qty - available,
                "cost": _to_decimal(row[10]),
                "market_value": _to_decimal(row[13]),
            }

        self._positions = new_positions

    def _sync_account(self) -> None:
        acct_file = self._stock_dir / "Account.csv"
        if not acct_file.exists():
            return

        for row in _read_gbk_csv(acct_file):
            if len(row) < 11 or row[6] == "总资产":
                continue
            self._account = {
                "total": _to_decimal(row[6]),
                "available": _to_decimal(row[7]),
                "frozen": _to_decimal(row[5]),
                "market_value": _to_decimal(row[10]),
            }
            break

    def _sync_deals(self, order_cache: dict[str, Order], on_fill: Callable[[Fill], None]) -> None:
        deal_file = self._stock_dir / "Deal.csv"
        if not deal_file.exists():
            return

        for row in _read_gbk_csv(deal_file):
            if len(row) < 24:
                continue
            remark = row[9].strip()
            if remark == "投资备注":  # 表头
                continue
            deal_id = row[14].strip()
            if not deal_id or deal_id in self._processed_fill_ids:
                continue
            self._processed_fill_ids.add(deal_id)

            symbol = _normalize_symbol(row[12], row[11])
            price = _to_decimal(row[17])
            qty = _to_int(row[18])
            side = "buy" if row[23].strip() == "买入" else "sell"
            fee = _to_decimal(row[21])

            self._deals.append(
                {
                    "deal_id": deal_id,
                    "remark": remark,
                    "symbol": symbol,
                    "side": side,
                    "qty": qty,
                    "price": price,
                    "time": f"{row[19].strip()} {row[20].strip()}",
                }
            )
            if len(self._deals) > 100:
                self._deals = self._deals[-100:]

            # 更新本进程订单
            cached = order_cache.get(remark)
            strategy_id = cached.strategy_id if cached else "qmt_file_bridge"
            if cached is not None:
                cached.filled_quantity += Decimal(qty)
                cached.avg_fill_price = price
                cached.status = OrderStatus.FILLED if cached.filled_quantity >= cached.quantity else OrderStatus.PARTIAL
                cached.updated_at = now_utc()

            fill = Fill(
                fill_id=deal_id,
                fill_price=price,
                fill_timestamp=now_utc(),
                filled_quantity=Decimal(qty),
                idempotency_key=deal_id,
                order_id=remark,
                strategy_id=strategy_id,
                symbol=symbol,
                broker_fill_id=deal_id,
                commission=fee,
            )
            on_fill(fill)


class QmtFileBridgeBroker(BrokerInterface):
    """QMT 文件桥 Broker（异步文件语义）

    Usage:
        # 实盘
        broker_real = QmtFileBridgeBroker(env="real")
        broker_real.connect()
        order_id = broker_real.submit_order(order)  # 返回本地 order_id

        # 模拟
        broker_sim = QmtFileBridgeBroker(env="sim")
        broker_sim.connect()
    """

    # 环境配置
    ENV_CONFIG: Final[dict[str, dict[str, str]]] = {
        "real": {
            "bridge_dir": r"E:\qmt_bridge",
            "orders_file": r"E:\qmt_bridge\orders_real.csv",
            "ack_file": r"E:\qmt_bridge\ack_real.csv",
            "stock_dir": r"E:\qmt_bridge\Stock",
            "account": "8887871993",
        },
        "sim": {
            "bridge_dir": r"E:\qmt_bridge_sim",
            "orders_file": r"E:\qmt_bridge_sim\orders_sim.csv",
            "ack_file": r"E:\qmt_bridge_sim\ack_sim.csv",
            "stock_dir": r"E:\qmt_bridge_sim\Stock",
            "account": "8886156677",
        },
    }

    def __init__(
        self,
        env: str = "sim",
        sync_interval: float = 3.0,
        http_port: int = 18901,
        risk_validator: RiskValidationPort | None = None,
        alert_sink: Callable[[dict], None] | None = None,
        phantom_grace_s: float = 180.0,
        cancel_hold_s: float = 20.0,
    ):
        """初始化 QMT 文件桥 Broker

        Args:
            env: 环境标识 "real"(实盘) 或 "sim"(模拟)
            sync_interval: 柜台同步轮询间隔（秒），默认 3 秒
            http_port: HTTP 桥快路径端口（93 号备忘 §12），默认 18901
            risk_validator: 风控校验端口（R-H5E-1，可选注入）。注入后仅 sim 环境
                在订单进桥前执行前置校验（HALT 违规或校验异常 → Fail-Closed 拒单
                不进桥）；env="real" 保持现状不触校验——实盘账户启用=Owner 门
                （裁定 #338⑤），装配层不得向 real 实例传入本参数。
            alert_sink: TRD-A10 丢弃告警出口 callable(payload: dict)，与本域既有约定
                同形（ex_core.eod_reconciliation.alert_sink / performance_monitor.alerter
                / compliance_drift_detector.alert_sink）：未注入=仅日志（零行为变更），
                注入后异常被吞没（告警不得打断柜台同步主链）。装配点
                qmt_file_bridge_integration 仅对 sim 实例接 OpsAlertFeed 通知板，
                real 实例保持不注入=实盘零变更。
            phantom_grace_s: 幽灵单（客户端已声称、柜台零收录）宽限期，默认 180 秒。
                超期即转 REJECTED 并外发告警——取代旧 `max_retry` 死参数（该参数声明了
                "#SENDING 超时重试最大次数"却全仓零消费者；真接线=重复下发，正是
                09-22 同 remark 36 张合同的重复合同成因，故退役不实现）。
            cancel_hold_s: 撤单暂缓窗，默认 20 秒。目标未获柜台凭证且龄 < 本窗 ⇒
                cancel_order 返回 False 且不写撤单行（关掉 submit→cancel 竞态触发面）；
                超窗必放行（撤单是风控动作，护栏不许挡住）。

        注：原 `max_retry: int = 3` 形参已退役（TRD-A10 净零对价，全仓零调用方传入，
        grep 证据见 docs/_working/three_piece_infra/p0_bridge/CASE.md §一）。
        """
        if env not in self.ENV_CONFIG:
            raise QmtFileBridgeError(f"非法环境标识: {env}，必须是 'real' 或 'sim'")

        self._env = env
        self._config = self.ENV_CONFIG[env]
        self._sync_interval = sync_interval
        self._risk_validator = risk_validator
        self._alert_sink = alert_sink
        self._phantom_grace_s = float(phantom_grace_s)
        self._cancel_hold_s = float(cancel_hold_s)
        if env == "sim" and risk_validator is None:
            # R-H5E-1 可见性：sim 未注入校验器=进桥前闸不生效（向后兼容放行语义）。
            # 运维红线留痕：装配层忘了注入时日志可见，而不是静默裸奔。
            _logger.warning(
                "sim Broker 未注入 risk_validator——进桥前风控前置校验不生效"
                "（向后兼容放行）；需要 R-H5E-1 闸门须显式传入 risk_validator"
            )

        # 文件路径
        self._bridge_dir = Path(self._config["bridge_dir"])
        self._orders_file = Path(self._config["orders_file"])
        self._ack_file = Path(self._config["ack_file"])
        self._stock_dir = Path(self._config["stock_dir"])

        # 状态缓存
        self._order_cache: dict[str, Order] = {}
        self._idempotency_map: dict[str, str] = {}  # idempotency_key -> order_id
        # 柜台侧以指令 order_id 列（=idempotency_key，即回执/挂单/成交的 remark）回查本地订单；
        # 生产链 order_id 与 idempotency_key 是两个独立 uuid4，配对必须走双键视图
        self._remark_to_order_id: dict[str, str] = {}  # 指令order_id(remark) -> 本地order_id
        self._pairing_cache: dict[str, Order] = {}  # order_id 与 remark 双键均可命中
        self._connected = False
        self._lock = threading.Lock()

        # ── TRD-A10 两缺陷治理状态（全部由 self._lock 串行，禁止新增第二把锁）──
        # 未获柜台收录的"声称"台账：指令 order_id(=remark) -> 认领时刻（epoch 秒）
        # 认领来源=自有 submit（不依赖闭源客户端日志，避开单点黑盒依赖 L07-S3-G7）
        self._claims: dict[str, float] = {}
        # 在途撤单：目标 remark -> 撤单指令 order_id（同目标不重复写行）
        self._cancel_inflight: dict[str, str] = {}
        # 暂缓撤单待补发：目标 remark -> 本地 order_id。
        # 护栏把撤单挡在窗内≠放弃风控动作：柜台一旦收录或窗口一到，下一轮自动补发，
        # 不留"挡了就不再有人试"的空洞（本班实测 risk_layer_orchestrator:392 是直通调用，
        # 调用方不重试，所以补发责任只能在 broker 侧）。
        self._cancel_pending: dict[str, str] = {}
        # "静默类"问题计数：让丢弃/吞回执/暂缓撤单在健康面读得出，而不是只进日志
        self._sync_counters: dict[str, int] = {
            "phantom_rejected": 0,  # 柜台零收录超时拒单化张数（原静默丢弃）
            "ack_unmatched": 0,  # 回执找不到对应订单（旧代码 continue 零痕迹）
            "ack_read_failed": 0,  # 回执文件读失败轮数（旧代码 return [], offset 零痕迹）
            "mark_unmatched": 0,  # 指令文件状态标记找不到对应订单
            "mark_scan_failed": 0,  # 指令文件读失败轮数
            "cancel_held": 0,  # 撤单暂缓窗内被挡下的次数（竞态触发面）
            "cancel_deferred_fired": 0,  # 暂缓后由同步轮补发成功的次数
            "cancel_deferred_dropped": 0,  # 暂缓期间目标已终态而无需补发的次数
            "cancel_guard_paused": 0,  # 柜台视图不可判定=护栏暂停、撤单照常下发（宁放勿挡）
            "counter_export_unavailable": 0,  # 柜台导出缺失/超龄=幽灵单判定暂停轮数
        }
        self._seen_unmatched_marks: set[str] = set()

        # HTTP 桥快路径（93 号备忘 §12：EXEC v16.4 沙箱内 18901；None=禁用纯文件模式）
        self._http_port = http_port

        # 同步线程
        self._sync_thread: threading.Thread | None = None
        self._sync_stop = threading.Event()

        # 成交回调
        self._fill_callbacks: list[FillCallback] = []
        # 回执文件读取偏移
        self._ack_offset = 0

        # 柜台全量镜像（单一职责拆出，本类委托）
        self._mirror = CounterStateMirror(self._stock_dir)

        # 断点 E4：execution_report 生产端（None=未接线，行为与历史一致）
        self._report_producer: object | None = None

    @property
    def broker_id(self) -> str:
        return f"qmt_{self._env}"

    def attach_execution_report_producer(self, producer: object) -> None:
        """接线 execution_report 生产端（断点 E4 闭合）。

        接上后柜台同步线程每轮把本地订单缓存交给 producer 观察，订单到达终态
        （FILLED/CANCELLED/REJECTED）即向 ``c1_market.execution_report`` 落一行
        聚合。producer 幂等（order_id 已发即跳过），重复观察不产生重复行。

        Args:
            producer: ``zephyr.ex_core.execution_report_producer.ExecutionReportProducer``
                实例（结构性鸭子类型，不在导入期依赖以避免 ex_core↔data 环）。
        """
        self._report_producer = producer
        _logger.info("execution_report 生产端已接线 env=%s producer=%s", self._env, type(producer).__name__)

    def order_cache_snapshot(self) -> list[Order]:
        """本地订单缓存快照（终态观察取数口，加锁防同步线程并发改字典）。"""
        with self._lock:
            return list(self._order_cache.values())

    def execution_report_stats(self) -> dict:
        """生产端计数快照（未接线返回空 dict）——健康检查/断点回归取证用。"""
        if self._report_producer is None:
            return {}
        return self._report_producer.stats.as_dict()

    def _observe_terminal_orders(self) -> None:
        """把订单缓存交给生产端观察终态（旁路：异常不打断同步线程）。"""
        if self._report_producer is None:
            return
        try:
            self._report_producer.observe(self.order_cache_snapshot())
        except Exception as e:  # noqa: BLE001 — 台账旁路不得打断柜台同步主链
            _logger.error("execution_report 产出观察异常(env=%s): %r", self._env, e)

    def connect(self) -> bool:
        """校验桥接目录可读写并启动同步线程"""
        with self._lock:
            try:
                # 确保目录存在
                self._bridge_dir.mkdir(parents=True, exist_ok=True)
                self._stock_dir.mkdir(parents=True, exist_ok=True)

                # 确保指令文件存在（写表头）
                if not self._orders_file.exists():
                    self._orders_file.write_text("order_id,action,symbol,side,qty,pricetype,price\n", encoding="ascii")

                # 确保回执文件存在
                if not self._ack_file.exists():
                    self._ack_file.touch()

                # 测试读写
                test_file = self._bridge_dir / ".rw_test"
                test_file.write_text("ok", encoding="ascii")
                test_file.unlink()

                self._connected = True

                # 启动同步线程
                if not (self._sync_thread and self._sync_thread.is_alive()):
                    self._sync_stop.clear()
                    self._sync_thread = threading.Thread(
                        target=self._sync_loop,
                        name=f"qmtfb-sync-{self._env}",
                        daemon=True,
                    )
                    self._sync_thread.start()

                _logger.info(
                    "QmtFileBridgeBroker connected env=%s dir=%s",
                    self._env,
                    self._bridge_dir,
                )
                return True
            except OSError as e:
                _logger.error("QmtFileBridgeBroker connect failed: %r", e)
                return False

    def disconnect(self) -> None:
        """停止同步线程"""
        self._sync_stop.set()
        if self._sync_thread and self._sync_thread.is_alive():
            self._sync_thread.join(timeout=5)
        self._connected = False
        _logger.info("QmtFileBridgeBroker disconnected env=%s", self._env)

    def submit_order(self, order: Order) -> str:
        """写入指令文件，返回本地 order_id（broker_order_id 异步回填）

        TRD-A10 缺陷②（submit→cancel 竞态）修正要点：
          1. 幂等检查与认领**同处一个临界区**（旧写法检查在锁外 :515、登记在锁内 :561，
             中间隔着指令落盘 ⇒ 两线程同 idempotency_key 双双过检=写两条指令行=两张柜台合同）；
          2. 缓存/声称登记**先于**指令落盘（旧写法落盘后才登记 ⇒ 同步线程可能在
             "已落盘未登记"窗口读到 #DONE/ack 却查无此单，被 _apply_acks 静 continue 吞掉）；
          3. 落盘异常 ⇒ 回滚认领（不留"认领了却从未下发"的假声称）。
        """
        # 幂等快路径（与修复前同位同语义：锁外只读，命中即返回；权威判定在下面的
        # 临界区里 check-then-claim 合一，竞态由那一次加锁关掉）
        existing_id = self._idempotency_map.get(order.idempotency_key)
        if existing_id is not None:
            _logger.info("幂等命中 idem=%s -> %s", order.idempotency_key, existing_id)
            return existing_id

        # R-H5E-1 进桥前风控前置校验（仅 sim；real 保持现状——实盘 Owner 门裁定 #338⑤）
        # 位置与修复前一致：先于任何状态变更，Fail-Closed 订单不进桥、不认领、不落盘
        if self._env == "sim" and self._risk_validator is not None:
            self._pretrade_risk_check(order)

        # A股约束校验：整手（纯校验，先于任何状态变更）
        rule = get_board_lot_rule(order.symbol)
        qty = int(order.quantity)
        if order.side == OrderSide.BUY and qty < rule.min_unit:
            raise QmtFileBridgeError(f"数量不合法: 买入 {qty} 股低于最小申报单位 {rule.min_unit}（{order.symbol}）")

        # 价格笼子（降级无盘口：UNKNOWN 原价通过，超限夹边）
        pricetype = "limit"
        price = 0.0
        if order.order_type == OrderType.MARKET:
            pricetype = "latest"
        elif order.limit_price is not None:
            cage = check_price_cage(order.side, order.limit_price, order.symbol)
            if cage.status == CageStatus.CLAMPED:
                _logger.warning(
                    "价格笼子夹边 %s %s: %s -> %s",
                    order.symbol,
                    order.side.value,
                    order.limit_price,
                    cage.clamped_price,
                )
            price = float(cage.clamped_price)

        remark = order.idempotency_key
        claimed_now = now_utc().timestamp()
        with self._lock:
            # 幂等拦截（check-then-claim 合一，同临界区）
            existing_id = self._idempotency_map.get(remark)
            if existing_id is not None:
                _logger.info("幂等命中 idem=%s -> %s", remark, existing_id)
                return existing_id
            order.status = OrderStatus.SUBMITTED
            order.updated_at = now_utc()
            self._order_cache[order.order_id] = order
            self._idempotency_map[remark] = order.order_id
            self._remark_to_order_id[remark] = order.order_id
            self._pairing_cache[order.order_id] = order
            self._pairing_cache[remark] = order
            self._claims[remark] = claimed_now

        inst = FileBridgeInstruction(
            order_id=remark,
            action="order",
            symbol=order.symbol,
            side="buy" if order.side == OrderSide.BUY else "sell",
            qty=qty,
            pricetype=pricetype,
            price=price,
        )
        try:
            self._append_instruction(inst)
        except Exception as exc:  # noqa: BLE001 — 下发失败必须回滚认领，否则留下永无对手机会的假声称
            with self._lock:
                self._claims.pop(remark, None)
                self._idempotency_map.pop(remark, None)
                self._remark_to_order_id.pop(remark, None)
                self._pairing_cache.pop(remark, None)
                self._pairing_cache.pop(order.order_id, None)
                self._order_cache.pop(order.order_id, None)
            order.status = OrderStatus.REJECTED
            order.updated_at = now_utc()
            _logger.error(
                "指令下发失败，已回滚认领并拒单（不静默）: env=%s order=%s remark=%s error=%r",
                self._env,
                order.order_id,
                remark,
                exc,
            )
            self._emit_alert(
                {
                    "event": "instruction_write_failed",
                    "order_id": order.order_id,
                    "remark": remark,
                    "reason": f"指令下发失败: {exc!r}",
                }
            )
            raise

        _logger.info("指令写入 %s: %s %s %s x%d %s", self._env, inst.order_id, inst.symbol, inst.side, qty, pricetype)
        return order.order_id

    def _pretrade_risk_check(self, order: Order) -> None:
        """sim 进桥前风控前置校验（R-H5E-1，裁定 #338⑤ paper/sim 准施工）。

        Fail-Closed 双闸（不许 fail-open）：
          - HALT 级违规 → 抛 QmtFileBridgeError，订单不进桥（不写指令文件、
            不走 HTTP 快路径），拒绝原因落 error 级执行证据日志；
          - 校验器自身异常 → 同样抛 QmtFileBridgeError 拒单（校验失效≠放行），
            异常链留痕。

        target_weight 口径：桥层无策略权重语义，以订单名义金额/账户总资产近似；
        柜台镜像未就绪（同步线程首轮未完成）时按 0.0 处理——此时仍可拦截
        Kill Switch 级状态违规（校验器自带状态）；权重类校验真源在上游
        TradingSession._is_blocked_by_risk / Saga step1（两层互补，不互替）。
        """
        try:
            violations: list[RiskViolation] = self._risk_validator.validate_order(
                symbol=order.symbol,
                target_weight=self._estimate_order_weight(order),
                current_holdings=self._holdings_as_weights(),
                limits=self._pretrade_limits(order),
            )
            # 红队批修正：HALT 扫描必须在 try 内——有 bug 的第三方校验器返回
            # None/非可迭代/元素缺 severity 时，旧写法在 try 外抛 TypeError/
            # AttributeError，违反本方法 QmtFileBridgeError 错误契约（虽仍不放行，
            # 但拒单原因与异常链失真）。
            halt_violations = [v for v in violations if v.severity == "HALT"]
        except Exception as exc:  # noqa: BLE001 — 校验失效类型不可枚举，Fail-Closed 必须全捕获
            _logger.error(
                "进桥前风控校验失效，Fail-Closed 拒单: env=%s order=%s symbol=%s error=%r",
                self._env,
                order.order_id,
                order.symbol,
                exc,
            )
            raise QmtFileBridgeError(
                f"风控校验失效（fail-closed 拒单，订单不进桥）: order={order.order_id} symbol={order.symbol}: {exc}"
            ) from exc

        if halt_violations:
            reasons = "; ".join(v.description for v in halt_violations)
            _logger.error(
                "进桥前风控拒单（订单不进桥）: env=%s order=%s symbol=%s side=%s qty=%s violations=%s",
                self._env,
                order.order_id,
                order.symbol,
                order.side.value,
                order.quantity,
                reasons,
            )
            raise QmtFileBridgeError(f"风控拒单（fail-closed，订单不进桥）: {reasons}")

    def _estimate_order_weight(self, order: Order) -> float:
        """订单名义金额 / 账户总资产 的权重近似（卖出为负；净值不可得=0.0）。"""
        total = self._mirror.get_account().get("total", Decimal("0"))
        if total <= 0:
            return 0.0
        order_value = order.quantity * (order.limit_price or Decimal("0"))
        weight = float(order_value / total)
        return -weight if order.side == OrderSide.SELL else weight

    def _holdings_as_weights(self) -> dict[str, float]:
        """柜台镜像持仓 → 权重字典（市值/总资产；总资产不可得=空字典）。"""
        account = self._mirror.get_account()
        total = account.get("total", Decimal("0"))
        if total <= 0:
            return {}
        return {
            bare: float(pos.get("market_value", Decimal("0")) / total)
            for bare, pos in self._mirror.get_positions().items()
        }

    def _pretrade_limits(self, order: Order) -> RiskLimits:
        """进桥校验限额（保守默认：单标的 10%、杠杆 1.0，与 Saga 默认同口径）。"""
        now = now_utc()
        return RiskLimits(
            as_of_date=now,
            idempotency_key=f"qmtfb-{self._env}-{order.order_id}",
            max_single_position=0.10,
            max_gross_leverage=1.0,
        )

    def cancel_order(self, broker_order_id: str) -> bool:
        """写入撤单指令

        Returns:
            True = 撤单指令已在途或已被本 broker 受理（同目标幂等，不重复写行）
            False = 本轮被暂缓窗挡下，**已登记待补发**（下一同步轮自动补发，
                    调用方无需重试；风控直通面拿到 False 也不会漏撤）

        broker_order_id 是 submit_order 返回的本地 order_id；柜台按指令 order_id
        列（=remark=idempotency_key）匹配目标单，必须先解析回 remark 再写入。

        TRD-A10 缺陷②（撤单竞态）修正要点——共享状态=(order 缓存, 声称台账, 柜台镜像
        可见性, 在途撤单集)四元组，串行原语**复用既有 self._lock**（本类 :403 起就有的
        那把，不新建第三把锁；实测旧写法在 :659 锁外读缓存）：
          1. 四元组在**一个临界区内一次读齐**，杜绝"读到旧缓存 + 柜台刚销案"的撕裂视图；
          2. 未获柜台凭证（无 sysid 回填且柜台挂单集查无该 remark）且订单龄 < 撤单暂缓窗
             ⇒ 不写撤单行、返回 False：撤一张柜台从未收录的单，旧写法无条件 True=撤单假成功，
             调用方以为已撤而那张单可能在柜台出现后成交=漏单；
          3. 柜台视图不可判定（导出缺失/超龄、或本进程无该单台账）⇒ **必放行**，
             撤单是风控动作，护栏只许在有据可查时生效；
          4. 超窗同样必放行（护栏不许长期挡住撤单）；
          5. 同目标撤单在途期间不重复写行（幂等），第二次调用返回 True（已有撤单在飞）；
          6. 返回 False 的含义是**延后**不是**放弃**：目标进 `_cancel_pending`，由同步轮
             在"柜台收录该委托"或"暂缓窗到期"时补发（`_drain_deferred_cancels`）。
        """
        with self._lock:
            cached = self._order_cache.get(broker_order_id) or self._pairing_cache.get(broker_order_id)
            remark = cached.idempotency_key if cached is not None else broker_order_id
            has_credential = bool(cached is not None and cached.broker_order_id)
            counter_confirmed = remark in self._mirror.get_orders()
            claimed_at = self._claims.get(remark)
            inflight = self._cancel_inflight.get(remark)
            if inflight is None:
                self._cancel_inflight[remark] = f"C{broker_order_id}"

        if cached is None:
            _logger.warning("撤单目标不在本地缓存（回退用 order_id 作 remark）: %s", broker_order_id)

        if inflight is not None:
            _logger.info("撤单指令已在途，不重复写行 %s: target=%s remark=%s", self._env, broker_order_id, remark)
            return True

        if not has_credential and not counter_confirmed and claimed_at is not None:
            now_ts = now_utc().timestamp()
            age_s = now_ts - claimed_at
            export_age_s = self._counter_export_age_s(now_ts)
            if export_age_s is None or export_age_s > _COUNTER_EXPORT_MAX_AGE_S:
                # 柜台视图缺失/超龄=不可判定 ⇒ 护栏**不生效**（撤单是风控动作，宁放勿挡），
                # 但必须留痕计数，不许"因为判不了就当没事"。
                with self._lock:
                    self._sync_counters["cancel_guard_paused"] += 1
                _logger.warning(
                    "撤单护栏暂停（柜台导出缺失/超龄 age=%s，无法证明该单是否被收录）→ 照常下发撤单: "
                    "env=%s target=%s remark=%s",
                    "缺失" if export_age_s is None else f"{export_age_s:.1f}s",
                    self._env,
                    broker_order_id,
                    remark,
                )
            elif age_s < self._cancel_hold_s:
                with self._lock:
                    self._cancel_inflight.pop(remark, None)
                    self._sync_counters["cancel_held"] += 1
                    self._cancel_pending[remark] = broker_order_id
                _logger.warning(
                    "撤单暂缓（柜台零收录且未超撤单窗 %.1fs<%.1fs）%s: target=%s remark=%s"
                    "——撤一张柜台从未收录的单会留下假成功，等柜台凭证或超窗后再撤",
                    age_s,
                    self._cancel_hold_s,
                    self._env,
                    broker_order_id,
                    remark,
                )
                self._emit_alert(
                    {
                        "event": "cancel_held",
                        "order_id": broker_order_id,
                        "remark": remark,
                        "reason": f"柜台零收录，撤单暂缓窗内（age={age_s:.1f}s < {self._cancel_hold_s}s）",
                    }
                )
                return False

        inst = FileBridgeInstruction(
            order_id=f"C{broker_order_id}",
            action="cancel",
            symbol=remark,  # 目标订单 remark（柜台配对键）
            side="",
            qty=0,
            pricetype="",
            price=0.0,
        )
        try:
            self._append_instruction(inst)
        except Exception as exc:  # 下发失败必须撤销在途标记，否则该目标永不再被尝试撤单
            with self._lock:
                self._cancel_inflight.pop(remark, None)
            _logger.error("撤单指令下发失败 env=%s target=%s: %r", self._env, broker_order_id, exc)
            raise
        _logger.info("撤单指令写入 %s: target=%s remark=%s", self._env, broker_order_id, remark)
        return True

    def query_order(self, broker_order_id: str) -> Order | None:
        """本地缓存查询（含柜台同步推进后的最新状态）"""
        with self._lock:
            order = self._order_cache.get(broker_order_id)
        if order is None:
            _logger.debug("query_order 未命中: %s", broker_order_id)
        return order

    def get_positions(self) -> PositionSnapshot:
        """读取 PositionStatics.csv + Account.csv 构造快照"""
        holdings: dict[str, Decimal] = {}
        market_values: dict[str, Decimal] = {}
        cash = Decimal("0")

        pos_file = self._stock_dir / "PositionStatics.csv"
        for row in _read_gbk_csv(pos_file):
            if len(row) < 19 or row[7] == "证券代码":
                continue
            qty = _to_int(row[9])
            if qty <= 0:
                continue
            symbol = _normalize_symbol(row[7], row[5])
            holdings[symbol] = Decimal(qty)
            market_values[symbol] = _to_decimal(row[13])

        acct_file = self._stock_dir / "Account.csv"
        for row in _read_gbk_csv(acct_file):
            if len(row) < 11 or row[6] == "总资产":
                continue
            cash = _to_decimal(row[7])  # 可用金额
            break

        return PositionSnapshot(
            as_of_timestamp=now_utc(),
            idempotency_key=f"pos-{self._env}-{int(now_utc().timestamp())}",
            portfolio_id=f"qmt_{self._env}",
            cash=cash,
            holdings=holdings,
            market_values=market_values,
            total_market_value=sum(market_values.values(), Decimal("0")),
        )

    def register_fill_callback(self, callback: FillCallback) -> None:
        """注册成交回调（柜台同步线程检测到新成交时扇出）"""
        self._fill_callbacks.append(callback)
        _logger.debug(
            "成交回调已注册 env=%s callbacks=%d",
            self._env,
            len(self._fill_callbacks),
        )

    # ── 柜台全量镜像查询接口（委托 CounterStateMirror）──

    def get_all_counter_orders(self) -> dict[str, dict]:
        """所有活跃挂单（含手动/其他终端）"""
        return self._mirror.get_orders()

    def get_counter_positions(self) -> dict[str, dict]:
        """所有持仓镜像"""
        return self._mirror.get_positions()

    def get_counter_account(self) -> dict[str, Decimal]:
        """资金镜像"""
        return self._mirror.get_account()

    def get_counter_deals(self) -> list[dict]:
        """当日成交列表"""
        return self._mirror.get_deals()

    def get_available_cash(self) -> Decimal:
        """可用资金"""
        return self._mirror.available_cash()

    def get_available_qty(self, symbol: str) -> int:
        """指定标的可卖数量（symbol 可带后缀）"""
        return self._mirror.available_qty(symbol)

    def get_pending_orders_count(self, symbol: str, side: str) -> int:
        """指定标的+方向的活跃挂单数（柜台挂单上限守卫用）"""
        return self._mirror.pending_count(symbol, side)

    # ── 内部：指令文件 ──

    def _append_instruction(self, inst: FileBridgeInstruction) -> None:
        """追加指令行（原子语义：整行一次写入）。
        HTTP 快路径（93 号备忘 §12）：先 POST /order 直投沙箱 EXEC v16.4（实测中位 32ms），
        任何失败（连接拒绝/超时/非 200）fail-open 降级写文件桥（handlebar 兜底，实测中位 5.7s）。
        ack 回执统一走 ack 文件（EXEC 两条路径都写 ack），HTTP 成功时文件桥的 #SENDING
        状态机不介入（订单从未入文件），由柜台镜像同步推进状态。"""
        line = f"{inst.order_id},{inst.action},{inst.symbol},{inst.side},{inst.qty},{inst.pricetype},{inst.price}\n"
        if self._http_post_order(line):
            return
        with self._lock:
            with open(self._orders_file, "a", encoding="ascii", newline="") as f:
                f.write(line)

    def _http_post_order(self, line: str) -> bool:
        """HTTP 桥快路径：POST /order 到沙箱 EXEC 策略（127.0.0.1:18901）。
        Returns:
            True=HTTP 受理（不必等 ack，柜台镜像 3s 轮询推进状态）
            False=任何失败（降级文件桥由调用方处理）
        """
        body = line.strip()
        req = (
            f"POST /order HTTP/1.1\r\nHost: 127.0.0.1\r\n"
            f"Content-Type: text/plain\r\nContent-Length: {len(body.encode('ascii'))}\r\n"
            f"Connection: close\r\n\r\n{body}"
        ).encode("ascii")
        try:
            with socket.create_connection(("127.0.0.1", self._http_port), timeout=2.0) as s:
                s.sendall(req)
                resp = b""
                while b"\r\n\r\n" not in resp:
                    chunk = s.recv(4096)
                    if not chunk:
                        return False   # 对端关闭未回包（毛刺，降级）
                    resp += chunk
                status = resp.split(b" ", 2)[1]
                return status == b"200"
        except OSError:
            return False   # 连接拒绝/超时（EXEC 未运行或收盘冻结）

    # ── 内部：同步线程 ──

    def _sync_loop(self) -> None:
        while not self._sync_stop.is_set():
            try:
                self._sync_round()
            except Exception as e:  # 同步失败不杀线程，下轮重试
                _logger.warning("柜台同步异常(env=%s): %r", self._env, e)
            self._sync_stop.wait(self._sync_interval)

    def _sync_round(self) -> None:
        """一轮柜台同步（原 _sync_loop 循环体原样抽出，语义不变；抽出后事件触发方
        与测试可逐轮驱动，不再只能靠线程 sleep 竞争时序）。

        对账时点必须在镜像刷新**之后**——用最新柜台视图判幽灵单，否则拿上一轮缓存误杀活单。
        """
        self._sync_local_channel()
        self._mirror.sync_all(self._pairing_cache, self._dispatch_fill)
        self._reconcile_unconfirmed_claims()
        self._drain_deferred_cancels()
        # 断点 E4：状态推进完毕后观察终态，成交/撤单/拒单落 execution_report
        self._observe_terminal_orders()

    def _sync_local_channel(self) -> None:
        """扫描指令文件状态标记 + 增量读取回执文件

        缓存/计数改写全程持 self._lock，与 submit_order/cancel_order 的临界区互斥
        （TRD-A10 缺陷②：旧写法这一段完全无锁）。柜台导出 sync_all 不在此锁内——
        它对订单字段的写是**单写手**（只有本线程），跨线程撕裂风险集中在
        check-then-act 的认领/撤单判定上，那两处已收进同一把锁。
        """
        with self._lock:
            _scan_instruction_states(
                self._orders_file,
                self._pairing_cache,
                self._sync_counters,
                self._seen_unmatched_marks,
            )
            acks, self._ack_offset = _read_new_acks(self._ack_file, self._ack_offset, self._sync_counters)
            _apply_acks(acks, self._pairing_cache, self._sync_counters, self._cancel_inflight)

    def _counter_export_age_s(self, now_ts: float) -> float | None:
        """柜台 Order.csv 导出龄期（秒）；文件不存在=None（不可判定，禁判幽灵单）"""
        path = self._stock_dir / "Order.csv"
        try:
            return max(0.0, now_ts - path.stat().st_mtime)
        except OSError:
            return None

    def _reconcile_unconfirmed_claims(self) -> None:
        """TRD-A10 缺陷① 脑侧兜底：客户端已声称、柜台始终零收录 ⇒ 显式拒单化（不再静默停在 SUBMITTED）

        判据与防线（全部实测语义，不猜客户端行为）：
          - 认领来源=self._claims（submit 时登记），**不读闭源客户端日志**
            （避开 L07-S3-G7 那条"活性依赖第三方日志"的单点黑盒依赖）；
          - 柜台镜像一旦出现该 remark ⇒ 立即销案（防线一：真挂单不误杀）；
          - 柜台 Order.csv 缺失或龄期 > _COUNTER_EXPORT_MAX_AGE_S ⇒ 本轮禁判并计数
            （防线二：回读平面断了不能反推"柜台没收到"，这正是 09-23"发得出、收不回"的坑）；
          - 超 `phantom_grace_s` 仍未收录 ⇒ REJECTED + error 日志 + alert_sink 外发 + 计数，
            并由紧随其后的 _observe_terminal_orders 落 execution_report 台账
            （=丢弃路径变响：台账上看得见这张被丢的单，不再蒸发）。
        """
        now_ts = now_utc().timestamp()
        with self._lock:
            claims = dict(self._claims)
            pending_cancels = dict(self._cancel_inflight)
        if not claims and not pending_cancels:
            return

        export_age_s = self._counter_export_age_s(now_ts)
        # 防线二（禁误杀）：柜台回读平面断了不能反推"柜台没收到"⇒ 本轮禁判，只计数留痕
        if _counter_export_unjudged(export_age_s):
            judged: dict[str, float] = {}
            if claims:
                _note_export_unavailable(self._sync_counters, self._lock, self._env, export_age_s, len(claims))
        else:
            judged = claims

        confirmed, expired = _split_claims_by_counter_view(
            judged, self._mirror.get_orders(), now_ts, self._phantom_grace_s
        )

        # 判据→改判全程在**同一把锁的同一临界区**内（禁第二把锁，禁 check-then-act 撕裂）
        with self._lock:
            _clear_counter_visible_claims(confirmed, self._claims)
            dropped = _reject_unseen_expired_claims(
                expired, judged, self._claims, self._pairing_cache, self._sync_counters, now_ts
            )
            _sweep_terminal_cancel_inflight(self._pairing_cache, self._cancel_inflight)

        for remark, order_id, age_s in dropped:
            _logger.error(
                "隔夜单/柜台零收录拒单化（原静默丢弃路径）: env=%s order=%s remark=%s age=%.1fs "
                "宽限=%.1fs 柜台导出龄=%.1fs",
                self._env,
                order_id,
                remark,
                age_s,
                self._phantom_grace_s,
                export_age_s if export_age_s is not None else -1.0,
            )
            self._emit_alert(
                {
                    "event": "phantom_order_rejected",
                    "order_id": order_id,
                    "remark": remark,
                    "reason": f"客户端已声称但柜台零收录 {age_s:.0f}s（宽限 {self._phantom_grace_s:.0f}s）→ REJECTED",
                }
            )

    def _drain_deferred_cancels(self) -> None:
        """暂缓撤单补发闸（每轮同步跑一次，事件驱动于"柜台视图刷新之后"）

        为什么必须有这一步：`cancel_order` 挡在暂缓窗内只对**本进程已提交且无柜台凭证**
        的目标生效，而风控直通调用面（`risk_layer_orchestrator.KillSwitchBrokerAdapter.
        cancel_order`:390-392）拿到 False 后并不重试 ⇒ "挡下即蒸发"会变成新的静默洞。
        这里把 False 明确定义为**延后**而不是**放弃**：
          - 柜台一旦可见该 remark（说明单子真在柜台）⇒ 立即补发；
          - 或暂缓窗已到（声称仍未销案）⇒ 立即补发（宁多撤一次空单，不可漏撤真单）；
          - 目标已终态（成交/已撤/拒单）⇒ 销案不补发，计数留痕。
        补发在锁外调用 cancel_order（其内部自有短临界区），本方法不持锁做文件/网络 I/O。
        """
        with self._lock:
            pending = dict(self._cancel_pending)
            claims = dict(self._claims)
        if not pending:
            return
        now_ts = now_utc().timestamp()
        visible = self._mirror.get_orders()
        for remark, local_order_id in pending.items():
            cached = self._pairing_cache.get(remark) or self._pairing_cache.get(local_order_id)
            if cached is not None and cached.status in _TERMINAL_STATUSES:
                with self._lock:
                    self._cancel_pending.pop(remark, None)
                    self._sync_counters["cancel_deferred_dropped"] += 1
                _logger.info(
                    "暂缓撤单无需补发（目标已终态 %s）: env=%s remark=%s",
                    cached.status.value,
                    self._env,
                    remark,
                )
                continue
            claimed_at = claims.get(remark)
            fire_now = remark in visible or claimed_at is None or (now_ts - claimed_at) >= self._cancel_hold_s
            if not fire_now:
                continue
            with self._lock:
                self._cancel_pending.pop(remark, None)
                self._sync_counters["cancel_deferred_fired"] += 1
            _logger.warning(
                "暂缓撤单补发: env=%s target=%s remark=%s 原因=%s",
                self._env,
                local_order_id,
                remark,
                "柜台已收录该委托" if remark in visible else "暂缓窗已到",
            )
            try:
                self.cancel_order(local_order_id)
            except Exception as exc:  # noqa: BLE001 — 补发失败不得杀同步线程，但必须留痕
                _logger.error(
                    "暂缓撤单补发失败（下一轮不再自动重试，需人工介入）: env=%s target=%s error=%r",
                    self._env,
                    local_order_id,
                    exc,
                )
                self._emit_alert(
                    {
                        "event": "deferred_cancel_failed",
                        "order_id": local_order_id,
                        "remark": remark,
                        "reason": f"暂缓撤单补发失败: {exc!r}",
                    }
                )

    def _emit_alert(self, payload: dict) -> None:
        """告警外发（域内既有约定：未注入=仅日志；注入后异常吞没，告警不得打断主链）"""
        if self._alert_sink is None:
            return
        try:
            self._alert_sink({**payload, "env": self._env, "broker_id": self.broker_id})
        except Exception as exc:  # noqa: BLE001 — 与 eod_reconciliation/alt_source_health_manager 同口径
            _logger.exception("alert_sink 告警外发失败（已吞没）: %r", exc)

    def bridge_diagnostics(self) -> dict:
        """TRD-A10 取证读面：未销案声称 / 在途撤单 / 静默类计数（健康检查与测试共用一口径）"""
        with self._lock:
            return {
                "unconfirmed_claims": sorted(self._claims),
                "cancel_inflight": dict(self._cancel_inflight),
                "cancel_pending": dict(self._cancel_pending),
                "sync_counters": dict(self._sync_counters),
                "phantom_grace_s": self._phantom_grace_s,
                "cancel_hold_s": self._cancel_hold_s,
            }

    def _dispatch_fill(self, fill: Fill) -> None:
        """成交回调扇出（remark 解析回本地 order_id，下游 OM 按其自己的 order_id 索引配对）"""
        local_id = self._remark_to_order_id.get(fill.order_id)
        if local_id and local_id != fill.order_id:
            fill = replace(fill, order_id=local_id)  # Fill 为 frozen dataclass
        for cb in self._fill_callbacks:
            try:
                cb(fill)
            except Exception as e:
                _logger.warning("成交回调异常: %r", e)


def _read_gbk_csv(path: Path) -> list[list[str]]:
    """GBK 容错读取官方导出 CSV（共享读，QMT 写端可能占用）"""
    try:
        with open(path, encoding="gbk", errors="replace", newline="") as f:
            return [row for row in csv.reader(f) if row]
    except OSError:
        return []


def _counter_export_unjudged(export_age_s: float | None) -> bool:
    """防线二判据：柜台 Order.csv 缺失（None）或龄期超可信窗 ⇒ 本轮禁判幽灵单。

    不可判定 ≠ "柜台零收录"——把回读平面故障反推成"柜台没收到"就是 09-23
    "发得出、收不回"的那条坑，故这里只回答"能不能判"，不改判任何单。
    """
    return export_age_s is None or export_age_s > _COUNTER_EXPORT_MAX_AGE_S


def _note_export_unavailable(
    counters: dict[str, int],
    lock: threading.Lock,
    env: str,
    export_age_s: float | None,
    unjudged_claims: int,
) -> None:
    """防线二留痕：禁判计数（锁内）+ 告警日志（锁外），禁静默。"""
    with lock:
        counters["counter_export_unavailable"] += 1
    _logger.warning(
        "柜台导出缺失/超龄（age=%s），幽灵单判定暂停 env=%s 未销案声称=%d",
        "None" if export_age_s is None else f"{export_age_s:.1f}s",
        env,
        unjudged_claims,
    )


def _split_claims_by_counter_view(
    judged: dict[str, float],
    visible: dict[str, dict],
    now_ts: float,
    grace_s: float,
) -> tuple[list[str], list[str]]:
    """按最新柜台视图把未销案声称分成（柜台已见=销案）/（超窗零收录=拒单）两组。

    Args:
        judged: remark → 认领时刻（本轮**可判**的声称；禁判时为空 dict）。
        visible: 柜台镜像当前挂单视图（remark → 记录）。
        now_ts: 本轮对账时点（epoch 秒）。
        grace_s: 幽灵单确认窗 `phantom_grace_s`。

    Returns:
        (confirmed, expired)——两组都是"本轮结论"，改判由调用方在锁内执行。
    """
    confirmed = [remark for remark in judged if remark in visible]
    expired = [
        remark
        for remark, claimed_at in judged.items()
        if remark not in visible and now_ts - claimed_at >= grace_s
    ]
    return confirmed, expired


def _clear_counter_visible_claims(confirmed: list[str], claim_ledger: dict[str, float]) -> None:
    """防线一落地：柜台镜像一旦出现该 remark ⇒ 立即销案（真挂单永不误杀）。"""
    for remark in confirmed:
        claim_ledger.pop(remark, None)


def _reject_unseen_expired_claims(
    expired: list[str],
    judged: dict[str, float],
    claim_ledger: dict[str, float],
    order_cache: dict[str, Order],
    counters: dict[str, int],
    now_ts: float,
) -> list[tuple[str, str, float]]:
    """超窗仍零收录 ⇒ 显式 REJECTED（丢弃路径变响），返回待锁外留痕的明细。

    只在锁内调用：销案 + 改判 + 计数必须与 `_split_claims_by_counter_view` 的
    判据同处一个临界区，否则并发 submit/cancel 会把"已判"和"已改"撕开。

    Returns:
        [(remark, order_id, age_s)]——order_id 查无此单时为 "-"（进程重启面，留痕不静默）。
    """
    dropped: list[tuple[str, str, float]] = []
    for remark in expired:
        claim_ledger.pop(remark, None)
        order = order_cache.get(remark)
        counters["phantom_rejected"] += 1
        age_s = now_ts - judged[remark]
        if order is not None and order.status not in _TERMINAL_STATUSES:
            order.status = OrderStatus.REJECTED
            order.updated_at = now_utc()
            dropped.append((remark, order.order_id, age_s))
        else:
            dropped.append((remark, order.order_id if order is not None else "-", age_s))
    return dropped


def _sweep_terminal_cancel_inflight(order_cache: dict[str, Order], inflight: dict[str, str]) -> None:
    """撤单在途标记自清洁：目标已终态就不再挡后续撤单。"""
    for remark in list(inflight):
        cached = order_cache.get(remark)
        if cached is not None and cached.status in _TERMINAL_STATUSES:
            inflight.pop(remark, None)


def _scan_instruction_states(
    orders_file: Path,
    order_cache: dict[str, Order],
    counters: dict[str, int] | None = None,
    seen_unmatched: set[str] | None = None,
) -> None:
    """扫描指令文件状态机标记：#FAIL → REJECTED（#DONE 由镜像经柜台确认推进）

    TRD-A10 缺陷① 补充语义（禁静默）：
      - `#DONE` 是客户端**自盖**标记，不是柜台收录凭证 ⇒ 订单继续挂在未销案声称台账上，
        由 `_reconcile_unconfirmed_claims` 判幽灵单（旧写法直接无视 #DONE，等价于
        "客户端说完成就算完成"，正是隔夜单停在 SUBMITTED 却零痕迹的那条路）；
      - 标记指向的 order_id 查无此单（进程重启/缓存丢失）→ error 留痕 + 计数，
        每轮重扫同一 order_id 只记一次（seen_unmatched 去噪，禁日志风暴）。
    """
    if not orders_file.exists():
        return
    try:
        with open(orders_file, encoding="ascii", errors="replace") as f:
            lines = f.readlines()
    except OSError as exc:
        _logger.error("指令文件读取失败，本轮状态标记全部丢失（不静默）: %s error=%r", orders_file, exc)
        if counters is not None:
            counters["mark_scan_failed"] = counters.get("mark_scan_failed", 0) + 1
        return
    for raw in lines:
        line = raw.strip()
        if not line.startswith("#"):
            continue
        parts = line.split(" ", 1)
        if len(parts) != 2:
            continue
        mark, rest = parts
        order_id = rest.split(",", 1)[0]
        cached = order_cache.get(order_id)
        if cached is None:
            if seen_unmatched is None:
                continue  # 无状态调用方（巡检/工具）：不去噪就不逐轮刷日志，计数交给有状态调用方
            if order_id not in seen_unmatched:
                seen_unmatched.add(order_id)
                if counters is not None:
                    counters["mark_unmatched"] = counters.get("mark_unmatched", 0) + 1
                _logger.error(
                    "指令状态标记 %s 查无本地订单（重启/缓存丢失，该单终态无人认领）: %s",
                    mark,
                    order_id,
                )
            continue
        if mark == "#FAIL" and cached.status not in _TERMINAL_STATUSES:
            cached.status = OrderStatus.REJECTED
            cached.updated_at = now_utc()
            _logger.warning("指令失败标记: %s -> REJECTED", order_id)


def _read_new_acks(ack_file: Path, offset: int, counters: dict[str, int] | None = None) -> tuple[list[FileBridgeAck], int]:
    """增量读取回执文件，返回 (新回执列表, 新偏移)

    TRD-A10 禁静默两条：
      - OSError（QMT 写端持独占句柄是常态，PermissionError ⊂ OSError）旧写法
        `return [], offset` 零痕迹=该轮回执全丢且无人知道 → 现在 error 留痕 + 计数；
      - 文件缩短（客户端重启重写/轮转）时 offset 永超 EOF ⇒ 此后所有回执**永久**静默丢弃
        （同 bug 的修法早已存在于 scripts/bridge_monitor_check.ps1 巡检侧，正码无防=双标）
        → 回植：offset 超界即重置 0 并留痕。
    """
    if not ack_file.exists():
        return [], offset
    try:
        size = ack_file.stat().st_size
    except OSError:
        return [], offset
    if offset > size:
        _logger.error(
            "回执文件缩短（offset=%d > size=%d，客户端重写/轮转）→ 偏移重置 0，重放新增部分",
            offset,
            size,
        )
        offset = 0
    try:
        with open(ack_file, encoding="ascii", errors="replace") as f:
            f.seek(offset)
            new_lines = f.readlines()
            new_offset = f.tell()
    except OSError as exc:
        if counters is not None:
            counters["ack_read_failed"] = counters.get("ack_read_failed", 0) + 1
        _logger.error("回执文件读取失败，本轮回执丢失（不静默）: %s error=%r", ack_file, exc)
        return [], offset
    acks: list[FileBridgeAck] = []
    for raw in new_lines:
        line = raw.strip()
        if not line:
            continue
        parts = line.split(",", 2)
        if len(parts) < 2:
            _logger.error("回执行格式不合规（列数<2）已丢弃: %r", line)
            continue
        acks.append(
            FileBridgeAck(
                order_id=parts[0],
                status=parts[1],
                detail=parts[2] if len(parts) > 2 else "",
            )
        )
    return acks, new_offset


def _apply_acks(
    acks: list[FileBridgeAck],
    order_cache: dict[str, Order],
    counters: dict[str, int] | None = None,
    cancel_inflight: dict[str, str] | None = None,
) -> None:
    """回执应用到订单缓存：FAIL → REJECTED

    TRD-A10 缺陷①：`SENT/CONFIRMED/CANCEL_SENT/RETRY` 是客户端**声称**，不是柜台收录凭证，
    绝不据此推进终态（旧写法对这几类一个都不消费=连日志都没有）；
    查无此单的 ack 必须留痕计数，不再 `continue` 吞掉。
    撤单回执（指令 id 形如 `C<本地 order_id>`）按目标单消费：销在途撤单标记，
    使后续撤单尝试不被"已在途"幂等永久挡住。
    """
    for ack in acks:
        cached = order_cache.get(ack.order_id)
        if cached is None and len(ack.order_id) > 1 and ack.order_id[0] == "C":
            target = order_cache.get(ack.order_id[1:])
            if target is not None:
                if cancel_inflight is not None:
                    cancel_inflight.pop(target.idempotency_key, None)
                _logger.info(
                    "撤单回执消费: ack=%s status=%s target_remark=%s detail=%s",
                    ack.order_id,
                    ack.status,
                    target.idempotency_key,
                    ack.detail,
                )
                continue
        if cached is None:
            if counters is not None:
                counters["ack_unmatched"] = counters.get("ack_unmatched", 0) + 1
            _logger.error(
                "回执查无本地订单（缓存丢失/重启/非本进程单）: order=%s status=%s detail=%s",
                ack.order_id,
                ack.status,
                ack.detail,
            )
            continue
        if ack.status in _CLAIM_ACK_STATUSES:
            _logger.info(
                "回执=客户端声称（不等于柜台收录，继续挂未销案台账）: order=%s status=%s detail=%s",
                ack.order_id,
                ack.status,
                ack.detail,
            )
            continue
        if ack.status == "FAIL" and cached.status not in _TERMINAL_STATUSES:
            cached.status = OrderStatus.REJECTED
            cached.updated_at = now_utc()
            _logger.warning("回执FAIL: %s detail=%s", ack.order_id, ack.detail)


def check_broker_health(broker: QmtFileBridgeBroker) -> dict:
    """Broker 健康检查（前端监控数据源，模块级函数防 God Class）

    Returns:
        dict: {component, type, ok, level(ok/degraded/down), env, connected,
               sync_thread_alive, export_age_seconds, counter, detail}
    """
    now = now_utc().timestamp()
    result: dict = {
        "component": f"broker_{broker._env}",
        "type": "broker",
        "ok": False,
        "level": "down",
        "env": broker._env,
        "connected": broker._connected,
        "sync_thread_alive": bool(broker._sync_thread and broker._sync_thread.is_alive()),
    }
    if not broker._connected:
        result["detail"] = "未连接（connect() 未调用或失败）"
        return result

    # 官方导出文件新鲜度（QMT 自动导出应秒级更新）
    exports: dict[str, float | None] = {}
    worst_age: float | None = None
    for name in ("Order.csv", "PositionStatics.csv", "Account.csv", "Deal.csv"):
        p = broker._stock_dir / name
        if p.exists():
            age = now - p.stat().st_mtime
            exports[name] = round(age, 1)
            worst_age = age if worst_age is None else max(worst_age, age)
        else:
            exports[name] = None
    result["export_age_seconds"] = exports

    # 柜台镜像概览
    diag = broker.bridge_diagnostics()
    counters = diag["sync_counters"]
    result["counter"] = {
        "pending_orders": len(broker._mirror.get_orders()),
        "positions": len(broker._mirror.get_positions()),
        "available_cash": str(broker._mirror.available_cash()),
        # TRD-A10：把"静默类"问题变成前端可读量（丢弃/吞回执/暂缓撤单不再只进日志）
        "unconfirmed_claims": len(diag["unconfirmed_claims"]),
        "unconfirmed_claim_remarks": diag["unconfirmed_claims"],
        "cancel_inflight": len(diag["cancel_inflight"]),
        "silently_dropped_total": counters.get("phantom_rejected", 0),
        "cancel_held_total": counters.get("cancel_held", 0),
        "cancel_guard_paused_total": counters.get("cancel_guard_paused", 0),
        "unmatched_ack_total": counters.get("ack_unmatched", 0),
        "unmatched_mark_total": counters.get("mark_unmatched", 0),
        "phantom_check_paused_rounds": counters.get("counter_export_unavailable", 0),
    }

    # 等级判定
    if not result["sync_thread_alive"]:
        result["level"] = "degraded"
        result["detail"] = "同步线程已停止"
    elif worst_age is None:
        result["level"] = "degraded"
        result["detail"] = "官方导出文件全部缺失（QMT 自动导出未配置？）"
    elif worst_age > 60:
        result["level"] = "degraded"
        result["detail"] = f"官方导出 {worst_age:.0f}s 未更新"
    else:
        result["ok"] = True
        result["level"] = "ok"
    return result


def _normalize_symbol(code: str, market: str) -> str:
    """证券代码标准化为 510300.SH 形态"""
    code = code.strip()
    if "." in code:
        return code
    market = market.strip().upper()
    if market in ("SH", "SZ", "BJ"):
        return f"{code}.{market}"
    return code


def _to_decimal(s: str) -> Decimal:
    """安全 Decimal 转换，失败返回 0"""
    try:
        return Decimal(s.strip().replace(",", ""))
    except (InvalidOperation, ValueError, AttributeError):
        return Decimal("0")


def _to_int(s: str) -> int:
    """安全 int 转换（容忍 float 字符串如 '1888.400'），失败返回 0"""
    try:
        return int(float(s.strip()))
    except (ValueError, OverflowError, AttributeError):
        return 0
