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
summary: "定义模块从创建到归档的全生命周期阶段、转换条件与退役流程。v1.1.0：MLC-001 planned→in_design 前置条件强化——纳�?GOV-MOD-001 §7 #5 功能域不重叠检查——从生命周期层面堵住'planned 阶段无功能域检查→experimental 阶段才发现重叠→只能事后合并'的漏洞�?
tags: [module, governance, lifecycle]
rule_form: declarative
scope: global
stability: evolving
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "§4.1", why: "DocStatus语义——active/deprecated生命周期状态定�?}
  - {target: PS-STD-003, at: "§3", why: "行为边界标准——退役流程中的ABS-22跨级降格禁止"}
ai_autonomy: human_gated
---
# 模块生命周期策略
> module_id: GOV-MOD-003 | version: 1.0.0 | status: active | layer: L1
---
## 1. 目的与范�?
本策略定�?ZephyrAlpha 系统中模块从创建到退役的全生命周期管理规则。适用于：
- `architecture-model/` 下所有模�?
- `01_policies_and_standards/` 下所�?doc_type 文件
- 候选池中的模块
本策�?*不适用�?*：临时草稿（ttl: session）、纯引用文件�?

## 2. SSoT 声明

本文档是 ZephyrAlpha 系统�?*模块生命周期管理**的唯一真源（SSoT）�?

**本文档定义了**�?
- 8 个生命周期阶段（planned→archived）及其定�?
- 阶段转换的前置条件与禁止逆向（MLC-001~002�?
- P0 模块的特殊生命周期约�?
- 退役流程（MLC-003�?

**本文档与以下文件互补**（非取代关系）：
- GOV-MOD-001：模块准入门控——生命周期以 planned 阶段为起点的前提是必须通过准入
- GOV-MOD-005·INJ-004：注入检查中使用本规范的 8 个合�?status 值验证模块状�?

**若其他文件中出现与本规范冲突的生命周期阶段定义或转换规则，以本文档为准�?*

## 3. 受控枚举定义

本文档定义了 **8 个生命周期阶�?*作为受控枚举——这些值的 SSoT 在本文件中，不可在其他文件中重新定义�?

| 枚举�?| 含义 | 进入条件（摘要） | 退出条�?|
|--------|------|---------|---------|
| `planned` | 规划�?| 新模�?ID 分配 | 准入通过（GOV-MOD-001）→ in_design |
| `in_design` | 设计�?| 准入通过 | 接口契约草案完成 �?in_dev |
| `in_dev` | 开发中 | 设计完成 | 代码实现+单测通过 �?testing |
| `testing` | 测试�?| 开发完�?| 集成测试+Owner 审批 �?active |
| `active` | 生产活跃 | 测试通过 | Owner 裁决 �?suspended/deprecated |
| `suspended` | 暂停�?| 外部依赖不可用等 | 原因消除 �?active |
| `deprecated` | 已废�?| 替代模块就绪 | 迁移完成 �?archived |
| `archived` | 已归�?| 迁移完成 | —（终态） |

**受控约束**：新增或删除阶段需要创�?ADR（见 §12 修改条件）。所有使�?`status` 字段的文件（GOV-MOD-001 §7 #3 准入否决条件、GOV-MOD-005 INJ-004）必须从本枚举表中消费值�?

## 4. 消费者注册表

以下文件直接依赖本文档——生命周期规则变更时必须同步更新�?

| 消费�?| 文件 | Tier | 依赖内容 |
|--------|------|:---:|---------|
| GOV-MOD-001 | module-admission-policy.md | 1 | §7 #3 准入否决条件 使用本规范的 `status` 枚举值（8 阶段列表）——INJ-004 映射 |
| GOV-MOD-005 | module-injection-rules.yaml | 1 | INJ-004 `valid_values` 直接从本文档 §3 枚举表复制——此复制值必须在本文档变更时同步 |
| GOV-MOD-004 | module-interface-contract-policy.md | 1 | IFC-005 契约状态受本规范阶段约束——契约状态映射到模块生命周期状�?|
| module-id-registry.json | `data/` | 1 | 每个模块�?`status` 字段值必须来自本规范枚举�?|
| GOV-ARCH-001 | governance/architecture/ | 2 | suspended/archived 阶段的模块在架构图中需特殊标识 |

