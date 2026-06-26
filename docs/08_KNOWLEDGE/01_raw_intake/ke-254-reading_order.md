---
module_id: KE-254
status: active
title: 3. Reading order / 推荐阅读顺序
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 3. Reading order / 推荐阅读顺序

3. Reading order / 推荐阅读顺序

**First time / 第一次读（5 分钟）**：`index.md`（本文）→ `overview.md` → `information_architecture.md §3.1`（文档抽屉清单）

**Architect / 架构师（完整视图顺序）**：`00` → `01` → `02` → `05` → `03` → `07` → `04` → `06` → `08` → `09` → `10`

> 顺序逻辑：先业务（00→01）→ 信息组织（02）→ 数据对象（05）→ 应用分层（03，后端 14 层）→ 集成接口（07）→ 技术基础设施（04）→ 安全（06，active v1.0.0）→ 运维（08，draft in-progress）→ 治理（09，三层边界 Policy/Factory/Runtime）→ 前端独立平台架构（10，与 03 物理隔离）

**Developer / 开发者**：`application_architecture.md` → `integration_architecture.md`（接口契约）→ `technology_architecture.md` → `data_architecture.md`（实现数据对象时参考）

**SRE / 运维**：`technology_architecture.md` → `operations_architecture.md`（运维域全景）→ `application_architecture.md §4` → `data_architecture.md §3/§9`（存储与归档策略）

**Quant researcher / 量化研究员**：`data_architecture.md §4/§5/§6` → `application_architecture.md`（PIT / Survivorship / 血缘是回测可信的前置条件）

**Data engineer / 数据工程师**：`data_architecture.md`（全篇）→ `integration_architecture.md §3/§4`（数据流拓扑与契约）→ `application_architecture.md §4.1 L00`

**Security / 安全合规**：`security_architecture.md`（安全架构全景 active v1.0.0）→ `governance_architecture.md`（治理三层边界 + 合规架构联动）→ `integration_architecture.md §5`（ACL 策略）→ `application_architecture.md §4.1`（ACL 落盘位置）

**Governance / 治理工程师**：`governance_architecture.md`（三层边界定义 + 39 系统分层 + 激活时间表）→ `application_architecture.md §5`（scripts 治理代码拓扑）→ `security_architecture.md`（治理与安全交集）→ KB:decisions namespace（KBG-0010 治理架构三层边界，原物理文件已迁入）→ 源讨论稿 `archive/reorg-2026-04-24/realized-as-adr/working-designs/governance-three-layer-boundary-design.md`（ARC-20260424-004，决策溯源）

**AI collaborator / AI 协作者（推荐首选路径 v1.8.0）**：`architecture_model/index.yaml`（全局索引，1 分钟定位任何模块）→ 按需读取 `architecture_model/layers/lXX.yaml`（模块属性 SSoT）→ `overview.md`（设计哲学）→ 按需读取视图正文（设计理由与叙事）

**Frontend developer / 前端开发者**：`frontend_architecture.md`（全篇）→ `integration_architecture.md §3/§4`（API 契约规范）→ `data_architecture.md §2`（了解所需业务数据对象）→ `application_architecture.md §4.1 L08`（api_gateway 子模块）→ `security_architecture.md`（前端安全策略，active v1.0.0）

---
