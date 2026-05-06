---
module_id: GOV-MOD-001
title: 模块准入门控策略
doc_type: policy
status: active
version: "1.1.0"
layer: L01
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-06"
valid_from: "2026-05-06"
ttl: permanent
summary: "定义任何模块注入/变更 ZephyrAlpha 系统前必须通过的准入条件与评审流程——覆盖新增、变更、迁移三类操作。v1.1.0：§7 新增 #5 功能域重叠否决条件 + §7.1 四步判定流程——从'事后SSoT冲突裁决'升格为'事前功能域重叠预防'。根源：MOD-INF-003/004 与 006 功能域重叠未被现有规则拦截——MAD-001 只管层归属，§7 #1 只管 ID 不重复，唯独没有'功能域是否已被覆盖'这道闸门。"
tags: [module, governance, admission, gate, update, change]
rule_form: declarative
scope: global
stability: evolving
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "§2.5", why: "frontmatter字段唯一真源——doc_type/status/rule_form合法性"}
  - {target: PS-STD-003, at: "§3", why: "行为边界标准——准入否决条件的ABS约束基准"}
ai_autonomy: human_gated
---

# 模块准入门控策略

> module_id: GOV-MOD-001 | version: 1.0.0 | status: active | layer: L1

---

## 1. 目的与范围

本策略定义 ZephyrAlpha 系统中任何模块**进入系统前**必须通过的准入条件。覆盖三类操作：

- **新增模块**：`architecture-model/` 下所有新模块
- **模块变更**：active 模块的接口修改、依赖变更、status 变化、优先级调整——变更视同重新注入，必须重走准入。涉及 active 模块的变更还须先通过 GOV-ARCH-002（架构变更门控）
- **迁移模块**：从候选池注入正式目录的模块

第三方模块（外部引入）除本章四级筛选外，还须通过 §10 的专项安全检查。

本策略**不适用于**：纯文档类文件（doc_type: template/register）、临时草稿（status: draft 且未申请注入）。

## 2. SSoT 声明

本文档是 ZephyrAlpha 系统中**模块准入门控**的唯一真源（SSoT）。

**本文档定义了**：
- 四级准入筛选规则（MAD-001~004）及其通过/否决条件
- 准入评审流程与 P0 额外条件（MAD-005）
- 准入否决条件（快速失败门控）
- 准入记录格式（写入 `module-id-registry.json`）
- 紧急豁免路径与条件
- 第三方模块专项检查

**本文档与以下文件互补**（非取代关系）：
- GOV-MOD-005：注入技术检查——准入通过后执行 INJ-001~008
- GOV-ARCH-002：架构变更门控——active 模块变更审批

**若其他文件中出现与本策略冲突的准入门控定义，以本文档为准。**

## 3. 受控枚举定义

本策略不定义独立的受控枚举。以下枚举值的 SSoT 在其他文件中：
- `status` 合法值（planned/in_design/in_dev/testing/active/suspended/deprecated/archived）→ GOV-MOD-003 §3
- `runtime_plane` 合法值（hot/warm/cold）→ GOV-MOD-005 · INJ-005 `valid_values`

本策略的 MAD 规则**消费**这些枚举值但不重新定义。

## 4. 消费者注册表

以下文件直接依赖本策略——本策略规则变更时，必须同步更新：

| 消费者 | 文件 | Tier | 依赖内容 |
|--------|------|:---:|---------|
| module-id-registry.json | `data/` | 1 | `admission_records` JSON 结构——准入记录格式变更时 schema 必须同步 |
| GOV-MOD-005 | module-injection-rules.yaml | 1 | INJ-001~008 在 MAD-001~005 通过后执行——§7 否决条件表映射 INJ 编号 |
| GOV-ARCH-002 | governance/architecture/ | 1 | active 模块变更须先通过架构审查再走本策略 |
| GOV-MOD-003 | module-lifecycle-policy.md | 2 | MLC-001 `planned→in_design` 前置条件是"通过 GOV-MOD-001 准入门控" |

**Tier 说明**（定义来自 glossary.md #20）：Tier 1 = 硬编码了本策略规则编号/字段名的文件（变更必须同步）。Tier 2 = 消费本策略但不硬编码编号（建议同步）。

## 5. 准入四级筛选

> **执行顺序说明**：§7（准入否决条件）在先——四项前置否决是快速失败（fail-fast）。四级筛选（MOD-P1~P4）在否决条件通过后执行。完整端到端流程（含 GOV-MOD-005 注入检查）参见 GOV-MOD-005 · `context.injection_flow`（YAML key path）。

