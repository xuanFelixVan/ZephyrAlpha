# [BLUEPRINT] MOD-INF-075 | docs/03_modules/_domain_infrastructure_runtime/shared_memory_zero_copy/blueprint.md
# [MODULE] zephyr.infra_runtime.shared_memory_zero_copy
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] 无（multiprocessing.shared_memory 标准库；fallback/时钟全注入）
# [CONSUMERS] 运行时装配批（42万条因子值跨进程零拷贝传递通道装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 通道名强制命名空间前缀(namespace/name); 生命周期 CREATED→ATTACHED→DETACHED→FREED 单向; 读写仅 CREATED/ATTACHED 态; 写越界(offset+len>size)拒绝; size>threshold 降级走注入 fallback 并标记 downgraded; free 幂等禁止(重复 free 抛错); 非法输入 Fail-Closed 抛错; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_runtime/shared_memory_zero_copy/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ZeroCopyError(占位 ZA-INF-UNREGISTERED-ZERO-COPY)——非法命名/未知通道/重复创建/非法状态迁移/越界读写/非法size时抛
# [TESTS] tests/infra_runtime/test_shared_memory_zero_copy.py
# [A_module] module_id=MOD-INF-075 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
ZeroCopyChannelManager — 共享内存零拷贝通道（MOD-INF-075）。

B10-01807（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-H1FS-008，A1交易决策架构
§29.1）：``multiprocessing.shared_memory`` 实现 42 万条因子值零拷贝传递
（目标约 0.01ms vs gRPC 3-15ms），含生命周期管理（create/attach/detach/
free）+ 命名空间隔离（name 前缀校验）+ 超限降级（size > threshold 走注入
fallback 回调并标记 downgraded）。不重复 A9 进程隔离建设。

降级通道以内存 buffer 兜底读写（确定性），每次写同步转发 fallback 回调
（承载降级 Redis 语义，本件不触网）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: namespace 参数
#   fields: 参数 namespace（无注解）
#   code: shared_memory_zero_copy.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: size_threshold 参数
#   fields: 参数 size_threshold（无注解）
#   code: shared_memory_zero_copy.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: fallback 参数
#   fields: 参数 fallback（无注解）
#   code: shared_memory_zero_copy.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: shared_memory_zero_copy.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ZeroCopyChannelManager
#   name_en: ZeroCopyChannelManager
#   intro: 零拷贝通道管理器（命名空间隔离 + 生命周期 + 超限降级）。
#   desc: 零拷贝通道管理器（命名空间隔离 + 生命周期 + 超限降级）。；公共方法（定义序）: create, attach, detach, free, write, read, info, channel_names；源码…
#   inputs: namespace size_threshold fallback clock
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: ZeroCopyChannelManager
#   downstream: 运行时装配批（42万条因子值跨进程零拷贝传递通道装配）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from enum import Enum
from multiprocessing import shared_memory
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "ChannelInfo",
    "ChannelState",
    "ZeroCopyChannelManager",
    "ZeroCopyError",
]


class ZeroCopyError(Exception):
    """零拷贝通道输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INF-UNREGISTERED-ZERO-COPY。
    """


class ChannelState(str, Enum):
    """通道生命周期状态机。"""

    CREATED = "created"
    ATTACHED = "attached"
    DETACHED = "detached"
    FREED = "freed"


@dataclass(frozen=True)
class ChannelInfo:
    """通道元信息视图（frozen）。"""

    name: str
    size: int
    state: ChannelState
    downgraded: bool
    created_at: float


class _Channel:
    """通道内部句柄（真实 shm 或降级 buffer 二选一）。"""

    def __init__(self, info: ChannelInfo, shm: shared_memory.SharedMemory | None) -> None:
        self.info = info
        self.shm = shm
        self.buffer = bytearray(info.size) if info.downgraded else None


