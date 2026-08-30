# [BLUEPRINT] MOD-CON-001 | docs/03_modules/_domain_contracts/ctr002_consumer_adapter/blueprint.md | §
# [MODULE] zephyr.shared.contracts.ctr002_consumer_adapter
# [DOMAIN] D_CONTRACTS
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.shared.contracts.factor_signal
# [CONSUMERS] D_SIGNAL 消费侧（运行时装配批接线）；factor_result_bridge 未建 provider 注入前瞻兼容
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] major 不兼容即拒; 缺必填 fail-closed; 新增字段收编 extra 并留痕; 版本只升不降; frozen
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] Ctr002AdapterError(ZA-SH-0055); 非法输入抛本异常
# [TESTS] tests/contracts/test_ctr002_consumer_adapter.py
# [A_module] module_id=MOD-CON-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
D-SIGNAL-163 CTR-002消费契约适配器（B13-04308 → MOD-CON-001）。

Schema版本协商（major不兼容即拒）+字段缺失/新增容忍策略+契约变更事件订阅。
信号消费方统一经适配器取数。

非职责：
  - 不直连因子存储/CH/Redis（provider 注入）
  - 不修改 CTR-002 契约定义（定义归 cross_layer_contracts.yaml codegen）
  - 不处理生产侧验证（归 MOD-CON-002 ctr002_producer_validator）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: version 参数
#   fields: 参数 version，类型注解 str | None
#   code: ctr002_consumer_adapter.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: incoming 参数
#   fields: 参数 incoming，类型注解 str | None
#   code: ctr002_consumer_adapter.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: supported 参数
#   fields: 参数 supported，类型注解 Sequence[str]
#   code: ctr002_consumer_adapter.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SchemaSource
#   name_en: SchemaSource
#   intro: CTR-002 契约 Schema 真源（手工推导，与 cross_layer_contracts.yaml 对齐）。
#   desc: CTR-002 契约 Schema 真源（手工推导，与 cross_layer_contracts.yaml 对齐）。；公共方法（定义序）: default_for, optional_default_map…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② parse_semver
#   name_en: parse_semver
#   intro: 解析语义版本为 (major, minor)。
#   desc: 解析语义版本为 (major, minor)。 支持 "X.Y" / "X.Y.Z"（忽略 patch）；失败返回 None。；源码 L211-L226
#   inputs: version
#   outputs: tuple[int, int] | None
# - id: A3
#   name_zh: ③ negotiate_version
#   name_en: negotiate_version
#   intro: 版本协商三态：exact / compatible / unsupported。
#   desc: 版本协商三态：exact / compatible / unsupported。 - exact：incoming 等于任一 supported 版本。 - compatible…；源码 L229-L252
#   inputs: incoming supported
#   outputs: str
# - id: A4
#   name_zh: ④ Ctr002ConsumerAdapter
#   name_en: Ctr002ConsumerAdapter
#   intro: CTR-002 消费契约适配器。
#   desc: CTR-002 消费契约适配器。 Args: supported_versions: 消费端支持的 schema 版本（默认 ("1.0",)）。；公共方法（定义序）: current_version, audit_l…
#   inputs: supported_versions
#   outputs: 返回值
#   （注：A4 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: tuple[int, int] | None
#   name_en: tuple[int, int] | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: D_SIGNAL 消费侧（运行时装配批接线）；factor_result_bridge 未建 provider 注入前瞻兼容
# - id: O2
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: D_SIGNAL 消费侧（运行时装配批接线）；factor_result_bridge 未建 provider 注入前瞻兼容
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from typing import Any, Callable, Final, Mapping, Sequence

from zephyr.shared.foundation.errors import ZephyrBaseError

logger = logging.getLogger(__name__)

__all__: Final = [
    "CTR002_SCHEMA",
    "AdaptationVerdict",
    "ContractChange",
    "Ctr002AdapterError",
    "Ctr002ConsumerAdapter",
    "negotiate_version",
    "parse_semver",
]


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class Ctr002AdapterError(ZephyrBaseError):
    """适配器配置/输入/版本非法（占位错误码，纪律⑦留对账批）。"""

    error_code = "ZA-SH-0055"


