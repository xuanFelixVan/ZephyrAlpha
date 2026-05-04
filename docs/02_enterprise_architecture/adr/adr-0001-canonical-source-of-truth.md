---
module_id: ADR-0001
title: 确立 docs/ 为唯一 canonical 真源
doc_type: adr
status: active
version: 1.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-04-17
superseded_by: null
supersedes: null
related_rationale: R1, R4, R5, R6
related_open_questions: []
tags:
- information-architecture
- governance
- migration
summary: 确立 `docs/` 为 ZephyrAlpha 2.0 全部文档的唯一 canonical 真源；旧树为只读归档与迁移来源；所有新内容只在新树创建，避免双真源并存导致的引用漂移。
date: '2026-04-22'
ttl: permanent
---

# ADR-0001: 确立 `docs/` 为唯一 canonical 真源

## 1. 状态（Status）

- **当前状态**：`accepted`
- **提议日期**：2026-04-17
- **拍板日期**：2026-04-17
- **被谁取代**：—
- **取代了谁**：—

## 2. 背景与问题（Context）

项目早期存在**双真源问题**：

- **旧树**：`D:\ZephyrAlpha\docs\`，历史文档与早期蓝图
- **新树**：`D:\ZephyrAlpha\docs\`，新一轮架构梳理

两套目录并存带来的具体问题：

- `.cursor/rules` 和 `AGENTS.md` 引用路径不一致，AI agent 读到冲突信息
- 新增内容不知道放哪里，有的人放旧树、有的放新树
- 同主题文档在两处各有一份，勾选/更新同步失败
- 迁移脚本、索引系统、pre-commit hook 必须处理两套路径

**相关讨论**：`architecture-rationale-log.md` Stage 1、Stage 2；结论 R1 / R4 / R5 / R6

## 3. 考虑过的方案（Options Considered）

### 方案 A：在旧树上原地治理

- **优点**：
  - 不用搬迁文件
  - 引用链无需重建
- **缺点**：
  - 旧树结构性混乱（目录编号、命名、层级都有历史债）
  - 补丁式修复无法根治
  - "边治理边写新内容"会持续污染
- **机构案例**：少数机构尝试过，普遍失败

### 方案 B：双树并存，新旧各司其职

- **优点**：
  - 保留旧树便于回溯
  - 新内容进新树不受干扰
- **缺点**：
  - **双真源**是机构治理的头号反模式
  - 任何规则、索引、迁移脚本都要处理"哪个是当前有效"
  - 新 AI agent 进来必定困惑
  - 引用链断裂风险极高
- **机构案例**：几乎没有机构长期维持双真源，最终都会收敛到一个

### 方案 C：建立新树 `docs/` 为唯一真源，旧树转只读归档（**本 ADR 选定**）

- **优点**：
  - 单一真源，所有规则、索引、AI 统一只读一处
  - 新内容可以按机构终局 IA 起草，不背历史债
  - 迁移过程可控（`migration-mapping.yaml` 跟踪）
  - 旧树保留作为历史凭证，不丢信息
- **缺点**：
  - 迁移初期需要双向引用（旧→新）
  - 搬迁工作量大（43 P0 + 106 P1 + 88 P2 蓝图）
- **机构案例**：Google、Microsoft、大型金融机构的内部知识重组都采用此模式

## 4. 决策（Decision）

**最终选择：方案 C —— 确立 `docs/` 为唯一 canonical 真源**

核心条款：

1. **真源声明**：`D:\ZephyrAlpha\docs\` 是 ZephyrAlpha 2.0 全部文档的唯一 canonical 真源
2. **旧树定位**：`D:\ZephyrAlpha\docs\`（旧树）为**只读归档**与**迁移来源**，禁止修改，禁止新增
3. **新内容约束**：所有新讨论、新设计、新决策**只在新树创建**
4. **迁移闸门**：旧树内容进入新树前，必须按新 IA 分类 + 统一 frontmatter + 通过 pre-commit 体检
5. **引用一致性**：所有规则文件（`.cursor/rules`、`AGENTS.md`、`.trae/rules`）只引用新树路径
6. **最终收口**：完成迁移后，旧树 `docs/` 应迁出到 `_legacy_archive/` 或类似占位

## 5. 后果（Consequences）

### 正面后果

- 单一真源消除 AI agent 读到冲突信息的风险
- 所有规则、索引、自动化只需处理一套路径
- 新内容质量可控（按新 IA 起草 + pre-commit 体检）
- 审计与合规路径清晰

### 负面后果 / 权衡

- 迁移期（预计持续 2~4 周）需要同时维护"迁入登记"
- 旧树的 dead link 无法立刻修复，需要迁移完成后批量修
- 依赖 `migration-mapping.yaml` 跟踪每份文档的新旧位置对应

### 未来需要重新审视的触发条件

- 出现第三方项目要求共享 `docs/` 时（重新评估顶层结构）
- 新树目录总数超过单 IA 设计容量时（重新评估分层）
- 外部合规要求强制双仓库时（极少发生）

## 6. 落地动作（Implementation）

详见 `19_development_workspace/taskbooks/taskbook.md` 中的"仓库搬迁与治理顺序"章节。

关键动作：

- [x] 新树骨架建立
- [x] 治理底座（`.cursor/rules`、`AGENTS.md`）更新为新路径
- [ ] P0 蓝图（43 份）迁移
- [ ] P1 蓝图（106 份）迁移 + 7 对重复合并
- [ ] P2 蓝图（88 份）迁移 + 88 份归档
- [ ] 7 对编号碰撞目录消解
- [ ] `module-inventory`、注册表、INDEX 重写
- [ ] 空壳目录清理 + Sentinel 验证

## 7. 参考

- 相关 ADR：ADR-0002（单 schema + 分阶段必填）、ADR-0003（双 AI 协作工作流）
- 相关文档：
  - `02_enterprise_architecture/architecture-rationale-log.md` Stage 1-2
  - `19_development_workspace/structure-and-mapping/target-information-architecture.md`
  - `19_development_workspace/taskbooks/taskbook.md`（仓库搬迁章节）
- 外部参考：Google "single source of truth" docs、Microsoft Azure Well-Architected Framework 信息架构章节

## 8. 修订记录

| 日期 | 说明 |
|------|------|
| 2026-04-17 | 初版：基于 rationale-log Stage 1-2 升格，拍板为 accepted。 |
