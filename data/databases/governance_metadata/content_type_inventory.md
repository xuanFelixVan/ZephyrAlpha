# 内容类型清查报告 — docs/01_policies_and_standards/

> 生成时间: 2026-06-13
> 扫描范围: 68 个 MD 文件
> 分类体系: A1-A7, B1-B10, C1-C5, D1-D7, E1-E8, F1-F6, G1-G6, H1-H5, I1-I6

---

## 一、逐文件内容类型清单

### 1. ~~domains/L00_data_source/~~（已迁移 2026-07-09）

> **路径迁移**：原 `domains/L00_data_source/` 物理目录已废弃（14层架构降级）。
> 内容已合并到 `rules/trae_050_domain_policy_data_factor.yaml`（DOM-L00-001）和 `rules/trae_049_ops_domain_manual.yaml`（DOM-L00-002）。

| 原文件 | module_id | 迁移目标 | 说明 |
|------|-----------|---------|------|
| governance/data_source_connection_policy.md | DOM-L00-001 | trae_050_domain_policy_data_factor.yaml | 数据源连接策略：ABS/COND规则、分层分类、超时/重试表、SSoT声明、消费者注册表 |
| operational/connector_onboarding_runbook.md | DOM-L00-002 | trae_049_ops_domain_manual.yaml | 连接器入职Runbook：步骤式入职流程、验证检查清单、回滚程序 |

### 2. ~~domains/L02_alpha_factor/~~（已迁移 2026-07-09）

> **路径迁移**：原 `domains/L02_alpha_factor/` 物理目录已废弃（14层架构降级）。
> 内容已合并到 `rules/trae_050_domain_policy_data_factor.yaml`（DOM-L02-001）和 `rules/trae_049_ops_domain_manual.yaml`（DOM-L02-002）。

| 原文件 | module_id | 迁移目标 | 说明 |
|------|-----------|---------|------|
| governance/factor_quality_policy.md | DOM-L02-001 | trae_050_domain_policy_data_factor.yaml | 因子质量策略：4维度质量检查、衰减检测、度量指标 |
| operational/factor_onboarding_runbook.md | DOM-L02-002 | trae_049_ops_domain_manual.yaml | 因子入职Runbook：灰度部署、相关性检查、配置参数 |

### 3. ~~domains/L04_risk_management/~~（已迁移 2026-07-09）

> **路径迁移**：原 `domains/L04_risk_management/` 物理目录已废弃（14层架构降级）。
> 内容已合并到 `rules/trae_051_domain_policy_risk_backtest.yaml`（DOM-L04-001）和 `rules/trae_049_ops_domain_manual.yaml`（DOM-L04-002）。

| 原文件 | module_id | 迁移目标 | 说明 |
|------|-----------|---------|------|
| governance/risk_limits_policy.md | DOM-L04-001 | trae_051_domain_policy_risk_backtest.yaml | 风险限额策略：止损/敞口/杠杆约束、阈值设置 |
| operational/stop_loss_config_runbook.md | DOM-L04-002 | trae_049_ops_domain_manual.yaml | 止损配置Runbook：YAML配置模板、边界值检查 |

### 4. ~~domains/L07_post_trade_analytics/~~（已迁移 2026-07-09）

> **路径迁移**：原 `domains/L07_post_trade_analytics/` 物理目录已废弃（14层架构降级）。
> 内容已合并到 `rules/trae_051_domain_policy_risk_backtest.yaml`（DOM-L07-001）和 `rules/trae_049_ops_domain_manual.yaml`（DOM-L07-002）。

| 原文件 | module_id | 迁移目标 | 说明 |
|------|-----------|---------|------|
| governance/post_trade_reporting_policy.md | DOM-L07-001 | trae_051_domain_policy_risk_backtest.yaml | 盘后报告策略：SLA截止期、临时报告触发条件 |
| operational/analytics_pipeline_runbook.md | DOM-L07-002 | trae_049_ops_domain_manual.yaml | 分析管线Runbook：幂等检查、部分失败处理 |

### 5. governance/ai/

| 文件 | module_id | 内容类型 | 说明 |
|------|-----------|---------|------|
| ai_hallucination_detection_rules.md | GOV-AI-009 | A1,A2,A3,A4, B1,B2,B6, C1,C3,C5, D1,D3, E1,E5, F1,F6, I5 | AI幻觉检测规则：10条HC规则、严重度分级、5层门禁架构 |
| ai_hallucination_self_check_policy.md | GOV-AI-003 | A1,A2,A3, B1,B6, C1,C3, D1,D3, E1, F1, I3 | AI幻觉自检策略：10项自检清单、已知幻觉模式表 |
| dual_editor_collaboration_policy.md | PSP-005 | A1,A2,A3, B1,B6, C3, D1, E1, G6, H2, I3 | 双编辑器协作策略：Cursor/Trae分工、编码安全规则 |
| handoff_protocol.md | GOV-AI-008 | A1,A2,A3, B1,B6, C3, D1, E1, G1,G4, I3 | 交接协议：8字段HandoffPackage YAML格式 |
| model_routing_policy.md | GOV-AI-002 | A1,A2,A3,A4, B1,B3,B4, C1,C3, D1,D2, E1, H2, I3 | 模型路由策略：路由决策树、降级/回退机制 |

