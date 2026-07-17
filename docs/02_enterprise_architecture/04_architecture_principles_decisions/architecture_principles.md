---
module_id: ARCH-004
title: Architecture Principles / 架构原则
doc_type: architecture_view
status: Active
version: 1.4.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-05-02
superseded_by: null
supersedes: null
related_rationale: R29, R30
related_open_questions: []
tags:
- architecture-principles
- open-source-first
- license-governance
- replaceability
- thin-adapter
- safety-red-lines
- security-principles
summary: ZephyrAlpha 2.0 架构原则集中 SSoT。v1.4.0：修复编号错乱（§1.1.x→§2.1.x，§3缺失重编号）、删除§0过期归集承诺、R2执行机制gap显式标注、§2.1机构对标表瘦身。v1.3.0：删除§2.3+§3未落地方法论。v1.1.0：§0+§1安全红线+§2开源优先。
date: '2026-07-09'
ttl: permanent
---

# Architecture Principles / 架构原则

---

## 0. 本文档定位

本文档是 ZephyrAlpha 2.0 **所有架构原则的 SSoT（Single Source of Truth / 唯一真源）**。

任何其他文件（KB 决策记录、视图文档、设计稿）中对同一原则的描述均为**只读引用**，不得独立修改原则正文。如有冲突，以本文档为准。

**v1.0.0 初始内容来源**：§2 "开源优先" 子原则提取自早期设计稿（不再适用）。

**v1.1.0 同步迁移完成**：安全红线 4 条已从 `overview.md` 归集至本文档 §1。

**关于 OCP / SSoT / 模块准入铁律**：这三项原则仍分别在 `KBG-0004`（OCP 扩展点）、`KBG-0001`（SSoT 唯一真源）、`KBG-0014`（模块准入四级铁律）中定义。v1.3.0 评估后决定**不归集到本文档**——各自 KBG 已是独立 SSoT，强行归集会产生双源同步负担。本文档仅承载安全红线（§1）和开源优先（§2）两类原则。

---

## 1. 安全红线（Safety Red Lines / 不可撤销原则）

以下 4 条原则是系统最高优先级约束，**任何架构决策、代码变更、AI 自治行为不得违反**。违反任一红线视为 P0 阻断。

| # | 原则 | 大白话 | 执行机制 |
|---|------|--------|----------|
| **R1** | **键盘不录 key** | API 密钥、数据库密码等秘密信息只能通过环境变量/密钥管理器注入，绝不手动键入 | pre-commit 检测 `key=` / `password=` / `secret=` 字面量 |
| **R2** | **日志不写 secret** | 任何日志系统（structlog/logging/print）的输出中不得包含密钥、token、私钥 | CI 门禁正则扫描 log 输出 |
| **R3** | **金融不盲信任 AI** | AI 生成的交易决策、风控参数、金额计算必须经过人工确认或确定性规则校验后才生效 | D_RISK 风控层 hard check before D_EXECUTION_CORE 执行 |
| **R4** | **PRD 永远不改** | 生产数据库（PRD）永远不做 DDL 变更/手动 UPDATE/DELETE；所有变更走迁移脚本 + 审计日志 | DB 权限只读连接 + 迁移脚本强制记录 |

### §1bis 门禁追溯（CI / 本地工件）

| # | gate_ref | 落地状态 | 说明 |
|---|----------|:---:|------|
| **R1** | `.pre-commit-config.yaml` → `pre-commit-hooks` / `detect-private-key`；服务端全量见 `.github/workflows/governance.yml`（`Arch Guard` 等步骤） | ✅ 已落地 | 防私钥误提交；密钥字面量与轮换另见 `secret-management-policy.md` |
| **R2** | **目标态**：运行时日志不得写出 secret、token、私钥 | ⚠️ **T1 待落地** | **当前**以 Code Review + `security_architecture.md` 日志约束为主，**尚无**「扫描所有运行时 log 输出」的独立 CI job。T1 实盘前必须在 `scripts/arch_guard/` 或专项 workflow 登记自动化扫描并回链本表 |
| **R3** | 设计侧：`cross_layer_contracts.yaml` + `invariants.yaml`（D_RISK ↔ D_EXECUTION_CORE）；CI：`python scripts/arch_guard/run_all.py`（由 governance workflow 调用） | ⚠️ **T1 待落地** | T1 实盘后须满足 hard-check 与适应度函数阈值 |
| **R4** | 数据治理策略（`data-retention-policy.md` 等）+ 迁移与审计流程；非单一脚本名 | ✅ 已落地 | 以权限与流程为主 |

**红线优先级**：高于所有其他架构原则。在其他原则（如 §2 "开源优先"）与红线冲突时，**红线无条件优先**。

**与 06-SEC 安全架构的关系**：06-SEC 定义了防御深度、GRC 矩阵、威胁模型等技术实现；本节定义的是不可妥协的最高原则。前者是"怎么做"，后者是"什么绝不能做"。

---

## 2. 开源优先 / Open Source First

### 2.1 专业机构为什么"开源优先"？

#### 2.1.1 直接对标（量化领域代表性机构）

| 机构 | 开源使用情况 | 关键证据 |
|------|------------|--------|
| **Two Sigma** | 重度使用 + 大量反哺 | 开源 `BeakerX`, `Arbuti`, `Cook`（数据科学生态）|
| **Man AHL** | 开源 `arctic` 时序库 | 全球 Python 时序管理标杆 |
| **Microsoft (Qlib)** | 开源 `Qlib` 完整 AI 量化平台 | 因子 / 训练 / 回测全栈 |

