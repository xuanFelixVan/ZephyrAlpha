# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
# [MODULE] zephyr.shared.contracts.core.trace_context
# [DOMAIN] D_SHARED
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
# [A_module] module_id=MOD-SHR_trace_context | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

# ==== BEGIN CODGEN:CTR-TRACE-001 ====
from dataclasses import dataclass
from datetime import datetime

# ---
# layer: cross_cutting
# category: data_contract
# status: auto_generated
# created: "2026-05-05"
# generated_by: codegen from cross_layer_contracts.yaml
# ---
"""
ZephyrAlpha — shared/contracts/trace_context.py

CTR-TRACE-001: TraceContext / 全链路追踪上下文

跨所有数据层的全链路追踪上下文。D_DATA 在首次产生数据时生成，后续每层追加 span。支持反向追溯：'这笔订单是因为哪个因子的哪个信号在哪个时刻产生的'。

SSoT: cross_layer_contracts.yaml -> CTR-TRACE-001
Version: 1.0
Status: AUTO-GENERATED -- DO NOT EDIT BY HAND
       Any manual changes will be overwritten by codegen.

AI Prompt
---------
    所有跨层传递的数据对象中都嵌入了一个可选的 trace_context 字段。 如果你是 D_DATA（数据入口），你 MUST 在首次产生 NormalizedMarketData 时创建新的 TraceContext，生成 UUID 作为 trace_id。 如果你是 D_FACTOR/D_SIGNAL/D_PORTFOLIO_CORE/D_EXECUTION_CORE/D_REPORTING（中间层），你在处理数据时 MUST： 1. 从上游数据中取出 trace_context； 2. 为本层创建一个新的 span（span_id 用 UUID，记录 parent_span_id 指向上游）； 3. 设置 root_cause_layer 为本层的标识（如 "factor"）； 4. 将更新后的 trace_context 嵌入到本层产出的数据对象中。 不要丢掉 trace_context——没有它，排障等于瞎猜。
"""


@dataclass(frozen=True)
class TraceContext:
    created_at: datetime
    idempotency_key: str
    service_name: str
    span_id: str
    trace_id: str
    parent_span_id: str | None = None
    schema_version: str = "1.0"


# ==== END CODGEN:CTR-TRACE-001 ====
