# [BLUEPRINT] MOD-CON-002 | docs/03_modules/_domain_contracts/ctr002_producer_validator/blueprint.md | §
# [MODULE] zephyr.shared.contracts.ctr002_producer_validator
# [DOMAIN] D_CONTRACTS
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.shared.contracts.ctr002_consumer_adapter; zephyr.shared.contracts.factor_signal
# [CONSUMERS] D_FACTOR 生产侧（运行时装配批接线；ctr002_producer MOD-L02-001 挂接候选）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 违约信号不出厂（collect 模式剔除+错误契约返回，strict 模式抛异常阻断）; Schema 源与 MOD-CON-001 同一实例不另造; PIT 校验 aware 归一本地 naive 比较; metrics_hook 异常不阻断验证; frozen
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ProducerValidationError(ZA-SH-0056，携 error_contract 结构化违约清单)
# [TESTS] tests/contracts/test_ctr002_producer_validator.py
# [A_module] module_id=MOD-CON-002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
D-SIGNAL-158 CTR-002生产侧契约验证（B2-05118 → MOD-CON-002）。

FactorSignal 出厂前强制验证：字段完整性/取值域/时间戳 PIT 校验；违约阻断
（strict 模式抛 ProducerValidationError）或错误契约返回（collect 模式产
ErrorContract 结构化违约清单，违约信号不出厂）；验证指标入 telemetry
（计数器 + metrics_hook 注入，hook 异常不阻断验证）。

与消费侧版本适配器（MOD-CON-001 ctr002_consumer_adapter）**共用同一 Schema 源**：
基础取值域规则直接复用 CTR002_SCHEMA.field_rules（同一实例），生产侧仅增补
PIT 时间戳/整型域/其余必填非空规则——规则源不另造、不漂移。

非职责：
  - 不做因子计算/信号构造（MOD-L02-001 ctr002_producer 职责）
  - 不做消费侧版本协商/字段容忍（MOD-CON-001 职责）

依据: D-SIGNAL §1.1；construction_backlog_dig.tsv B2-05118。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: signal 参数
#   fields: 参数 signal，类型注解 Any
#   code: ctr002_producer_validator.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: strict 参数
#   fields: 参数 strict（无注解）
#   code: ctr002_producer_validator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① Ctr002ProducerValidator
#   name_en: Ctr002ProducerValidator
#   intro: CTR-002 生产侧契约验证器。
#   desc: CTR-002 生产侧契约验证器。 Args: clock: 时钟注入（PIT 校验基准，默认 datetime.datetime.now）。 metrics_hook: 指标注…；公共方法（定义序）: schema,…
#   inputs: clock metrics_hook
#   outputs: 返回值
# - id: A2
#   name_zh: ② validate_ctr002_producer
#   name_en: validate_ctr002_producer
#   intro: 便捷函数：默认验证器验证单条 FactorSignal。
#   desc: 便捷函数：默认验证器验证单条 FactorSignal。；源码 L308-L310
#   inputs: signal strict
#   outputs: ValidationReport
#   （注：A2 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: ValidationReport
#   name_en: ValidationReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: D_FACTOR 生产侧（运行时装配批接线；ctr002_producer MOD-L02-001 挂接候选）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass
from typing import Any, Callable, Final, Sequence

from zephyr.shared.contracts.ctr002_consumer_adapter import CTR002_SCHEMA, SchemaSource, parse_semver
from zephyr.shared.foundation.errors import ZephyrBaseError

logger = logging.getLogger(__name__)

__all__: Final = [
    "ErrorContract",
    "ProducerValidationError",
    "Ctr002ProducerValidator",
    "ValidationReport",
    "validate_ctr002_producer",
]


# ──────────────────────────────────────────────────────────────────────────────
# 错误契约与异常
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ErrorContract:
    """违约错误契约（结构化返回，CTR-ERR 思路）。"""

    contract_id: str
    producer_domain: str
    violations: tuple[str, ...]
    factor_id: str = ""
    symbol: str = ""


class ProducerValidationError(ZephyrBaseError):
    """CTR-002 生产侧验证违约阻断（占位错误码，纪律⑦留对账批）。"""

    error_code = "ZA-SH-0056"

    def __init__(self, message: str, error_contract: ErrorContract | None = None) -> None:
        super().__init__(message)
        self.error_contract = error_contract


@dataclass(frozen=True)
class ValidationReport:
    """单条 FactorSignal 验证结果。"""

    ok: bool
    violations: tuple[str, ...] = ()
    error_contract: ErrorContract | None = None


