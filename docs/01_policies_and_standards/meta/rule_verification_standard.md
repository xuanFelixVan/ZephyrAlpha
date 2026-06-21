---
module_id: PS-STD-012
title: 规则验证标准
doc_type: standard
status: active
version: "1.2.1"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-02"
ttl: permanent
summary: "定义 ZephyrAlpha 规则体系的验证标准——五级验证（V1 自动化阻断/V2 自动化警告/V3 人工审查/V4 审计抽样/V5 深度内容审计）、验证频率矩阵、违规响应流程。V5 新增：四步审计流程+判定速查表+可脚本化评估。对标 OWASP ASVS v5、Kubernetes Conformance、ISO 42001 §8 验证要求。"
tags: [verification, conformance, compliance, meta-standard, owasp-asvs, kubernetes, iso-42001]
rule_form: declarative
scope: global
stability: evolving
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "§2~§3", why: "字段定义+受控词表——验证字段合法性依据"}
ai_autonomy: human_gated
---

# 规则验证标准

> **module_id**: PS-STD-012 | **version**: 1.2.1 | **status**: active | **layer**: cross_layer

---

## 1. 目的与范围

### 1.1 目的

本标准定义 ZephyrAlpha 规则体系的**验证标准**——如何确认规则被遵守、违规如何发现、发现后如何处理。

**根因**：PS-STD-003（行为边界）定义了"什么不能做"，但没有定义"怎么确认没做"。这导致：
- 每个 AI session 自行判断是否违规
- 没有统一的验证频率和验证方法
- 格式错误（如 PS-STD-003 的 `***` 分隔符问题）可以长期未被发现

> **对标**：
> - OWASP ASVS v5：三级验证体系（L1 自动化 / L2 人工+自动化 / L3 深度分析）
> - Kubernetes Conformance：标准化一致性测试套件
> - ISO 42001 §8.2：AI 系统运行验证要求
> - SOC 2 CC5.1：控制措施持续监控

### 1.2 范围

适用于 `01_policies_and_standards/` 下所有规则文档及其 enforcement 机制。

---

## 2. 验证分级体系

对标 OWASP ASVS v5 的三级体系 + 本项目特有需求，设定 **V1–V4 四级自动化与制度化验证**；**§7 V5** 为额外安排的深度内容审计（语义与标签一致性），不计入同一套频率矩阵的「级别编号」扩展——文档开头 summary 所称「五级」= V1~V4 + V5。

| 级别 | 名称 | 执行者 | 触发方式 | 响应时间 | 对标 |
|:---:|------|--------|---------|:---:|------|
| **V1** | 自动化阻断 | pre-commit / CI | 每次提交 | 即时 | OWASP ASVS L1 |
| **V2** | 自动化警告 | pre-commit / 扫描脚本 | 每次提交 / 每日 | 即时通知 | — |
| **V3** | 人工审查 | Owner / 审计员 | 每月 / 每季度 | 7 天内 | OWASP ASVS L2 |
| **V4** | 审计抽样 | 外部审计 | 每年 | 30 天内 | SOC 2 CC5.1 |

### 2.1 V1 自动化阻断

当以下条件触发时，操作被**自动阻止**：

| 触发条件 | 阻断规则 | 来源 |
|---------|---------|------|
| frontmatter 缺失或格式错误 | META-V01~V02 | PS-STD-001 §14 |
| doc_type 使用未定义值 | META-V03 | PS-STD-001 §14 |
| 修改 `stability: frozen` 文件 | P0 变更 | PS-STD-009 §2 |
| 删除 `ttl: permanent` 文件 | 禁止删除 | — |
| `blueprint_refs` 引用的蓝图不存在 | META-V16 | PS-STD-001 §14 |
| `index.md` 文件状态与实际 frontmatter `status` 不一致 | META-V21 | PS-STD-012 §2.1 |

**V1 阻断不可绕过**。任何 V1 阻断必须先修复问题，才能继续操作。

### 2.2 V2 自动化警告

以下条件触发时，生成**警告但允许继续**：

| 触发条件 | 警告规则 | 来源 |
|---------|---------|------|
| `date` 格式非 YYYY-MM-DD | META-V07 | PS-STD-001 §14 |
| `doc_type` 与存放路径不匹配 | META-V08 | PS-STD-001 §14 |
| `layer` 字段值不在合法列表 | META-V12 | PS-STD-001 §14 |
| `safety_level: H` 且 `review_status: unreviewed` | P1 警告 | PS-STD-001 §10.16 |
| `module_id` 前缀不在注册表中 | — | — |

**V2 警告累计**：同一类型警告在同一文件中出现 3 次以上 → 升格为 V1 阻断。

### 2.3 V3 人工审查

