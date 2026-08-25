# [BLUEPRINT] MOD-SIG-087 | docs/03_modules/_domain_signal/factor_result_bridge/blueprint.md
# [MODULE] zephyr.signal_ashare.factor_result_bridge
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] D_ASHARE_SIGNAL 信号合成侧（运行时装配批接线）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 版本三态裁定(exact/compatible/unsupported); 不支持的版本fail-closed拒收产空批次+is_degraded; is_degraded只透传不制造; 每次消费产不可变审计记录; 纯内存判定核心无IO(provider/audit_sink注入)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] provider异常->FactorResultBridgeError; 不支持版本->verdict.accepted=False(不抛异常)
# [TESTS] tests/signal_ashare/test_factor_result_bridge.py
# [A_module] module_id=MOD-SIG-087 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D-SIGNAL-158 因子计算结果消费桥接器（CAND-TESTB-027 / B13-04307）。

D-FACTOR→D-SIGNAL 统一消费桥接（anti-corruption layer）：信号侧不再直连因子
存储，一律经本桥接器消费因子计算结果。

职责：
  - 版本化 schema 契约消费：exact（受支持版本直通）/ compatible（同主版本兼容
    透传）/ unsupported（fail-closed 拒收，产空批次 + is_degraded=True，绝不
    静默按错版本解析）。
  - is_degraded 透传：上游降级标记（D-SIGNAL-77 factor_availability_monitor
    语义）原样带出；桥接器自身不制造降级。
  - 消费审计：每次消费产一条不可变审计记录；audit_sink 外置持久化，sink 异常
    不阻断消费。

非职责（MVP 边界）：
  - CTR-002 消费契约适配器（B13-04308，W-P1-16）未建——取数经 provider 回调
    注入，适配器落地后接线；真实 Redis/CH provider 装配留运行时装配批。

依据: A3数据架构 §17.12；construction_backlog_dig.tsv B13-04307。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from zephyr.shared.foundation.errors import ZephyrBaseError

log = logging.getLogger(__name__)

__all__ = [
    "ConsumptionVerdict",
    "FactorResultBatch",
    "FactorResultBridge",
    "FactorResultBridgeError",
]


class FactorResultBridgeError(ZephyrBaseError):
    """桥接器取数/解析失败（错误码未登，纪律⑦留错误码对账批）。"""


@dataclass(frozen=True)
class FactorResultBatch:
    """一批因子计算结果（CTR-002 消费形态的最小承载）。

    Attributes:
        schema_version: 契约版本（SemVer，如 "1.0"）。
        factor_values: (factor_id, symbol, value) 三元组序列。
        as_of: 批次数据时点（PIT 语义）。
        is_degraded: 上游降级标记（factor_availability_monitor 语义）。
        metadata: 溯源元数据（来源/批次号等）。
    """

    schema_version: str
    factor_values: tuple[tuple[str, str, float], ...]
    as_of: datetime.datetime
    is_degraded: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ConsumptionVerdict:
    """一次消费裁定结果。

    Attributes:
        batch: 消费到的批次（拒收时为空批次）。
        accepted: 是否接受消费。
        degraded: 输出降级标记（上游透传或拒收 fail-closed）。
        version_action: 版本裁定 exact/compatible/unsupported。
        reason: 裁定理由（拒收时必填）。
    """

    batch: FactorResultBatch
    accepted: bool
    degraded: bool
    version_action: str
    reason: str = ""


def _parse_version(version: str) -> tuple[int, int] | None:
    """解析 'major.minor' 版本号，非法返回 None。"""
    parts = str(version).split(".")
    if len(parts) < 2:
        return None
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None


