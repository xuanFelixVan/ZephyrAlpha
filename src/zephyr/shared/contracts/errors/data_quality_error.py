# [A_module] module_id=MOD-SHR_data_quality_error | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md | §

# [MODULE] zephyr.shared.contracts.errors.data_quality_error

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS] data.default_quality_gate

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
CTR-ERR-001: DataQualityError / 行情质量门禁不通过错误

L00 行情质量门禁不通过时抛出的错误。包含具体的质量缺陷分类和恢复建议。

SSoT: cross_layer_contracts.yaml → CTR-ERR-001
Version: 1.0
Status: AUTO-GENERATED — DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当 L00 的质量门禁检测到行情数据异常时，MUST 抛出 DataQualityError 而非普通 Exception。 每个 DataQualityError 携带 failure_reason（具体原因枚举）和 recovery_hint（恢复建议）。 禁止静默丢弃——必须显式抛出，让 L02 和 L12 Telemetry 感知。
"""


# ==== BEGIN CODGEN:CTR-ERR-001 ====
from dataclasses import dataclass, field

from typing import Optional

from zephyr.shared.contracts.core.trace_context import TraceContext
# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-05"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/data_quality_error.py

CTR-ERR-001: DataQualityError / 行情质量门禁不通过错误

L00 行情质量门禁不通过时抛出的错误。包含具体的质量缺陷分类和恢复建议。

SSoT: cross_layer_contracts.yaml -> CTR-ERR-001
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    当 L00 的质量门禁检测到行情数据异常时，MUST 抛出 DataQualityError 而非普通 Exception。 每个 DataQualityError 携带 failure_reason（具体原因枚举）和 recovery_hint（恢复建议）。 禁止静默丢弃——必须显式抛出，让 L02 和 L12 Telemetry 感知。
"""

@dataclass(frozen=True)
class DataQualityError:
    error_id: str
    failure_reason: str
    idempotency_key: str
    quality_score: float
    recovery_hint: str
    symbol: str
    failed_field: Optional[str] = None
    failed_value: Optional[str] = None
    schema_version: str = "1.0"
    trace_context: Optional[TraceContext] = None

# ==== END CODGEN:CTR-ERR-001 ====





































