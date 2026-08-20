# [BLUEPRINT] MOD-MKT-004 | docs/03_modules/_domain_mkt_data/failover/blueprint.md
# [MODULE] zephyr.market_data.failover.manager
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.market_data.vendor_registry; zephyr.market_data.vendor_base; zephyr.shared.foundation.errors
# [CONSUMERS] D_EX_SOR
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] FailoverEvent/FailoverConfig frozen; FailoverPolicy/FailoverReason Enum; _active_vendor_id/_history加Lock; 切换原子(先确认目标可用); 同vendor不切自身
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FailoverError(ZA-MKT-0004)
# [TESTS] tests/market_data/failover/test_failover_manager.py
# [A_module] module_id=MOD-MKT-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_MKT_DATA — Failover Manager (故障切换管理器)

主备切换管理: 主数据源健康检查失败时切换到备用源, 主源恢复后可选切回。
基于 VendorRegistry 查找可用 vendor, 按 FailoverPolicy 策略选择备用源。

属 A 类基础设施(高可用机制), 纯基础层不涉及策略。

设计真源: depgraph MOD-MKT-004
蓝图: docs/03_modules/_domain_mkt_data/failover/blueprint.md
"""

from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from threading import Lock
from typing import Callable

from zephyr.market_data.vendor_base import MarketDataVendor, VendorStatus
from zephyr.market_data.vendor_registry import VendorRegistry
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)


class FailoverError(ZephyrBaseError):
    """故障切换配置非法——空优先级列表/vendor 未注册。"""

    error_code = "ZA-MKT-0004"


class FailoverPolicy(str, Enum):
    """切换策略。"""

    PRIORITY = "priority"  # 按优先级列表切换
    ROUND_ROBIN = "round_robin"  # 轮询切换


class FailoverReason(str, Enum):
    """切换原因。"""

    HEALTH_CHECK_FAILED = "health_check_failed"
    MANUAL = "manual"
    AUTO_FAILBACK = "auto_failback"
    INITIAL = "initial"
    ALL_FAILED = "all_failed"


@dataclass(frozen=True)
class FailoverConfig:
    """故障切换配置——不可变。

    Attributes:
        priority_list: vendor_id 优先级列表(主→备), 不可空
        policy: 切换策略
        auto_failback: 主源恢复后是否自动切回
        history_max: 历史记录最大条数
    """

    priority_list: tuple[str, ...]
    policy: FailoverPolicy = FailoverPolicy.PRIORITY
    auto_failback: bool = True
    history_max: int = 100


@dataclass(frozen=True)
class FailoverEvent:
    """切换事件——不可变。

    Attributes:
        from_vendor: 切换前 vendor_id(初始切换为 None)
        to_vendor: 切换后 vendor_id(全部失败为 None)
        reason: 切换原因
        timestamp: 切换时间(UTC)
        detail: 附加详情
    """

    from_vendor: str | None
    to_vendor: str | None
    reason: FailoverReason
    timestamp: datetime
    detail: str = ""


# 切换事件回调类型
FailoverCallback = Callable[[FailoverEvent], None]


class FailoverManager:
    """故障切换管理器——主备切换 + 自动恢复。

    基于 VendorRegistry 管理多 vendor 的主备切换:
      - 主源 health_check 失败 → 切到下一个可用备用源
      - 主源恢复(auto_failback=True) → 切回主源
      - 无可用源 → 记录 ALL_FAILED 事件, active=None

    线程安全: _active_vendor_id / _history 读写加 Lock。
    切换原子性: 先确认目标 vendor 可用再切换 active。

    Usage:
        registry = VendorRegistry()
        # 注册 tushare(primary) / akshare(secondary)
        registry.register(tushare_vendor)
        registry.register(akshare_vendor)

        config = FailoverConfig(
            priority_list=("tushare", "akshare"),
            auto_failback=True,
        )
        mgr = FailoverManager(registry, config)

        # 选初始活跃源
        mgr.check_and_failover()  # -> 选 tushare

        # 定期检查(主源挂了自动切)
        event = mgr.check_and_failover()  # tushare 挂了 -> 切 akshare
    """

    def __init__(
        self,
        registry: VendorRegistry,
        config: FailoverConfig,
    ) -> None:
        if not config.priority_list:
            raise FailoverError("priority_list 不能为空")
        self._registry = registry
        self._config = config
        self._active_vendor_id: str | None = None
        self._rr_index: int = 0  # 轮询索引
        self._history: deque[FailoverEvent] = deque(maxlen=config.history_max)
        self._lock = Lock()
        self._callbacks: list[FailoverCallback] = []

    def get_active(self) -> MarketDataVendor | None:
        """获取当前活跃 vendor。未设置或已注销返回 None。"""
        with self._lock:
            vid = self._active_vendor_id
        if vid is None:
            return None
        return self._registry.get(vid)

    @property
    def active_vendor_id(self) -> str | None:
        """当前活跃 vendor ID(只读)。"""
        with self._lock:
            return self._active_vendor_id

    @property
    def history(self) -> list[FailoverEvent]:
        """切换历史(副本, 按时间正序)。"""
        with self._lock:
            return list(self._history)

    @property
    def config(self) -> FailoverConfig:
        """配置(只读)。"""
        return self._config

    def on_failover(self, callback: FailoverCallback) -> None:
        """注册切换事件回调。"""
        self._callbacks.append(callback)

    # ---- 核心切换逻辑 ----

    def check_and_failover(self) -> FailoverEvent | None:
        """健康检查 + 自动切换。

        流程:
          1. active=None: 选首个可用 vendor (INITIAL)
          2. active 不可用: 切到下一个可用 vendor (HEALTH_CHECK_FAILED)
          3. auto_failback 且 active!=primary 且 primary 可用: 切回 (AUTO_FAILBACK)
          4. active 可用: 无操作, 返回 None

        Returns:
            FailoverEvent | None(无切换返回 None)
        """
        with self._lock:
            active_id = self._active_vendor_id

        # 1. 初始: 选首个可用
        if active_id is None:
            return self._select_initial()

        # 检查 active 是否仍注册且可用
        active = self._registry.get(active_id)
        if active is None or not self._is_healthy(active):
            # 2. active 不可用 → 切换
            reason_detail = "active vendor 已注销" if active is None else "health_check 失败"
            return self._do_failover(FailoverReason.HEALTH_CHECK_FAILED, reason_detail)

        # 3. auto_failback 检查
        if self._config.auto_failback:
            primary_id = self._config.priority_list[0]
            if active_id != primary_id:
                primary = self._registry.get(primary_id)
                if primary is not None and self._is_healthy(primary):
                    return self._switch_to(
                        primary_id,
                        FailoverReason.AUTO_FAILBACK,
                        "主源已恢复, 自动切回",
                    )

        # 4. active 可用, 无操作
        return None

    def failover(self, reason: str = "manual") -> FailoverEvent | None:
        """手动切换到下一个可用 vendor。

        Args:
            reason: 切换原因描述

        Returns:
            FailoverEvent | None(无可用 vendor 返回 ALL_FAILED 事件)
        """
        return self._do_failover(FailoverReason.MANUAL, reason)

    def failback(self) -> FailoverEvent | None:
        """手动切回主源。

        主源可用才切换, 否则返回 None。

        Returns:
            FailoverEvent | None(主源不可用返回 None)
        """
        primary_id = self._config.priority_list[0]
        with self._lock:
            if self._active_vendor_id == primary_id:
                return None  # 已是主源
        primary = self._registry.get(primary_id)
        if primary is None or not self._is_healthy(primary):
            return None
        return self._switch_to(primary_id, FailoverReason.AUTO_FAILBACK, "手动 failback")

    # ---- 内部方法 ----

    def _select_initial(self) -> FailoverEvent | None:
        """选初始活跃 vendor——按策略选首个可用。"""
        target = self._find_next_available(exclude=None)
        if target is None:
            return self._record_event(
                from_vendor=None,
                to_vendor=None,
                reason=FailoverReason.ALL_FAILED,
                detail="无可用 vendor(初始)",
            )
        return self._switch_to(target, FailoverReason.INITIAL, "初始选择")

    def _do_failover(self, reason: FailoverReason, detail: str) -> FailoverEvent | None:
        """执行切换——选下一个可用 vendor(排除当前 active)。"""
        with self._lock:
            current = self._active_vendor_id

        # 标记当前为 ERROR(若存在)
        if current is not None:
            vendor = self._registry.get(current)
            if vendor is not None:
                vendor.set_status(VendorStatus.ERROR)

        target = self._find_next_available(exclude=current)
        if target is None:
            # 无可用源
            with self._lock:
                self._active_vendor_id = None
            event = self._record_event(
                from_vendor=current,
                to_vendor=None,
                reason=FailoverReason.ALL_FAILED,
                detail=detail + " | 无可用 vendor",
            )
            return event

        return self._switch_to(target, reason, detail)

    def _switch_to(
        self,
        target_id: str,
        reason: FailoverReason,
        detail: str,
    ) -> FailoverEvent | None:
        """切换到指定 vendor(原子: 先确认可用再切)。"""
        target = self._registry.get(target_id)
        if target is None or not self._is_healthy(target):
            return None

        with self._lock:
            current = self._active_vendor_id
            if current == target_id:
                return None  # 幂等: 已是目标

        # 切换
        with self._lock:
            self._active_vendor_id = target_id
        target.set_status(VendorStatus.ACTIVE)

        event = self._record_event(
            from_vendor=current,
            to_vendor=target_id,
            reason=reason,
            detail=detail,
        )
        _logger.info(
            "故障切换: %s -> %s (reason=%s)",
            current,
            target_id,
            reason.value,
        )
        return event

    def _find_next_available(self, exclude: str | None) -> str | None:
        """按策略找下一个可用 vendor(排除 exclude)。

        PRIORITY: 按 priority_list 顺序找首个可用
        ROUND_ROBIN: 从 _rr_index 开始轮询找首个可用
        """
        if self._config.policy == FailoverPolicy.ROUND_ROBIN:
            return self._find_round_robin(exclude)
        return self._find_priority(exclude)

    def _find_priority(self, exclude: str | None) -> str | None:
        """按优先级列表找首个可用 vendor。"""
        for vid in self._config.priority_list:
            if vid == exclude:
                continue
            vendor = self._registry.get(vid)
            if vendor is not None and self._is_healthy(vendor):
                return vid
        return None

    def _find_round_robin(self, exclude: str | None) -> str | None:
        """轮询找下一个可用 vendor。"""
        plist = self._config.priority_list
        n = len(plist)
        if n == 0:
            return None
        with self._lock:
            start = self._rr_index
        for i in range(n):
            idx = (start + i) % n
            vid = plist[idx]
            if vid == exclude:
                continue
            vendor = self._registry.get(vid)
            if vendor is not None and self._is_healthy(vendor):
                with self._lock:
                    self._rr_index = (idx + 1) % n
                return vid
        return None

    def _is_healthy(self, vendor: MarketDataVendor) -> bool:
        """健康检查(异常视为不可用)。"""
        try:
            return vendor.health_check()
        except Exception:
            _logger.exception("health_check 异常: %s", vendor.vendor_id)
            return False

    def _record_event(
        self,
        from_vendor: str | None,
        to_vendor: str | None,
        reason: FailoverReason,
        detail: str,
    ) -> FailoverEvent:
        """记录切换事件 + 通知回调。"""
        event = FailoverEvent(
            from_vendor=from_vendor,
            to_vendor=to_vendor,
            reason=reason,
            timestamp=datetime.now(timezone.utc),
            detail=detail,
        )
        with self._lock:
            self._history.append(event)
        # 通知回调(锁外, 避免死锁)
        for cb in self._callbacks:
            try:
                cb(event)
            except Exception:
                _logger.exception("failover 回调异常(已隔离)")
        return event

    def __repr__(self) -> str:
        with self._lock:
            return (
                f"FailoverManager(active={self._active_vendor_id!r}, "
                f"policy={self._config.policy.value}, "
                f"history={len(self._history)})"
            )


__all__ = [
    "FailoverCallback",
    "FailoverConfig",
    "FailoverError",
    "FailoverEvent",
    "FailoverManager",
    "FailoverPolicy",
    "FailoverReason",
]