#### 2.1.2 核心原因（从专业机构招聘资料 + 技术博客提炼）

1. **边际成本更低**：维护一个活跃开源项目 vs 自研从零，后者人力成本 10-50 倍
2. **社区质量反哺**：Bug 由全球开发者发现，而不是只有你一个人
3. **人才流动性**：新员工熟悉开源工具，onboarding 成本低
4. **监管透明**：开源代码比自研代码更容易通过审计（可读、有历史、有社区审查）
5. **退出成本低**：用开源意味着随时可换（社区分叉），自研意味着绑死自己

#### 2.1.3 独立开发者更应该开源优先（3-10 倍更重要）

| 维度 | 机构（10 人团队） | ZephyrAlpha（1 人 + AI） |
|-----|---------------|:---:|
| 人力成本 | 高 | **无限制** |
| 测试资源 | 专职 QA | **无 QA** |
| Bug 修复时间 | 有 oncall | **只有你** |
| 开源节省的人力 | 1× | **3-10×** |

**结论**：单人 + AI 的开发模式比专业机构**更应该**开源优先。

---

### 2.2 五条子原则

#### 原则 1：Open Source First / 开源优先原则

> 任何新模块在架构设计稿的 §1 必须包含"OSS Candidates 调研结果"，证明已做过 GitHub 扫描。未做 OSS Scan 的设计稿不予进入 IOA 评审。

**执行标准**：
- 每个新的 `design_draft`、`adr`、`c4_view` 类文档必须含"OSS Candidates"小节
- 至少调研 3 个同类开源项目
- 明确决策结论（Buy / Buy+Wrap / Hybrid / Build）

---

#### 原则 2：Thin Adapter Over Thick Implementation / 薄适配器优于厚实现

> 当决策为 Buy/Buy+Wrap 时，必须通过 OCP 扩展点 + ACL 适配器引入，避免业务逻辑与开源项目深度耦合。

**实现路径**（对齐 KBG-0004 + 03-AA §4.4）：
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

> 所有依赖项的许可证必须通过 SBOM 自动扫描（D_COMPLIANCE 文件治理）。GPL/AGPL 项目进入代码库前必须经过 ARB 特批。

**许可证分类标准**：

| 许可证类型 | 是否允许自动引入 | 条件 |
|----------|:---:|------|
| MIT / Apache 2.0 / BSD | ✅ 允许 | 无额外条件 |
| MPL 2.0 / LGPL | ⚠️ 允许（需登记） | 仅限动态链接，不修改源码 |
| GPL / AGPL | ❌ 禁止自动引入 | 必须经 ARB 特批 + Owner 签字 |
| 无许可证（Unlicensed） | ❌ 禁止 | 等同于 All Rights Reserved |

---

#### 原则 4：Contribute Back When Patched / 修改必反哺

> 对开源项目的 patch/fork 必须有明确记录；可贡献的改进优先提交 PR 而不是私有 fork。

**执行标准**：
- 每次对 OSS 库做 monkey-patch / fork 时 → 写入 `adr/` 记录原因 + 评估是否可提 PR
- 私有 fork 的生命周期 ≤ 3 个月——超过 3 个月未合并回上游 → 触发评估：是否应替换该 OSS 库
- 长期维护的私有 fork → 必须在 `technology_landscape.yaml` 中标注 `quadrant: hold`（警戒指標）

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

## 3. 与其他文档的关系

| 关系 | 对象 | 说明 |
|:---|:---|:---|
| 本文档引用 | `KBG-0004`（OCP 扩展点） | §2.2 原则 2 依赖 OCP 扩展点基础设施 |
| 本文档引用 | `KBG-0014`（模块准入铁律） | 模块准入 MOD-P1~P4 是独立的决策维度 |
| 本文档引用 | `technology_landscape.yaml` | 技术全景图承载具体 OSS 条目登记，本文档承载"为什么选/不选"的决策原则 |
| 本文档被引用 | `overview.md` | 00-overview §0 的安全红线已归集至本文档 §1（v1.1.0 完成） |
| 本文档被引用 | `application_architecture.md` | 03-AA §4.4 的 ACL 三段是原则 2"薄适配器"的基础设施实现 |

---

## 4. 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-05-02 | 1.0.0 | 初始版。5 条 Open Source First 子原则 + 专业机构对标证据。 |
| 2026-05-02 | 1.1.0 | **安全红线归集**：§0 新增安全红线 4 条（R1-R4），从 `overview.md` 归集完成，附带执行机制 + 大白话解释。`overview.md` 同步更新为引用链接。消除同一事实双源问题。 |
| 2026-07-06 | 1.3.0 | 删除 §2.3（5 条硬约束，孤岛概念+第1/4条重叠+第5条引用失效概念）+ §3（BvB 五维评分法，未落地的方法论附录）。清理 OQ-032 悬空引用。 |
| 2026-07-09 | 1.4.0 | **大修复**：(1) 修复编号错乱——§1.1.1/2/3 重编号为 §2.1.1/2/3，原§4/§5 重编号为 §3/§4；(2) 删除 §0 过期归集承诺（OCP/SSoT/模块准入铁律不再归集，各自 KBG 是独立 SSoT）；(3) §1bis 门禁追溯表新增"落地状态"列，R2/R3 显式标注"T1 待落地"；(4) §2.1 机构对标表瘦身——删除 JPMorgan/Bloomberg/Netflix 3 家非量化机构，保留 Two Sigma/Man AHL/Microsoft Qlib 3 家量化领域代表性机构；(5) §3 修正交叉引用错误（§1.2→§2.2）和过期描述（"未来应归集"→"已归集"）。 |
