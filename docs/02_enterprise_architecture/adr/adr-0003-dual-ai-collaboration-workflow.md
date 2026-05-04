---
module_id: ADR-0003
title: 采用 Kimi 发散 + Opus 收口的双 AI 协作工作流
doc_type: adr
status: superseded
version: 1.1.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-04-17
superseded_by: "非 ADR 机制取代——参见 docs/02_enterprise_architecture/target-architecture/vibe-coding-development-workflow.md + architecture-rationale-log.md 双管线"
superseded_at: '2026-04-27'
superseded_rationale: R71, R72, R76
supersedes: null
related_rationale: R9, R10, R71, R72, R76
related_open_questions: []
tags:
- ai-workflow
- cost-optimization
- collaboration
- handoff-protocol
- superseded
- wave0-arbitrated
summary: 采用双 AI 协作工作流：低成本发散模型（Kimi 等）负责头脑风暴与初稿，高质量收口模型（Opus 4.7）负责结构化与修错；通过 handoff-log
  作为结构化交接锚点，pre-commit `--scan-all` 作为收工体检闸门。
date: '2026-04-22'
ttl: permanent
---

# ADR-0003: 采用 Kimi 发散 + Opus 收口的双 AI 协作工作流

> ⚠️ **本 ADR 已被取代（2026-04-27 Wave 0 终审）**
>
> Wave 0 终审升级了 AI 协作工作流，从单管线（Kimi 发散 + Opus 收口）升级为：
> - **起草管线**：Kimi → GLM → Qwen 三步流水线
- **审计管线**：GLM → Kimi → Qwen 三轮独立审计
- **终审环节**：Cursor + Opus 4.7 在草稿区 `drafts-and-audits/` 批量裁定
- **单一草稿区**：草稿/审计/裁定同区，通过 frontmatter `audit_status` 字段做状态机驱动
- **V-12 蓝图真源准入门禁**：pre-commit 强制校验 Provenance 三件套

决策记录：[rationale-log R71/R72/R76/R80]（已随开发工作区迁至项目外部独立目录）。

## 1. 状态（Status）

- **当前状态**：`superseded`（2026-04-27 Wave 0 终审）
- **提议日期**：2026-04-17
- **拍板日期**：2026-04-17
- **被谁取代**：该 ADR 描述的工作流已被 Wave 0/Wave 1 终审全面升级——详见 rationale-log R71/R72/R76/R80（双管线 + 单一草稿区 + V-12 门禁）
- **取代了谁**：—

## 2. 背景与问题（Context）

单 AI 长期协作遇到的实际问题：

- **高端模型成本过高**：持续用 Opus 4.7 讨论一个复杂主题，token 成本显著
- **发散与收敛是两种不同能力**：高精度模型（Opus）在"立范式"与"查错"上强，但"发散思维"不如专门优化过的模型
- **免费模型有能力但有风险**：Kimi（Trae 环境）免费且发散能力强，但历史上踩过编码错误、格式错误、YAML 伪语法等坑（详见 `.trae/rules/encoding-safety.md` 第八章）
- **会话切换没有交接锚点**：从 Trae 切回 Cursor，上下文完全丢失，容易重复讨论

**实际需求**：

- 用**便宜 + 发散**的模型做头脑风暴、初稿
- 用**贵 + 精准**的模型做结构化、立范式、查错收口
- 两者之间有**结构化交接**，不让上下文丢失
- 每次收工有**机器可验证的健康闸门**，防止错误累积

**相关讨论**：`architecture-rationale-log.md` Stage 13-14；结论 R9（旧树"自动保存"是两层机制）、R10（新树应迁移的是机制）

## 3. 考虑过的方案（Options Considered）

### 方案 A：全程只用 Opus 4.7

- **优点**：
  - 质量稳定、不出错
  - 不需要交接协议
- **缺点**：
  - 成本高
  - 发散阶段被"高精度推理"拖慢创意
- **适合**：只做小型项目，不在意成本

### 方案 B：全程只用免费模型（如 Kimi）

- **优点**：
  - 零成本
- **缺点**：
  - 格式、YAML、Markdown 易出错（已踩坑记录在 `.trae/rules/encoding-safety.md`）
  - 立范式、查错能力弱
  - 长期累积小错导致文档体系腐烂
- **适合**：纯探索阶段，不涉及长期资产

### 方案 C：轮换使用不同模型，无固定分工

- **优点**：
  - 灵活
- **缺点**：
  - 没有明确的"哪一方负责什么"
  - 交接协议难以标准化
- **适合**：短期试验

### 方案 D：双 AI 分工 + 结构化交接（**本 ADR 选定**）

