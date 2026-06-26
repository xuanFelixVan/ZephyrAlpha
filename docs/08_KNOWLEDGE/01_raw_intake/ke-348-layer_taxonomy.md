---
module_id: KE-348
status: active
title: 4.1 14-layer taxonomy / 14 层分层体系
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 4.1 14-layer taxonomy / 14 层分层体系

4.1 14-layer taxonomy / 14 层分层体系

> **SSoT 声明**：模块属性（子模块清单、接口签名、优先级、运行平面归属）的
> **Single Source of Truth** 是 [`architecture_model/layers/*.yaml`](architecture_model/layers/)。
> 本节及任何其他 Markdown 文件中的模块属性描述均为**只读引用**，不得作为权威来源。
> 如有冲突，以 YAML 文件为准。

> **📋 14 层模块完整清单**：见 [`architecture_model/layers/`](architecture_model/layers/) 目录下的 YAML 定义文件（L00~L13 + shared），每个文件包含模块 ID、职责、优先级、运行时平面归属等结构化数据。

**关键设计决策（永久保留）**：

- **L00 ACL（R33/J5）**：`connectors/` 定位为 Anti-Corruption Layer，将外部 Vendor 数据格式"翻译"为内部 canonical schema，防止 Vendor 命名约定渗透到核心业务层。选 ACL 而非 Adapter/Facade 的原因：Adapter 只做接口适配不做领域模型翻译，Facade 是简化调用复杂度的门面——ACL 的核心价值是**将外部领域概念翻译为内部领域语言**。
- **L05 strategic/（R31）**：strategic asset allocation 本质是 portfolio construction 的长周期版本（BlackRock Aladdin P1 模式），业界无顶级机构将其独立成层。
- **L05 meta_router/（N11/OQ-023）**：元策略路由归入 L05 语义最准、工程最简——与 `optimization/` / `rebalancing/` 共用 `StrategyRegistry`，天然协同。
- **L10 命名（R32）**：业界绝大多数顶级机构 L10 均命名为 `compliance`；`governance` 是组织级决策行为，进入 docs 不进代码层。
- **L10 ai_security/（OQ-076/KBG-0009）**：AISG 防泄密子系统，治理归属跨 09-GOV 全三层。
- **L11 scout/（OQ-079）**：Scout Agent 自动抓取外部资讯 + 内部 repo diff，喂养 KMS L1 事实层。
- **L12 命名（OQ-030/R31）**：`system_telemetry` 比 `observability` 更精确——强调"结构化指标流给 AI 读"。

| Layer ID | Layer Name | Directory |
|:---|:---|:---|
| L00 | Data Source | `data/` |
| L01 | Infrastructure | `infra_ops/` |
| L02 | Alpha Factor | `factor/` |
| L03 | Signal Generation | `signal/` |
| L04 | Risk Management | `risk/` |
| L05 | Portfolio Construction | `pf_core/` |
| L06 | Trade Execution | `ex_core/` |
| L07 | Post-Trade Analytics | `reporting/` |
| L08 | Human-AI Interface | `frontend/` |
| L09 | Research & Innovation | `research/` |
| L10 | Governance & Compliance | `compliance/` |
| L11 | ML Platform | `ml_train/` |
| L12 | System Telemetry | `infra_ops/` |
| L13 | Experiment Pipeline | `simulation/` |
| — | Shared | `shared/` |