任何模块注入前必须**依次通过**以下四级筛选，任一级未通过即拒绝注入：

### MAD-001：架构必要性（MOD-P1）

模块必须在架构模型的架构分层中有**唯一且明确**的层归属（当前层数见 `architecture-model/_index.yaml`）。

- 通过条件：层归属唯一，且该层在 `_index.yaml` 中已定义
- 否决条件：无层归属、层归属模糊、层归属与现有模块冲突

### MAD-002：Phase 相关性（MOD-P2）

模块必须在当前 Phase 的优先级列表中。

- 通过条件：模块在当前 Phase 的 P0/P1 优先级列表中
- 否决条件：模块不在当前 Phase 范围内 → 延迟，放入候选池等待后续 Phase

### MAD-003：依赖关系合规（MOD-P3）

- 通过条件：depends_on 中所有模块 ID 已在注册表中存在，依赖图无环，且依赖方向符合 GOV-ARCH-001 的跨层规则（cold 层禁止依赖 hot 层）
- 否决条件：引用不存在的模块 ID、形成循环依赖、或违反跨层依赖方向约束

### MAD-004：接口可定义性（MOD-P4）

模块的接口必须可以被明确定义，禁止 AI 幻觉补全。

- 通过条件：接口来源于已有文档或 Owner 明确说明
- 否决条件：接口定义依赖 AI 推测 → 暂停，等待接口定义完成

## 6. 准入评审流程

```
模块提交 → MOD-P1 检查 → MOD-P2 检查 → MOD-P3 检查 → MOD-P4 检查 → 准入通过
                ↓              ↓              ↓              ↓
            拒绝注入       延迟注入       延迟注入       暂停等待
```

### MAD-005：P0 模块额外条件

当模块优先级为 P0 时，除四级筛选外还必须满足：

1. 接口契约在 `cross-layer-contracts.yaml` 中已定义且状态为 `frozen`
2. 已关联至少一个 ADR
3. 已分配 `runtime_plane`（hot/warm/cold）

## 7. 准入否决条件

以下情况**立即否决**，不进入评审流程：

| # | 否决条件 | 依据 |
|---|---------|------|
| 1 | module_id 在 `module-id-registry.json` 中已存在 | INJ-001 |
| 2 | depends_on 中包含不存在的模块 ID | INJ-002 |
| 3 | status 字段不是合法值之一（planned/in_design/in_dev/testing/active/suspended/deprecated/archived） | INJ-004 |
| 4 | P0 模块未分配 runtime_plane | INJ-005 |
| 5 | 功能域与已存在模块重叠——新模块的 summary/title/tags 与已有模块的 `responsibility_domain` 或核心职责明显重叠（判定流程见 §7.1） | MTH-008, IRN-003 |

### 7.1 功能域重叠判定流程（§7 #5 执行细则）

> 本流程是 §7 #5 否决条件的操作化执行指南。

**四步判定**：

```
Step 1：关键词交集扫描
  └── 新模块 summary + title 中的核心名词 vs 所有现有模块 summary + title
  └── 判定：交集 ≥ 60% → 🔴 标记"高风险重叠"，跳 Step 4
         交集 30%~60% → 🟡 标记"疑似重叠"，跳 Step 2
         交集 < 30% → ✅ 跳过 #5，进入后续筛选

Step 2：responsibility_domain 精确匹配
  └── 新模块声明的 responsibility_domain 是否已被任何现有模块的 responsibility_domain 完全覆盖？
  └── 是 → 🔴 否决——创建新蓝图
         否 → 🟡 跳 Step 3

Step 3：covers[] 子域交叉
  └── 新模块的 covers[] 是否与任何现有模块的 covers[] 存在交集？
  └── 是 → 🔴 否决——子域被覆盖 → 应升级原蓝图（version bump + changelog）
         否 → ✅ 通过 #5

Step 4：输出否决建议
  └── 不创建新模块。建议路径（优先级递减）：
      ① 升级已有蓝图 {module_id}：version bump + changelog 记录新增节
      ② 若新责任无法归入任何已有蓝图 → 提交 Owner 裁定
      ③ 禁止：创建平行蓝图覆盖已有子域
```

