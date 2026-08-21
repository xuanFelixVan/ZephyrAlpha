# [A_module] module_id=MOD-L13-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L13-001 | docs/03_modules/_domain_simulation/blueprint.md
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
"""

实验 Experimentation
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

命名消歧：本包为实验管线抽象（ExperimentPipelineBase/策略仿真/Scout 实验），非 QMT 模拟盘撮合；模拟盘链路见 ex_core/trading_session.py + data/tick_subscriber.py。

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策： 目录双轨治理

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: NormalizedMarketData 市场数据上下文（CTR-001 契约消费）
#   fields: 标准化行情数据，作实验对照上下文
#   code: cross_layer_contracts.yaml CTR-001
# - id: I2
#   name: 模型推断结果（CTR-P1-004/005 ModelServing）
#   fields: Scout Agent 调用 D_ML_TRAIN 模型推断输出
#   code: cross_layer_contracts.yaml CTR-P1-004/005
# 层: 算法
# - id: A1
#   name_zh: ① 包入口子模块聚合导出
#   name_en: simulation/__init__.py eager imports
#   intro: 急切导入 4 个实验子模块并列入包级 __all__
#   desc: __init__.py L51-54 导入 strategy_simulator/scenario_generator/risk_simulator/result_analyzer（pipeline_base 仅列 __all__）
#   inputs: I1 I2
#   outputs: 实验子模块命名空间
# - id: A2
#   name_zh: ② 自动化对照实验链
#   name_en: experimentation pipeline
#   intro: Scout 抓外部资讯+repo diff，设计执行 A/B 测试/因子消融/策略变种并沉淀结论到 KMS
#   desc: 场景生成 → 策略模拟 → 风险模拟 → 结果分析（蓝图职责，子模块分工执行）
#   inputs: A1
#   outputs: 实验结论与运行遥测
# 层: 输出
# - id: O1
#   name_zh: ExperimentResult 实验结论契约
#   name_en: CTR-P1-014
#   intro: 实验结论发布给研究与训练域
#   downstream: D_RESEARCH/D_ML_TRAIN（CTR-P1-014 生产者）
# - id: O2
#   name_zh: 实验运行遥测上报
#   name_en: CTR-P1-013 TelemetryEmitter
#   intro: 实验运行数据上报系统可观测性
#   downstream: 遥测 system-telemetry（CTR-P1-013 消费者）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
# A2 --> O2
"""

from __future__ import annotations

from zephyr.simulation import (
    result_analyzer,  # noqa: F401 — 包级导出
    risk_simulator,  # noqa: F401
    scenario_generator,  # noqa: F401
    strategy_simulator,  # noqa: F401
)

__all__ = [
    "pipeline_base",
    "strategy_simulator",
    "scenario_generator",
    "risk_simulator",
    "result_analyzer",
]