### 6. governance/architecture/

| 文件 | module_id | 内容类型 | 说明 |
|------|-----------|---------|------|
| architecture_review_policy.md | GOV-ARCH-002 | A1,A2,A3, B1,B6, C1,C3, D1, E1,E5, I5 | 架构评审策略：评审触发条件、检查清单、否决条件 |
| architecture_versioning_policy.md | GOV-ARCH-003 | A1,A2,A3, B1,B6, C1, D1, E1,E7, G2, I5 | 架构版本策略：版本编号规则、变更日志要求 |
| ctr_injection_rules_policy.md | GOV-ARC-CTR-001 | A1,A2,A3,A4, B1,B6, C2,C5, D1,D4,D5,D6,D7, E1,E2,E3,E4,E5,E6,E7,E8, G1,G4, I5 | CTR注入规则策略：YAML结构化7域注入规则、受控枚举 |
| gate_strategy_standard.md | GOV-ARCH-006 | A1,A2,A3, B1,B2,B6, C1,C3, D1,D5, E1,E5,E6, G1,G4, I5 | 门禁策略标准：5级门禁体系(G1-G5)、YAML schema |
| infra_layer_dependency_rules_policy.md | GOV-ARCH-010 | A1,A2,A3,A4, B1,B6, C1,C3, D1,D5, E1,E5, I5 | 基础层依赖规则：DEPTH_0/DEPTH_1依赖规则、EventBus模式 |
| phase_transition_protocol.md | GOV-ARCH-005 | A1,A2,A3, B1,B2,B5,B6, C1,C3, D1,D5, E1,E5,E6, I5 | 阶段转换协议：双门禁协议、稳定性阶段 |
| system_qualification_standard.md | GOV-ARCH-004 | A1,A2,A3, B1,B6, C1,C3, D1,D5, E1,E5, I5 | 系统资质标准：工程/架构资质框架 |

### 7. governance/compliance/

| 文件 | module_id | 内容类型 | 说明 |
|------|-----------|---------|------|
| audit_protocol.md | GOV-CMP-003 | A1,A2,A3, B1,B6, C1,C3, D1,D5, E1,E4, F4,F5, G1,G4, I5 | 审计协议：12维度177脚本4类审计、报告模板 |
| audit_trail_policy.md | GOV-CMP-002 | A1,A2,A3, B1,B6, C1,C3, D1,D5, E1,E4, I5 | 审计追踪策略：AUD-001~004规则 |
| regulatory_taxonomy_policy.md | GOV-CMP-001 | A1,A2,A3, B1, C2, D1,D2, E1, I5 | 监管分类策略：按市场分类的监管框架 |

### 8. governance/data/

| 文件 | module_id | 内容类型 | 说明 |
|------|-----------|---------|------|
| data_lineage_policy.md | GOV-DATA-002 | A1,A2,A3, B1,B6, C1,C3, D1,D5, E1,E4, I5 | 数据血缘策略：DLG-001~003规则 |
| data_quality_policy.md | GOV-DATA-001 | A1,A2,A3, B1,B6, C1,C3, D1,D5, E1,E4, F4,F5, I5 | 数据质量策略：5质量维度、DQA-001~003 |
| data_retention_policy.md | GOV-DATA-003 | A1,A2,A3, B1,B6, C1,C3, D1,D5, E1,E4, H3, I5 | 数据保留策略：保留期表格、DRP-001~003 |

### 9. governance/document/

| 文件 | module_id | 内容类型 | 说明 |
|------|-----------|---------|------|
| compression_workflow_standard.md | GOV-DOC-011 | A1,A2,A3,A4,A5,A6, B1,B6, C5, D1,D5, E1, F6, G1,G3,G5, I5 | 压缩工作流标准：蓝图铁律(B-00~B-22)、10字段代码头、反模式 |
| directory_structure_standard.md | GOV-DOC-002 | A1,A2,A3, B1,B6, C2, D1,D5, E1, G1, I5 | 目录结构标准：LPC双轨架构、反幻觉路径映射 |
| document_control_policy.md | GOV-DOC-009 | A1,A2,A3,A4, B1,B6, C2, D1,D5,D6, E1,E2,E3,E4,E5,E6,E7,E8, G4, I5 | 文档控制策略：DOC-001~009原则、depends_on格式规范 |
| document_discovery_policy.md | GOV-DOC-010 | A1,A2,A3, B1,B6, C2, D1,D5,D6, E1, I3 | 文档发现策略：3条发现路径、module_id搜索范式 |
| document_lifecycle_standard.md | GOV-DOC-006 | A1,A2,A3,A4,A5,A6, B1,B2,B5,B6,B9, C1,C3, D1,D5,D6, E1,E2,E3,E4,E5,E6,E7,E8, G2,G6, I5,I6 | 文档生命周期标准：TTL 4级分类、文档状态机、LATEST覆写模式 |
| encoding_safety_standard.md | GOV-DOC-005 | A1,A2,A3, B1,B5, D3, E1, F1,F2, G1,G6, H2, I3,I5 | 编码安全标准：UTF-8强制、损坏识别4信号、git checkout修复流 |
| file_naming_standard.md | GOV-DOC-003 | A1,A2,A3,A4,A6, B3,B6, C2,C5, D1,D6, E1,E7, G1,G2,G5, I5,I6 | 文件命名标准：kebab-case规则、GATE-11检测规则(13条)、TECH_VERSION_TOKENS白名单 |
| file_operation_safety_policy.md | GOV-DOC-007 | A1,A2,A3, B1,B5,B6, C3, D1,D4, E1, F6, H1, I3 | 文件操作安全策略：删除三问/三步、移动两步、不可触碰锚文件 |
| file_path_standard.md | GOV-DOC-004 | A1,A2,A3, B6, C2, D1,D5, E1, G1,G5, I5,I6 | 文件路径标准：21种文件类型→路径映射、根目录白名单、路径-所有权映射 |
| unified_numbering_standard.md | GOV-DOC-001 | A1,A2,A3, B3, C1,C2,C4,C5, D1,D5,D6, E1,E7, G1,G2,G4, I5 | 统一编号标准：L00-L13层编号、D-XXX域编号、违规检测(NUM-V01~V06) |

