# [BLUEPRINT] MOD-EX-001 | docs/03_modules/_domain_execution_core/fill_handler/blueprint.md
# [MODULE] zephyr.ex_core.fill_handler
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.shared.contracts.fill; zephyr.shared.contracts.order; zephyr.shared.contracts.enums.order_enums; zephyr.shared.state_store
# [CONSUMERS] D_EX_CORE域内模块 ; Fill Processor (D-EX-CORE-08, 阶段2)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] fill_id幂等; filled_quantity单调递增; Decimal全程计算; FillSummary不可变; 状态转换遵循VALID_TRANSITIONS; 配置dedup_store时去重集持久化(重启存活)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DuplicateFillError(ZA-EX-001-01); InvalidFillError(ZA-EX-001-02); OrderNotFoundError(ZA-EX-001-03)
# [TESTS] tests/ex_core/test_fill_handler.py; tests/ex_core/test_fill_id_dedup_persistence.py
# [A_module] module_id=MOD-EX-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_EX_CORE — Fill Handler (部分成交处理器)

D_EX_CORE 域的成交回报处理器——接收 Fill（CTR-005），累积到对应 Order（CTR-004），
更新已成交数量、加权均价、佣金，并驱动成交相关状态转换（SUBMITTED→PARTIAL→FILLED）。

从 OrderManager._on_fill() 拆出的独立模块，提供更丰富的成交查询能力
（FillSummary / 剩余量 / 成交历史）和 fill_id 幂等保证。