## 5. 生命周期阶段
模块生命周期包含以下 8 个阶段，必须**严格按序**转换（suspended 为可恢复例外，见 MLC-002）：

```
planned �?in_design �?in_dev �?testing �?active �?suspended �?deprecated �?archived
```
### MLC-001：阶段转换必须满足前置条�?

任何模块从一个阶段转换到下一阶段，必须满足该转换的前置条件。禁止跳过阶段�?

| 转换 | 前置条件 |
|------|---------|
| planned �?in_design | 通过 GOV-MOD-001 准入门控（含 §7 #5 功能域不重叠检查）|
| in_design �?in_dev | 接口契约草案完成；P0 模块需接口契约状态为 `frozen`（P0 约束详见 §8�?|
| in_dev �?testing | 代码实现完成，单元测试通过 |
| testing �?active | 集成测试通过，Owner 审批（P0 额外约束详见 §8�?|
| active �?suspended | Owner 决策暂停（外部依赖不可用/业务暂停/等待条件�?|
| suspended �?active | 暂停原因已消除，Owner 审批恢复—�?*此回退不创建新 module_id** |
| active �?deprecated | 有替代模块或 Owner 裁决退役（P0 额外约束详见 §6�?|
| deprecated �?archived | 90 天保留期满，所有引用已迁移，Owner 批准物理删除 |

### MLC-002：逆向转换限制

模块阶段**禁止**以下逆向转换�?

| 禁止的逆向 | 替代做法 |
|-----------|---------|
| active �?in_dev | 创建新模块（�?module_id），旧模块标�?deprecated |
| testing �?in_dev | **例外允许**：测试发现非破坏�?bug 可回退�?in_dev 修复，修复后重新�?testing。不改变 module_id，但须在 Session Log 记录回退原因 |
| active �?testing | 创建新模�?|
| suspended �?任何�?suspended 之前的阶�?| 先恢复至 active（suspended �?active 允许），再决策后续路�?|

## 6. 阶段详情

### planned

模块已在架构模型中规划，但尚未开始设计�?

- 必须有：module_id、层归属、优先级
- 禁止：代码实现、接口定�?

### in_design

模块正在设计阶段，定义接口和依赖关系�?

- 必须有：接口契约草案、依赖清�?
- 禁止：代码实现（仅允许伪代码/接口定义�?

> **契约冻结时序说明**：GOV-MOD-001 �?MOD-P4（接口可定义性）检查的�?模块边界是否清晰可定�?——并非要�?契约�?frozen"。模块通过准入后进�?in_design，在此阶段完成契�?draft→frozen（GOV-MOD-004·IFC-005），然后才能 in_design→in_dev。不存在先有鸡还是先有蛋的问题�?

### in_dev

模块正在开发阶段，代码实现中�?

- 必须有：接口契约（frozen）、代码骨�?
- 禁止：注入到 active 环境

### testing

模块正在测试阶段，验证功能与接口一致性�?

- 必须有：单元测试、集成测试计�?
- 禁止：生产环境使�?

### active

模块已上线，可在生产环境使用�?

- 必须有：完整文档、测试覆盖、Owner 签收
- 变更必须走变更门控（GOV-ARCH-002�?

### suspended

模块�?Owner 主动暂停，不进行任何操作�?

- 触发条件：外部依赖不可用、业务需求暂停、等待上游条件满�?
- 必须有：暂停原因记录�?Session Log �?
- 恢复路径：suspended �?active（原因消除后，Owner 审批恢复，不创建�?module_id�?
- 禁止：新功能开发、接口变�?
- 暂停期间仍须响应安全补丁

### deprecated

模块已废弃，禁止新功能开发�?

- 必须有：`superseded_by` 指向替代模块（或 `N/A`�?
- 禁止：新功能开发、接口变�?
- 保留期限：至少保�?90 天供引用迁移

### archived

模块已物理删除，仅在 module-id-registry.json 中保留元数据记录�?

- 进入条件：deprecated �?90 �?+ Owner 批准物理删除
- 必须有：删除日期、删除审批人（Owner�?
- **ID 永不回收原则**：module_id 在注册表中永恒保留，禁止重新分配给新模块
- 禁止：重新激活、重新注�?

## 7. 退役流�?