### 10. governance/engineering/

| 文件 | module_id | 内容类型 | 说明 |
|------|-----------|---------|------|
| code_construction_standards.md | GOV-ENG-001 | A1,A2,A3,A4,A5,A6, B1,B6,B7, C1, D5,D7, E1,E5, F6, G1,G2,G4, I3,I5 | 代码构建标准：命名约定、类型注解3层强制、SSoT守卫、反幻觉代码规则 |
| code_restructuring_safety_policy.md | GOV-ENG-004 | A1,A2,A3, B1,B5,B6,B7, C1, D1,D4,D5, E1, F6, G5, I3,I5 | 代码重构安全策略：9条安全铁律、5步价值分析法、真源声明表(27条) |
| expansion_1500_module_spec.md | GOV-ENG-003 | A2,A3, B1,B6, C1,C3, D1,D5, E1, F4, G4, I4 | 1500模块扩展规格：命名空间验证、depgraph性能基准、容量分析 |
| file_header_standard.md | GOV-ENG-002 | A1,A2,A3, B1,B2,B6, C1,C2, D1,D5, E1,E5,E6, G1,G2,G3,G4,G5, I5 | 文件头标准：6种头部格式、10字段代码头、头部状态机、枚举定义 |

### 11. governance/module/

| 文件 | module_id | 内容类型 | 说明 |
|------|-----------|---------|------|
| ai_behavior_iron_policy.md | GOV-MOD-002 | A1,A2,A3,A4,A5,A6,A7, B4,B6, C1,C3,C5, D1,D4, E1,E2,E3,E4,E5,E6,E7,E8, F6, I5,I6 | AI行为铁律：11条铁律(IRN-001~011)、零残留原则(ZR-001~009)、ABS映射表 |
| module_admission_policy.md | GOV-MOD-001 | A1,A2,A3,A4,A5,A6,A7, B1,B3,B6, C1,C3,C5, D1,D4,D5, E1,E2,E3,E4,E5, G4, I3,I5 | 模块准入策略：4级准入筛选(MAD-001~004)、5项否决条件、功能域重叠4步判断 |
| module_injection_rules_policy.md | GOV-MOD-005 | A1,A2,A3,A4, B1,B2,B6, C1,C2,C5, D1,D4,D5,D6,D7, E1,E2,E3,E4,E5,E6,E7,E8, G1,G4, I5 | 模块注入规则策略：8条INJ规则、YAML结构化策略、受控枚举、消费者注册表 |
| module_interface_contract_policy.md | GOV-MOD-004 | A1,A2,A3,A4,A5,A6,A7, B1,B5,B9, C1,C2, D1,D4,D5, E1,E2,E3,E4,E5,E6,E7,E8, F6, G4, I3,I5 | 模块接口契约策略：7条IFC规则、契约生命周期、语义版本、跨层契约注册表 |
| module_lifecycle_policy.md | GOV-MOD-003 | A1,A2,A3,A4,A5,A6, B1,B2,B5,B9, C1,C2,C5, D1,D4,D5, E1,E2,E3,E4,E5,E6,E7,E8, G4, I3,I5 | 模块生命周期策略：8个生命周期阶段、反向转换限制、退役7步流程 |
| multi_registry_synchronization_standard.md | GOV-MOD-007 | A1,A2,A3, B1,B6, C2, D1,D4,D5, E1,E2,E3, F6, G4, I5 | 多注册表同步标准：15类注册表、12操作×14注册表写入矩阵、4个验证脚本（⚠️文件存在编码损坏） |

### 12. governance/security/

