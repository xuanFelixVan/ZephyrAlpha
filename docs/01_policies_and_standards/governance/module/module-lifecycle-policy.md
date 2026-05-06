---
module_id: GOV-MOD-003
title: 模块生命周期策略
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
summary: "定义模块从创建到归档的全生命周期阶段、转换条件与退役流程。v1.1.0：MLC-001 planned→in_design 前置条件强化——纳入 GOV-MOD-001 §7 #5 功能域不重叠检查——从生命周期层面堵住'planned 阶段无功能域检查→experimental 阶段才发现重叠→只能事后合并'的漏洞。"
tags: [module, governance, lifecycle]
rule_form: declarative
scope: global
stability: evolving
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "§4.1", why: "DocStatus语义——active/deprecated生命周期状态定义"}
  - {target: PS-STD-003, at: "§3", why: "行为边界标准——退役流程中的ABS-22跨级降格禁止"}
ai_autonomy: human_gated
---
# 模块生命周期策略
> module_id: GOV-MOD-003 | version: 1.0.0 | status: active | layer: L1
---
## 1. 目的与范围
本策略定义 ZephyrAlpha 系统中模块从创建到退役的全生命周期管理规则。适用于：
- `architecture-model/` 下所有模块
- `01_policies_and_standards/` 下所有 doc_type 文件
- 候选池中的模块
本策略**不适用于**：临时草稿（ttl: session）、纯引用文件。

## 2. SSoT 声明

本文档是 ZephyrAlpha 系统中**模块生命周期管理**的唯一真源（SSoT）。

**本文档定义了**：
- 8 个生命周期阶段（planned→archived）及其定义
- 阶段转换的前置条件与禁止逆向（MLC-001~002）
- P0 模块的特殊生命周期约束
- 退役流程（MLC-003）

**本文档与以下文件互补**（非取代关系）：
- GOV-MOD-001：模块准入门控——生命周期以 planned 阶段为起点的前提是必须通过准入
- GOV-MOD-005·INJ-004：注入检查中使用本规范的 8 个合法 status 值验证模块状态

**若其他文件中出现与本规范冲突的生命周期阶段定义或转换规则，以本文档为准。**

## 3. 受控枚举定义

本文档定义了 **8 个生命周期阶段**作为受控枚举——这些值的 SSoT 在本文件中，不可在其他文件中重新定义：

| 枚举值 | 含义 | 进入条件（摘要） | 退出条件 |
|--------|------|---------|---------|
| `planned` | 规划中 | 新模块 ID 分配 | 准入通过（GOV-MOD-001）→ in_design |
| `in_design` | 设计中 | 准入通过 | 接口契约草案完成 → in_dev |
| `in_dev` | 开发中 | 设计完成 | 代码实现+单测通过 → testing |
| `testing` | 测试中 | 开发完成 | 集成测试+Owner 审批 → active |
| `active` | 生产活跃 | 测试通过 | Owner 裁决 → suspended/deprecated |
| `suspended` | 暂停中 | 外部依赖不可用等 | 原因消除 → active |
| `deprecated` | 已废弃 | 替代模块就绪 | 迁移完成 → archived |
| `archived` | 已归档 | 迁移完成 | —（终态） |

**受控约束**：新增或删除阶段需要创建 ADR（见 §12 修改条件）。所有使用 `status` 字段的文件（GOV-MOD-001 §7 #3 准入否决条件、GOV-MOD-005 INJ-004）必须从本枚举表中消费值。

## 4. 消费者注册表

以下文件直接依赖本文档——生命周期规则变更时必须同步更新：

| 消费者 | 文件 | Tier | 依赖内容 |
|--------|------|:---:|---------|
| GOV-MOD-001 | module-admission-policy.md | 1 | §7 #3 准入否决条件 使用本规范的 `status` 枚举值（8 阶段列表）——INJ-004 映射 |
| GOV-MOD-005 | module-injection-rules.yaml | 1 | INJ-004 `valid_values` 直接从本文档 §3 枚举表复制——此复制值必须在本文档变更时同步 |
| GOV-MOD-004 | module-interface-contract-policy.md | 1 | IFC-005 契约状态受本规范阶段约束——契约状态映射到模块生命周期状态 |
| module-id-registry.json | `data/` | 1 | 每个模块的 `status` 字段值必须来自本规范枚举表 |
| GOV-ARCH-001 | governance/architecture/ | 2 | suspended/archived 阶段的模块在架构图中需特殊标识 |