> 通用退役原则参�?`../../meta/rule-lifecycle-and-change-standard.md`（PS-STD-009）�?（退役流�?+ 废弃级联）。以下为模块特有的退役步骤�?

### MLC-003：退役必须完成引用迁�?

模块�?active 转为 deprecated 前，必须完成以下步骤�?

1. 确认所有依赖方已迁移到替代模块
2. 全项目搜索旧 module_id，确认无断链
3. �?`module-id-registry.json` 中标�?`status: deprecated`
4. 设置 `superseded_by` 字段
5. 保留文件至少 90 天，90 天后�?Owner 批准方可物理删除（进�?archived�?
6. **延期机制**：如�?90 天到期后仍有引用未迁移，Owner 可批准延期（最长再�?90 天）。延期必须在 Session Log 中记录原因和截止日期
7. **契约级联废弃**：模块进�?`archived` 时，触发以下级联动作（IFC-007）：
   a. 该模块在 `cross-layer-contracts.yaml` 中的所�?frozen 契约自动标记�?`deprecated`
   b. 消费者在迁移期限内完成迁移（从模块归档之日起算，迁移期限�?GOV-MOD-004 §18 废弃流程�?
   c. 期满后契约自动进�?`archived` 状�?

## 8. P0 模块的特殊生命周期约�?

P0 模块（系统核心依赖）除上述通用规则外，额外受以下约束：

| 阶段转换 | 通用要求 | P0 额外要求 |
|---------|---------|-----------|
| in_design �?in_dev | 接口契约草案 | 接口契约必须 `frozen`（非 P0 �?`draft`�?|
| testing �?active | 集成测试通过，Owner 审批 | 必须通过 GOV-ARCH-002 架构审查 + 至少关联 1 �?ADR |
| active �?deprecated | 有替代模�?| 必须创建退�?ADR，记录影响分析和迁移方案 |
| 任何阶段 | �?| 所有阶段转换必须在 Session Log 中记录，�?P0 仅记录关键转�?|

### P0 与普通模块的关键区别

| 维度 | 普通模�?| P0 模块 |
|------|---------|---------|
| planned 阶段 | 通过 GOV-MOD-001 准入门控（含 MOD-P4�?| 通过 GOV-MOD-001 准入门控 + Owner 可行性背�?|
| in_design 阶段 | 接口契约状态为 frozen（P0 约束详见 §6�?| 接口契约状态为 frozen + Owner 终审批准 |
| in_dev→testing | 自动化测试（INJ-006）通过 �?Owner 审核 | 自动化测试通过 �?Owner 审核 + Owner 额外集成演练 |
| testing→active | Owner 审批（P0 额外约束详见 §6�?| Owner 审批 + Owner 执行发布 |
| suspended | 普通挂起——流程级暂停 | 不可挂起——P0 模块 suspended 视为不可接受风险，必须走紧急修复流�?|
| 退�?| 标准退役流程（�?§7 MLC-003�?| 禁止退役——P0 退役前必须�?P1+ 模块中完成等效替代并 active �?30 �?|

## 9. 标准间引用规�?

### normative（必须遵守——修改这些引用源时本文档也须同步更新�?

| 引用目标 | 引用位置 | 依赖内容 |
|---------|---------|---------|
| PS-STD-001 §4.1 | §2 MLC-001 status 语义 | active/deprecated 生命周期状态定�?|
| PS-STD-003 §3 ABS-22 | §7 MLC-003 退�?| 跨级降格禁止——deprecated 不能直接标记�?archived |
| GOV-MOD-001 MOD-P4 | §6 in_design | 接口可定义性筛选——决定模块是否能进入设计阶段 |
| GOV-MOD-004 IFC-005 | §6 in_design | 契约冻结时序——in_design 阶段接口契约必须 frozen |

### informative（仅供参考——变更时须评估影响但不强制同步）

| 引用目标 | 引用位置 | 用�?|
|---------|---------|------|
| GOV-MOD-005 INJ-004 | §3 受控枚举�? �?status �?| 注入�?status 合法性检查——本策略是合法值的 SSoT |
| PS-STD-009 §5 | §7 退役概�?| 通用废弃流程框架——本策略补充模块特有步骤 |
| GOV-ARCH-002 | §8 P0 约束 | P0 模块 active→deprecated 的架构审�?|