- **优点**：
  - ✅ 成本最优（发散用便宜模型、收口用贵模型）
  - ✅ 职责清晰（Kimi 发散、Opus 收敛）
  - ✅ 有 handoff-log 作为结构化交接锚点
  - ✅ 有 `--scan-all` 健康闸门防止错误累积
  - ✅ 可扩展到更多模型（Composer 2 做机械批量任务）
- **缺点**：
  - 需要维护 handoff-log 协议
  - 需要明确每个模型的"可做/不可做"边界（`.trae/rules/encoding-safety.md`）
- **机构案例**：主流 AI-assisted 研发团队的标准做法

## 4. 决策（Decision）

**最终选择：方案 D —— 双 AI 协作工作流**

### 4.1 模型分工

| 角色 | 模型候选 | 职责 |
|------|---------|------|
| **发散 / 头脑风暴 / 初稿** | Kimi K2.5（Trae 环境）、Grok 4.20、Gemini 3 Pro | 产生 idea、拓展思路、初步结构化 |
| **收口 / 立范式 / 查错 / 决策** | Opus 4.7 Medium | 架构决策、ADR 写作、格式查错、机构标准对齐 |
| **机械批量 / 迁移** | Composer 2 | 批量改引用、批量加 frontmatter、格式化重构 |

### 4.2 交接协议

所有 Kimi 会话**必须**在收工时填写交接工单（handoff-log，已随开发工作区迁至项目外部独立目录）。

每条 entry 模板：

```markdown
### 会话 YYYY-MM-DD-NN：一句话标题

- **讨论主题**：...
- **改动文件**：（列清单）
- **新结论**：（写进了哪份文档）
- **新未决**：（登记到 open-questions 了吗）
- **体检结果**：`--scan-all` 输出摘要
- **交棒给**：Cursor/Opus 或 用户
- **下一轮建议**：...
```

### 4.3 收工体检闸门

```powershell
python scripts/hooks/doc_guard_pre_commit.py --scan-all --docs-root docs
```

输出必须为 `✅ 文档质量检查全部通过`，才可交棒。

### 4.4 AI 写作边界

所有 AI（Kimi、Opus、Composer、其他）必须遵守：

- `.trae/rules/encoding-safety.md`（Trae 侧完整版）
- `.cursor/rules/encoding-tool-guard.mdc`（Cursor 侧精简版）
- `discussion-document-standard.md` v2.0.0（文档标准）

## 5. 后果（Consequences）

### 正面后果

- Token 成本显著下降（发散期用免费 / 低价模型）
- 质量不降（收口期 Opus 修错）
- 会话之间无上下文黑洞（handoff-log 承接）
- 错误可被机器检出（`--scan-all`）
- 可扩展到更多模型分工

### 负面后果 / 权衡

- 需要维护三份规则文件（`.cursor/rules`、`.trae/rules`、`discussion-document-standard.md`）
- Kimi 历史错误（YAML 伪语法等）需要持续打补丁
- 切换模型时上下文不如全程一个模型紧凑

### 未来需要重新审视的触发条件

- 某个免费模型质量显著提升，单模型即可胜任收口（可简化为单模型）
- Opus 价格大幅下降（重新评估成本侧）
- 出现更专门的"交接协议"工具（替代 handoff-log 手工填写）

## 6. 落地动作（Implementation）

- [x] 建立 `.trae/rules/encoding-safety.md` 第八章（YAML/Markdown 硬约束）
- [x] 建立 `.cursor/rules/encoding-tool-guard.mdc` 第六章（精简同步）
- [x] 建立 `handoff-log.md` 交接模板
- [x] 建立 `doc_guard_pre_commit.py --scan-all` 一键体检
- [x] 建立 `document-triage-guide.md` 内容分流指南
- [ ] 未来：Kimi 收工命令 / Opus 收工命令的模板化
- [ ] 未来：Composer 2 批量任务的标准 prompt 模板

## 7. 参考

- 相关 ADR：ADR-0001（唯一真源）、ADR-0002（单 schema + 分阶段必填）
- 相关文档：
  - `.trae/rules/encoding-safety.md`
  - `.cursor/rules/encoding-tool-guard.mdc`
  - 交接工单与文档分流指南（已迁至项目外部开发工作区）
  - `scripts/hooks/doc_guard_pre_commit.py`
- 外部参考：
  - Anthropic Opus 4.x 定价与能力官方说明
  - Kimi K2.5 能力评测
  - GitHub Copilot "multi-agent" 协作模式设计

## 8. 修订记录

| 日期 | 说明 |
|------|------|
| 2026-04-17 | 初版：确立 Kimi 发散 + Opus 收口 + Composer 2 机械批量的双/三 AI 协作工作流。 |