## 5. 生命周期阶段
模块生命周期包含以下 8 个阶段，必须**严格按序**转换（suspended 为可恢复例外，见 MLC-002）：

```
planned → in_design → in_dev → testing → active → suspended → deprecated → archived
```
### MLC-001：阶段转换必须满足前置条件

任何模块从一个阶段转换到下一阶段，必须满足该转换的前置条件。禁止跳过阶段。

| 转换 | 前置条件 |
|------|---------|
| planned → in_design | 通过 GOV-MOD-001 准入门控（含 §7 #5 功能域不重叠检查）|
| in_design → in_dev | 接口契约草案完成；P0 模块需接口契约状态为 `frozen`（P0 约束详见 §8） |
| in_dev → testing | 代码实现完成，单元测试通过 |
| testing → active | 集成测试通过，Owner 审批（P0 额外约束详见 §8） |
| active → suspended | Owner 决策暂停（外部依赖不可用/业务暂停/等待条件） |
| suspended → active | 暂停原因已消除，Owner 审批恢复——**此回退不创建新 module_id** |
| active → deprecated | 有替代模块或 Owner 裁决退役（P0 额外约束详见 §6） |
| deprecated → archived | 90 天保留期满，所有引用已迁移，Owner 批准物理删除 |

### MLC-002：逆向转换限制

模块阶段**禁止**以下逆向转换：

| 禁止的逆向 | 替代做法 |
|-----------|---------|
| active → in_dev | 创建新模块（新 module_id），旧模块标记 deprecated |
| testing → in_dev | **例外允许**：测试发现非破坏性 bug 可回退至 in_dev 修复，修复后重新走 testing。不改变 module_id，但须在 Session Log 记录回退原因 |
| active → testing | 创建新模块 |
| suspended → 任何在 suspended 之前的阶段 | 先恢复至 active（suspended → active 允许），再决策后续路径 |

## 6. 阶段详情

### planned

模块已在架构模型中规划，但尚未开始设计。

- 必须有：module_id、层归属、优先级
- 禁止：代码实现、接口定义

### in_design

模块正在设计阶段，定义接口和依赖关系。

- 必须有：接口契约草案、依赖清单
- 禁止：代码实现（仅允许伪代码/接口定义）

> **契约冻结时序说明**：GOV-MOD-001 的 MOD-P4（接口可定义性）检查的是"模块边界是否清晰可定义"——并非要求"契约已 frozen"。模块通过准入后进入 in_design，在此阶段完成契约 draft→frozen（GOV-MOD-004·IFC-005），然后才能 in_design→in_dev。不存在先有鸡还是先有蛋的问题。

### in_dev

模块正在开发阶段，代码实现中。

- 必须有：接口契约（frozen）、代码骨架
- 禁止：注入到 active 环境

### testing

模块正在测试阶段，验证功能与接口一致性。

- 必须有：单元测试、集成测试计划
- 禁止：生产环境使用

### active

模块已上线，可在生产环境使用。

- 必须有：完整文档、测试覆盖、Owner 签收
- 变更必须走变更门控（GOV-ARCH-002）

### suspended

模块被 Owner 主动暂停，不进行任何操作。

- 触发条件：外部依赖不可用、业务需求暂停、等待上游条件满足
- 必须有：暂停原因记录在 Session Log 中
- 恢复路径：suspended → active（原因消除后，Owner 审批恢复，不创建新 module_id）
- 禁止：新功能开发、接口变更
- 暂停期间仍须响应安全补丁

### deprecated

模块已废弃，禁止新功能开发。

- 必须有：`superseded_by` 指向替代模块（或 `N/A`）
- 禁止：新功能开发、接口变更
- 保留期限：至少保留 90 天供引用迁移

### archived

模块已物理删除，仅在 module-id-registry.json 中保留元数据记录。

- 进入条件：deprecated 满 90 天 + Owner 批准物理删除
- 必须有：删除日期、删除审批人（Owner）
- **ID 永不回收原则**：module_id 在注册表中永恒保留，禁止重新分配给新模块
- 禁止：重新激活、重新注入

