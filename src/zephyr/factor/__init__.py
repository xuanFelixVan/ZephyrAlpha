# [A_module] module_id=MOD-L02-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] zephyr.factor
# [DOMAIN] D_FACTOR
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""

ZephyrAlpha — D_FACTOR Alpha Factor Layer

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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: factor_base 子模块符号 4个
#   fields: FactorBase / FactorMeta / FactorRegistry / autodiscover_factors（因子基类/元类/注册表/自动发现）
#   code: zephyr.factor.factor_base L52
# - id: I2
#   name: bus_factor_defense 子模块符号 7个
#   fields: BusFactorRisk / DecisionLog / ModuleOwnership / OpsRunbook / create_decision_log / evaluate_bus_factor / generate_runbook
#   code: zephyr.factor.bus_factor_defense L43
# 层: 算法
# - id: A1
#   name_zh: ① 包级聚合再导出
#   name_en: zephyr.factor.__init__
#   intro: 把两个子模块的符号汇成 zephyr.factor 统一入口，并声明 __all__
#   desc: import 两子模块 11 个符号 → __all__ 声明（含 4 个子模块名占位）；CODEGEN-GUARD 标记禁止重生成，factor_base 为 SSoT
#   inputs: I1 I2
#   outputs: zephyr.factor 包级公共命名空间
#   invariant: 包级导出以 factor_base 为 SSoT（base.py shim 已消除）
# 层: 输出
# - id: O1
#   name_zh: zephyr.factor 包公共 API
#   name_en: __all__ 11项
#   intro: 因子层对外统一出口，下游按 CTR-002 契约消费 FactorSignal
#   downstream: D_SIGNAL / D_RISK / D_PORTFOLIO_CORE（CTR-002 FactorSignal 生产方）；D_DATA（CTR-BP-001~003 背压）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

# 5.143.5 修复: 补充 __all__ 声明的符号导入, 避免调用方 ImportError
from zephyr.factor.bus_factor_defense import (
    BusFactorRisk,
    DecisionLog,
    ModuleOwnership,
    OpsRunbook,
    create_decision_log,
    evaluate_bus_factor,
    generate_runbook,
)
from zephyr.factor.factor_base import FactorBase, FactorMeta, FactorRegistry, autodiscover_factors
from zephyr.factor.factor_availability_monitor import FactorAvailabilityMonitor
from zephyr.factor.factor_factory import FactorFactory
from zephyr.factor.factor_production_pipeline import FactorProductionPipeline
from zephyr.factor.wq_alpha_87 import WqAlpha87

__all__ = [
    "FactorBase",
    "FactorMeta",
    "FactorRegistry",
    "alpha_signal_pipeline",
    "autodiscover_factors",
    "factor_base",
    "momentum_factor",
    "value_factor",
    "technical_indicators",
    "bus_factor_defense",
]

# CODEGEN-GUARD: __init__-manual-exports
# 包级导出以 factor_base 为 SSoT（base.py 已删除，2026-07-14 shim 消除）
# CODEGEN-GUARD: CTR-declarations-manual
# DO NOT regenerate: CTR declarations are manually curated SSoT annotations

__all__.append("FactorAvailabilityMonitor")

__all__.append("FactorFactory")

__all__.append("FactorProductionPipeline")

__all__.append("WqAlpha87")
