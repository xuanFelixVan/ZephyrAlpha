# [BLUEPRINT] MOD-SIG-133 | docs/03_modules/_domain_signal/shared_kernel_sync/blueprint.md
# [MODULE] zephyr.signal_ashare.shared_kernel_sync
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（协议核心纯内存；bus/时钟/告警回调全注入）
# [CONSUMERS] 运行时装配批（统一注入点装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 三命名空间词表闭合(common_params|market_state|feature_cache)；单一真源注册表；写即版本递增(每键独立从1起)；每次写经注入bus发布变更事件；读侧版本戳比对→漂移清单(确定性排序)+告警回调；bus未注入跳过发布不旁路校验；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal/shared_kernel_sync/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SharedKernelError(占位 ZA-SIG-UNREGISTERED-SHARED-KERNEL)——非法命名空间/空key/读未知键/空reader_id/版本戳非法/比对未知键时抛
# [TESTS] tests/signal_ashare/test_shared_kernel_sync.py
# [A_module] module_id=MOD-SIG-133 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
SharedKernelSync — 策略共享内核同步器（MOD-SIG-133）。

B14-04730（AUD-DRAFT-001-DIGEST P2 波 P2-W06，CAND-TESTB-059，A9
D-SIGNAL-101）：公共参数/市场状态/特征缓存三命名空间（词表闭合）
单一真源注册表 + 版本广播（写即版本递增+变更事件经注入bus发布）
+ 一致性校验（读侧版本戳比对，漂移清单+告警回调）。

查重分工：event_bus=事件总线实现（本件=经注入bus发布变更事件，
不实现总线）；feature_store 族=特征存储（本件=跨策略版本一致性
同步，不做特征计算）。

纯内存/DI设计；外部副作用（OS调用/网络/进程控制）全部经注入回调。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: bus 参数
#   fields: 参数 bus（无注解）
#   code: shared_kernel_sync.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: shared_kernel_sync.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: alert_sink 参数
#   fields: 参数 alert_sink（无注解）
#   code: shared_kernel_sync.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SharedKernelSync
#   name_en: SharedKernelSync
#   intro: 策略共享内核同步器（单一真源注册表+版本广播+一致性校验）。
#   desc: 策略共享内核同步器（单一真源注册表+版本广播+一致性校验）。；公共方法（定义序）: write, read, version_of, keys, snapshot_versions, check_drift；源码 L1…
#   inputs: bus clock alert_sink
#   outputs: 返回值
#   （注：A1 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（7 定义）
#   name_en: public defs
#   intro: SharedKernelSync
#   downstream: 运行时装配批（统一注入点装配）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Final, Iterable, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "KernelChangeEvent",
    "KernelDrift",
    "KernelNamespace",
    "ReaderStamp",
    "SharedKernelError",
    "SharedKernelSync",
    "VersionedValue",
]


class SharedKernelError(Exception):
    """共享内核同步协议输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-SHARED-KERNEL。
    """


class KernelNamespace(str, Enum):
    """共享内核命名空间词表（三类闭合）。"""

    COMMON_PARAMS = "common_params"
    MARKET_STATE = "market_state"
    FEATURE_CACHE = "feature_cache"


@dataclass(frozen=True)
class KernelChangeEvent:
    """内核变更事件（写即版本递增后经注入bus发布）。"""

    namespace: KernelNamespace
    key: str
    version: int
    changed_at: datetime.datetime


@dataclass(frozen=True)
class VersionedValue:
    """带版本戳的注册表读取结果。"""

    namespace: KernelNamespace
    key: str
    value: Any
    version: int
    updated_at: datetime.datetime


@dataclass(frozen=True)
class ReaderStamp:
    """读侧版本戳（读方持有的 (命名空间,键)→版本 观察）。"""

    namespace: KernelNamespace | str
    key: str
    version: int


@dataclass(frozen=True)
class KernelDrift:
    """一致性漂移记录（读侧版本戳与单一真源不一致）。"""

    reader_id: str
    namespace: KernelNamespace
    key: str
    reader_version: int
    current_version: int
    at: datetime.datetime


def _coerce_namespace(ns: KernelNamespace | str) -> KernelNamespace:
    """命名空间收敛：枚举或其字符串值，其余 Fail-Closed。"""
    if isinstance(ns, KernelNamespace):
        return ns
    if isinstance(ns, str):
        try:
            return KernelNamespace(ns)
        except ValueError:
            pass
    raise SharedKernelError(f"非法命名空间: {ns!r}（词表闭合三类）")


def _validate_key(key: str) -> str:
    """键名非空白校验。"""
    if not key or not str(key).strip():
        raise SharedKernelError(f"key 为空: {key!r}")
    return key