## 10. AI 可消费性声�?

> 对标 Anthropic CLAUDE.md——直接向 AI 说明如何解析和执行本文档�?

**AI 可直接执行的状态机规则**�?
- MLC-001 转换表（§5）→ 8×8 状态转换矩阵，可机械化检�?
- MLC-002 反向转换限制 �?�?suspended→active �?testing→in_dev 外，所有反向禁�?
- MLC-003 退役步�?�?7 步流程，每步可检查和记录
- status 受控枚举�?�?8 个合法值（planned/in_design/in_dev/testing/active/suspended/deprecated/archived�?

**需人类判断的规�?*�?
- planned→in_design：需 Owner 审批模块设计可行�?
- testing→active：需 Owner 审批 + 集成测试通过
- 退役延期：需 Owner 书面批准，最长再�?90 �?

**最小必读路�?*（全�?AI session）：
1. §1 目的与范�?�?知道管辖范围
2. §2 SSoT 声明 �?知道本文档权威边�?
3. §3 受控枚举 �?知道 `status` �?8 个合法�?
4. §5 生命周期阶段 �?知道 8 个阶段和 MLC-001 转换�?
5. §7 退役流�?�?知道 MLC-003 7 步步�?

**Token 预算**：本文档�?1700 字（�?frontmatter），单次读取 �?2500 tokens�?

## 11. 变更同步规则

本策�?`stability: evolving`——生命周期阶段和转换条件会随 Phase 边界变化。以下矩阵定义变更类型与消费者同步要求：

| 变更类型 | 影响范围 | 同步动作 | 时机 |
|---------|---------|---------|------|
| 新增/删除生命周期阶段 | 全部 Tier 1 消费�?| 更新所有文件中�?`status` 枚举列表 + MLC-001 转换�?| �?commit |
| 修改 MLC-001 转换条件 | GOV-MOD-001（Tier 1�?| 确保准入规则与前置条件一�?| �?commit |
| 修改 §3 受控枚举�?| GOV-MOD-005（Tier 1�?| 更新 INJ-004 `valid_values` 列表 | �?commit |
| 修改 MLC-003 退役步�?| GOV-MOD-004（Tier 1�?| 更新 IFC-007 消费者迁移步骤引�?| �?commit �?24h �?|
| 修改 P0 特殊约束 | 全部 Tier 1 | 评估 P0 模块是否需重新审批 | �?commit |
| frontmatter 仅变�?| �?| 不需同步 | �?|

**消费者通知机制**：上述表�?通知"动作的执行方式见 GOV-MOD-002 §10 消费者通知机制——Session Log 条目 + ADR + module-id-registry.json 三层通知体系�?

## 12. 修改条件

本策�?`ai_autonomy: human_gated`——生命周期阶段定义不可由 AI 自主修改�?

| 级别 | 变更范围 | 审批�?| 要求 |
|:---:|---------|--------|------|
| L0 | 错别字、措辞优化、格式调�?| AI 自批 | Session Log 记录 |
| L1 | 转换条件措辞微调（不改变语义�?| AI 可建议，Owner 确认 | Session Log 提案 |
| L2 | 新增/删除生命周期阶段 | Owner 审批 | 必须创建 KB 决策记录 |
| L3 | 修改 MLC-001~003 规则本体 | Owner 审批 | 必须创建 KB 决策记录 + 全部 Tier 1 消费者同�?|
| �?| `status` 枚举值新�?删除 | Owner 审批 | 必须创建 KB 决策记录——违反可能导致所有依赖模块的 `status` 字段值非�?|

## 13. 字段不重复声�?

### 字段定义归属声明

本标准定义以下字�?枚举值（以本标准为准）：
- `status` �?8 个生命周期阶段枚举值（planned/in_design/in_dev/testing/active/suspended/deprecated/archived）：�?§3 受控枚举�?

本标准引用以下字段（�?PS-STD-001 为准，本标准不重复定义）�?
- frontmatter 所有字段：�?PS-STD-001 §2
- doc_type 受控词表：见 PS-STD-001 §3
- status 基础语义（active/deprecated）：�?PS-STD-001 §4.1

**禁止**：其他标准中重复定义上述 `status` 枚举值。发现重复定义时，以本文档为准，其他标准改为引用 §3�?

