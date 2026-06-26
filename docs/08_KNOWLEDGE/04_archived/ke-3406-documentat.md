---
module_id: KE-3406
title: 4. 当前已形成的关键结论
category: documentation
ttl: permanent
---

# 4. 当前已形成的关键结论

4. 当前已形成的关键结论

| 编号 | 结论 | 含义 |
|------|------|------|
| R1 | ZephyrAlpha 2.0 需要新架构 | 既有项目不再适合作为长期唯一真源 |
| R2 | 当前问题是多代理组织治理问题 | 不是普通单人项目文档问题 |
| R3 | 决策连续性是最小刚需 | 决策记忆是记忆系统的最小落地点 |
| R4 | 组织记忆系统需要整体设计 | 不应把问题缩成单一聊天记忆 |
| R5 | 当前阶段先做全貌架构 | 先定抽屉，再谈细颗粒制度与实现 |
| R6 | `19_development_workspace` 必须存在 | 用于承载讨论、设计稿、任务书与未决问题 |
| R7 | 当前工作区已形成简易决策记忆系统 v0 | 原因、结果、未决、任务已经各有承载文档 |
| R8 | 现在应先做格式规范化 | 先让讨论文档具备可升格、可检索、可入库的统一结构 |
| R9 | 前置项目“自动保存到项目里”是两层机制 | Cursor transcript 自动保存 + 仓库规则强制 Session Log |
| R10 | 新项目应迁移的是机制，不是原样复制旧日志 | 新项目要重建 session log 制度与 intake 规则 |
| R11 | 前置项目聊天记录未来应分批吸收 | 先登记来源，再按 `raw / candidate / active` 处理 |
| R12 | 元数据契约已是机构标准 | `organizational-memory-system-design.md` §5.2 的 7 大类字段无需修正 |
| R13 | 异步流水线是专业机构标准 | 主对话模型不负责记忆整理，后台异步处理 |
| R14 | 知识边界分层策略已明确 | 知识库存全文，记忆系统存索引，避免双真源 |
| R15 | 记忆系统 canonical 物理落位（初版） | 索引层在 `08_ai_engineering_and_agent_ops/memory-and-context/` 的方案；**status: superseded**（需重新讨论，见 OQ-001 已重新打开） |
| R16 | 记忆系统内部结构（初版） | decision/operational/knowledge/context-services/memory-governance 的语义分类；**status: superseded**（需重新讨论） |
| R17 | 记忆系统 P0/P1/P2 划分（初版） | P0 = Decision Memory System 的方案；**status: superseded**（需重新讨论，见 OQ-002 已重新打开） |
| R18 | 跨域核心价值链已确认 | 数据→研究→模型→策略→组合→执行→报告；横向治理贯穿；细颗粒度数据契约延后 |
| R19 | 记忆系统在治理体系中的四层分布（初版） | 政策定义+索引存储+输入源+生产线的四层方案；**status: superseded**（需重新讨论） |
| R20 | 异步流水线脚本位置（初版） | `scripts/governance/memory-pipeline/` 的方案；**status: superseded**（需重新讨论，见 OQ-010 已重新打开） |
| R21 | 机构分层原则（初版） | 治理≠审计≠产品的分层方案；**status: superseded**（需重新讨论） |
| R22 | 记忆系统治理体系（初版） | 四层分工方案；**status: superseded**（需重新讨论） |
| R23 | 治理体系五层架构 | **当前结论**：L1政策层(00_governance/) → L2标准层(01_policies/) → L3架构层(02_enterprise/) → L4域级层(各XX_*/) → L5执行层(scripts/src) |
| R24 | 横向治理三条主线 | **当前结论**：政策控制(00_governance/) + 风险监控(17_risk/) + 记忆沉淀(08_ai_engineering/memory-and-context/) |
| R25 | 记忆系统的治理定位 | **当前结论**：记忆系统不是独立治理域，而是AI工程域(08/)的核心能力；治理政策(00/)定义规则，AI工程域(08/)实现能力 |
| R26 | 采用单一 frontmatter schema + 分阶段必填闸门 | **当前结论**：所有文档共用完整 schema，不同 `status` 对应不同必填集；取代 v1 的"沙盒档/正式档"双轨。落地：KBG-0002、`discussion-document-standard.md` v2.0.0 |
| R27 | ADR canonical 家 = `02_enterprise_architecture/adr/`；草稿区 = workspace | **当前结论**：正式 ADR 在 canonical 域；草稿在 `adr-drafts/`，拍板后搬家。落地：KBG-0001 隐含条款、`adr/README.md` |
| R28 | `doc_type` 和 `module_id` 必须规范化 | **当前结论**：`doc_type` 采用 15 项受控词表；`module_id` 统一 `<DOMAIN>-<TYPE>-<NNN>` 格式（ADR 保留 `ADR-NNNN` 短格式）。落地：`discussion-document-standard.md` v2.0.0 §3/§4 |
| R29 | Superseded 用 append-only 字段表示，禁止删除线；taskbook 状态用 `[ ]/[/]/[x]/[~]` 四符号 | **当前结论**：machine-readable 优先于视觉效果；所有失效内容保留原文 + 状态字段。落地：标准 v2.0.0 §6.2 / §8 |
| R30 | 文档分类从 4 类扩展到 8 类机构完整图谱 | **当前结论**：新增 ADR / roadmap / risk-register / session-log 四类；明确 ADR / rationale-log / Decision Memory Index 三者边界。落地：`document-triage-guide.md` v2.0.0 §1/§1.2 |
| R31 | strategic_decision 不独立成层，移入 pf_core/strategic/ | **当前结论（2026-04-18 会话 12 锁定）**：业界 4 种主流模式扫描后采纳 BlackRock Aladdin 模式（P1）。strategic asset allocation 本质是 portfolio construction 的长周期版本，业界没有任何顶级机构把它列为