**自动化潜力**：Step 1（关键词扫描）可脚本化；Step 2-3（responsibility_domain + covers[]）需该字段落地后自动化。当前阶段：AI 手动执行四步判定，每次创建新模块时记录判定过程于 Session Log。

## 8. 准入记录

每次准入评审必须记录以下信息，写入 `module-id-registry.json` 的 `admission_records` 数组：

- 评审时间（ISO 8601）、评审者（AI / Owner）
- 四级筛选结果（通过/未通过/原因）
- P0 额外条件结果（如适用）
- 最终决定（admitted / deferred / rejected / paused）
- 是否紧急豁免（`override: true/false`）

记录格式（与 INJ 检查结果统一存放）：
```json
{
  "module_id": "GOV-MOD-XXX",
  "admission_records": [{
    "date": "2026-05-01T12:00:00Z",
    "reviewer": "AI",
    "p1_arch": "passed",
    "p2_phase": "passed",
    "p3_dep": "passed",
    "p4_iface": "passed",
    "p0_extras": "N/A",
    "decision": "admitted",
    "override": false
  }]
}
```

> **临届状态声明**：四级筛选通过 = 准入临时通过。最终注入以 GOV-MOD-005 全部 INJ 检查通过为准。INJ 检查失败视为准入回退——模块回到"未准入"状态，修正后重新提交。

## 9. 紧急豁免路径

当模块被否决但 Owner 认为存在紧急业务需要时，可启动紧急豁免：

1. **Owner 发起**：Owner 以书面形式（session log 或 ADR）声明豁免理由
2. **记录否决原因**：明确记录哪一级筛选未通过、原因
3. **风险接受声明**：Owner 明确声明接受该模块注入的技术风险
4. **限时有效**：豁免仅在当前 Phase 有效。下一 Phase 开始前，被豁免的模块必须补齐所有筛选条件，否则自动回退为"未准入"
5. **豁免记录**：在 `module-id-registry.json` 中标注 `admission_override: true` + 豁免原因

## 10. 第三方模块专项检查

外部引入的第三方模块，除四级筛选外，必须额外通过以下检查：

| # | 检查项 | 通过条件 | 否决后果 |
|---|--------|---------|---------|
| 1 | **来源信任链** | 模块来源可追溯（官方仓库/认证发布者） | 拒绝注入 |
| 2 | **许可证合规** | 许可证与本项目兼容（Apache 2.0 / MIT / BSD 等） | 拒绝注入 |
| 3 | **安全审计** | 无已知 CVE（严重/高危），或 CVE 已有缓解方案 | 暂停，等待安全评估 |
| 4 | **隔离声明** | 明确第三方模块的运行平面（hot/warm/cold）和资源边界 | 暂停，等待声明完成 |

## 11. 标准间引用规范

### 11.1 规范性引用（Normative）

以下文件的规定条款通过本文本的引用而构成本策略的条款。标明日期/版本的引用，后续修改不适用。未标明日期/版本的引用，其最新版本适用。

| 引用文件 | 节 | 角色 |
|---------|---|------|
| PS-STD-001 | §2 | frontmatter字段合法性——本文件所有frontmatter字段格式遵循其约束 |
| PS-STD-003 | §3 | 行为边界标准ABS——准入否决条件的宪法级边界基准——被ABS明确禁止的行为，本策略的MAD规则不能以"本策略另有规定"为由突破 |

### 11.2 信息性引用（Informative）

| 引用文件 | 节 | 角色 |
|---------|---|------|
| GOV-MOD-005 | context.injection_flow | 模块注入技术检查——准入通过后执行的完整INJ-001~008检查流程 |
| GOV-ARCH-002 | 全文 | 架构变更门控——active模块变更需先通过其审批后再走本策略的四级筛选 |

## 12. AI可消费性声明

本文件按 Anthropic CLAUDE.md 规范设计，面向 Vibe Coding AI 自治消费。

### 12.1 最低阅读路径（Minimum Reading Path）

1. **§2 SSoT声明**：确定本文件的管理域——准入门控的唯一真源
2. **§5 准入四级筛选**：MAD-001~004 四道关卡的具体通过/否决条件
3. **§7 准入否决条件**：4 种立即否决场景的快速速查表

### 12.2 Token 预算

| 项目 | 值 |
|------|---|
| 全文 Token | ~1400 |
| 精简路径（SSoT+MAD+否决条件+变更记录 front） | ~500 |

### 12.3 查找索引

