---
module_id: ARCH-004
title: Architecture Principles / 架构原则
doc_type: architecture_view
status: Active
version: 2.0.1
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-05-02
superseded_by: null
supersedes: VIEW-00-OVERVIEW
related_rationale: R26, R27, R28, R29, R30
related_open_questions: []
tags:
- architecture-principles
- architecture-methodology
- togaf
- c4
- iso-42010
- open-source-first
- license-governance
- replaceability
- thin-adapter
- safety-red-lines
- security-principles
- domain-driven
summary: ZephyrAlpha 架构原则+方法论集中 SSoT。包含架构方法论（TOGAF/C4/功能域裁定/三棵树）+ 4 条安全红线 + 5 条开源优先子原则 + 核心架构决策。
date: '2026-07-19'
ttl: permanent
---

# Architecture Principles / 架构原则

---

## 0. 本文档定位

本文档是 ZephyrAlpha 2.0 **所有架构原则与方法的 SSoT（Single Source of Truth / 唯一真源）**。

包含两类内容：
1. **架构方法论**（§1）——怎么描述架构（TOGAF/C4/功能域裁定/三棵树）
2. **架构原则**（§2-§3）——应该怎么做（安全红线/开源优先）
3. **核心架构决策**（§4）——系统定位与定死的决策

任何其他文件中对同一原则或方法论的描述均为**只读引用**，不得独立修改正文。如有冲突，以本文档为准。

---

## 1. 架构方法论

### 1.1 三标准合成

本项目用三个国际标准来组织架构文档（不是发明新方法，是站在巨人肩膀上）：

| 标准 | 大白话 | 在本项目中的作用 |
|------|--------|-----------------|
| **ISO/IEC/IEEE 42010:2011** | 一个系统要从多个角度看，每个角度解决不同人的关心 | 方法论：用多个视图描述系统 |
| **TOGAF 9.2 / 10** | 从业务→信息→应用→技术四层看系统 | 四层视图分类法 |
| **C4 Model** (Simon Brown) | 画图从大到小分四级：全景→容器→组件→代码 | 应用层可视化：画 L1 系统上下文 + L2 容器图 |

### 1.2 功能域唯一分类裁定

**裁定**：按功能分域是唯一的分类方式。逻辑层只作为域的一个属性（layer_id），不当作独立的分类法。

| 裁定项 | 结论 | 大白话理由 |
|--------|------|-----------|
| 逻辑层 vs 功能域 | **功能域唯一** | 两套分类并存=AI 每次要判断用哪套=幻觉温床 |
| 逻辑层怎么保留 | 作为域的 layer_id 属性 | 属性不是分类，不会产生两套并行的分法 |
| 逻辑层 YAML 文件 | 废弃，合并进 depgraph | 避免两个地方同时存同一信息（真源分裂） |

**当前域层级分布**：由 depgraph `domains` 表派生（详见 depgraph 数据库或 `domains` 表）。禁止在本文硬编码域数量/节点数/边数。

### 1.3 TOGAF 四层

文档按 TOGAF 四层组织（就是从四个角度看系统，上层驱动下层）：
- **BA 业务架构**：系统服务谁、做什么、核心流程是什么
- **IA 信息架构**：有哪些信息资产、怎么组织
- **AA 应用架构**：有哪些模块/服务、怎么交互
- **TA 技术架构**：用什么技术栈支撑

> **注**：TOGAF 四层是**看文档的角度**，不是代码的物理分层。代码怎么放以功能域为准（见§1.2裁定）。

### 1.4 C4 模型

TOGAF 解决"从哪些角度看系统"，C4 解决"应用架构内部怎么画图"（从大到小分四级，像 Google Earth 从卫星到街道）：

| 级别 | 大白话 | 本项目用法 |
|------|--------|-----------|
| **L1 — System Context** | 系统在外部世界的位置（卫星视角） | ✅ 必画 |
| **L2 — Container** | 系统内的独立部署单元（城市视角） | ✅ 必画 |
| **L3 — Component** | 容器内的组件（街道视角） | 🟡 按需，在蓝图内 |
| **L4 — Code** | 类/函数级别（建筑内部） | ❌ 不画（代码本身就是文档）|

### 1.5 三棵树映射

项目有三个顶层目录（"三棵树"），各归一个架构视图管：

| 目录 | 大白话 | 归属视图 | 归属文档 |
|------|--------|---------|---------|
| `docs/` | 所有文档（架构/蓝图/规则/报告） | 信息架构 | `information_architecture.md` |
| `src/` | 所有业务代码 | 应用架构 | `application_architecture.md` |
| `scripts/` | 所有脚本（治理/生成器/工具） | 应用架构（子视图） | `application_architecture.md` |

---

## 2. 安全红线（Safety Red Lines / 不可撤销原则）

以下 4 条原则是系统最高优先级约束，**任何架构决策、代码变更、AI 自治行为不得违反**。违反任一红线视为 P0 阻断。

