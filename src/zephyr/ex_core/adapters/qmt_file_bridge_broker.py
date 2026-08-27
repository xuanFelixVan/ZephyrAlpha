# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
# [MODULE] zephyr.ex_core.adapters.qmt_file_bridge_broker
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.trading.trading_contracts.broker_interface; zephyr.ex_core.board_lot; zephyr.ex_core.price_cage; zephyr.shared.contracts.order; zephyr.shared.contracts.position
# [CONSUMERS] zephyr.ex_core.order_manager
# [STARTUP] manual
# [MATURITY] draft
# [INVARIANTS] 文件状态机幂等(#SENDING→#DONE); 3秒轮询柜台同步; 双实例物理隔离(env=real/sim)
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
  - 通过指令CSV文件与沙箱内哑执行器(v14)双向通信
  - submit_order 写入指令文件返回本地 order_id，broker_order_id 异步回填
  - 3秒轮询官方导出 CSV，同步柜台状态/成交/持仓
  - 双实例物理隔离：env="real"(实盘) / env="sim"(模拟)

约束:
  - 无实时连接，纯文件轮询
  - 无实时盘口，预校验降级为无盘口模式
  - 算法单排队在 LocalOrderQueue，本类只负责单笔下发的文件写入
  - 柜台全量镜像由 CounterStateMirror 承担（单一职责，本类委托）