| 概念 | 章节 | 解析 |
|------|------|------|
| module_id 重复 | §7 #1 | 立即否决，依据 INJ-001 |
| P0 额外条件 | §6 | 接口契约+ADR+运行平面 |
| 紧急豁免 | §9 | 限时有效，下一 Phase 必须补齐 |

## 13. 变更同步规则

本策略 `stability: evolving`——会随 Phase 边界而变化。以下矩阵定义变更类型与消费者同步要求：

| 变更类型 | 影响范围 | 同步动作 | 时机 |
|---------|---------|---------|------|
| 修改 MAD-001~004 筛选条件 | Tier 1 消费者 | 更新对应规则映射 + Tier 2 通知 | 同 commit |
| 新增/删除 §7 否决条件 | GOV-MOD-005（Tier 1） | 更新 INJ 编号映射 | 同 commit |
| 修改 admission_records 格式 | module-id-registry.json（Tier 1） | 更新 JSON schema | 同 commit |
| 修改紧急豁免规则（§9） | 全部 Tier 1+2 消费者 | 通知 + 评估影响 | 同 commit 或 24h 内 |
| frontmatter 仅变更（summary/tags/version） | 无 | 不需要同步 | — |
| 新增/重编号章节 | 全部消费者 | 更新交叉引用中的 § 编号 | 同 commit |

**违反同步规则的后果**：准入规则变更但 module-id-registry.json schema 未同步 → 准入记录写入失败 → 模块无法通过准入 → 系统不可用。

**消费者通知机制**：上述表中"通知"动作的执行方式见 GOV-MOD-002 §10 消费者通知机制——Session Log 条目 + ADR + module-id-registry.json 三层通知体系。

## 14. 修改条件

本策略 `ai_autonomy: human_gated`——AI 不可自主修改。以下为分级修改规则：

| 级别 | 变更范围 | 审批方 | 要求 |
|:---:|---------|--------|------|
| L0 | 错别字、措辞优化、格式调整 | AI 自批 | Session Log 记录即可 |
| L1 | MAD 规则条件微调（如新增通过条件） | Owner 审批 | Session Log 提案 → Owner 确认 |
| L2 | MAD 规则新增/删除、否决条件变更 | Owner 审批 | 须创建 ADR |
| L3 | 章节结构变更（新增/合并/删除） | Owner 审批 | 须创建 ADR + 对照 PS-STD-002 §3.2.4 确认合规 |
| — | `status` 从 draft 提升为 active | Owner 唯一 | 按 PS-STD-009 变更门控 P1 流程 |

## 15. 废弃流程

若本策略被更高层级的治理文件取代：

1. **搜索影响**：对全部 Tier 1 消费者执行全项目搜索 `MAD-001|MAD-002|MAD-003|MAD-004|MAD-005`——确认所有引用都有迁移路径
2. **通知期**：30 天提前通知全部消费者（Session Log + ADR）
3. **废弃标记**：`status: deprecated`，`superseded_by` 指向替代文件
4. **过渡期**：至少 90 天保留本文件，期间消费者完成迁移
5. **延期**：90 天到期后有引用未迁移 → Owner 可批准延期（最长再延 90 天）——必须在 Session Log 记录原因和新的截止日期
6. **归档**：过渡期满、全部引用已迁移 → `status: archived`——保留 module-id-registry.json 元数据（ID 永不回收原则，见 GOV-MOD-003 §4·archived）

## 16. 审查周期

对标 ISO 11179 §6.2 定期审查要求，本策略应在以下时机进行审查：

| 触发条件 | 审查内容 |
|---------|---------|
| 每次 Phase 边界（scaffold→1, 1→2...） | 四级筛选是否仍覆盖当前 Phase 的模块类型 |
| 新模块类型引入 | MAD 规则是否需要新增筛选条件 |
| 架构模型层级变更 | MAD-001 层归属检查的依据是否仍然有效 |
| 最低频率：每 6 个月 | 全量审查——即使无 Phase 变化 |

## 17. 完整性自检清单

创建或重大修改本策略时，逐项勾选：

