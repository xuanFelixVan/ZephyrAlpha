"""
ZephyrAlpha 门禁子包
====================

职责：提供 AI Agent 决策门禁——Agent 执行关键操作前进行合规检查与风险评估。

子模块：
  - circuit_breaker.py           断路器门禁（熔断/恢复状态机）
  - contract_template_manager.py  合约模板管理器
  - gate_engine.py                门禁引擎（通用门禁流程编排）
  - task_completion_gate.py       任务完成门禁（提交前合规检查）
  - g1_ingest.yaml                G1 摄入门禁策略配置
  - g2_triage.yaml                G2 分诊门禁策略配置
  - g3_evaluate.yaml              G3 评估门禁策略配置
  - g4_activate.yaml              G4 激活门禁策略配置
  - g5_extract.yaml               G5 提取门禁策略配置

架构归属：B-track 独立能力，bounded_context: true——所有 Layer 中
的 Gate 操作均通过本子包接口调用，禁止跨层直接操作门禁逻辑。
统一决策入口：任何涉及风险控制的 AI 决策在此汇总评估。
"""
