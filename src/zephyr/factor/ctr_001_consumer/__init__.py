# [A_module] module_id=MOD-UNK_ctr_001_consumer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor.ctr_001_consumer
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""ZephyrAlpha — D_FACTOR Alpha Factor Layer

SSoT: cross_layer_contracts.yaml v3.0

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策： 目录双轨治理

Phase B 骨架 — 因子基类 / 元类 / 注册表 / 自动发现

CTR 契约依赖声明（承重墙标记）
------------------------------
本层是以下跨层数据契约的来源或目标。任何修改本层接口的行为 MUST 先通过 ContractImpactAnalyzer 评估影响范围。

作为消费者（Consumer）：
  - CTR-001  NormalizedMarketData    ← D_DATA
  - CTR-ERR-001  DataQualityError    ← D_DATA

作为生产者（Producer）：
  - CTR-002  FactorSignal            -> D_SIGNAL, D_RISK, D_PORTFOLIO_CORE
  - CTR-BP-001~003  Backpressure     -> D_DATA（背压信号——暂停/降速/恢复数据推送）
  - CTR-ERR-002  FactorComputationError -> D_SIGNAL

"""

from __future__ import annotations

# STUB: from .factor_base import (FactorBase, FactorMeta, FactorRegistry, autodiscover_factors)
# Reason: factor_base.py does not exist in ctr_001_consumer/; this is a CTR consumer stub package

__all__ = []

# CODEGEN-GUARD: __init__-manual-exports
# 包级导出以 factor_base 为 SSoT（base.py 为 codegen 占位；禁止混用两套 FactorBase）
# CODEGEN-GUARD: CTR-declarations-manual
# DO NOT regenerate: CTR declarations are manually curated SSoT annotations