- [ ] §1 目的与范围：明确覆盖新增、变更、迁移三类操作方向
- [ ] §2 SSoT 声明：互补关系覆盖 GOV-MOD-005 / GOV-ARCH-002
- [ ] §3 受控枚举：声明了 status 和 runtime_plane 的 SSoT 位置
- [ ] §4 消费者注册表：全部 Tier 1/2 消费者已列出，Tier 级别正确
- [ ] §7 否决条件：每条否决条件映射到正确的 INJ 编号
- [ ] §9 紧急豁免：定义了限时有效 + 自动回退 + 豁免记录
- [ ] §10 第三方检查：覆盖信任链/许可证/安全审计/隔离声明
- [ ] §11 标准间引用：normative 和 informative 分类正确
- [ ] §13 变更同步规则：每种变更类型有明确的同步动作和时机
- [ ] §15 废弃流程：覆盖通知→过渡期→延期机制→归档全流程

## 18. 变更记录

| 日期 | 版本 | 变更说明 |
|------|------|---------|
| 2026-05-06 | 1.1.0 | **SSoT 操作化——§7 新增 #5 功能域重叠否决条件 + §7.1 四步判定流程**。根源：MOD-INF-003/004 与 006 功能域重叠未被拦截——MAD-001 只管层归属唯一，§7 #1 只挡 module_id 重复，缺少"功能域是否已被覆盖"这道闸门。修复：(1) §7 #5 否决条件：新模块 summary/title/tags 与现有模块 responsibility_domain/covers[] 重叠 → 否决；(2) §7.1 四步判定流程：关键词扫描→responsibility_domain匹配→covers[]交叉→输出升级建议。治根逻辑：从"事后 SSoT 冲突裁决"升格为"事前功能域重叠预防"。版本号 minor +1。 |
| 2026-05-01 | 0.6.3 | P2 格式修正：§8 JSON 键名 p1_id→p1_arch（MAD-001 架构必要性）、p2_doc→p2_phase（MAD-002 Phase 相关性）——与 MAD 规则语义对齐 |
| 2026-05-01 | 0.6.2 | 消费者通知机制交叉引用：§13 变更同步规则添加通知机制引用——消费者通知方式见 GOV-MOD-002 §10（Session Log/ADR/registry 三层体系） |
| 2026-05-01 | 0.6.1 | 交叉引用漂移修复：消费者注册表 §5→§7 否决条件映射 INJ 编号——Round 10 插入 §3/§4 后未同步的 self-ref |
| 2026-05-01 | 0.6.0 | 对齐 PS-STD-002 §3.2.4（行为规则型条件性章节）：新增 §3 受控枚举声明 + §4 消费者注册表（Tier 1/2）+ §13 变更同步规则 + §14 修改条件（L0~L3 分级）+ §15 废弃流程（通知→过渡→延期→归档）+ §16 审查周期（ISO 11179）+ §17 完整性自检清单。修正 C1（YAML 路径引用格式）、C2（硬编码层数→引用 architecture-model）、C3（MOD-P3 命名一致性）。全文章节重编号 §3→§18。 |
| 2026-05-01 | 0.5.2 | Common Core 对齐 PS-STD-002 §3.2.1：新增 §2 SSoT声明 + §9 标准间引用规范（normative/informative）+ §10 AI可消费性声明（minimum reading path + lookup_index）+ 全文章节重编号（§2~§8 → §3~§11） |
| 2026-05-01 | 0.5.1 | 深颗粒审计修复：§2 执行顺序添加 GOV-MOD-005 §context.injection_flow 交叉引用——让全新 AI session 一次读完就知道端到端注入流程的完整顺序 |
| 2026-05-01 | 0.5.0 | 元规则对齐审计：frontmatter 添加 valid_from 字段（doc_type-vocabulary.yaml 要求）+ 字段排序对齐 PS-STD-001 §2.3 + layer cross_layer→L1（PS-STD-004 §4.2）+ depends_on 移除 GOV-MOD-005/GOV-ARCH-002 同级引用对齐链深=1层死规则（PS-STD-001 §2.1） |
| 2026-05-01 | 0.4.0 | 第三轮补缺：MAD-003 补齐跨层依赖方向约束（GOV-ARCH-001）+ 紧急豁免增加 30 天上限 + 准入记录定义 JSON format |
| 2026-05-01 | 0.3.0 | 补齐 G1~G10 细颗粒审查缺漏：新增模块变更（UPDATE）准入覆盖 + 临届状态声明 + 紧急豁免路径 + 第三方模块专项检查 + §4 执行顺序说明 |
| 2026-05-01 | 0.2.0 | #24 审批修复：ABS/COND → MAD-（MAD-001~MAD-005）。补齐 `ai_autonomy: human_gated`。`date` → 2026-05-01。 |
| 2026-04-30 | 0.1.0 | 初始版本 |
