---
module_id: KE-869
status: active
title: 3.4 旧版编号废弃对照表
category: governance
ttl: permanent
---

# 3.4 旧版编号废弃对照表

3.4 旧版编号废弃对照表

以下对照表列出 docs 目录编号中的**业务域抽屉**与 L{XX} 层编号的对应关系。这些 docs 目录编号在架构语义中**已废弃**，仅作为物理路径保留。

| docs 目录编号 | docs 目录名称 | 对应 L{XX} 层 | 映射说明 |
|-------------|-------------|-------------|---------|
| `09_data_platform` | 数据平台 | **L00** Data Source | 数据接入/存储/质量 → L00 统一管辖 |
| `10_research_and_factor_lab` | 研究与因子实验室 | **L02** Alpha Factor + **L09** Research Innovation | 因子研究 → L02；实验框架 → L09 |
| `11_model_and_ml_platform` | 模型与 ML 平台 | **L11** ML Platform | 直接对应 |
| `12_strategy_and_portfolio` | 策略与组合 | **L03** Signal Generation + **L05** Portfolio Construction | 信号规则 → L03；组合优化 → L05 |
| `13_execution_and_order_lifecycle` | 执行与订单生命周期 | **L06** Trade Execution | 直接对应 |
| `14_reporting_and_distribution` | 报告与分发 | **L07** Post-Trade Analytics | 直接对应 |
| `07_ai_engineering`（已合并至 `03_modules/_b_track_interfaces/`） | AI 工程与代理运维 | **L08** Human-AI Interface + **L11** ML Platform | Agent 交互 → L08；ML 引擎 → L11 |

以下 docs 目录编号**不存在 L{XX} 对应**（因为它们属于治理/架构/平台/知识层，不是业务域层）：

| docs 目录编号 | 性质 | 说明 |
|-------------|------|------|
| `00_governance` | 治理层 | 横向贯穿，不对应任何单一 L{XX} |
| `01_policies_and_standards` | 治理层 | 横向贯穿 |
| `02_enterprise_architecture` | 架构层 | 架构元数据，不是业务层 |
| `03_domain_architecture` | 架构层 | 领域架构视图 |
| `03_modules` | 架构层 | 模块按 L{XX} 子目录组织 |
| `06_security_and_identity` | 平台能力层 | 横向贯穿 |
| `07_sre_and_platform_ops` | 平台能力层 | 横向贯穿 |
| `08_knowledge` | 知识沉淀层 | 跨时空知识资产 |
| `16_compliance_and_legal` | 治理层 | 横向贯穿（部分与 L10 重叠） |
| `17_risk_and_controls` | 治理层 | 横向贯穿（部分与 L04 重叠） |
| `18_audit_and_evidence` | 治理层 | 横向贯穿 |
| `19_development_workspace` | ~~过程区~~ 已删除 | 迁至项目外部独立目录（2026-05-02） |
| `99_archive` | 历史区 | 归档区 |

---