SSoT: docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
"""

from __future__ import annotations

import csv
import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Final

from zephyr.ex_core.board_lot import get_board_lot_rule
from zephyr.ex_core.price_cage import CageStatus, check_price_cage
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order, OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.position import PositionSnapshot
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


class CounterStateMirror:
    """柜台全量镜像（2026-08-26 新增，2026-08-27 自 Broker 拆出）

    大脑必须知道 QMT 里所有状态，不只是本进程提交的订单：
    所有挂单（含手动/其他终端）、持仓（可用/冻结）、资金（可用/冻结）、当日成交。
    数据源：QMT 官方自动导出 Stock/*.csv（GBK）。
    """

    def __init__(self, stock_dir: Path):
        self._stock_dir = stock_dir
        self._orders: dict[str, dict] = {}       # remark -> {sysid, status, symbol, price, qty, filled_qty, side}
        self._positions: dict[str, dict] = {}    # bare_symbol -> {qty, available_qty, frozen_qty, cost, market_value}
        self._account: dict[str, Decimal] = {}   # {total, available, frozen, market_value}
        self._deals: list[dict] = []             # 当日成交（最新 100 条）
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
        return sum(
            1 for o in self._orders.values()
            if o["symbol"].split(".")[0] == bare and o["side"] == side
        )

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
                    OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED,
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

            self._deals.append({
                "deal_id": deal_id,
                "remark": remark,
                "symbol": symbol,
                "side": side,
                "qty": qty,
                "price": price,
                "time": f"{row[19].strip()} {row[20].strip()}",
            })
            if len(self._deals) > 100:
                self._deals = self._deals[-100:]

            # 更新本进程订单
            cached = order_cache.get(remark)
            strategy_id = cached.strategy_id if cached else "qmt_file_bridge"
            if cached is not None:
                cached.filled_quantity += Decimal(qty)
                cached.avg_fill_price = price
                cached.status = (
                    OrderStatus.FILLED
                    if cached.filled_quantity >= cached.quantity
                    else OrderStatus.PARTIAL
                )
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
        max_retry: int = 3,
    ):
        """初始化 QMT 文件桥 Broker

        Args:
            env: 环境标识 "real"(实盘) 或 "sim"(模拟)
            sync_interval: 柜台同步轮询间隔（秒），默认 3 秒
            max_retry: #SENDING 超时重试最大次数，默认 3 次
        """
        if env not in self.ENV_CONFIG:
            raise QmtFileBridgeError(f"非法环境标识: {env}，必须是 'real' 或 'sim'")

        self._env = env
        self._config = self.ENV_CONFIG[env]
        self._sync_interval = sync_interval
        self._max_retry = max_retry

        # 文件路径
        self._bridge_dir = Path(self._config["bridge_dir"])
        self._orders_file = Path(self._config["orders_file"])
        self._ack_file = Path(self._config["ack_file"])
        self._stock_dir = Path(self._config["stock_dir"])

        # 状态缓存
        self._order_cache: dict[str, Order] = {}
        self._idempotency_map: dict[str, str] = {}  # idempotency_key -> order_id
        self._connected = False
        self._lock = threading.Lock()

        # 同步线程
        self._sync_thread: threading.Thread | None = None
        self._sync_stop = threading.Event()

        # 成交回调
        self._fill_callbacks: list[FillCallback] = []
        # 回执文件读取偏移
        self._ack_offset = 0

        # 柜台全量镜像（单一职责拆出，本类委托）
        self._mirror = CounterStateMirror(self._stock_dir)

    @property
    def broker_id(self) -> str:
        return f"qmt_{self._env}"

    def connect(self) -> bool:
        """校验桥接目录可读写并启动同步线程"""
        with self._lock:
            try:
                # 确保目录存在
                self._bridge_dir.mkdir(parents=True, exist_ok=True)
                self._stock_dir.mkdir(parents=True, exist_ok=True)

                # 确保指令文件存在（写表头）
                if not self._orders_file.exists():
                    self._orders_file.write_text(
                        "order_id,action,symbol,side,qty,pricetype,price\n", encoding="ascii"
                    )

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
                    self._env, self._bridge_dir,
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
        """写入指令文件，返回本地 order_id（broker_order_id 异步回填）"""
        # 幂等拦截
        if order.idempotency_key in self._idempotency_map:
            existing_id = self._idempotency_map[order.idempotency_key]
            _logger.info("幂等命中 idem=%s -> %s", order.idempotency_key, existing_id)
            return existing_id

        # A股约束校验：整手
        rule = get_board_lot_rule(order.symbol)
        qty = int(order.quantity)
        if order.side == OrderSide.BUY and qty < rule.min_unit:
            raise QmtFileBridgeError(
                f"数量不合法: 买入 {qty} 股低于最小申报单位 {rule.min_unit}（{order.symbol}）"
            )

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
                    order.symbol, order.side.value, order.limit_price, cage.clamped_price,
                )
            price = float(cage.clamped_price)

        inst = FileBridgeInstruction(
            order_id=order.idempotency_key,
            action="order",
            symbol=order.symbol,
            side="buy" if order.side == OrderSide.BUY else "sell",
            qty=qty,
            pricetype=pricetype,
            price=price,
        )
        self._append_instruction(inst)

        # 本地缓存
        order.status = OrderStatus.SUBMITTED
        order.updated_at = now_utc()
        with self._lock:
            self._order_cache[order.order_id] = order
            self._idempotency_map[order.idempotency_key] = order.order_id

        _logger.info("指令写入 %s: %s %s %s x%d %s", self._env, inst.order_id, inst.symbol, inst.side, qty, pricetype)
        return order.order_id

    def cancel_order(self, broker_order_id: str) -> bool:
        """写入撤单指令（仅表示指令已写入，不表示柜台已撤）"""
        inst = FileBridgeInstruction(
            order_id=f"C{broker_order_id}",
            action="cancel",
            symbol=broker_order_id,  # 目标订单 remark
            side="",
            qty=0,
            pricetype="",
            price=0.0,
        )
        self._append_instruction(inst)
        _logger.info("撤单指令写入 %s: target=%s", self._env, broker_order_id)
        return True

    def query_order(self, broker_order_id: str) -> Order | None:
        """本地缓存查询（含柜台同步推进后的最新状态）"""
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
            self._env, len(self._fill_callbacks),
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
        """追加指令行（原子语义：整行一次写入）"""
        line = (
            f"{inst.order_id},{inst.action},{inst.symbol},{inst.side},"
            f"{inst.qty},{inst.pricetype},{inst.price}\n"
        )
        with self._lock:
            with open(self._orders_file, "a", encoding="ascii", newline="") as f:
                f.write(line)

    # ── 内部：同步线程 ──

    def _sync_loop(self) -> None:
        while not self._sync_stop.is_set():
            try:
                self._sync_local_channel()
                self._mirror.sync_all(self._order_cache, self._dispatch_fill)
            except Exception as e:  # 同步失败不杀线程，下轮重试
                _logger.warning("柜台同步异常(env=%s): %r", self._env, e)
            self._sync_stop.wait(self._sync_interval)

    def _sync_local_channel(self) -> None:
        """扫描指令文件状态标记 + 增量读取回执文件"""
        _scan_instruction_states(self._orders_file, self._order_cache)
        acks, self._ack_offset = _read_new_acks(self._ack_file, self._ack_offset)
        _apply_acks(acks, self._order_cache)

    def _dispatch_fill(self, fill: Fill) -> None:
        """成交回调扇出"""
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


def _scan_instruction_states(orders_file: Path, order_cache: dict[str, Order]) -> None:
    """扫描指令文件状态机标记：#FAIL → REJECTED（#DONE 由镜像经柜台确认推进）"""
    if not orders_file.exists():
        return
    try:
        with open(orders_file, encoding="ascii", errors="replace") as f:
            lines = f.readlines()
    except OSError:
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
            continue
        if mark == "#FAIL" and cached.status not in (
            OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED,
        ):
            cached.status = OrderStatus.REJECTED
            cached.updated_at = now_utc()
            _logger.warning("指令失败标记: %s -> REJECTED", order_id)


def _read_new_acks(ack_file: Path, offset: int) -> tuple[list[FileBridgeAck], int]:
    """增量读取回执文件，返回 (新回执列表, 新偏移)"""
    if not ack_file.exists():
        return [], offset
    try:
        with open(ack_file, encoding="ascii", errors="replace") as f:
            f.seek(offset)
            new_lines = f.readlines()
            new_offset = f.tell()
    except OSError:
        return [], offset
    acks: list[FileBridgeAck] = []
    for raw in new_lines:
        line = raw.strip()
        if not line:
            continue
        parts = line.split(",", 2)
        if len(parts) < 2:
            continue
        acks.append(FileBridgeAck(
            order_id=parts[0],
            status=parts[1],
            detail=parts[2] if len(parts) > 2 else "",
        ))
    return acks, new_offset


def _apply_acks(acks: list[FileBridgeAck], order_cache: dict[str, Order]) -> None:
    """回执应用到订单缓存：FAIL → REJECTED"""
    for ack in acks:
        cached = order_cache.get(ack.order_id)
        if cached is None:
            continue
        if ack.status == "FAIL" and cached.status not in (
            OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED,
        ):
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
        "sync_thread_alive": bool(
            broker._sync_thread and broker._sync_thread.is_alive()
        ),
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
    result["counter"] = {
        "pending_orders": len(broker._mirror.get_orders()),
        "positions": len(broker._mirror.get_positions()),
        "available_cash": str(broker._mirror.available_cash()),
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