def _make_error_contract(
    violations: Sequence[str],
    *,
    factor_id: str = "",
    symbol: str = "",
) -> ErrorContract:
    """构造 CTR-002 违约错误契约。"""
    return ErrorContract(
        contract_id="CTR-002",
        producer_domain="D_FACTOR",
        violations=tuple(violations),
        factor_id=factor_id,
        symbol=symbol,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 生产侧增补规则（基础取值域规则 = CTR002_SCHEMA.field_rules，同一 Schema 源）
# ──────────────────────────────────────────────────────────────────────────────

#: 生产侧增补：其余必填字段非空字符串
_EXTRA_NON_EMPTY_STR: Final = ("symbol", "idempotency_key")
#: 生产侧增补：整型取值域（字段名, 下界含）
_EXTRA_INT_DOMAINS: Final = (("max_retries", 0), ("timeout_ms", 1))


def _to_local_naive(ts: datetime.datetime) -> datetime.datetime:
    """aware → 本地 naive（astimezone 系统时区）；naive 原样。"""
    if ts.tzinfo is None:
        return ts
    return ts.astimezone().replace(tzinfo=None)


class Ctr002ProducerValidator:
    """CTR-002 生产侧契约验证器。

    Args:
        clock: 时钟注入（PIT 校验基准，默认 datetime.datetime.now）。
        metrics_hook: 指标注入 ``hook(name, value)``（异常不阻断验证）。
    """

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        metrics_hook: Callable[[str, int], None] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._metrics_hook = metrics_hook
        self._total_validated = 0
        self._total_violations = 0

    @property
    def schema(self) -> SchemaSource:
        """Schema 源（与 MOD-CON-001 同一实例）。"""
        return CTR002_SCHEMA

    @property
    def total_validated(self) -> int:
        return self._total_validated

    @property
    def total_violations(self) -> int:
        return self._total_violations

    # ── 验证 ──────────────────────────────────────────────────────────

    def validate(self, signal: Any, *, strict: bool = False) -> ValidationReport:
        """验证单条 FactorSignal。

        Args:
            signal: 待验证信号（FactorSignal 实例）。
            strict: True 时违约即抛 ProducerValidationError（违约阻断）；
                False 时返回携 ErrorContract 的报告（错误契约返回，违约信号不出厂）。

        Raises:
            ProducerValidationError: strict=True 且存在违约。
        """
        violations = self._collect_violations(signal)
        self._total_validated += 1
        self._emit("ctr002_producer.validated", 1)
        ok = not violations
        if not ok:
            self._total_violations += 1
            self._emit("ctr002_producer.violation", 1)
        error_contract = None
        if not ok:
            error_contract = _make_error_contract(
                violations,
                factor_id=str(getattr(signal, "factor_id", "") or ""),
                symbol=str(getattr(signal, "symbol", "") or ""),
            )
            if strict:
                raise ProducerValidationError(
                    f"CTR-002 生产侧验证违约（{len(violations)} 条）: {violations[0]}",
                    error_contract=error_contract,
                )
        return ValidationReport(ok=ok, violations=tuple(violations), error_contract=error_contract)

    def validate_batch(self, signals: Sequence[Any], *, strict: bool = False) -> list[ValidationReport]:
        """批量验证（逐条独立，互不影响）。"""
        return [self.validate(s, strict=strict) for s in signals]

    # ── 规则执行 ──────────────────────────────────────────────────────

    def _collect_violations(self, signal: Any) -> list[str]:
        violations: list[str] = []
        from zephyr.shared.contracts.factor_signal import FactorSignal

        if not isinstance(signal, FactorSignal):
            return [f"not_factor_signal: {type(signal).__name__} 非 FactorSignal 实例"]

        # ① 基础取值域（与消费侧同一 Schema 源 CTR002_SCHEMA.field_rules）
        for rule in CTR002_SCHEMA.field_rules:
            val = getattr(signal, rule.field, None)
            if val is None:
                continue
            msg = self._check_rule(rule.field, rule.rule, val)
            if msg:
                violations.append(msg)

        # ② 生产侧增补：其余必填字段非空
        for name in _EXTRA_NON_EMPTY_STR:
            val = getattr(signal, name, None)
            if not isinstance(val, str) or not val.strip():
                violations.append(f"{name}={val!r} 必须为非空字符串")

        # ③ 生产侧增补：整型取值域
        for name, lower in _EXTRA_INT_DOMAINS:
            val = getattr(signal, name, None)
            if val is None:
                continue
            if not isinstance(val, int) or isinstance(val, bool) or val < lower:
                violations.append(f"{name}={val!r} 必须为 ≥{lower} 的整数")

        # ④ 生产侧增补：PIT 时间戳（as_of_date 不得晚于当前时点）
        as_of = signal.as_of_date
        if isinstance(as_of, datetime.datetime):
            now = _to_local_naive(self._clock())
            if _to_local_naive(as_of) > now:
                violations.append(f"as_of_date={as_of!r} PIT违规：晚于当前时点 {now!r}")
        else:
            violations.append(f"as_of_date={as_of!r} 必须为 datetime 类型")
        return violations

    @staticmethod
    def _check_rule(field_name: str, rule: str, val: Any) -> str:
        if rule == "prob_range":
            if not isinstance(val, (int, float)) or isinstance(val, bool) or not (0.0 <= float(val) <= 1.0):
                return f"{field_name}={val!r} 不在 [0,1] 范围内"
        elif rule == "non_empty_str":
            if not isinstance(val, str) or not val.strip():
                return f"{field_name}={val!r} 必须为非空字符串"
        elif rule == "finite_number":
            if not isinstance(val, (int, float)) or isinstance(val, bool) or not math.isfinite(float(val)):
                return f"{field_name}={val!r} 必须为有限数值"
        elif rule == "semver_str":
            if parse_semver(val) is None:
                return f"{field_name}={val!r} 必须为合法语义版本"
        elif rule == "datetime_type":
            if not isinstance(val, datetime.datetime):
                return f"{field_name}={val!r} 必须为 datetime 类型"
        return ""

    # ── 指标 ──────────────────────────────────────────────────────────

    def _emit(self, name: str, value: int) -> None:
        if self._metrics_hook is None:
            return
        try:
            self._metrics_hook(name, value)
        except Exception:  # noqa: BLE001
            logger.warning("ctr002_producer metrics_hook 异常（不阻断验证）", exc_info=True)


def validate_ctr002_producer(signal: Any, *, strict: bool = False) -> ValidationReport:
    """便捷函数：默认验证器验证单条 FactorSignal。"""
    return Ctr002ProducerValidator().validate(signal, strict=strict)