| 文件 | module_id | 内容类型 | 说明 |
|------|-----------|---------|------|
| access_control_policy.md | GOV-SEC-002 | A1,A2,A3,A4, C1,C3, D1, E1,E5, I5 | 访问控制策略：5角色、ACS-001~005规则、权限矩阵(7资源×5角色) |
| secret_management_policy.md | GOV-SEC-001 | A1,A2,A3,A4,A5, B1,B9, C1,C3, D2, E1,E4, H2,H3, I5 | 密钥管理策略：SEC-001~006规则、密钥轮换周期、泄漏响应6步流程 |
| security_incident_response_policy.md | GOV-SEC-003 | A1,A2,A3,A4, B1,B4,B9,B10, C1,C3, D1, E1, H1,H4, I5 | 安全事件响应策略：SIR-001~004规则、P0-P3事件分级、P0响应7步流程 |

### 13. governance/task/

| 文件 | module_id | 内容类型 | 说明 |
|------|-----------|---------|------|
| task_card_standard.md | GOV-TASK-001 | A1,A2,A3,A4,A5,A6,A7, B1,B2,B3,B5,B6,B7, C1,C3, D1,D5,D7, E1,E5, F1,F2,F3,F4,F5,F6, G1,G2,G3,G4,G5, H1,H3, I3,I5 | 任务卡标准：70字段模板、8步工作流、MTH-006深挖协议、G0-G7门禁、PERF-001诊断SOP |
| task_lifecycle_standard.md | GOV-TASK-004 | A1,A2,A3,A4, B2,B4, C1,C3, D1, E1,E5, I5 | 任务生命周期标准：取消权限、优先级仲裁、P0膨胀防护 |
| task_closure_standard.md | GOV-TASK-005 | A1,A2, B1,B5,B6,B7, C3, D1, E1, I3 | 任务关闭标准：关闭4条件、清理3步法、验证门禁 |

### 14. meta/

| 文件 | module_id | 内容类型 | 说明 |
|------|-----------|---------|------|
| behavior_boundaries_standard.md | PS-STD-003 | A1,A3,A7, C2,C4,C5, D1, E1,E5,E6, I1,I4 | 行为边界标准：绝对/条件禁止分类法、ABS条目作为所有禁止行为SSoT |
| blueprint_architecture_standard.md | PS-STD-005 | A2,A3, B3, C1,C2,C4, D1,D5, E1,E7, G1,G2, I1,I4 | 蓝图架构标准：3层蓝图金字塔(系统/域/模块)、目录放置、ID命名 |
| document_structure_standard.md | PS-STD-002 | A2,A3, C2,C5, D1, E1,E2,E3,E4,E5,E6,E7,E8, G1,G4,G5, I1,I4 | 文档结构标准：L1/L2/L3模板体系、标准子类型、治理机制 |
| glossary_glossary.md | META-GLS-001 | C2, D1, E1, I4 | 术语表：术语SSoT、ISO 11179对齐 |
| governance_methodology_standard.md | PS-STD-011 | A1,A2,A3, C5, D1, E1, I1,I2 | 治理方法论标准：2条最高原则+13条核心原则(MTH-001~013) |
| governance_metrics_standard.md | PS-STD-006 | A2,A3, C1,C3, D1, E1,E4, F4,F5, I4 | 治理度量标准：6个KPI、测量方法、报告频率、告警阈值 |
| meta_standard_constitution_standard.md | PS-STD-000 | A1,A2,A3, C2,C4,C5, D1, E1,E5,E6, I1,I2 | 元标准宪法：宪法vs注册表二元分类(不可逆性判据)、最高优先级元标准 |
| metadata_registry.md | PS-STD-001 | A2,A3, C2,C5, D1,D5, E1,E7, G1,G4, I4 | 元数据注册表：双SSoT(YAML=PS-REG-012=数据, MD=PS-STD-001=规则)、4域(A-D) |
| rule_classification_and_arbitration_standard.md | PS-STD-004 | A3, C2,C4,C5, D1, E1, I1,I2 | 规则分类与仲裁标准：5维分类(域/层/范围/稳定性/执行者)、冲突仲裁推导链 |
| rule_lifecycle_and_change_standard.md | PS-STD-009 | A1,A2,A3,A4, B2,B5,B9, C1,C5, D1, E1,E2,E3,E4, I5 | 规则生命周期与变更标准：规则生命周期状态机、P0-P3变更审批、退役级联 |
| rule_verification_standard.md | PS-STD-012 | A2,A3, B6,B7, C1,C3, D1, E1,E4, F2, I4 | 规则验证标准：5级验证(V1-V5)、验证频率矩阵、违规响应 |
| terminology_mapping_reference.md | GOV-027 | C2, D1, E1, I4 | 术语映射参考：双向映射(自然语言↔行业术语) |

### 15. operational/devops/

| 文件 | module_id | 内容类型 | 说明 |
|------|-----------|---------|------|
| architecture_change_playbook.md | OPS-DEV-002 | A2,A3, B1, C1,C3, D1, E1, H1 | 架构变更Playbook：L1-L4变更分级、审批要求 |

### 16. operational/vibe_coding/

