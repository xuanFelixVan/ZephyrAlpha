---
module_id: ADR-0021
doc_type: adr
title: SSoT Validator — Phase 0 唯一强制门禁
version: 1.0.0
status: active
date: '2026-04-24'
owner: ZephyrAlpha-Owner
ttl: permanent
related_adrs:
- ADR-0001
- ADR-0002
- ADR-0013
- ADR-0015
priority: P0
phase: Phase-0
layer: cross_layer
classification: confidential
language: zh
created_by: agent
valid_from: '2026-04-24'
superseded_by: null
supersedes: null
related_rationale: []
related_open_questions: []
tags: [adr, vibe-coding]
summary: "**Phase 0 唯一强制门禁** SSoT Validator（三级违规分级 + pre-commit 阻塞 + 4-6 人日升级）| accepted"
---

# ADR-0021: SSoT Validator — Phase 0 唯一强制门禁

**状态**：Accepted
**日期**：2026-04-24
**决策者**：ZephyrAlpha-Owner
**优先级**：P0（最高）
**阶段**：Phase 0（强制前置，阻塞一切下游建设）

---

## 1. 状态（Status）

- **当前状态**：`accepted`
- **提议日期**：2026-04-24
- **拍板日期**：2026-04-24
- **被谁取代**：—
- **取代了谁**：—

## 2. 背景与问题（Context）

### 2.1 为什么现在必须决策

11 源审计（`vibe-coding-audit-merged.md` §Kimi 根因 #7）识别出 **"SSoT 矛盾未清零"** 是所有下游建设的**前置阻塞根因**：

- 老树残留的 `docs/` 路径与新树 `docs/` 路径在任务卡、配置文件、代码注释中并存
- `frontmatter.status` / `frontmatter.version` / `frontmatter.module_id` 存在孤立违规（部分 ADR 用 `status: Draft` 旧值，部分用 `Active` 新值）
- 跨文档引用链接（相对路径）在历次搬家后有死链
- 14 层 `l<NN>_` 命名出现历史口径歧义（`l10_compliance` vs `l10_compliance` vs `l10_compliance_governance`）
- 合规率预估（2026-04-22 手动抽查）：全库 frontmatter **≤ 10%**

### 2.2 Phase 0 地位

- ThoughtWorks SpecKit "Constitution 阶段"要求：任何建设工作前必须先把"宪法"（规范）锁定
- `phase-transition-protocol.md` 明确 Phase 0 → Phase 1 门禁"SSoT 合规率 100%"
- **若带着矛盾进入 Phase 1**，所有 `import-linter` 规则、`Fitness Functions`、entity-graph 都将基于错误基线构建 → 级联返工

### 2.3 历史证据

Qwen 技术评审（§Qwen 选型表 #P0-1）与 Opus 4.7 §四"Phase 0 耗时升级裁定"一致：

- 原估 Phase 0 = 2-3 人日（假设合规率 80%）
- 实测合规率 ≤ 10% → 升级为 **4-6 人日**（自动修复 + 人工仲裁 + 回归验证）

---

## 3. 考虑过的方案（Options Considered）

### 方案 A：并行建设 + 事后清理（Defer-and-Cleanup）

- **做法**：Phase 0 跳过 SSoT 校验，进入 Phase 1 核心服务建设，待 Phase 2 再统一清理
- **优点**：Phase 0 压力小，AI 编码体验连续
- **缺点**：
  - Kimi 根因 #7 警告：事后清理产生**级联错误**（引用错误基线构建的代码需重写，不是改字段）
  - 老树 11 源审计已证伪此路径
- **结论**：**否决**

### 方案 B：只做 lint 式字段校验（Shallow Check）

- **做法**：只校验 frontmatter 字段合法性，不校验跨文档引用 / 路径一致性 / 命名口径
- **优点**：实现快（半人日）
- **缺点**：漏掉根因 #7 的核心矛盾（跨文档引用 + 路径 + 命名），与不做差异不大
- **结论**：**否决（覆盖不足）**

### 方案 C：深度 SSoT Validator + Phase 0 强制门禁 ✅

- **做法**：
  1. 扩展现有 `scripts/governance/validate_ssot.py`（骨架已存在）
  2. 三级违规分级：**P0**（层 ID 无效 / 死链 / 跨抽屉引用破损）/ **P1**（status 值漂移 / version 倒挂）/ **P2**（其他轻微）
  3. pre-commit hook 拒绝 P0 > 0
  4. CI 每次 PR 全库扫描 + 生成修复建议
  5. Phase 0 出口门禁：P0 = 0 且 P1 ≤ 5 才允许进入 Phase 1
- **优点**：覆盖根因 #7 全部分枝，可量化、可回归
- **缺点**：Phase 0 实际耗时从 2-3 升到 4-6 人日（用户已接受）
- **结论**：**采纳**

---

## 4. 决策（Decision）

**最终选择：方案 C —— 深度 SSoT Validator + Phase 0 强制门禁**

### 4.1 关键决策点

| 决策点 | 选择 | 理由 |
|-------|------|------|
| Phase 0 是否阻塞下游 | **是（P0 违规 > 0 时强制阻塞）** | ThoughtWorks Constitution 原则 + Kimi 根因 #7 |
| Validator 实现方式 | **扩展现有 `scripts/governance/d5_architecture/validate_ssot.py`** | 避免重复造轮子，骨架已有 |
| 违规分级 | **P0 / P1 / P2 三级** | P0 立即阻塞；P1 告警；P2 记录 |
| 规则配置源 | **`ssot-authority-map.md`** | 规则即文档，人类可读 |
| pre-commit 接入 | **是** | 从源头阻止违规引入 |
| CI 接入 | **是** | PR 级全库扫描 + 报告 |
| Phase 0 出口门禁 | **P0 = 0 且 P1 ≤ 5** | P1 少量漂移容忍，但 P0 零容忍 |
| 估计工时 | **4-6 人日**（升级值）| 合规率 10% 现实反馈 |