设计真源: D-EX-CORE-48 "部分成交状态更新与后续处理"
蓝图: docs/03_modules/_domain_execution_core/fill_handler/blueprint.md
SSoT: depgraph MOD-EX-001

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 成交回报 Fill（CTR-005）
#   fields: fill_id + order_id + fill_price + filled_quantity + commission + fill_timestamp
#   code: process_fill(fill, order) L143
# - id: I2
#   name: 委托订单 Order（CTR-004 可变）
#   fields: order_id + quantity + filled_quantity + avg_fill_price + status
#   code: process_fill(fill, order) L143
# 层: 算法
# - id: A1
#   name_zh: ① 成交处理主流程
#   name_en: FillHandler.process_fill
#   intro: 校验+幂等拦截后累积成交量、算加权均价、驱动状态转换并生成汇总
#   desc: 校验数量>0与order_id匹配 → fill_id幂等拦截 → new_filled=old+fill.qty → new_avg=(old_avg×old_filled+price×qty)/new_filled → 按累积量驱动SUBMITTED→PARTIAL→FILLED → 汇总佣金构建FillSummary → 回调通知
#   inputs: I1 I2
#   outputs: FillSummary + Order就地更新
#   invariant: fill_id幂等；filled_quantity单调递增；Decimal全程计算
# - id: A2
#   name_zh: ② 成交状态转换
#   name_en: FillHandler._try_transition
#   intro: 按_FILL_TRANSITIONS表尝试状态跳转，非法转换只记警告不抛异常
#   desc: 查 _FILL_TRANSITIONS 合法路径（PENDING不接受成交；SUBMITTED→PARTIAL/FILLED；PARTIAL→FILLED），非法仅 log 不阻断
#   inputs: A1
#   outputs: order.status 更新
#   invariant: 状态转换遵循 _FILL_TRANSITIONS 合法路径
# - id: A3
#   name_zh: ③ 成交查询
#   name_en: get_summary / get_fills / get_remaining
#   intro: 按order_id查成交汇总、成交历史和剩余未成交量
#   desc: 内存字典 _summaries/_fills 直查，无记录返回 None
#   inputs: A1
#   outputs: FillSummary / list[Fill] / Decimal
# 层: 输出
# - id: O1
#   name_zh: 成交汇总 FillSummary
#   name_en: FillSummary
#   intro: 总量/已成交/剩余/加权均价/笔数/总佣金/是否完成的不可变快照
#   invariant: frozen 不可变；remaining=max(total-filled,0)
#   downstream: 聚合根管理器 MOD-EX-049；Fill Processor（D-EX-CORE-08 阶段2）
# - id: O2
#   name_zh: 订单就地更新 Order
#   name_en: Order（就地修改）
#   intro: filled_quantity/avg_fill_price/status/updated_at 被就地更新的订单对象
#   downstream: D_EX_CORE域内模块
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A1 --> A3
# A1 --> O1
# A1 --> O2
# A3 --> O1
"""

from __future__ import annotations

import json
import logging
import threading
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Final

from zephyr.shared.contracts.enums.order_enums import OrderStatus
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order
from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.state_store import AppendOnlyDedupSet

logger = logging.getLogger(__name__)

__all__: Final = [
    "FillSummary",
    "FillHandler",
    "DuplicateFillError",
    "InvalidFillError",
    "OrderNotFoundError",
]


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class DuplicateFillError(ZephyrBaseError):
    """重复处理同一 fill_id 的成交（幂等拦截，非致命）。"""

    error_code = "ZA-EX-001-01"


class InvalidFillError(ZephyrBaseError):
    """成交回报数据非法（零数量/负数等）。"""

    error_code = "ZA-EX-001-02"


class OrderNotFoundError(ZephyrBaseError):
    """成交回报对应的订单不存在。"""

    error_code = "ZA-EX-001-03"


# ──────────────────────────────────────────────────────────────────────────────
# Fill JSONL 落盘序列化（56号文 G3：进程退出不丢当日 Fill）
# ──────────────────────────────────────────────────────────────────────────────


def _fill_to_json_dict(fill: Fill) -> dict:
    """Fill(CTR-005) → JSON 可序列化 dict（Decimal→str，datetime→ISO8601）。

    trace_context 不落盘（可选分析上下文字段，对账链路不消费，省去嵌套序列化）。
    """
    return {
        "fill_id": fill.fill_id,
        "order_id": fill.order_id,
        "strategy_id": fill.strategy_id,
        "symbol": fill.symbol,
        "fill_price": str(fill.fill_price),
        "filled_quantity": str(fill.filled_quantity),
        "commission": str(fill.commission),
        "fill_timestamp": fill.fill_timestamp.isoformat(),
        "idempotency_key": fill.idempotency_key,
        "broker_fill_id": fill.broker_fill_id,
        "slippage": str(fill.slippage) if fill.slippage is not None else None,
        "schema_version": fill.schema_version,
    }


def _fill_from_json_dict(d: dict) -> Fill:
    """JSON dict → Fill(CTR-005)（_fill_to_json_dict 逆变换）。"""
    slippage = d.get("slippage")
    return Fill(
        fill_id=d["fill_id"],
        order_id=d["order_id"],
        strategy_id=d["strategy_id"],
        symbol=d["symbol"],
        fill_price=Decimal(d["fill_price"]),
        filled_quantity=Decimal(d["filled_quantity"]),
        commission=Decimal(d.get("commission", "0")),
        fill_timestamp=datetime.fromisoformat(d["fill_timestamp"]),
        idempotency_key=d["idempotency_key"],
        broker_fill_id=d.get("broker_fill_id"),
        slippage=Decimal(slippage) if slippage is not None else None,
        schema_version=d.get("schema_version", "1.0"),
        trace_context=None,
    )


def _trade_date_of(fill: Fill) -> str:
    """成交的交易日（本地时区 YYYYMMDD，A股交易日=券商终端本地日期口径）。"""
    return fill.fill_timestamp.astimezone().strftime("%Y%m%d")


# ──────────────────────────────────────────────────────────────────────────────
# 成交相关状态转换规则（与 OrderManager.VALID_TRANSITIONS 对齐）
# ──────────────────────────────────────────────────────────────────────────────

_FILL_TRANSITIONS: Final[dict[OrderStatus, set[OrderStatus]]] = {
    OrderStatus.PENDING: set(),  # PENDING 不接受成交（需先 SUBMITTED）
    OrderStatus.SUBMITTED: {OrderStatus.PARTIAL, OrderStatus.FILLED},
    OrderStatus.PARTIAL: {OrderStatus.FILLED},  # PARTIAL→PARTIAL 无需转换
    OrderStatus.FILLED: set(),
    OrderStatus.CANCELLED: set(),
    OrderStatus.REJECTED: set(),
    OrderStatus.EXPIRED: set(),
}


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型 (frozen 不可变)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class FillSummary:
    """成交汇总——不可变快照。

    描述一笔订单的成交状态：总量、已成交、剩余、均价、笔数、佣金。
    每次 process_fill 后生成新实例。
    """

    order_id: str
    total_quantity: Decimal
    filled_quantity: Decimal
    remaining_quantity: Decimal
    avg_fill_price: Decimal | None
    fill_count: int
    total_commission: Decimal
    is_complete: bool
    last_fill_timestamp: datetime | None


# ──────────────────────────────────────────────────────────────────────────────
# FillHandler
# ──────────────────────────────────────────────────────────────────────────────


class FillHandler:
    """部分成交处理器——Fill 累积+加权均价+状态转换+查询。

    用法::

        handler = FillHandler()
        summary = handler.process_fill(fill, order)
        # order.filled_quantity / avg_fill_price 已更新
        # summary 包含完整成交汇总
        remaining = handler.get_remaining(order.order_id)
    """

    def __init__(
        self,
        dedup_store: AppendOnlyDedupSet | None = None,
        fills_dir: str | Path | None = None,
    ) -> None:
        """初始化成交处理器。

        Args:
            dedup_store: fill_id 持久化去重集（#ARCH-QUANT-002，Qwen P0-2①）。
                提供时幂等拦截集由 append-only 文件承载，进程重启后
                同一 fill_id 重放仍被拦截（不再"重启即去重失效"）。
                None=纯内存 set（既有行为）。
            fills_dir: Fill JSONL 落盘目录（56号文 G3，与 AppendOnlyDedupSet
                同目录风格——调用方传 "data/fills" 风格相对/绝对路径）。
                提供时 process_fill 尾部把每笔 Fill 追加写入
                {fills_dir}/YYYYMMDD.jsonl（按成交日本地时区分文件），
                进程退出不丢当日 Fill（病根修复：_fills 原仅内存字典，
                重启后当日成交明细全失）。None=不落盘（既有行为）。
        """
        self._fills: dict[str, list[Fill]] = defaultdict(list)
        self._processed_fill_ids: set[str] | AppendOnlyDedupSet = dedup_store if dedup_store is not None else set()
        self._summaries: dict[str, FillSummary] = {}
        self._callbacks: list[Callable[[Fill, FillSummary], None]] = []
        # 幂等门原子化锁（AI-R3 复审 P2 治本）：纯内存 set 场景下
        # check-then-add 非原子，多线程同 fill_id 存在双入账窗口
        self._dedup_lock = threading.Lock()
        # Fill JSONL 落盘目录（None=不落盘）与追加写锁（多线程 append 防行交错）
        self._fills_dir: Path | None = Path(fills_dir) if fills_dir is not None else None
        self._persist_lock = threading.Lock()
        if self._fills_dir is not None:
            self._fills_dir.mkdir(parents=True, exist_ok=True)

    # ── 核心处理 ──────────────────────────────────────────────────────────

    def _claim_fill_id(self, fill_id: str) -> bool:
        """原子认领 fill_id（AI-R3 复审 P2 治本：消除 check-then-add 双入账窗口）。

        与 PositionTracker.apply_fill 同款模式——以去重集 add 返回值做单步门：
        持久化去重集场景 add 自身持锁原子；纯内存 set 场景用 _dedup_lock 串行。

        Returns:
            True=首次见到（已登记，调用方继续入账）；False=已处理（幂等拦截）。
        """
        if isinstance(self._processed_fill_ids, AppendOnlyDedupSet):
            return self._processed_fill_ids.add(fill_id)
        with self._dedup_lock:
            if fill_id in self._processed_fill_ids:
                return False
            self._processed_fill_ids.add(fill_id)
            return True

    def process_fill(self, fill: Fill, order: Order) -> FillSummary:
        """处理一笔成交——更新订单成交状态，返回成交汇总。

        幂等: 同一 fill_id 重复调用不会重复累积，返回上次缓存的 summary。
        状态转换: 根据累积量判断 SUBMITTED→PARTIAL / →FILLED。
        就地更新: order 对象的 filled_quantity / avg_fill_price / status / updated_at 被修改。

        Args:
            fill: 成交回报（CTR-005，不可变）。
            order: 委托指令（CTR-004，可变——就地更新）。

        Returns:
            FillSummary: 成交汇总快照。

        Raises:
            InvalidFillError: 成交数量 <= 0。
            OrderNotFoundError: fill.order_id 与 order.order_id 不匹配。
        """
        # ── 校验 ──
        if fill.filled_quantity <= 0:
            raise InvalidFillError(f"成交数量必须 > 0, 实际={fill.filled_quantity} (fill_id={fill.fill_id})")
        if fill.order_id != order.order_id:
            raise OrderNotFoundError(f"成交回报 order_id={fill.order_id} 与传入订单 order_id={order.order_id} 不匹配")

        # ── 幂等检查（原子单步门，AI-R3 复审 P2 治本）──
        # 认领即登记（at-most-once）：登记后入账前 crash 该 fill 视为已处理，
        # 与 PositionTracker.apply_fill 去重登记先行同语义——宁可少计不重复计
        if not self._claim_fill_id(fill.fill_id):
            logger.debug("幂等拦截: fill_id=%s 已处理，跳过", fill.fill_id)
            cached = self._summaries.get(order.order_id)
            if cached is not None:
                return cached
            # 持久化去重集场景（Qwen P0-2①）：重启后重放——fill_id 见过但
            # 本进程无缓存 summary。按订单当前状态构建只读 summary 返回，
            # 绝不重复累积（否则重启重放=重复记账）。
            logger.warning(
                "幂等拦截(重启后重放): fill_id=%s 已处理, 按订单当前状态返回 summary",
                fill.fill_id,
            )
            current_filled = order.filled_quantity or Decimal("0")
            total_qty = order.quantity
            return FillSummary(
                order_id=order.order_id,
                total_quantity=total_qty,
                filled_quantity=current_filled,
                remaining_quantity=max(total_qty - current_filled, Decimal("0")),
                avg_fill_price=order.avg_fill_price if current_filled > 0 else None,
                fill_count=0,
                total_commission=Decimal("0"),
                is_complete=current_filled >= total_qty,
                last_fill_timestamp=None,
            )

        # ── 记录成交 ──
        self._fills[order.order_id].append(fill)

        # ── 累积计算 ──
        old_filled = order.filled_quantity or Decimal("0")
        new_filled = old_filled + fill.filled_quantity

        # 加权均价
        old_avg = order.avg_fill_price or Decimal("0")
        if old_filled > 0:
            new_avg = (old_avg * old_filled + fill.fill_price * fill.filled_quantity) / new_filled
        else:
            new_avg = fill.fill_price

        # 更新 Order 字段（就地修改）
        order.filled_quantity = new_filled
        order.avg_fill_price = new_avg
        order.updated_at = datetime.now(UTC)

        # ── 状态转换 ──
        total_qty = order.quantity
        if new_filled >= total_qty:
            self._try_transition(order, OrderStatus.FILLED)
        elif new_filled > 0:
            # SUBMITTED→PARTIAL 或 PARTIAL 保持
            if order.status != OrderStatus.PARTIAL:
                self._try_transition(order, OrderStatus.PARTIAL)

        # over-fill 警告
        if new_filled > total_qty:
            logger.warning(
                "成交超量: order_id=%s total=%s filled=%s (over=%s)",
                order.order_id,
                total_qty,
                new_filled,
                new_filled - total_qty,
            )

        # ── 计算佣金 ──
        total_commission = sum(
            (f.commission for f in self._fills[order.order_id]),
            start=Decimal("0"),
        )

        # ── 构建 FillSummary ──
        fills = self._fills[order.order_id]
        summary = FillSummary(
            order_id=order.order_id,
            total_quantity=total_qty,
            filled_quantity=new_filled,
            remaining_quantity=max(total_qty - new_filled, Decimal("0")),
            avg_fill_price=new_avg if new_filled > 0 else None,
            fill_count=len(fills),
            total_commission=total_commission,
            is_complete=new_filled >= total_qty,
            last_fill_timestamp=fill.fill_timestamp,
        )
        self._summaries[order.order_id] = summary

        logger.info(
            "成交处理: order_id=%s fill_id=%s qty=%s filled=%s/%s avg=%s commission=%s status=%s",
            order.order_id,
            fill.fill_id,
            fill.filled_quantity,
            new_filled,
            total_qty,
            new_avg,
            total_commission,
            order.status,
        )

        # ── 通知回调 ──
        for cb in self._callbacks:
            try:
                cb(fill, summary)
            except Exception:  # noqa: BLE001 — 回调失败不阻断处理
                logger.warning(
                    "成交回调异常: %s <- %s",
                    order.order_id,
                    cb.__qualname__,
                    exc_info=True,
                )

        # ── Fill JSONL 落盘（56号文 G3：进程退出不丢当日 Fill）──
        self._persist_fill(fill)

        return summary

    # ── Fill JSONL 落盘 / 回放（56号文 G3）─────────────────────────────────

    def _persist_fill(self, fill: Fill) -> None:
        """把 Fill 追加写入 {fills_dir}/YYYYMMDD.jsonl（append-only）。

        落盘失败仅记录日志不阻断成交主流程（持久化是旁路审计链，
        不可因磁盘异常拖垮 process_fill——与回调异常隔离同语义）。
        """
        if self._fills_dir is None:
            return
        trade_day = _trade_date_of(fill)
        path = self._fills_dir / f"{trade_day}.jsonl"
        line = json.dumps(
            {"trade_date": trade_day, "fill": _fill_to_json_dict(fill)},
            ensure_ascii=False,
        )
        try:
            with self._persist_lock, open(path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except OSError:
            logger.error("Fill 落盘失败: fill_id=%s path=%s", fill.fill_id, path, exc_info=True)

    def query_fills_by_date(self, trade_date: str) -> list[Fill]:
        """按交易日回放落盘的 Fill 列表（56号文 G3 盘后查询）。

        进程退出后重启，当日 Fill 仍可从 JSONL 完整回放（病根修复）。
        行顺序=写入顺序（成交处理顺序）。

        Args:
            trade_date: 交易日，"YYYY-MM-DD" 或 "YYYYMMDD"（内部归一）。

        Returns:
            list[Fill]：该日落盘的全部成交；文件不存在返回空列表。

        Raises:
            ValueError: 未配置 fills_dir（本功能依赖落盘目录）。
        """
        if self._fills_dir is None:
            raise ValueError("未配置 fills_dir，query_fills_by_date 不可用（FillHandler 初始化时传入落盘目录）")
        day = trade_date.replace("-", "")
        path = self._fills_dir / f"{day}.jsonl"
        if not path.is_file():
            return []
        fills: list[Fill] = []
        with self._persist_lock, open(path, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    fills.append(_fill_from_json_dict(record["fill"]))
                except (json.JSONDecodeError, KeyError, ValueError) as exc:
                    # 坏行（crash 残行/schema 不兼容）跳过——与 AppendOnlyDedupSet
                    # 末行残缺丢弃同风格：宁可少读不阻断回放
                    logger.warning("Fill JSONL 坏行跳过: path=%s line=%d err=%s", path, lineno, exc)
        return fills

    # ── 查询 ──────────────────────────────────────────────────────────────

    def get_summary(self, order_id: str) -> FillSummary | None:
        """获取订单的成交汇总（无成交返回 None）。"""
        return self._summaries.get(order_id)

    def get_fills(self, order_id: str) -> list[Fill]:
        """获取订单的成交历史（按处理顺序）。"""
        return list(self._fills.get(order_id, []))

    def get_remaining(self, order_id: str) -> Decimal | None:
        """获取订单的剩余未成交数量（无记录返回 None）。"""
        summary = self._summaries.get(order_id)
        if summary is None:
            return None
        return summary.remaining_quantity

    # ── 回调 ──────────────────────────────────────────────────────────────

    def register_callback(self, callback: Callable[[Fill, FillSummary], None]) -> None:
        """注册成交回调——每次 process_fill 后同步调用。"""
        self._callbacks.append(callback)

    # ── 统计 ──────────────────────────────────────────────────────────────

    @property
    def order_count(self) -> int:
        """有成交记录的订单数量。"""
        return len(self._fills)

    @property
    def total_fill_count(self) -> int:
        """总成交笔数。"""
        return sum(len(fills) for fills in self._fills.values())

    # ── 内部 ──────────────────────────────────────────────────────────────

    def _try_transition(self, order: Order, target: OrderStatus) -> None:
        """尝试状态转换，非法转换记录日志但不抛异常。

        与 OrderManager._transition_status 不同——FillHandler 不阻断
        非法转换（可能由并发填充导致），仅记录警告。
        """
        if order.status == target:
            return  # 已在目标状态
        allowed = _FILL_TRANSITIONS.get(order.status, set())
        if target not in allowed:
            logger.warning(
                "状态转换跳过: %s -> %s 不在合法路径 (order_id=%s)",
                order.status,
                target,
                order.order_id,
            )
            return
        order.status = target
        order.updated_at = datetime.now(UTC)