## 7. 退役流程

> 通用退役原则参见 `../../meta/rule-lifecycle-and-change-standard.md`（PS-STD-009）§5（退役流程 + 废弃级联）。以下为模块特有的退役步骤。

### MLC-003：退役必须完成引用迁移

模块从 active 转为 deprecated 前，必须完成以下步骤：

1. 确认所有依赖方已迁移到替代模块
2. 全项目搜索旧 module_id，确认无断链
3. 在 `module-id-registry.json` 中标记 `status: deprecated`
4. 设置 `superseded_by` 字段
5. 保留文件至少 90 天，90 天后经 Owner 批准方可物理删除（进入 archived）
6. **延期机制**：如果 90 天到期后仍有引用未迁移，Owner 可批准延期（最长再延 90 天）。延期必须在 Session Log 中记录原因和截止日期
7. **契约级联废弃**：模块进入 `archived` 时，触发以下级联动作（IFC-007）：
   a. 该模块在 `cross-layer-contracts.yaml` 中的所有 frozen 契约自动标记为 `deprecated`
   b. 消费者在迁移期限内完成迁移（从模块归档之日起算，迁移期限见 GOV-MOD-004 §18 废弃流程）
   c. 期满后契约自动进入 `archived` 状态

## 8. P0 模块的特殊生命周期约束

P0 模块（系统核心依赖）除上述通用规则外，额外受以下约束：

| 阶段转换 | 通用要求 | P0 额外要求 |
|---------|---------|-----------|
| in_design → in_dev | 接口契约草案 | 接口契约必须 `frozen`（非 P0 可 `draft`） |
| testing → active | 集成测试通过，Owner 审批 | 必须通过 GOV-ARCH-002 架构审查 + 至少关联 1 个 ADR |
| active → deprecated | 有替代模块 | 必须创建退役 ADR，记录影响分析和迁移方案 |
| 任何阶段 | — | 所有阶段转换必须在 Session Log 中记录，非 P0 仅记录关键转换 |

### P0 与普通模块的关键区别

| 维度 | 普通模块 | P0 模块 |
|------|---------|---------|
| planned 阶段 | 通过 GOV-MOD-001 准入门控（含 MOD-P4） | 通过 GOV-MOD-001 准入门控 + Owner 可行性背书 |
| in_design 阶段 | 接口契约状态为 frozen（P0 约束详见 §6） | 接口契约状态为 frozen + Owner 终审批准 |
| in_dev→testing | 自动化测试（INJ-006）通过 → Owner 审核 | 自动化测试通过 → Owner 审核 + Owner 额外集成演练 |
| testing→active | Owner 审批（P0 额外约束详见 §6） | Owner 审批 + Owner 执行发布 |
| suspended | 普通挂起——流程级暂停 | 不可挂起——P0 模块 suspended 视为不可接受风险，必须走紧急修复流程 |
| 退役 | 标准退役流程（见 §7 MLC-003） | 禁止退役——P0 退役前必须在 P1+ 模块中完成等效替代并 active 满 30 天 |

## 9. 标准间引用规范

### normative（必须遵守——修改这些引用源时本文档也须同步更新）

| 引用目标 | 引用位置 | 依赖内容 |
|---------|---------|---------|
| PS-STD-001 §4.1 | §2 MLC-001 status 语义 | active/deprecated 生命周期状态定义 |
| PS-STD-003 §3 ABS-22 | §7 MLC-003 退役 | 跨级降格禁止——deprecated 不能直接标记为 archived |
| GOV-MOD-001 MOD-P4 | §6 in_design | 接口可定义性筛选——决定模块是否能进入设计阶段 |
| GOV-MOD-004 IFC-005 | §6 in_design | 契约冻结时序——in_design 阶段接口契约必须 frozen |

### informative（仅供参考——变更时须评估影响但不强制同步）

| 引用目标 | 引用位置 | 用途 |
|---------|---------|------|
| GOV-MOD-005 INJ-004 | §3 受控枚举：8 个 status 值 | 注入时 status 合法性检查——本策略是合法值的 SSoT |
| PS-STD-009 §5 | §7 退役概览 | 通用废弃流程框架——本策略补充模块特有步骤 |
| GOV-ARCH-002 | §8 P0 约束 | P0 模块 active→deprecated 的架构审查 |