| 文件 | module_id | 内容类型 | 说明 |
|------|-----------|---------|------|
| ai_incident_and_emergency_runbook.md | OPS-VC-004 | A1,A2, B1,B4,B9,B10, C1,C3, D1,D3, E1, F1, H1,H4 | AI事件与应急Runbook：AI异常+系统应急统一响应、幻觉/越权/违规场景 |
| vibe_coding_gate_runbook.md | OPS-VC-005 | A1,A2, B6,B7,B8, C3, D1, E1,E5, H4 | Vibe Coding门禁Runbook：Session启动检查清单、上下文加载、GATE覆盖映射 |
| vibe_coding_session_state_runbook.md | OPS-VC-002 | A2,A3, B2, C1, D1, E1, I3 | Vibe Coding会话状态Runbook：5状态会话机(INIT/ACTIVE/PAUSED/COMPLETED/FAILED) |

---

## 二、内容类型统计汇总

### 全部发现的内容类型（共49种）

| 编号 | 内容类型 | 中文名称 | 包含文件数 | 占比 |
|------|---------|---------|:---------:|:----:|
| **A1** | 禁止项/Prohibitions | 禁止项 | 50 | 73.5% |
| **A2** | 强制项/Mandatory items | 强制项 | 66 | 97.1% |
| **A3** | 约束/Constraints | 约束 | 60 | 88.2% |
| **A4** | 条件规则/Conditional rules | 条件规则 | 22 | 32.4% |
| **A5** | 默认值/Default values | 默认值 | 9 | 13.2% |
| **A6** | 异常处理/Exception handling | 异常处理 | 8 | 11.8% |
| **A7** | 覆盖/绕过规则/Override rules | 覆盖规则 | 5 | 7.4% |
| **B1** | 步骤式程序/Step-by-step procedures | 步骤式程序 | 61 | 89.7% |
| **B2** | 状态机/State machines | 状态机 | 11 | 16.2% |
| **B3** | 决策树/Decision trees | 决策树 | 6 | 8.8% |
| **B4** | 升级/Escalation | 升级 | 5 | 7.4% |
| **B5** | 回滚/Rollback | 回滚 | 11 | 16.2% |
| **B6** | 检查清单/Checklists | 检查清单 | 62 | 91.2% |
| **B7** | 验证/Verification | 验证 | 7 | 10.3% |
| **B8** | 入职/Onboarding | 入职 | 3 | 4.4% |
| **B9** | 弃用/Deprecation | 弃用 | 7 | 10.3% |
| **B10** | 事件响应/Incident response | 事件响应 | 2 | 2.9% |
| **C1** | 层级/等级体系/Tier systems | 层级体系 | 42 | 61.8% |
| **C2** | 分类法/Category taxonomies | 分类法 | 21 | 30.9% |
| **C3** | 优先级分类/Priority classifications | 优先级分类 | 39 | 57.4% |
| **C4** | 范围定义/Scope definitions | 范围定义 | 5 | 7.4% |
| **C5** | 规则分类/Rule classification | 规则分类 | 15 | 22.1% |
| **D1** | 交叉引用表/Cross-reference tables | 交叉引用表 | 68 | 100% |
| **D2** | 框架映射/Framework mapping | 框架映射 | 3 | 4.4% |
| **D3** | 症状-原因映射/Symptom-cause mapping | 症状-原因映射 | 4 | 5.9% |
| **D4** | 消费者注册表/Consumer registries | 消费者注册表 | 11 | 16.2% |
| **D5** | 依赖声明/Dependency declarations | 依赖声明 | 32 | 47.1% |
| **D6** | 模块ID引用/Module ID references | 模块ID引用 | 8 | 11.8% |
| **D7** | 脚本/命令引用/Script/command references | 脚本引用 | 9 | 13.2% |
| **E1** | SSoT声明/SSoT declarations | SSoT声明 | 68 | 100% |
| **E2** | 变更同步规则/Change sync rules | 变更同步规则 | 14 | 20.6% |
| **E3** | 修改条件/Modification conditions | 修改条件 | 14 | 20.6% |
| **E4** | 审查周期/Review cycles | 审查周期 | 19 | 27.9% |
| **E5** | AI自治声明/AI autonomy declarations | AI自治声明 | 18 | 26.5% |
| **E6** | 稳定性声明/Stability declarations | 稳定性声明 | 12 | 17.6% |
| **E7** | 版本控制/Version control | 版本控制 | 11 | 16.2% |
| **E8** | 文档所有权/Document ownership | 文档所有权 | 9 | 13.2% |
| **F1** | 错误模式/Error patterns | 错误模式 | 5 | 7.4% |
| **F2** | 诊断程序/Diagnostic procedures | 诊断程序 | 3 | 4.4% |
| **F3** | 根因分析/Root cause analysis | 根因分析 | 1 | 1.5% |
| **F4** | 度量指标/Metrics | 度量指标 | 6 | 8.8% |
| **F5** | 质量维度/Quality dimensions | 质量维度 | 4 | 5.9% |
| **F6** | 反模式/Anti-patterns | 反模式 | 9 | 13.2% |
| **G1** | 文件格式规范/File format specs | 文件格式规范 | 17 | 25.0% |
| **G2** | 命名约定/Naming conventions | 命名约定 | 8 | 11.8% |
| **G3** | 头部/尾部标准/Header/footer standards | 头部标准 | 3 | 4.4% |
| **G4** | 字段定义/Field definitions | 字段定义 | 15 | 22.1% |
| **G5** | 模板结构/Template structures | 模板结构 | 7 | 10.3% |
| **G6** | 编码规则/Encoding rules | 编码规则 | 3 | 4.4% |
| **H1** | Runbook程序/Runbook procedures | Runbook程序 | 9 | 13.2% |
| **H2** | 配置参数/Configuration parameters | 配置参数 | 8 | 11.8% |
| **H3** | 超时/阈值设置/Timeout/threshold settings | 超时阈值 | 5 | 7.4% |
| **H4** | 监控/告警/Monitoring/alerting | 监控告警 | 3 | 4.4% |
| **I1** | 原则/Principles | 原则 | 6 | 8.8% |
| **I2** | 背景/Background | 背景 | 3 | 4.4% |
| **I3** | 示例/Examples | 示例 | 19 | 27.9% |
| **I4** | 术语表/Glossary | 术语表 | 8 | 11.8% |
| **I5** | 变更历史/Change history | 变更历史 | 40 | 58.8% |
| **I6** | 文档元数据/Document metadata | 文档元数据 | 4 | 5.9% |