# ──────────────────────────────────────────────────────────────────────────────
# 延迟导入 FactorSignal（避免循环 + 允许 typing-only）
# ──────────────────────────────────────────────────────────────────────────────


def _factor_signal_cls():
    from zephyr.shared.contracts.factor_signal import FactorSignal

    return FactorSignal


# ──────────────────────────────────────────────────────────────────────────────
# Schema 元数据（从 CTR-002 FactorSignal 推导，MVP 内嵌避免运行时 codegen 依赖）
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class FieldRule:
    """单字段校验规则。"""

    field: str
    rule: str  # prob_range | non_empty_str | finite_number | semver_str | datetime_type


@dataclass(frozen=True)
class SchemaSource:
    """CTR-002 契约 Schema 真源（手工推导，与 cross_layer_contracts.yaml 对齐）。"""

    current_version: str
    required_fields: tuple[str, ...]
    optional_defaults: tuple[tuple[str, Any], ...]
    field_rules: tuple[FieldRule, ...]

    def default_for(self, field_name: str) -> Any:
        for k, v in self.optional_defaults:
            if k == field_name:
                return v
        raise KeyError(field_name)

    def optional_default_map(self) -> dict[str, Any]:
        """可选字段默认值映射视图（tuple 真源的便捷投影）。"""
        return dict(self.optional_defaults)


CTR002_SCHEMA: Final[SchemaSource] = SchemaSource(
    current_version="1.0",
    required_fields=(
        "as_of_date",
        "factor_id",
        "idempotency_key",
        "raw_value",
        "symbol",
    ),
    optional_defaults=(
        ("confidence", 1.0),
        ("exceptions", ("",)),  # 实际构造时须为 list[str]（defaults_factory 规避共享可变态）
        ("extra", {}),
        ("factor_version", "1.0"),
        ("is_valid", True),
        ("max_retries", 2),
        ("normalized_value", None),
        ("rank_pct", None),
        ("retry_policy", "linear"),
        ("schema_version", "1.0"),
        ("timeout_ms", 3000),
        ("trace_context", None),
    ),
    field_rules=(
        FieldRule("confidence", "prob_range"),
        FieldRule("rank_pct", "prob_range"),
        FieldRule("raw_value", "finite_number"),
        FieldRule("factor_id", "non_empty_str"),
        FieldRule("schema_version", "semver_str"),
        FieldRule("as_of_date", "datetime_type"),
    ),
)


# ──────────────────────────────────────────────────────────────────────────────
# semver 解析与版本协商
# ──────────────────────────────────────────────────────────────────────────────


def parse_semver(version: str | None) -> tuple[int, int] | None:
    """解析语义版本为 (major, minor)。

    支持 "X.Y" / "X.Y.Z"（忽略 patch）；失败返回 None。
    """
    if not version:
        return None
    parts = str(version).strip().split(".")
    if len(parts) not in (2, 3):
        return None
    try:
        major = int(parts[0])
        minor = int(parts[1])
        return major, minor
    except ValueError:
        return None


def negotiate_version(
    incoming: str | None,
    supported: Sequence[str],
) -> str:
    """版本协商三态：exact / compatible / unsupported。

    - exact：incoming 等于任一 supported 版本。
    - compatible：同 major，minor 在 supported 范围内。
    - unsupported：major 不一致 或 incoming 非法。
    """
    parsed = parse_semver(incoming)
    if parsed is None:
        return "unsupported"
    in_major, _ = parsed
    supported_parsed = [parse_semver(v) for v in supported]
    # exact
    for sp in supported_parsed:
        if sp is not None and sp == parsed:
            return "exact"
    # compatible（同 major）
    for sp in supported_parsed:
        if sp is not None and sp[0] == in_major:
            return "compatible"
    return "unsupported"


# ──────────────────────────────────────────────────────────────────────────────
# 适配裁决
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AdaptationVerdict:
    """单条 payload 适配结果。"""

    accepted: bool
    version_action: str  # exact/compatible/unsupported
    signal: Any | None  # FactorSignal | None
    missing_fields: tuple[str, ...] = ()
    filled_defaults: tuple[str, ...] = ()
    absorbed_extras: tuple[str, ...] = ()
    reason: str = ""


