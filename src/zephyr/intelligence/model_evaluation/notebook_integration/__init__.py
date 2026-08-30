# [A_module] module_id=MOD-GOV-init | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-036 | docs/03_modules/_cross_layer/model-capability-exam/blueprint.md
# [MODULE] zephyr.intelligence.model_evaluation.notebook_integration
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
D_RESEARCH Research & Innovation
=====================================

域量化架构 · D_RESEARCH 研究创新层

职责
----
量化研究实验：新因子发现、策略回测框架、学术论文复现、idea 孵化与验证。
[N/A — 骨架占位，尚未实现]

CTR 契约依赖声明（承重墙标记）
------------------------------
本层是以下跨层数据契约的来源或目标——Phase B 实现前 MUST 阅读对应 YAML 定义。
任何修改本层接口的行为 MUST 先通过 ContractImpactAnalyzer 评估影响范围。

作为消费者（Consumer）：
  - CTR-001  NormalizedMarketData      ← D_DATA

作为全局配置消费者（Consumer）：
  - CTR-P1-010  SystemConfiguration    ← 基础设施

SSoT: cross_layer_contracts.yaml v3.0

架构归属
--------
LPC 双轨架构 C 轨（业务脊柱 · 带 l<NN>_ 前缀）
架构决策： 目录双轨治理

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包内子模块公共符号
#   fields: import 再导出符号: annotations, BacktestEngineBase, BacktestResult, FactorDiscovery
#   code: __init__.py import L69
# 层: 算法
# - id: A1
#   name_zh: ① 包公共面再导出
#   name_en: __init__ re-export
#   intro: 再导出 BacktestEngineBase, BacktestResult, FactorDiscovery（共 3 符号）
#   desc: __init__ import L69；__all__ 3 项（AST 事实）
#   inputs: I1
#   outputs: __all__ 公共符号表
# 层: 输出
# - id: O1
#   name_zh: 公共 API 面（3 符号）
#   name_en: __all__
#   intro: BacktestEngineBase, BacktestResult, FactorDiscovery
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.backtest.core.engine_base import BacktestEngineBase, BacktestResult, FactorDiscovery

__all__ = ["BacktestEngineBase", "BacktestResult", "FactorDiscovery"]