## 10. AI 可消费性声明

> 对标 Anthropic CLAUDE.md——直接向 AI 说明如何解析和执行本文档。

**AI 可直接执行的状态机规则**：
- MLC-001 转换表（§5）→ 8×8 状态转换矩阵，可机械化检查
- MLC-002 反向转换限制 → 除 suspended→active 和 testing→in_dev 外，所有反向禁止
- MLC-003 退役步骤 → 7 步流程，每步可检查和记录
- status 受控枚举值 → 8 个合法值（planned/in_design/in_dev/testing/active/suspended/deprecated/archived）

**需人类判断的规则**：
- planned→in_design：需 Owner 审批模块设计可行性
- testing→active：需 Owner 审批 + 集成测试通过
- 退役延期：需 Owner 书面批准，最长再延 90 天

**最小必读路径**（全新 AI session）：
1. §1 目的与范围 → 知道管辖范围
2. §2 SSoT 声明 → 知道本文档权威边界
3. §3 受控枚举 → 知道 `status` 的 8 个合法值
4. §5 生命周期阶段 → 知道 8 个阶段和 MLC-001 转换表
5. §7 退役流程 → 知道 MLC-003 7 步步骤

**Token 预算**：本文档约 1700 字（含 frontmatter），单次读取 ≤ 2500 tokens。

## 11. 变更同步规则

本策略 `stability: evolving`——生命周期阶段和转换条件会随 Phase 边界变化。以下矩阵定义变更类型与消费者同步要求：

| 变更类型 | 影响范围 | 同步动作 | 时机 |
|---------|---------|---------|------|
| 新增/删除生命周期阶段 | 全部 Tier 1 消费者 | 更新所有文件中的 `status` 枚举列表 + MLC-001 转换表 | 同 commit |
| 修改 MLC-001 转换条件 | GOV-MOD-001（Tier 1） | 确保准入规则与前置条件一致 | 同 commit |
| 修改 §3 受控枚举表 | GOV-MOD-005（Tier 1） | 更新 INJ-004 `valid_values` 列表 | 同 commit |
| 修改 MLC-003 退役步骤 | GOV-MOD-004（Tier 1） | 更新 IFC-007 消费者迁移步骤引用 | 同 commit 或 24h 内 |
| 修改 P0 特殊约束 | 全部 Tier 1 | 评估 P0 模块是否需重新审批 | 同 commit |
| frontmatter 仅变更 | 无 | 不需同步 | — |

**消费者通知机制**：上述表中"通知"动作的执行方式见 GOV-MOD-002 §10 消费者通知机制——Session Log 条目 + ADR + module-id-registry.json 三层通知体系。

## 12. 修改条件

本策略 `ai_autonomy: human_gated`——生命周期阶段定义不可由 AI 自主修改：

| 级别 | 变更范围 | 审批方 | 要求 |
|:---:|---------|--------|------|
| L0 | 错别字、措辞优化、格式调整 | AI 自批 | Session Log 记录 |
| L1 | 转换条件措辞微调（不改变语义） | AI 可建议，Owner 确认 | Session Log 提案 |
| L2 | 新增/删除生命周期阶段 | Owner 审批 | 必须创建 ADR |
| L3 | 修改 MLC-001~003 规则本体 | Owner 审批 | 必须创建 ADR + 全部 Tier 1 消费者同步 |
| — | `status` 枚举值新增/删除 | Owner 审批 | 必须创建 ADR——违反可能导致所有依赖模块的 `status` 字段值非法 |

## 13. 字段不重复声明

### 字段定义归属声明

本标准定义以下字段/枚举值（以本标准为准）：
- `status` 的 8 个生命周期阶段枚举值（planned/in_design/in_dev/testing/active/suspended/deprecated/archived）：见 §3 受控枚举表

本标准引用以下字段（以 PS-STD-001 为准，本标准不重复定义）：
- frontmatter 所有字段：见 PS-STD-001 §2
- doc_type 受控词表：见 PS-STD-001 §3
- status 基础语义（active/deprecated）：见 PS-STD-001 §4.1