> **未发现的内容类型**: H5(部署程序) — 0个文件包含此类型

---

## 三、格式推荐分析

### 推荐逻辑

| 判定维度 | YAML_RECOMMENDED | MD_RECOMMENDED | EITHER |
|---------|-----------------|----------------|--------|
| 数据结构 | 高度结构化、规则schema | 叙事性、上下文依赖 | 两者皆可 |
| 机器可解析性 | 需要程序消费 | 主要供人/AI阅读 | 两者皆可 |
| 双SSoT模式 | 适合做数据SSoT | 适合做规则SSoT | 不涉及 |
| 变更频率 | 频繁且需同步 | 较稳定 | 两者皆可 |

### 逐类型推荐

| 编号 | 内容类型 | 推荐 | 推理 |
|------|---------|------|------|
| **A1** | 禁止项 | EITHER | 简单禁止声明在MD和YAML中均可清晰表达；ABS条目需YAML注册，但规则解释需MD |
| **A2** | 强制项 | EITHER | 同A1，强制要求在两种格式中均可表达 |
| **A3** | 约束 | EITHER | 约束条件在两种格式中表达力相当 |
| **A4** | 条件规则 | EITHER | 条件逻辑在MD中可用表格/步骤表达，在YAML中可用条件键表达 |
| **A5** | 默认值 | YAML_RECOMMENDED | 默认值是结构化数据，YAML key-value天然适合；程序需要读取默认值 |
| **A6** | 异常处理 | YAML_RECOMMENDED | 异常规则通常有条件→动作结构，YAML可精确schema化；MD中需大量表格 |
| **A7** | 覆盖/绕过规则 | YAML_RECOMMENDED | 覆盖规则是条件化的结构化数据，YAML可表达条件链和豁免机制 |
| **B1** | 步骤式程序 | MD_RECOMMENDED | 步骤需要上下文说明、前置条件、预期结果等叙事性内容；YAML难以表达步骤间逻辑 |
| **B2** | 状态机 | YAML_RECOMMENDED | 状态+转换+条件是高度结构化数据；YAML可定义states/transitions/guards schema |
| **B3** | 决策树 | MD_RECOMMENDED | 决策树需要条件说明和分支解释，叙事性较强；纯YAML决策树可读性差 |
| **B4** | 升级 | MD_RECOMMENDED | 升级流程需要上下文说明、触发条件描述、响应动作指导 |
| **B5** | 回滚 | MD_RECOMMENDED | 回滚程序需要步骤说明、前置检查、验证方法等叙事性内容 |
| **B6** | 检查清单 | EITHER | 检查项列表在MD表格和YAML数组中均可清晰表达 |
| **B7** | 验证 | MD_RECOMMENDED | 验证步骤需要预期输出描述、失败处理指导等上下文 |
| **B8** | 入职 | MD_RECOMMENDED | 入职流程需要引导性说明、示例、注意事项等叙事内容 |
| **B9** | 弃用 | YAML_RECOMMENDED | 弃用规则是结构化数据（版本→日期→替代→迁移步骤），YAML可schema化 |
| **B10** | 事件响应 | MD_RECOMMENDED | 事件响应需要场景描述、处理步骤、决策指导等大量叙事内容 |
| **C1** | 层级体系 | YAML_RECOMMENDED | 层级定义是结构化分类数据，YAML可定义层级schema和枚举值 |
| **C2** | 分类法 | YAML_RECOMMENDED | 分类法是结构化分类体系，YAML可定义类别→子类别→属性层级 |
| **C3** | 优先级分类 | EITHER | 优先级标签(P0-P3)在两种格式中均可表达；YAML适合枚举，MD适合说明 |
| **C4** | 范围定义 | YAML_RECOMMENDED | 范围定义是结构化边界数据，YAML可精确定义包含/排除规则 |
| **C5** | 规则分类 | YAML_RECOMMENDED | 规则分类是结构化标签体系，YAML可定义分类维度和枚举值 |
| **D1** | 交叉引用表 | EITHER | 引用表在MD表格和YAML映射中均可表达；MD表格可读性更好 |
| **D2** | 框架映射 | EITHER | 框架映射表在两种格式中表达力相当 |
| **D3** | 症状-原因映射 | MD_RECOMMENDED | 诊断映射需要症状描述、原因分析、处理建议等叙事内容 |
| **D4** | 消费者注册表 | YAML_RECOMMENDED | 注册表数据天然适合YAML；程序需要解析消费者列表 |
| **D5** | 依赖声明 | YAML_RECOMMENDED | 依赖声明是结构化数据，YAML可定义depends_on schema；程序需要解析依赖图 |
| **D6** | 模块ID引用 | YAML_RECOMMENDED | 模块ID是结构化标识符，YAML可定义命名空间和格式规则 |
| **D7** | 脚本/命令引用 | EITHER | 命令引用在MD代码块和YAML列表中均可表达 |
| **E1** | SSoT声明 | YAML_RECOMMENDED | SSoT声明是结构化元数据，YAML可定义真源路径和同步规则 |
| **E2** | 变更同步规则 | YAML_RECOMMENDED | 同步规则是条件→动作结构化数据，YAML可定义同步目标和触发条件 |
| **E3** | 修改条件 | YAML_RECOMMENDED | 修改条件是结构化约束，YAML可定义条件层级(L0-L3)和审批要求 |
| **E4** | 审查周期 | EITHER | 审查周期在YAML枚举和MD说明中均可表达 |
| **E5** | AI自治声明 | YAML_RECOMMENDED | 自治级别(immutable_core/human_gated/ai_modifiable)是枚举值，YAML天然适合 |
| **E6** | 稳定性声明 | YAML_RECOMMENDED | 稳定性级别(frozen/stable/evolving/volatile)是枚举值，YAML天然适合 |
| **E7** | 版本控制 | YAML_RECOMMENDED | 版本信息是结构化数据，YAML可定义版本号格式和变更日志schema |
| **E8** | 文档所有权 | YAML_RECOMMENDED | 所有权是结构化元数据，YAML可定义owner/reviewers/approvers |
| **F1** | 错误模式 | MD_RECOMMENDED | 错误模式需要描述、示例、识别方法等叙事内容 |
| **F2** | 诊断程序 | MD_RECOMMENDED | 诊断步骤需要叙事性指导、判断标准和处理建议 |
| **F3** | 根因分析 | MD_RECOMMENDED | 根因分析方法论需要叙事性说明和推理链 |
| **F4** | 度量指标 | EITHER | 指标定义在YAML schema和MD说明中均可表达 |
| **F5** | 质量维度 | EITHER | 质量维度框架在两种格式中均可表达 |
| **F6** | 反模式 | EITHER | 反模式描述需要示例（MD更好），但分类标签需要结构化（YAML更好） |
| **G1** | 文件格式规范 | YAML_RECOMMENDED | 格式规范是结构化schema定义，YAML可精确定义格式规则和验证约束 |
| **G2** | 命名约定 | EITHER | 命名规则在MD正则表达式说明和YAML pattern定义中均可表达 |
| **G3** | 头部/尾部标准 | EITHER | 头部标准模板在MD代码块和YAML schema中均可表达 |
| **G4** | 字段定义 | YAML_RECOMMENDED | 字段定义是结构化schema，YAML可定义字段名/类型/必填/枚举值 |
| **G5** | 模板结构 | EITHER | 模板在MD示例和YAML schema中均可表达 |
| **G6** | 编码规则 | YAML_RECOMMENDED | 编码规则是结构化约束，YAML可定义编码格式和验证规则 |
| **H1** | Runbook程序 | EITHER | Runbook在MD步骤式文档和YAML结构化流程中均可表达 |
| **H2** | 配置参数 | YAML_RECOMMENDED | 配置参数天然适合YAML key-value格式；程序需要读取配置 |
| **H3** | 超时/阈值 | YAML_RECOMMENDED | 阈值是数值型配置，YAML可定义参数名/类型/默认值/范围 |
| **H4** | 监控/告警 | EITHER | 监控规则在YAML告警配置和MD说明中均可表达 |
| **I1** | 原则 | MD_RECOMMENDED | 原则需要叙事性阐述、理由说明和适用范围描述 |
| **I2** | 背景 | MD_RECOMMENDED | 背景信息是纯叙事性内容，MD天然适合 |
| **I3** | 示例 | MD_RECOMMENDED | 示例需要上下文说明和代码/配置展示，MD可读性更好 |
| **I4** | 术语表 | EITHER | 术语定义在MD表格和YAML映射中均可表达 |
| **I5** | 变更历史 | EITHER | 变更日志在MD表格和YAML列表中均可表达 |
| **I6** | 文档元数据 | YAML_RECOMMENDED | 元数据天然适合YAML frontmatter格式 |

