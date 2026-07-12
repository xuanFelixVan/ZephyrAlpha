# [BLUEPRINT] MOD-L00-001 | docs/03_modules/_domain-data/datasource-core/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.quality_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_quality_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: data
# category: quality_interface
# status: active
# created: "2026-05-05"
# ---

"""D_DATA — Data Quality Gate

数据质量门禁。对 D_DATA 接入的原始市场数据进行质量校验，不合格数据拒绝下发。

核心职责：
  - 行情质量评分（缺失检测、异常值检测、时间戳校验）
  - 停牌/涨跌停检测
  - 质量问题分级告警：DataQualityError（CTR-ERR-001）

CTR 契约：
  生产者 — CTR-ERR-001 (DataQualityError) -> D_FACTOR

依赖方向：D_DATA 内部——provider -> quality_gate -> 下游 D_FACTOR/D_SIGNAL/D_RESEARCH
"""

from __future__ import annotations

import abc
import inspect
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import ClassVar


class QualityFailureReason(str, Enum):
    MISSING_TICK = "missing_tick"
    STALE_DATA = "stale_data"
    OUTLIER_PRICE = "outlier_price"
    TIMESTAMP_FUTURE = "timestamp_future"
    SUSPENSION_DETECTED = "suspension_detected"
    VOLUME_ZERO = "volume_zero"


class RecoveryHint(str, Enum):
    RETRY = "RETRY"
    SKIP_SYMBOL = "SKIP_SYMBOL"
    SWITCH_SOURCE = "SWITCH_SOURCE"
    HALT = "HALT"


@dataclass(frozen=True)
class QualityReport:
    """单条数据质量校验报告"""

    symbol: str
    quality_score: float  # 0.0 ~ 1.0，< 0.7 不合格
    passed: bool
    failure_reason: QualityFailureReason | None = None
    failed_field: str | None = None
    failed_value: str | None = None
    recovery_hint: RecoveryHint = RecoveryHint.SKIP_SYMBOL
    checked_at: datetime = field(default_factory=datetime.utcnow)


class DataQualityGate(abc.ABC):
    """数据质量门禁抽象基类（OCP 扩展点）

    实现者要求：
      - check(): 逐条校验行情数据，返回 QualityReport
      - quality_score < 0.7 时 MUST 抛出 DataQualityError（CTR-ERR-001）
      - 停牌标的 MUST 标记 is_suspended=True 而非静默跳过
      - 每种 failure_reason 必须给出对应的 recovery_hint

    安全约束：
      - 禁止静默丢弃数据——不合格必须显式抛出 CTR-ERR-001
      - 禁止降级质量阈值——0.7 是硬编码最低线
    """

    QUALITY_THRESHOLD: ClassVar[float] = 0.7
    _registry: ClassVar[dict[str, type[DataQualityGate]]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not inspect.isabstract(cls) and "__gate_id__" in cls.__dict__:
            DataQualityGate._registry[cls.__gate_id__] = cls

    @abc.abstractmethod
    def check(
        self,
        symbol: str,
        open_price: Decimal,
        high: Decimal,
        low: Decimal,
        close: Decimal,
        volume: Decimal,
        timestamp: datetime,
        prev_close: Decimal | None = None,
    ) -> QualityReport:
        """对单条行情数据执行质量校验"""
        ...

    @staticmethod
    def is_within_normal_range(price: Decimal, prev_close: Decimal, limit_pct: Decimal = Decimal("0.10")) -> bool:
        """涨跌停范围校验（A 股 ±10%，科创板/创业板 ±20%）"""
        if prev_close <= Decimal("0"):
            return False
        change_pct = abs(price - prev_close) / prev_close
        return change_pct <= limit_pct


__all__ = [
    "DataQualityGate",
    "QualityFailureReason",
    "QualityReport",
    "RecoveryHint",
]