class SharedKernelSync:
    """策略共享内核同步器（单一真源注册表+版本广播+一致性校验）。"""

    def __init__(
        self,
        *,
        bus: Callable[[KernelChangeEvent], None] | Any | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
        alert_sink: Callable[[KernelDrift], None] | None = None,
    ) -> None:
        if bus is not None:
            publish = getattr(bus, "publish", None)
            self._publish = publish if callable(publish) else bus
            if not callable(self._publish):
                raise SharedKernelError(f"bus 不可调用且无 publish 方法: {type(bus)!r}")
        else:
            self._publish = None
        self._clock = clock or datetime.datetime.now
        self._alert_sink = alert_sink
        # namespace -> key -> (value, version, updated_at)
        self._store: dict[KernelNamespace, dict[str, tuple[Any, int, datetime.datetime]]] = {
            ns: {} for ns in KernelNamespace
        }

    # ------------------------------------------------------------------
    # 写侧（单一真源 + 版本广播）
    # ------------------------------------------------------------------
    def write(self, namespace: KernelNamespace | str, key: str, value: Any) -> VersionedValue:
        """写入即版本递增（每键独立从1起），变更事件经注入bus发布。"""
        ns = _coerce_namespace(namespace)
        k = _validate_key(key)
        bucket = self._store[ns]
        _, prev_version, _ = bucket.get(k, (None, 0, None))
        version = prev_version + 1
        at = self._clock()
        bucket[k] = (value, version, at)
        if self._publish is not None:
            self._publish(KernelChangeEvent(namespace=ns, key=k, version=version, changed_at=at))
        _log.info("内核写入: %s/%s → v%d", ns.value, k, version)
        return VersionedValue(namespace=ns, key=k, value=value, version=version, updated_at=at)

    # ------------------------------------------------------------------
    # 读侧
    # ------------------------------------------------------------------
    def read(self, namespace: KernelNamespace | str, key: str) -> VersionedValue:
        """读取当前值（带版本戳）；未知键 Fail-Closed。"""
        ns = _coerce_namespace(namespace)
        k = _validate_key(key)
        bucket = self._store[ns]
        if k not in bucket:
            raise SharedKernelError(f"未知键: {ns.value}/{k!r}")
        value, version, at = bucket[k]
        return VersionedValue(namespace=ns, key=k, value=value, version=version, updated_at=at)

    def version_of(self, namespace: KernelNamespace | str, key: str) -> int:
        """键的当前版本号。"""
        return self.read(namespace, key).version

    def keys(self, namespace: KernelNamespace | str) -> tuple[str, ...]:
        """命名空间内键清单（确定性升序）。"""
        ns = _coerce_namespace(namespace)
        return tuple(sorted(self._store[ns]))

    def snapshot_versions(self) -> Mapping[tuple[KernelNamespace, str], int]:
        """全注册表版本快照（(命名空间,键)→版本）。"""
        return {(ns, k): version for ns in KernelNamespace for k, (_, version, _) in self._store[ns].items()}

    # ------------------------------------------------------------------
    # 一致性校验
    # ------------------------------------------------------------------
    def check_drift(self, reader_id: str, stamps: Iterable[ReaderStamp]) -> tuple[KernelDrift, ...]:
        """读侧版本戳比对：与真源不一致即产出漂移清单+告警（确定性排序）。"""
        if not reader_id or not str(reader_id).strip():
            raise SharedKernelError(f"reader_id 为空: {reader_id!r}")
        drifts: list[KernelDrift] = []
        for stamp in stamps:
            if not isinstance(stamp, ReaderStamp):
                raise SharedKernelError(f"版本戳类型非法: {type(stamp)!r}")
            ns = _coerce_namespace(stamp.namespace)
            k = _validate_key(stamp.key)
            if isinstance(stamp.version, bool) or not isinstance(stamp.version, int) or stamp.version < 1:
                raise SharedKernelError(f"版本戳非法: {stamp.version!r}（须为正整数）")
            current = self.version_of(ns, k)
            if stamp.version != current:
                drift = KernelDrift(
                    reader_id=reader_id,
                    namespace=ns,
                    key=k,
                    reader_version=stamp.version,
                    current_version=current,
                    at=self._clock(),
                )
                drifts.append(drift)
        drifts.sort(key=lambda d: (d.reader_id, d.namespace.value, d.key))
        for drift in drifts:
            if self._alert_sink is not None:
                self._alert_sink(drift)
            _log.warning(
                "内核漂移告警: reader=%s %s/%s 读侧=v%d 真源=v%d",
                drift.reader_id,
                drift.namespace.value,
                drift.key,
                drift.reader_version,
                drift.current_version,
            )
        return tuple(drifts)
