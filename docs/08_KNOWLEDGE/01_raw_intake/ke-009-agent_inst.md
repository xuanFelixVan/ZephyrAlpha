---
module_id: KE-009
title: 5.2.4 关键方法论文件速查
category: agent_instruction
ttl: permanent
---

# 5.2.4 关键方法论文件速查

5.2.4 关键方法论文件速查

> 以下文件定义了项目级核心方法论。按需查阅，不在每次 session 冷启动时全量加载。

| 场景 | 方法论文件 | 说明 |
|------|---------|------|
| 全局基线 | `docs/01_policies_and_standards/meta/governance_methodology_standard.yaml` | 思维基线——最优先行原则（先判断最优→再检查约束）+ MTH-001~013 |
| 全局基线 | `docs/01_policies_and_standards/meta/meta-standard-constitution-standard.md` | 规则体系最高元规则——什么进宪法（ABS）、什么进登记表（COND/REC） |
| 文档规则 | `docs/01_policies_and_standards/rules/trae_029_doc_operation_security.yaml` | 文档控制8原则——SSoT唯一、创建前必查、先读后改、引用不复制 |
| 文档规则 | `docs/01_policies_and_standards/meta/document_structure_standard.yaml` | 标准文档模板元标准——L1/L2/L3三层模板体系 |
| 施工规则 | `docs/01_policies_and_standards/meta/behavior_boundaries_standard.yaml` | ABS绝对禁止（48条）+ COND条件禁止 + REC推荐做法 |
| 施工规则 | `docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml` | 编码安全标准——UTF-8强制、BOM禁止、PowerShell陷阱 |
| 施工规则 | `docs/01_policies_and_standards/governance/ai/ai-hallucination-self-check-policy.md` | AI幻觉自检清单——6项（路径/模块ID/接口/依赖/SSoT/编号） |
| 门禁规则 | `docs/01_policies_and_standards/governance/architecture/gate-strategy-standard.md` | 5级门禁策略（G0~G4）+ Gate Pipeline 触发条件 |
| 门禁规则 | `docs/01_policies_and_standards/governance/module/module-admission-policy.md` | 模块准入门控——四级筛选（MAD-001~005） |
| 门禁规则 | `docs/01_policies_and_standards/governance/module/module-lifecycle-policy.md` | 模块生命周期——8阶段状态机（planned→archived） |
| 架构决策 | `docs/01_policies_and_standards/governance/architecture/adr-protocol.md` | ADR协议——谁提ADR、怎么审批、怎么归档 |
| 架构决策 | `docs/01_policies_and_standards/governance/architecture/architecture-review-policy.md` | 架构评审门控——触发条件、评审清单（6项）、否决条件（7项） |
| 仲裁规则 | `docs/01_policies_and_standards/meta/rule_classification_and_arbitration_standard.yaml` | 规则冲突裁决——五维分类+推导链（stability→layer→scope→Owner） |
| 审计规则 | `docs/01_policies_and_standards/meta/rule_verification_standard.yaml` | 规则验证标准——V1~V4四级验证（自动化阻断/警告/人工审查/审计抽样） |
| 交接协议 | `docs/01_policies_and_standards/governance/ai/handoff-protocol.md` | 跨会话交接协议——HandoffPackage 8必填字段 |
| 脚本系统 | `scripts/governance/index.md` | 80+审计脚本体系总入口 + run_all.py调度 + 12维度审计框架 |