**禁止**：其他标准中重复定义上述 `status` 枚举值。发现重复定义时，以本文档为准，其他标准改为引用 §3。

## 14. 跨标准字段交叉引用

| 本标准定义的字段/枚举 | 引用此值的其他标准 | 引用方式 |
|---------------------|-------------------|---------|
| `status` 8 阶段枚举值 | GOV-MOD-001 | §7 #3 准入否决条件 检查 status 合法性（INJ-004 映射）——消费本规范 §3 枚举表 |
| `status` 8 阶段枚举值 | GOV-MOD-005 | INJ-004 `valid_values` 直接从本规范 §3 复制——同步更新本表 |
| `status` 8 阶段枚举值 | GOV-MOD-004 | IFC-005 契约状态受本规范阶段约束——契约状态映射到生命周期状态 |
| `status` 8 阶段枚举值 | module-id-registry.json | `status` 字段值必须来自本规范枚举表 |

字段名或枚举值变更时，必须同步更新所有交叉引用方（见 §11 变更同步规则）。

## 15. 废弃流程

本策略定义了模块的废弃流程（MLC-003，§7），但本策略自身也可能被取代：

1. **搜索影响**：对全部 Tier 1 消费者搜索 `MLC-001|MLC-002|MLC-003`——确认所有引用都有迁移路径
2. **通知期**：30天提前通知全部消费者（Session Log + ADR）
3. **废弃标记**：`status: deprecated`，`superseded_by` 指向替代文件
4. **过渡期**：至少 90 天——新生命周期策略与旧策略并轨运行
5. **归档**：过渡期满 → `status: archived`

## 16. 异常豁免机制

**默认**：MLC-001 和 MLC-002 对所有模块同等约束。

**例外通道**：以下场景可申请豁免：

| 豁免场景 | 豁免内容 | 约束 |
|---------|---------|------|
| Phase 边界转换 | 临时跳过 testing→active 的集成测试前置条件 | Owner 审批，仅限 scaffold→1 |
| testing→in_dev 回退 | 允许从 testing 退回 in_dev | 前提：因外部依赖不可用导致（已在 MLC-001 表中标注为允许例外） |
| 紧急热修复 | 跳过 in_design→in_dev 的接口契约冻结条件 | 24h 内补齐契约 + Session Log 记录 |

**豁免规则**：每份豁免必须指定：豁免的 MLC 编号、豁免范围（具体模块）、有效截止日期。过期不续。

## 17. 审查周期

对标 ISO 11179 §6.2 定期审查要求，本策略应在以下时机进行审查：

| 触发条件 | 审查内容 |
|---------|---------|
| 每次 Phase 边界 | 8 阶段模型是否仍匹配当前架构节奏 |
| 新模块类型引入 | 是否需要新增阶段（如 `security_review`） |
| P0 模块列表变更 | P0 特殊生命周期约束是否需调整 |
| GOV-MOD-001 准入门控变更 | MLC-001 planned→in_design 前置条件是否需要更新 |
| 最低频率：每 6 个月 | 全量审查 |

## 18. 完整性自检清单

- [ ] §1 目的与范围：明确管辖所有模块的生命周期
- [ ] §2 SSoT 声明：互补关系覆盖 GOV-MOD-001/MOD-005/MOD-004/ARCH-001
- [ ] §3 受控枚举：8 阶段枚举完整——进入/退出条件对齐 MLC-001
- [ ] §4 消费者注册表：全部 Tier 1/2 消费者已列出
- [ ] §5 生命周期阶段：MLC-001 转换表覆盖全部 7 条转换边
- [ ] §6 阶段详情：每个阶段有进入/退出条件+停留时长建议
- [ ] §7 退役流程：MLC-003 7 步完整——含延期机制
- [ ] §8 P0 约束：P0 模块在所有阶段的额外约束已定义
- [ ] §9 标准间引用：normative 和 informative 分类正确
- [ ] §11 变更同步规则：每种变更类型有明确的同步动作和时机
- [ ] §13 字段不重复声明：status 枚举值归属已声明——禁止其他标准重复定义
- [ ] §14 跨标准字段交叉引用：消费者映射表已覆盖 GOV-MOD-001/005/004 + registry
- [ ] §15 废弃流程：覆盖本策略自身被取代的处置
- [ ] §16 异常豁免：豁免场景+约束完整，过期自动回退

