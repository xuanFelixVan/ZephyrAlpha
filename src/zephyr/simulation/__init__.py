# [A_module] module_id=MOD-UNK_simulation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L13-001 | docs/03_modules/_domain-simulation/experiment-core/blueprint.md
# [MODULE] zephyr.simulation
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [CONSUMERS]
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""实验 Experimentation
=====================================

域量化架构 · 实验 自动化实验层

职责
----
AI 时代的"自动化实验"层：Scout Agent 自动抓取外部资讯 + 内部 repo diff，
设计并执行对照实验（A/B 测试、因子消融、策略变种）、沉淀实验结论到 KMS。

架构真源
--------
architecture_model/index.yaml（53域清单，layer_id 属性枚举 D_DATA-实验）

CTR 契约依赖声明（承重墙标记）
------------------------------
作为生产者（Producer）：
  - CTR-P1-014 (ExperimentResult) — 实验结论，发布至 D_RESEARCH/D_ML_TRAIN

作为消费者（Consumer）：
  - CTR-001 (NormalizedMarketData) — 实验需要市场数据上下文
  - CTR-P1-004/005 (ModelServing) — Scout Agent 调用 D_ML_TRAIN 模型推断
  - CTR-P1-013 (TelemetryEmitter) — 实验运行数据上报 遥测

与 D_ML_TRAIN/遥测 的关系
-----------------
D_ML_TRAIN ml_platform       : ML 生命周期（训练/推理/模型注册）
遥测 system-telemetry  : 系统可观测性
实验 experimentation   : 自动化实验（Scout + A/B + 结论沉淀）

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策： 目录双轨治理
"""

from __future__ import annotations

__all__ = [
    "pipeline_base",
]