class ZeroCopyChannelManager:
    """零拷贝通道管理器（命名空间隔离 + 生命周期 + 超限降级）。"""

    def __init__(
        self,
        *,
        namespace: str,
        size_threshold: int,
        fallback: Callable[[str, bytes], None] | None = None,
        clock: Callable[[], float] | None = None,
    ) -> None:
        if not namespace or "/" in namespace:
            raise ZeroCopyError(f"namespace 非法: {namespace!r}")
        if not isinstance(size_threshold, int) or size_threshold <= 0:
            raise ZeroCopyError(f"size_threshold 非正: {size_threshold!r}")
        self._namespace = namespace
        self._threshold = size_threshold
        self._fallback = fallback
        self._clock = clock or time.monotonic
        self._channels: dict[str, _Channel] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _full_name(self, name: str) -> str:
        if not name or "/" in name:
            raise ZeroCopyError(f"通道名非法: {name!r}（须为命名空间内短名，全名 {self._namespace}/<name>）")
        return f"{self._namespace}/{name}"

    def _channel_of(self, name: str) -> _Channel:
        ch = self._channels.get(name)
        if ch is None:
            raise ZeroCopyError(f"未知通道: {self._namespace}/{name}（命名空间隔离）")
        return ch

    def _require_io_state(self, ch: _Channel, op: str) -> None:
        if ch.info.state is ChannelState.FREED:
            raise ZeroCopyError(f"通道已释放，禁止 {op}: {ch.info.name}")
        if ch.info.state is ChannelState.DETACHED:
            raise ZeroCopyError(f"通道已分离，禁止 {op}: {ch.info.name}")

    # ── 生命周期 ──────────────────────────────────────────────────────────

    def create(self, name: str, size: int) -> ChannelInfo:
        """创建通道：size > threshold → 降级（内存 buffer + fallback 标记）。"""
        full = self._full_name(name)
        if not isinstance(size, int) or size <= 0:
            raise ZeroCopyError(f"size 非法: {size!r}")
        if name in self._channels:
            raise ZeroCopyError(f"通道重复创建: {full}")
        downgraded = size > self._threshold
        shm: shared_memory.SharedMemory | None = None
        if not downgraded:
            try:
                shm = shared_memory.SharedMemory(name=full, create=True, size=size)
            except Exception as exc:  # noqa: BLE001 — OS 级失败统一收敛
                raise ZeroCopyError(f"共享内存创建失败: {full} ({exc})") from exc
        info = ChannelInfo(
            name=full,
            size=size,
            state=ChannelState.CREATED,
            downgraded=downgraded,
            created_at=self._clock(),
        )
        self._channels[name] = _Channel(info=info, shm=shm)
        if downgraded:
            _log.warning("通道超限降级: %s size=%d > threshold=%d", full, size, self._threshold)
        return info

    def attach(self, name: str) -> ChannelInfo:
        """挂接通道（CREATED/DETACHED → ATTACHED；真实通道重开句柄）。"""
        self._full_name(name)
        ch = self._channel_of(name)
        if ch.info.state is ChannelState.FREED:
            raise ZeroCopyError(f"通道已释放，禁止挂接: {ch.info.name}")
        if ch.info.state is ChannelState.ATTACHED:
            return ch.info  # 幂等
        if not ch.info.downgraded and ch.shm is None:
            try:
                ch.shm = shared_memory.SharedMemory(name=ch.info.name, create=False)
            except Exception as exc:  # noqa: BLE001
                raise ZeroCopyError(f"共享内存挂接失败: {ch.info.name} ({exc})") from exc
        ch.info = ChannelInfo(
            name=ch.info.name,
            size=ch.info.size,
            state=ChannelState.ATTACHED,
            downgraded=ch.info.downgraded,
            created_at=ch.info.created_at,
        )
        return ch.info

    def detach(self, name: str) -> ChannelInfo:
        """分离通道（CREATED/ATTACHED → DETACHED）。

        管理器持有属主句柄不关闭（Windows 下唯一句柄关闭即销毁映射段，
        跨进程消费方自行关闭各自句柄），段在 free 时才 close+unlink。
        """
        ch = self._channel_of(name)
        if ch.info.state is ChannelState.FREED:
            raise ZeroCopyError(f"通道已释放，禁止分离: {ch.info.name}")
        if ch.info.state is ChannelState.DETACHED:
            return ch.info  # 幂等
        ch.info = ChannelInfo(
            name=ch.info.name,
            size=ch.info.size,
            state=ChannelState.DETACHED,
            downgraded=ch.info.downgraded,
            created_at=ch.info.created_at,
        )
        return ch.info

    def free(self, name: str) -> None:
        """释放通道（→ FREED；真实通道 close+unlink，重复 free 抛错）。"""
        ch = self._channel_of(name)
        if ch.info.state is ChannelState.FREED:
            raise ZeroCopyError(f"通道重复释放: {ch.info.name}")
        if ch.shm is not None:
            ch.shm.close()
            ch.shm.unlink()
            ch.shm = None
        ch.buffer = None
        ch.info = ChannelInfo(
            name=ch.info.name,
            size=ch.info.size,
            state=ChannelState.FREED,
            downgraded=ch.info.downgraded,
            created_at=ch.info.created_at,
        )

    # ── 读写 ─────────────────────────────────────────────────────────────

    def write(self, name: str, data: bytes | bytearray | memoryview, offset: int = 0) -> None:
        """写入通道（降级通道同步转发 fallback 回调）。"""
        ch = self._channel_of(name)
        self._require_io_state(ch, "写入")
        payload = bytes(data)
        if offset < 0 or offset + len(payload) > ch.info.size:
            raise ZeroCopyError(f"写越界: offset={offset} len={len(payload)} size={ch.info.size}")
        if ch.info.downgraded:
            assert ch.buffer is not None
            ch.buffer[offset : offset + len(payload)] = payload
            if self._fallback is not None:
                try:
                    self._fallback(ch.info.name, payload)
                except Exception:  # noqa: BLE001 — 降级回调不阻断（蓝图 §1）
                    _log.exception("fallback 降级回调失败: %s", ch.info.name)
        else:
            assert ch.shm is not None
            ch.shm.buf[offset : offset + len(payload)] = payload

    def read(self, name: str, length: int | None = None, offset: int = 0) -> bytes:
        """读取通道（length=None 读至末尾）。"""
        ch = self._channel_of(name)
        self._require_io_state(ch, "读取")
        end = ch.info.size if length is None else offset + length
        if offset < 0 or end > ch.info.size or (length is not None and length < 0):
            raise ZeroCopyError(f"读越界: offset={offset} length={length} size={ch.info.size}")
        if ch.info.downgraded:
            assert ch.buffer is not None
            return bytes(ch.buffer[offset:end])
        assert ch.shm is not None
        return bytes(ch.shm.buf[offset:end])

    # ── 查询 ─────────────────────────────────────────────────────────────

    def info(self, name: str) -> ChannelInfo:
        """单通道元信息（未知 → Fail-Closed）。"""
        return self._channel_of(name).info

    def channel_names(self) -> tuple[str, ...]:
        """命名空间内通道全名（确定性排序）。"""
        return tuple(sorted(ch.info.name for ch in self._channels.values()))