## 14. 跨标准字段交叉引�?

| 本标准定义的字段/枚举 | 引用此值的其他标准 | 引用方式 |
|---------------------|-------------------|---------|
| `status` 8 阶段枚举�?| GOV-MOD-001 | §7 #3 准入否决条件 检�?status 合法性（INJ-004 映射）——消费本规范 §3 枚举�?|
| `status` 8 阶段枚举�?| GOV-MOD-005 | INJ-004 `valid_values` 直接从本规范 §3 复制——同步更新本�?|
| `status` 8 阶段枚举�?| GOV-MOD-004 | IFC-005 契约状态受本规范阶段约束——契约状态映射到生命周期状�?|
| `status` 8 阶段枚举�?| module-id-registry.json | `status` 字段值必须来自本规范枚举�?|

字段名或枚举值变更时，必须同步更新所有交叉引用方（见 §11 变更同步规则）�?

## 15. 废弃流程

本策略定义了模块的废弃流程（MLC-003，�?），但本策略自身也可能被取代�?

1. **搜索影响**：对全部 Tier 1 消费者搜�?`MLC-001|MLC-002|MLC-003`——确认所有引用都有迁移路�?
2. **通知�?*�?0天提前通知全部消费者（Session Log + ADR�?
3. **废弃标记**：`status: deprecated`，`superseded_by` 指向替代文件
4. **过渡�?*：至�?90 天——新生命周期策略与旧策略并轨运行
5. **归档**：过渡期�?�?`status: archived`

## 16. 异常豁免机制

**默认**：MLC-001 �?MLC-002 对所有模块同等约束�?

**例外通道**：以下场景可申请豁免�?

| 豁免场景 | 豁免内容 | 约束 |
|---------|---------|------|
| Phase 边界转换 | 临时跳过 testing→active 的集成测试前置条�?| Owner 审批，仅�?scaffold�? |
| testing→in_dev 回退 | 允许�?testing 退�?in_dev | 前提：因外部依赖不可用导致（已在 MLC-001 表中标注为允许例外） |
| 紧急热修复 | 跳过 in_design→in_dev 的接口契约冻结条�?| 24h 内补齐契�?+ Session Log 记录 |

**豁免规则**：每份豁免必须指定：豁免�?MLC 编号、豁免范围（具体模块）、有效截止日期。过期不续�?

## 17. 审查周期

对标 ISO 11179 §6.2 定期审查要求，本策略应在以下时机进行审查�?

| 触发条件 | 审查内容 |
|---------|---------|
| 每次 Phase 边界 | 8 阶段模型是否仍匹配当前架构节�?|
| 新模块类型引�?| 是否需要新增阶段（�?`security_review`�?|
| P0 模块列表变更 | P0 特殊生命周期约束是否需调整 |
| GOV-MOD-001 准入门控变更 | MLC-001 planned→in_design 前置条件是否需要更�?|
| 最低频率：�?6 个月 | 全量审查 |

## 18. 完整性自检清单

- [ ] §1 目的与范围：明确管辖所有模块的生命周期
- [ ] §2 SSoT 声明：互补关系覆�?GOV-MOD-001/MOD-005/MOD-004/ARCH-001
- [ ] §3 受控枚举�? 阶段枚举完整——进�?退出条件对�?MLC-001
- [ ] §4 消费者注册表：全�?Tier 1/2 消费者已列出
- [ ] §5 生命周期阶段：MLC-001 转换表覆盖全�?7 条转换边
- [ ] §6 阶段详情：每个阶段有进入/退出条�?停留时长建议
- [ ] §7 退役流程：MLC-003 7 步完整——含延期机制
- [ ] §8 P0 约束：P0 模块在所有阶段的额外约束已定�?
- [ ] §9 标准间引用：normative �?informative 分类正确
- [ ] §11 变更同步规则：每种变更类型有明确的同步动作和时机
- [ ] §13 字段不重复声明：status 枚举值归属已声明——禁止其他标准重复定�?
- [ ] §14 跨标准字段交叉引用：消费者映射表已覆�?GOV-MOD-001/005/004 + registry
- [ ] §15 废弃流程：覆盖本策略自身被取代的处置
- [ ] §16 异常豁免：豁免场�?约束完整，过期自动回退