@dataclass(frozen=True)
class BatchVerdict:
    """批量适配结果。"""

    total: int
    accepted_signals: tuple[Any, ...]  # tuple[FactorSignal, ...]
    rejections: tuple[Any, ...]  # tuple[AdaptationVerdict, ...]


@dataclass(frozen=True)
class Rejection:
    """批量中单个拒绝项（含索引）。"""

    index: int
    version_action: str
    missing_fields: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class ContractChange:
    """契约变更事件。"""

    contract_id: str
    old_version: str
    new_version: str
    note: str


class Ctr002ConsumerAdapter:
    """CTR-002 消费契约适配器。

    Args:
        supported_versions: 消费端支持的 schema 版本（默认 ("1.0",)）。
    """

    def __init__(
        self,
        supported_versions: Sequence[str] = ("1.0",),
    ) -> None:
        if not supported_versions:
            raise Ctr002AdapterError("supported_versions 不得为空")
        for v in supported_versions:
            if parse_semver(v) is None:
                raise Ctr002AdapterError(f"非法版本号: {v!r}")
        self._supported = tuple(supported_versions)
        self._subscribers: list[Callable[[ContractChange], None]] = []
        self._current_version: str = CTR002_SCHEMA.current_version
        self._audit_log: list[str] = []

    @property
    def current_version(self) -> str:
        return self._current_version

    @property
    def audit_log(self) -> tuple[str, ...]:
        return tuple(self._audit_log)

    # ── 订阅 ──────────────────────────────────────────────────────────

    def subscribe(self, callback: Callable[[ContractChange], None]) -> None:
        if not callable(callback):
            raise Ctr002AdapterError("callback 必须为可调用对象")
        self._subscribers.append(callback)

    # ── 发布变更 ──────────────────────────────────────────────────────

    def publish_contract_change(self, new_version: str, note: str) -> int:
        """发布契约版本变更通知，返回实际通知到的订阅者数量。

        Raises:
            Ctr002AdapterError: 版本降级、非法版本。
        """
        pv = parse_semver(new_version)
        if pv is None:
            raise Ctr002AdapterError(f"非法版本号: {new_version!r}")
        old_v = parse_semver(self._current_version)
        assert old_v is not None  # current_version 恒合法
        if pv <= old_v:
            raise Ctr002AdapterError(f"版本不得降级: {self._current_version} -> {new_version}")
        change = ContractChange(
            contract_id="CTR-002",
            old_version=self._current_version,
            new_version=new_version,
            note=note,
        )
        self._current_version = new_version
        self._audit_log.append(f"CHANGE: CTR-002 {change.old_version}->{change.new_version} | {note}")
        notified = 0
        for cb in self._subscribers:
            try:
                cb(change)
                notified += 1
            except Exception:  # noqa: BLE001
                logger.warning(
                    "CTR-002 变更通知失败: subscriber=%s",
                    getattr(cb, "__qualname__", str(cb)),
                    exc_info=True,
                )
        return notified

    # ── 单条适配 ──────────────────────────────────────────────────────

    def adapt(self, payload: Mapping[str, Any]) -> AdaptationVerdict:
        """把原始 payload 适配为 FactorSignal。

        流程：
          1. 版本协商（major 不兼容即拒）。
          2. 必填字段检查。
          3. 可选字段补默认值（list/dict 每次构造独立实例）。
          4. 未知字段收编到 extra。
          5. 字段取值域校验（confidence/rank_pct 等）。
          6. 构造 FactorSignal 产出。

        Raises:
            Ctr002AdapterError: payload 非 mapping / 异常输入。
        """
        if not isinstance(payload, Mapping):
            raise Ctr002AdapterError("payload 必须为 Mapping")
        incoming_version = payload.get("schema_version", self._current_version)
        action = negotiate_version(str(incoming_version), self._supported)
        if action == "unsupported":
            return AdaptationVerdict(
                accepted=False,
                version_action="unsupported",
                signal=None,
                reason=f"不支持的版本: {incoming_version!r} (supported={self._supported})",
            )

        # 必填检查
        missing: list[str] = []
        for req in CTR002_SCHEMA.required_fields:
            if req not in payload:
                missing.append(req)
        if missing:
            return AdaptationVerdict(
                accepted=False,
                version_action=action,
                signal=None,
                missing_fields=tuple(missing),
                reason=f"缺少必填字段: {missing}",
            )

        # 组装 kwargs
        kwargs: dict[str, Any] = {}
        filled: list[str] = []
        for req in CTR002_SCHEMA.required_fields:
            kwargs[req] = payload[req]
        for opt_name, opt_default in CTR002_SCHEMA.optional_defaults:
            if opt_name in payload:
                kwargs[opt_name] = payload[opt_name]
            else:
                filled.append(opt_name)
                # 规避共享可变默认值
                if opt_name in ("exceptions",):
                    kwargs[opt_name] = []
                elif opt_name == "extra":
                    kwargs[opt_name] = {}
                else:
                    kwargs[opt_name] = opt_default

        # 未知字段收编 extra
        known = set(CTR002_SCHEMA.required_fields)
        known.update({k for k, _ in CTR002_SCHEMA.optional_defaults})
        extras: dict[str, Any] = {}
        absorbed: list[str] = []
        for k, v in payload.items():
            if k not in known:
                absorbed.append(k)
                extras[k] = v
        if extras:
            current_extra = kwargs.get("extra", {})
            if current_extra is None:
                current_extra = {}
            merged = dict(current_extra)
            merged.update(extras)
            kwargs["extra"] = merged

        # 字段取值域校验
        validation = self._validate_fields(kwargs)
        if validation:
            return AdaptationVerdict(
                accepted=False,
                version_action=action,
                signal=None,
                reason=validation,
            )

        FactorSignal = _factor_signal_cls()
        signal = FactorSignal(**kwargs)
        return AdaptationVerdict(
            accepted=True,
            version_action=action,
            signal=signal,
            filled_defaults=tuple(filled),
            absorbed_extras=tuple(absorbed),
        )

    # ── 批量适配 ──────────────────────────────────────────────────────

    def adapt_batch(self, payloads: Sequence[Mapping[str, Any]]) -> BatchVerdict:
        accepted: list[Any] = []
        rejections: list[Rejection] = []
        for idx, pl in enumerate(payloads):
            verdict = self.adapt(pl)
            if verdict.accepted:
                accepted.append(verdict.signal)
            else:
                rejections.append(
                    Rejection(
                        index=idx,
                        version_action=verdict.version_action,
                        missing_fields=verdict.missing_fields,
                        reason=verdict.reason,
                    )
                )
        return BatchVerdict(
            total=len(payloads),
            accepted_signals=tuple(accepted),
            rejections=tuple(rejections),
        )

    # ── 字段校验 ──────────────────────────────────────────────────────

    def _validate_fields(self, kwargs: dict[str, Any]) -> str:
        for rule in CTR002_SCHEMA.field_rules:
            val = kwargs.get(rule.field)
            if val is None:
                continue
            if rule.rule == "prob_range":
                if not (0.0 <= float(val) <= 1.0):
                    return f"{rule.field}={val!r} 不在 [0,1] 范围内"
            elif rule.rule == "non_empty_str":
                if not isinstance(val, str) or not val.strip():
                    return f"{rule.field}={val!r} 必须为非空字符串"
            elif rule.rule == "finite_number":
                try:
                    v = float(val)
                except (ValueError, TypeError):
                    return f"{rule.field}={val!r} 必须为数值"
                if v != v:  # NaN
                    return f"{rule.field}={val!r} 不得为 NaN"
            elif rule.rule == "semver_str":
                if parse_semver(val) is None:
                    return f"{rule.field}={val!r} 必须为合法语义版本"
            elif rule.rule == "datetime_type":
                if not isinstance(val, datetime.datetime):
                    return f"{rule.field}={val!r} 必须为 datetime 类型"
        return ""
