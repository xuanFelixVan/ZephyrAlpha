from __future__ import annotations

from dataclasses import dataclass, field

from zephyr.shared.contracts.trace_context import TraceContext
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-04"
# generated_by: codegen from cross-layer-contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/data_quality_error.py

CTR-ERR-001: DataQualityError / 行情质量门禁不通过错误

L00 行情质量门禁不通过时抛出的错误。包含具体的质量缺陷分类和恢复建议。

SSoT: cross-layer-contracts.yaml → CTR-ERR-001
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当 L00 的质量门禁检测到行情数据异常时，MUST 抛出 DataQualityError 而非普通 Exception。 每个 DataQualityError 携带 failure_reason（具体原因枚举）和 recovery_hint（恢复建议）。 禁止静默丢弃——必须显式抛出，让 L02 和 L12 Telemetry 感知。
"""

@dataclass(frozen=True)
class DataQualityError:
    error_id: str
    symbol: str
    failure_reason: str
    quality_score: float
    recovery_hint: str
    schema_version: str = "1.0"
    failed_field: Optional[str] = None
    failed_value: Optional[str] = None
    trace_context: Optional[TraceContext] = None