以下内容需人工定期审查：

| 审查内容 | 频率 | 审查人 | 检查点 |
|---------|:---:|--------|------|
| doc_type 语义准确性 | 每月 | Owner | 所有文件 doc_type 是否与实际内容匹配 |
| `summary` 质量 | 每月 | Owner | summary 是否足够帮助 AI 理解文档 |
| `tags` 覆盖率 | 每季度 | Owner | tags 是否覆盖 AI 检索关键词 |
| `depends_on` 完整性 | 每月 | Owner | 依赖关系是否最新 |

### 2.4 V4 审计抽样

每年由外部视角（不同 AI / 不同模型 / 人类审计员）进行一次抽样审计：

- 随机抽取 20% 的规则文件
- 按 V1~V3 标准重新验证
- 产出审计报告（`doc_type: audit_report`）

---

## 3. 验证频率矩阵

| 规则类型 | V1 阻断 | V2 警告 | V3 审查 | V4 抽样 |
|---------|:---:|:---:|:---:|:---:|
| `stability: frozen` | 每次修改 | 每次修改 | 每月 | 每年 |
| `stability: stable` | 每次修改 | 每次修改 | 每季度 | 每年 |
| `stability: evolving` | 每次修改 | 每次修改 | 每季度 | 可选 |
| `doc_type: policy` | 每次修改 | 每次修改 | 每月 | 每年 |
| `doc_type: standard` | 每次修改 | 每次修改 | 每季度 | 每年 |
| `doc_type: operational_rule` | 每次执行 | 每次提交 | 每月 | 每年 |

---

## 4. 违规响应流程

```
发现违规 → 判断级别 → 执行响应

V1 阻断：
  1. 阻止当前操作
  2. AI 记录违规到 Session Log
  3. 修复问题后重新提交

V2 警告：
  1. 允许继续操作
  2. AI 记录警告到 Session Log
  3. 同类型警告 3 次 → 升格为 V1

V3 审查发现：
  1. 记录到审查报告
  2. 分类：立即修复 / 下次修复 / 记入 Backlog
  3. Owner 裁定优先修复顺序

V4 抽样发现：
  1. 产出审计报告
  2. 向 Owner 提出系统性改进建议
```

---

## 5. 禁止行为

- **禁止**：绕过 V1 阻断继续操作
- **禁止**：忽略 V2 警告超过 3 次不处理
- **禁止**：跳过 V3 审查周期
- **禁止**：在 V4 审计中隐瞒已知问题

---
## 7. 深度内容审计方法（V5 级验证）

> **定位**：V1~V4 主要依赖机器可读字段（doc_type、module_id、status、stability 等）进行验证。
> 但存在一类"标签正确但内容错误"的问题——文件 frontmatter 声明自己是 policy，内容却是施工图。
> V5 级验证专门解决这类"字段验证通过但语义不符"的深层问题。
>
> **对标**：ISO 42001 §8.2 AI 系统影响评估——验证不能只查标签，必须审计实际行为与声明的一致性。
>
> **触发频率**：每次目录结构变更后、每次文件批量搬迁后、每次规则体系重大重构后。

### 7.1 审计流程（四步法）

```
Step 1：字段扫描（自动化，对应 V1~V2）
    └── 遍历所有文件 frontmatter → 检查 doc_type 是否在受控词表中
    └── 检查 doc_type 是否匹配所在目录的合法值（如 governance/ 下不能有 operational_rule）
    └── 检查文件名后缀是否匹配 doc_type（§一.0 强制映射表）
    └── 产出："字段违规清单"

Step 2：内容读取（人工/AI 深度审查，对应 V5）
    └── 对 Step 1 通过的文件，逐文件打开并阅读正文内容
    └── 判断标准：
        ├── 声明式规则（policy/standard/protocol）→ 正文应是"什么必须/禁止/推荐"，不是"怎么做"
        ├── 过程式规则（operational_rule）→ 正文应是"Step 1→N 操作步骤"，不是声明式禁令
        ├── 注册表（register）→ 正文应是结构化数据清单，不是叙事散文
        └── 索引入口（index）→ 正文应只是目录导航，不含规则文本
    └── 产出："内容-标签不一致清单"

Step 3：交叉验证
    └── 对照 directory-structure-standard.md 的反向映射表——确认每种内容类型是否在正确的目录
    └── 对照 module_id 命名空间——确认前缀是否匹配目录
    └── 对照 depends_on 引用链——确认引用的文件是否存在且 doc_type 一致
    └── 产出："跨文件一致性清单"

Step 4：判定与修复
    └── 对每个不一致项做出判定：
        ├── 放错目录 → 搬迁到正确目录（见 directory-structure-standard.md §5.1.2 反向映射表）
        ├── doc_type 写错 → 修改 frontmatter doc_type 为正确值
        ├── 文件名误导 → 按 §一.0 强制映射表改名
        └── 内容根本不是规则 → 搬出 01_policies_and_standards/，放到正确位置
    └── 产出："修复操作清单" + "修复后验证"
```