class FactorResultBridge:
    """因子计算结果消费桥接器。

    Args:
        provider: 取数回调 ``provider(as_of=None) -> FactorResultBatch``
            （CTR-002 适配器/特征存储读取职责，注入式，本件不 import 存储）。
        supported_versions: 受支持契约版本元组（SemVer）。
        audit_sink: 审计持久化回调 ``sink(record: dict)``（可选，异常不阻断）。
        clock: 时钟注入（测试可控）。
    """

    def __init__(
        self,
        provider: Callable[..., FactorResultBatch],
        *,
        supported_versions: Sequence[str] = ("1.0",),
        audit_sink: Callable[[dict], None] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if not callable(provider):
            raise FactorResultBridgeError("provider 必须为可调用对象")
        self._provider = provider
        self._supported: dict[int, list[int]] = {}
        for v in supported_versions:
            parsed = _parse_version(v)
            if parsed is None:
                raise FactorResultBridgeError(f"受支持版本号非法: {v!r}")
            self._supported.setdefault(parsed[0], []).append(parsed[1])
        self._audit_sink = audit_sink
        self._clock = clock or (lambda: datetime.datetime.now(datetime.timezone.utc))
        self._audit_log: list[dict] = []

    @property
    def audit_log(self) -> tuple[dict, ...]:
        """消费审计记录（不可变快照）。"""
        return tuple(self._audit_log)

    def _adjudicate_version(self, version: str) -> tuple[str, str]:
        """版本三态裁定。返回 (action, reason)。"""
        parsed = _parse_version(version)
        if parsed is None:
            return "unsupported", f"契约版本号非法: {version!r}"
        major, minor = parsed
        minors = self._supported.get(major)
        if minors is None:
            return "unsupported", f"契约主版本不受支持: {version!r}"
        if minor in minors:
            return "exact", ""
        return "compatible", f"同主版本兼容透传: {version!r}"

    def consume(self, as_of: datetime.datetime | None = None) -> ConsumptionVerdict:
        """消费一批因子计算结果：取数→版本裁定→降级透传→审计。"""
        started = self._clock()
        try:
            batch = self._provider(as_of=as_of)
        except Exception as exc:  # noqa: BLE001 — provider 边界统一翻译
            raise FactorResultBridgeError(f"因子结果取数失败: {exc}") from exc
        if not isinstance(batch, FactorResultBatch):
            raise FactorResultBridgeError(
                f"provider 返回类型非法: {type(batch).__name__}（期望 FactorResultBatch）"
            )

        action, reason = self._adjudicate_version(batch.schema_version)
        if action == "unsupported":
            empty = FactorResultBatch(
                schema_version=batch.schema_version,
                factor_values=(),
                as_of=batch.as_of,
                is_degraded=True,
                metadata=dict(batch.metadata),
            )
            verdict = ConsumptionVerdict(
                batch=empty, accepted=False, degraded=True, version_action=action, reason=reason
            )
        else:
            verdict = ConsumptionVerdict(
                batch=batch,
                accepted=True,
                degraded=batch.is_degraded,
                version_action=action,
                reason=reason,
            )

        self._record_audit(verdict, started)
        return verdict

    def _record_audit(self, verdict: ConsumptionVerdict, started: datetime.datetime) -> None:
        """写消费审计：内存不可变记录 + 外置 sink（sink 异常不阻断，留痕降级）。"""
        finished = self._clock()
        record = {
            "as_of": verdict.batch.as_of.isoformat(),
            "consumed_at": finished.isoformat(),
            "schema_version": verdict.batch.schema_version,
            "value_count": len(verdict.batch.factor_values),
            "accepted": verdict.accepted,
            "degraded": verdict.degraded,
            "version_action": verdict.version_action,
            "reason": verdict.reason,
            "elapsed_ms": max(0.0, (finished - started).total_seconds() * 1000.0),
        }
        self._audit_log.append(record)
        if self._audit_sink is not None:
            try:
                self._audit_sink(dict(record))
            except Exception:  # noqa: BLE001 — sink 故障不阻断消费
                log.warning("factor_result_bridge: audit_sink 异常，审计仅留内存", exc_info=True)