## 19. 变更记录

| 日期 | 版本 | 变更说明 |
|------|------|---------|
| 2026-05-06 | 1.1.0 | **SSoT 操作化——MLC-001 planned→in_design 前置条件纳入功能域不重叠检查**。根源：MOD-INF-003/004 在 planned 阶段未被拦截进入 experimental——当时生命周期规则只要求"通过 GOV-MOD-001 准入门控"，而准入规则缺少功能域重叠检查（GOV-MOD-001 §7 #5 为本次同步新增）。修复：MLC-001 前置条件从模糊的"通过准入门控"升级为"通过准入门控（含 §7 #5 功能域不重叠检查）"——堵住生命周期最早阶段无重叠检查的漏洞。版本号 minor +1。 |
| 2026-05-01 | 0.6.4 | 交叉引用漂移修复：§7 b 迁移期限引用 GOV-MOD-004 §17→§18（GOV-MOD-004 插入 §6 禁止行为后废弃流程从 §17 变为 §18，第三轮全貌审计捕获） |
| 2026-05-01 | 0.6.3 | 交叉引用事实性错误修复：§3/§4/§14 三处 MAD-004→§7 #3 准入否决条件（GOV-MOD-001 的 status 枚举消费者——MAD-004 是接口可定义性规则，不是 status 检查） + §5 MLC-001 两处 §6→§8（P0 额外约束集中定义在 §8，不在 §6） |
| 2026-05-01 | 0.6.2 | 消费者通知机制交叉引用：§11 变更同步规则添加通知机制引用——消费者通知方式见 GOV-MOD-002 §10（Session Log/ADR/registry 三层体系） |
| 2026-05-01 | 0.6.1 | 交叉引用漂移修复：10 处 stale ref（§5→§7，共 10 处）+ 补 PS-STD-002 §3.2.4 条件性章节：§13 字段不重复声明 + §14 跨标准字段交叉引用——status 8 阶段枚举被多文件消费，交叉引用映射表 + 字段归属声明 |
| 2026-05-01 | 0.6.0 | 对齐 PS-STD-002 §3.2.4（行为规则型条件性章节）：新增 §3 受控枚举定义（8阶段枚举表含进入/退出条件）+ §4 消费者注册表（Tier 1/2 含 GOV-MOD-001/005/004/ARCH-001）+ §11 变更同步规则 + §12 修改条件（L0~L3分级）+ §13 废弃流程 + §14 异常豁免机制（3场景含Phase/热修复/回退）+ §15 审查周期（ISO 11179）+ §16 完整性自检清单。修正 C7（MLC-003 硬编码30天→引用 GOV-MOD-004 §13）+ C8（IFC-005→GOV-MOD-004·IFC-005 标注文件来源）。全文章节重编号 §3→§17。 |
| 2026-05-01 | 0.5.2 | Common Core 对齐 PS-STD-002 §3.2.1：新增 §2 SSoT声明 + §7 标准间引用规范（normative/informative）+ §8 AI可消费性声明 + 全文章节重编号（§2~§6 → §3~§9） |
| 2026-05-01 | 0.5.0 | 元规则对齐审计：frontmatter 添加 valid_from + 字段排序对齐 PS-STD-001 §2.3 + layer cross_layer→L1 + depends_on 移除 GOV-MOD-001/004/005 同级引用对齐链深=1层死规则（PS-STD-001 §2.1） |
| 2026-05-01 | 0.4.0 | 第三轮补缺：MLC-001 添加 P0 约束交叉引用（§5）+ in_design 添加契约冻结时序说明澄清 MOD-P4/IFC-005 顺序 + 退役延期机制（最长再延 90 天） |
| 2026-05-01 | 0.3.0 | 补齐 G5/G13/G14/G15/G16 细颗粒审查缺漏：testing→in_dev 回退例外 + 新增 suspended/archived 阶段 + P0 特殊约束 + depends_on 补齐 GOV-MOD-004 |
| 2026-05-01 | 0.2.0 | #24 审批修复：depends_on 结构化 + ai_autonomy: human_gated |
| 2026-04-30 | 0.1.0 | 初始版本 |