### 7.2 审计判定速查表

| 发现内容 | doc_type 声称为 | 实际内容为 | 判定 | 操作 |
|---------|:---:|---------|------|------|
| 蓝图（模块架构设计） | `policy` | 蓝图 | 🔴 标签+位置均错误 | 搬到 `03_modules/l*/模块名/blueprint.md` |
| 施工图（实施步骤） | `operational_rule` | 模块施工图 | 🔴 内容非操作规则 | 搬到 `03_modules/l*/模块名/construction-plan.md` |
| ADR 讨论稿 | `protocol` | 讨论草稿 | 🔴 内容类型错误 | 迁入 **`KB:decisions`** namespace（Git-backed）；若以 Markdown 草稿承载则在 `_development_workspace/` 或仓库批准的草稿路径撰写——禁止写入已删除的旧 `docs/02_enterprise_architecture/adr/` 树 |
| 路线图 | `standard` | 路线图 | 🔴 内容类型错误 | 搬到 `02_enterprise_architecture/` 或归档 |
| 会话日志 | `policy` | 会话记录 | 🔴 | 搬到 `session_logs/` |
| 声明式规则 | `policy`/`standard`/`protocol` | 确实是规则 | ✅ | 原地不动 |
| 过程式步骤 | `operational_rule` | 确实是操作流程 | ✅ | 原地不动 |

### 7.3 可脚本化的部分

| 检查项 | 脚本实现难度 | 建议实现位置 |
|--------|:---:|------|
| doc_type 是否在词表中 | ⭐ 容易 | GATE-11 pre-commit（已实现） |
| doc_type 是否匹配目录 | ⭐ 容易 | GATE-11 pre-commit（已实现） |
| 文件名后缀是否匹配 doc_type | ⭐ 容易 | GATE-11 N-08 新规则 |
| index.md 文件清单 vs 磁盘实际文件 | ⭐⭐ 中等 | `scripts/governance/check_index_integrity.py` |
| 内容关键词 vs doc_type（如 content 含"Step" 但 doc_type=policy） | ⭐⭐⭐ 较难 | `scripts/governance/scan_deep_content.py`（启发式，需人工复核） |
| 全文内容 vs doc_type 匹配 | ⭐⭐⭐⭐ 困难 | 人工审查 + AI 辅助（V5） |

> **大白话**：前三个检查项是机器干的活——脚本一秒扫完。最后两个才是你刚刚让我做的事情——打开文件看内容，判断它到底是不是它声称的那个类型。这个过程没有办法完全自动化，因为"内容像不像规则"需要理解上下文。但前三个检查项做好了，人工审查的工作量就从 70+ 个文件缩减到 3~5 个可疑文件。

---

## 8. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.2.1 | 2026-05-06 | §2：澄清 V1–V4 与 §7「V5 深度审计」关系；§2.1 `index.md` 失真阻断正式注册为 **META-V21**（PS-STD-001 §14.1）。§7.2：ADR 讨论稿处置改为 **KB:decisions**，移除对已删除 `docs/02_enterprise_architecture/adr/` 的指引。修正 §8 历史行 1.1.0 叙述（索引阻断不与 META-V17 混用）。版本号 patch +1。 |
| 1.2.0 | 2026-05-02 | **新增 V5 深度内容审计（minor）**。新增 §7：定义四步审计流程（字段扫描→内容读取→交叉验证→判定修复）、审计判定速查表（7 种常见不一致类型）、可脚本化程度评估（4 级难度）。对标 ISO 42001 §8.2。废除旧 doc_type-vocabulary.yaml v1.1.0 中"文件名不需要与 doc_type 一致"条款。旧 §6~§6 升格为 §7~§8。版本号 minor +1。 |
| 1.1.0 | 2026-05-01 | 新增 **索引一致性 / index 失真** V1 阻断项草案（后在 v1.2.1 正式编号为 **META-V21**，不得与 META-V17「废弃蓝图引用」混用）。版本号 minor +1。 |
| 1.0.1 | 2026-05-01 | 状态升格：draft → active。V1~V4 已在 PS-STD-001 §14 META-V 规则中实现，正式激活为标准。版本号 patch +1。 |
| 1.0.0 | 2026-05-01 | 初始创建——meta/ 目录系统审查后补齐。对标 OWASP ASVS v5 / Kubernetes Conformance / ISO 42001 §8 |