| # | 原则 | 大白话 | 执行机制 |
|---|------|--------|----------|
| **R1** | **键盘不录 key** | API 密钥、数据库密码等秘密信息只能通过环境变量/密钥管理器注入，绝不手动键入 | pre-commit 检测 `key=` / `password=` / `secret=` 字面量 |
| **R2** | **日志不写 secret** | 任何日志系统（structlog/logging/print）的输出中不得包含密钥、token、私钥 | CI 门禁正则扫描 log 输出 |
| **R3** | **金融不盲信任 AI** | AI 生成的交易决策、风控参数、金额计算必须经过人工确认或确定性规则校验后才生效 | 风控层 hard check before 执行层 |
| **R4** | **PRD 永远不改** | 生产数据库（PRD）永远不做 DDL 变更/手动 UPDATE/DELETE；所有变更走迁移脚本 + 审计日志 | DB 权限只读连接 + 迁移脚本强制记录 |

### §2bis 门禁追溯（CI / 本地工件）

| # | gate_ref | 落地状态 | 说明 |
|---|----------|:---:|------|
| **R1** | `.pre-commit-config.yaml` → `pre-commit-hooks` / `detect-private-key`；服务端全量见 `.github/workflows/governance.yml`（`Arch Guard` 等步骤） | ✅ 已落地 | 防私钥误提交 |
| **R2** | 源码静态扫描 + 运行时日志扫描 | ⚠️ **部分落地** | **源码扫描已接入 CI**：`detect_secrets.py`（pre-commit 增量）+ `scan_secret_leak.py`（CI 全库深度扫描，对标 06-SEC §6.3 L3-Audit）。**运行时 .log 文件扫描待 T1 实盘后落地**——项目当前未到实盘阶段，无运行时日志可扫。辅助脚本 `scan_runtime_log_secrets.py` 已开发但功能与 `scan_secret_leak.py` 重叠，未接入 CI |
| **R3** | **目标态**：风控参数 hard check before 执行层 | ⚠️ **T1 待落地** | CI：`python scripts/arch_guard/run_all.py`（由 governance workflow 调用）。T1 实盘后须满足 hard-check 与适应度函数阈值 |
| **R4** | 数据治理策略（权限只读连接 + 迁移审计流程） | ✅ 已落地 | `database_service.py` 双连接机制：`get_governance_conn(read_only=True)` / `get_depgraph_conn(read_only=True)` 返回独立只读连接（PRAGMA query_only=1 / SET default_transaction_read_only=on） |

**红线优先级**：高于所有其他架构原则。在其他原则（如 §3 "开源优先"）与红线冲突时，**红线无条件优先**。

**与 06-SEC 安全架构的关系**：06-SEC 定义了防御深度、GRC 矩阵、威胁模型等技术实现；本节定义的是不可妥协的最高原则。前者是"怎么做"，后者是"什么绝不能做"。

---

## 3. 开源优先 / Open Source First

### 3.1 专业机构为什么"开源优先"？

#### 3.1.1 直接对标（量化领域代表性机构）

| 机构 | 开源使用情况 | 关键证据 |
|------|------------|--------|
| **Two Sigma** | 重度使用 + 大量反哺 | 开源 `BeakerX`, `Arbuti`, `Cook`（数据科学生态）|
| **Man AHL** | 开源 `arctic` 时序库 | 全球 Python 时序管理标杆 |
| **Microsoft (Qlib)** | 开源 `Qlib` 完整 AI 量化平台 | 因子 / 训练 / 回测全栈 |

#### 3.1.2 核心原因（从专业机构招聘资料 + 技术博客提炼）

1. **边际成本更低**：维护一个活跃开源项目 vs 自研从零，后者人力成本高一个数量级
2. **社区质量反哺**：Bug 由全球开发者发现，而不是只有你一个人
3. **人才流动性**：新员工熟悉开源工具，onboarding 成本低
4. **监管透明**：开源代码比自研代码更容易通过审计（可读、有历史、有社区审查）
5. **退出成本低**：用开源意味着随时可换（社区分叉），自研意味着绑死自己

#### 3.1.3 独立开发者更应该开源优先

| 维度 | 机构（10 人团队） | ZephyrAlpha（1 人 + AI） |
|-----|---------------|:---:|
| 人力成本 | 高 | **无限制** |
| 测试资源 | 专职 QA | **无 QA** |
| Bug 修复时间 | 有 oncall | **只有你** |
| 开源节省的人力 | 基线 | **远高于机构** |

**结论**：单人 + AI 的开发模式比专业机构**更应该**开源优先。

---

### 3.2 五条子原则

#### 原则 1：Open Source First / 开源优先原则

> 任何新模块在架构设计稿的 §1 必须包含"OSS Candidates 调研结果"，证明已做过 GitHub 扫描。未做 OSS Scan 的设计稿不予进入 IOA 评审。