### 推荐统计

| 推荐类别 | 类型数量 | 类型列表 |
|---------|:-------:|---------|
| **YAML_RECOMMENDED** | 26 | A5,A6,A7, B2,B9, C1,C2,C4,C5, D4,D5,D6, E1,E2,E3,E5,E6,E7,E8, G1,G4,G6, H2,H3, I6 |
| **MD_RECOMMENDED** | 14 | B1,B3,B4,B5,B7,B8,B10, D3, F1,F2,F3, I1,I2,I3 |
| **EITHER** | 19 | A1,A2,A3,A4, B6, C3, D1,D2,D7, E4, F4,F5,F6, G2,G3,G5, H1,H4, I4,I5 |

---

## 四、关键发现与建议

### 4.1 高频内容类型（>50%文件包含）

| 排名 | 类型 | 文件数 | 占比 | 推荐 |
|:----:|------|:------:|:----:|------|
| 1 | D1 交叉引用表 | 68 | 100% | EITHER |
| 2 | E1 SSoT声明 | 68 | 100% | YAML_RECOMMENDED |
| 3 | B6 检查清单 | 62 | 91.2% | EITHER |
| 4 | B1 步骤式程序 | 61 | 89.7% | MD_RECOMMENDED |
| 5 | A2 强制项 | 66 | 97.1% | EITHER |
| 6 | A3 约束 | 60 | 88.2% | EITHER |
| 7 | A1 禁止项 | 50 | 73.5% | EITHER |
| 8 | I5 变更历史 | 40 | 58.8% | EITHER |
| 9 | C1 层级体系 | 42 | 61.8% | YAML_RECOMMENDED |
| 10 | C3 优先级分类 | 39 | 57.4% | EITHER |