### 4.2 违规分级详则

**P0（立即阻塞 pre-commit）**：

- 层 ID 不在 `l00_` ~ `l13_` 或 `shared/` 白名单
- frontmatter 缺失 `module_id` / `title` / `status` / `version`
- 跨文档引用链接死链（相对路径指向不存在的文件）
- 命名口径冲突（同一层多个命名并存）

**P1（告警但不阻塞，Phase 0 出口 ≤ 5）**：

- `status` 值不在枚举（`Draft` / `Active` / `superseded` / `deprecated` / `skipped`）
- `version` 倒挂（新修订版本号小于旧修订）
- `related_adrs` 引用不存在的 ADR ID

**P2（记录）**：

- tag 重复 / 大小写不一
- summary 超过 300 字
- 修订记录时间顺序错乱

### 4.3 规则配置分离

**规则**写在 `docs/01_policies_and_standards/ssot-validation-rules.md`（Stage J 待建）（人类可读 + AI 可消费）；**实现**在 `scripts/governance/d5_architecture/validate_ssot.py`。两者通过 YAML 中间件桥接。

---

## 5. 后果（Consequences）

### 5.1 正面后果

- **根因 #7 清零**：Phase 0 末全库 SSoT 合规率 100%（P0 = 0）
- **Phase 1 可靠基线**：所有 `import-linter` 规则 / `Fitness Functions` / entity-graph 在正确基线上构建，避免级联返工
- **文档治理闭环**：pre-commit + CI 双防线，Phase 1 后也不会回退
- **新成员 / AI Agent 友好**：违规立即可见，不需要"摸着石头过河"

### 5.2 负面后果 / 权衡

- **Phase 0 阻塞期延长**：2-3 人日 → 4-6 人日（双倍）；AI 协作短期受限
- **pre-commit 变慢**：全库扫描耗时估计 3-5s（可接受）
- **规则演化压力**：`ssot-authority-map.md` 需要按季度复盘

### 5.3 未来需要重新审视的触发条件

- 违规率连续 3 个月 < 0.5% 且 0 P0 事件 → 放宽 pre-commit 为告警模式
- 团队规模 ≥ 3 人 → Validator 需要"分 owner 分 scope"并行校验
- 进入 Phase 2 真实资金 → 合规审计要求升级，新增 P0 分级项
- 引入 Knowledge Graph 存储 → 可能替换 YAML 规则为 SPARQL/Cypher 查询

---

## 6. 落地动作（Implementation）

### 6.1 立即动作（Phase 0 内完成）

| # | 动作 | 物理位置 | 验收 |
|---|------|---------|------|
| 1 | 产出 `ssot-validation-rules.md` | `docs/01_policies_and_standards/`（Stage J 待建） | 规则表 ≥ 15 条，含示例 |
| 2 | 扩展 `validate_ssot.py` | `scripts/governance/d5_architecture/` | 覆盖 P0/P1/P2 三级检查 |
| 3 | pre-commit hook 接入 | `.pre-commit-config.yaml` | P0 > 0 拒绝 commit |
| 4 | CI PR 钩子 | `.github/workflows/ssot.yml` | PR 上自动扫描 + 评论 |
| 5 | 全库首次扫描 + 修复 | — | P0 = 0，P1 ≤ 5 |
| 6 | Phase 0 出口验证 + 签字 | `docs/09_audit/findings/phase0-exit-YYYYMMDD.md` | 签字人 = Owner |

### 6.2 下游消费（Phase 1 启动后）

- `02_enterprise_architecture/target-architecture/09-governance-architecture.md §6.4` 的 T0 门禁直接引用本 ADR
- `phase-transition-protocol.md` 的 Phase 0 exit_criteria `ssot_compliance_rate: 100%` 依赖本 Validator 产出的合规率数字
- 后续 ADR-0015 ~ ADR-0020（6 大核心服务）的落地任务卡都必须过 Validator 才能进入施工

---

## 7. 参考

- **真源章节**：
  - `vibe-coding-audit-merged.md §Kimi 根因 #7 SSoT 矛盾未清零`
  - `vibe-coding-audit-merged.md §Qwen Phase 0 升级`
  - `vibe-coding-audit-merged.md §Opus 4.7 §四 Phase 0 耗时升级裁定`
- **相关 ADR**：
  - [ADR-0001](./adr-0001-canonical-source-of-truth.md)：SSoT 根本原则
  - [ADR-0002](./adr-0002-single-schema-with-phased-required-fields.md)：frontmatter 规范
  - [ADR-0013](./adr-0013-governance-system-admission-criteria.md)：治理系统准入
- **相关架构视图**：
  - [`09-governance-architecture.md §6.3 T0` + `§6.4 SSoT Validator`](../target-architecture/09-governance-architecture.md)
  - [`phase-transition-protocol.md` Phase 0 → Phase 1 门禁](../../01_policies_and_standards/governance/architecture/phase-transition-protocol.md)
- **相关规则文档**：
  - `ssot-authority-map.md`（规则配置源）
  - `docs/01_policies_and_standards/ssot-validation-rules.md`（本 ADR 落地动作产出，Stage J 待建）
- **外部参考**：
  - ThoughtWorks SpecKit: Constitution phase requirements
  - Google ADR convention "decisions create facts"

---

## 8. 修订记录

| 日期 | 说明 |
|------|------|
| 2026-04-24 | v1.0.0 初版：Phase 0 唯一强制门禁（由 `vibe-coding-audit-merged.md` 三源共识推导）。B-e-1 产出。 |