**执行标准**：
- 新增架构设计类文档（如模块蓝图、技术选型记录）必须含"OSS Candidates"小节
- 至少调研 3 个同类开源项目
- 明确决策结论（Buy / Buy+Wrap / Hybrid / Build）

---

#### 原则 2：Thin Adapter Over Thick Implementation / 薄适配器优于厚实现

> 当决策为 Buy/Buy+Wrap 时，必须通过 OCP 扩展点 + ACL 适配器引入，避免业务逻辑与开源项目深度耦合。

**实现路径**：
```
开源项目 API
    ↓
ACL adapter（薄层封装，翻译为 canonical schema）
    ↓
OCP 扩展点基类（业务层只依赖抽象接口，不依赖具体开源库）
    ↓
业务逻辑
```

**关键约束**：
- 业务代码**禁止**直接 `import` 开源库的内部类/函数
- 所有 OSS 交互必须经过 adapter，adapter 实现 OCP 基类接口
- 更换开源库 → 只换 adapter，业务代码零变动
- Adapter 代码量应 ≤ 业务逻辑代码量的 20%（"薄"的量化标准）

---

#### 原则 3：License-as-Code / 许可证即代码

> 所有依赖项的许可证必须通过 SBOM 自动扫描。GPL/AGPL 项目进入代码库前必须经过架构评审特批。

**许可证分类标准**：

| 许可证类型 | 是否允许自动引入 | 条件 |
|----------|:---:|------|
| MIT / Apache 2.0 / BSD | ✅ 允许 | 无额外条件 |
| MPL 2.0 / LGPL | ⚠️ 允许（需登记） | 仅限动态链接，不修改源码 |
| GPL / AGPL | ❌ 禁止自动引入 | 必须经架构评审特批 + Owner 签字 |
| 无许可证（Unlicensed） | ❌ 禁止 | 等同于 All Rights Reserved |

---

#### 原则 4：Contribute Back When Patched / 修改必反哺

> 对开源项目的 patch/fork 必须有明确记录；可贡献的改进优先提交 PR 而不是私有 fork。

**执行标准**：
- 每次对 OSS 库做 monkey-patch / fork 时 → 在模块蓝图或独立设计记录中写明原因 + 评估是否可提 PR
- 私有 fork 的生命周期 ≤ 3 个月——超过 3 个月未合并回上游 → 触发评估：是否应替换该 OSS 库
- 长期维护的私有 fork → 必须在技术全景登记中标注为"hold"警戒

---

#### 原则 5：Replace-ability Before Adoption / 先保替换性，再引入

> 引入任何开源项目前，必须证明：如果该项目死亡（archive/abandon），系统在 2 周内可切换到替代方案。

**评估清单**（每次引入 OSS 时必须填写）：
1. **替代方案**：是否已有 1+ 个备选 OSS 项目？（是/否，列出备选名称）
2. **抽象层完整性**：当前 adapter 是否封装了所有 OSS 特定调用？（是/否）
3. **迁移成本**：替换 OSS 需要修改多少个文件？（目标 ≤ 3 个 adapter 文件）
4. **数据迁移**：替换是否需要数据格式迁移？（是/否，若是需提供迁移脚本）

**不满足 2 周替换承诺的 OSS → 禁止引入**。此原则确保 OSS 是"借力"而非"绑死"。

---

## 4. 核心架构决策

**系统定位**：ZephyrAlpha 是个人量化投资系统的 AI 原生重构，采用功能域唯一物理分类体系（按功能把代码分成独立的块，每块一个域，不按技术层分），Python 全栈，Vibe Coding 驱动（用 AI IDE 写代码，Cursor + Trae 双工具）。

**核心架构决策**（定死的原则，不可推翻）：
- **功能域唯一分类**：按功能分域，不按技术层分。逻辑层只作为域的一个属性（layer_id），不当并行分类（两套分类法并存=AI 不知道用哪套=幻觉温床）。
- **全景图派生**：所有结构化数据（域清单/模块清单/依赖关系/容量统计）从 depgraph 数据库自动生成，禁止手编（手编必过时）。
- **运行时三平面**（引擎平面 / Vibe Coding 平面 / 治理平面）→ 三个独立的平面各管各的：引擎跑策略、Vibe Coding 写代码、治理管规则
- **治理三层**（制度标准层 / 企业架构层 / 蓝图施工层）→ 三层从上到下，每层有准入和退出门禁
- **安全红线**：4 条不可撤销（详见 §2）
- **技术栈**：Python + Pydantic + SQLite/PostgreSQL + ChromaDB + MCP 协议

---

## 5. 与其他文档的关系

| 关系 | 对象 | 说明 |
|:---|:---|:---|
| 本文档被引用 | `application_architecture.md` | 应用架构视图，与本文档原则交叉引用 |
| 已合并删除 | `overview.md` | v2.0.0 合并——永恒指导内容已归集至本文档 §1+§4，overview.md 已删除 |