**发现**: 高频类型中EITHER占多数，说明当前MD格式能满足大部分高频需求。但E1(SSoT声明)和C1(层级体系)高频且推荐YAML，暗示双SSoT模式（YAML数据+MD规则）对这两个类型价值最大。

### 4.2 双SSoT模式适用性分析

项目已有PS-STD-001/PS-REG-012双SSoT先例（MD=规则SSoT, YAML=数据SSoT）。以下类型组合最适合双SSoT模式：

| 双SSoT候选 | MD角色 | YAML角色 | 典型文件 |
|-----------|--------|---------|---------|
| E1+E5+E6 | 规则解释（为什么这样声明） | 枚举值定义（stability/ai_autonomy值域） | GOV-ENG-002, GOV-MOD-002 |
| C1+C3 | 层级说明（层级含义和判定标准） | 层级枚举（P0-P3/L00-L13值域） | GOV-DOC-001, GOV-TASK-001 |
| D4+D5 | 依赖说明（依赖原因和变更影响） | 依赖图数据（消费者列表/depends_on） | GOV-MOD-005, GOV-DOC-009 |
| E2+E3 | 同步规则说明 | 同步触发条件和目标注册表 | GOV-MOD-007, GOV-MOD-005 |

### 4.3 编码损坏警告

**GOV-MOD-007** (multi_registry_synchronization_standard.md) 存在明显编码损坏——大量中文字符显示为乱码。鉴于该项目有编码安全标准(GOV-DOC-005)，建议优先修复此文件。

### 4.4 内容类型密度分析

| 文件 | 类型数 | 说明 |
|------|:------:|------|
| GOV-TASK-001 (task_card_standard.md) | 26 | 内容类型最密集，涵盖A/B/C/D/E/F/G/H/I全部9大类 |
| GOV-MOD-002 (ai_behavior_iron_policy.md) | 20 | 铁律+零残留+ABS映射，E类全覆盖 |
| GOV-MOD-005 (module_injection_rules_policy.md) | 20 | YAML结构化策略，D/E类全覆盖 |
| GOV-MOD-004 (module_interface_contract_policy.md) | 20 | 契约生命周期+语义版本，E类全覆盖 |
| GOV-MOD-003 (module_lifecycle_policy.md) | 19 | 8阶段生命周期+退役流程 |
| GOV-DOC-006 (document_lifecycle_standard.md) | 19 | TTL分类+状态机+LATEST覆写 |
| GOV-DOC-009 (document_control_policy.md) | 17 | DOC-001~009+depends_on格式 |
| GOV-ARC-CTR-001 (ctr_injection_rules_policy.md) | 17 | 7域注入规则+受控枚举 |

**发现**: governance/module/ 目录下的文件内容类型密度最高，平均每文件含19种类型。这些文件是双SSoT改造的优先候选——YAML抽取结构化数据（枚举/注册表/状态机/依赖声明）可大幅降低MD文件复杂度。

---

## 五、分类体系参照

| 大类 | 编号范围 | 中文名称 | 子类型数 |
|------|---------|---------|:-------:|
| A | A1-A7 | 规则类/Rule-like | 7 |
| B | B1-B10 | 流程类/Process-Workflow | 10 |
| C | C1-C5 | 分类类/Classification-Taxonomy | 5 |
| D | D1-D7 | 引用类/Reference-Mapping | 7 |
| E | E1-E8 | 元结构类/Meta-Structural | 8 |
| F | F1-F6 | 诊断类/Diagnostic-Analytical | 6 |
| G | G1-G6 | 模板类/Template-Format | 6 |
| H | H1-H5 | 运维类/Operational | 5 |
| I | I1-I6 | 说明类/Explanatory-Contextual | 6 |
| **合计** | | | **60** |

> 实际发现: 59种（H5部署程序未在任何文件中发现）
