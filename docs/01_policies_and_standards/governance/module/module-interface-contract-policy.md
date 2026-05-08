---
module_id: GOV-MOD-004
title: 模块接口契约策略
doc_type: policy
status: active
version: "1.0.0"
layer: L01
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-02"
valid_from: "2026-05-02"
ttl: permanent
summary: "定义模块间接口契约要求、契约注册表、版本兼容规则、一致性验证、破坏性变更处理、退役级联规则及模块间运行时交互规则。v1.0.0 升格：被 19 处引用（6 个文件），实质已�?active 成熟度。draft→active 升格�?2026-05-02 审计驱动�?
tags: [module, governance, interface, contract, discovery, conformance]
rule_form: declarative
scope: global
stability: evolving
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "§2.5", why: "frontmatter字段唯一真源——策略文件的合同ID/版本管理字段定义"}
  - {target: PS-STD-003, at: "§3", why: "行为边界标准——破坏性变更的ABS约束"}
ai_autonomy: human_gated
---
# 模块接口契约策略
> module_id: GOV-MOD-004 | version: 1.0.0 | status: active | layer: L1
---
## 1. 目的与范�?本策略定�?ZephyrAlpha 系统中模块间交互必须定义的接口契约规则。适用于：
- 所�?P0 模块的接口定�?- 跨层模块间的交互接口
- 模块对外暴露�?API / 事件 / 数据接口
本策�?*不适用�?*：临时草案（ttl: session）、未注入的模块接口讨论稿�?
## 2. SSoT 声明

本文档是 ZephyrAlpha 系统�?*模块接口契约**的唯一真源（SSoT）�?
**本文档定义了**�?- 接口契约�?7 个必填字段（IFC-001）及唯一标识规则（IFC-002�?- 语义化版本规则（IFC-003）：MAJOR/MINOR/PATCH 判定标准
- 契约注册表（IFC-004）：`cross-layer-contracts.yaml` 维护规则
- 契约生命周期（IFC-005）：draft→frozen→deprecated→archived
- 一致性验证（IFC-006）：`validate_module_schema.py --check-contracts`
- Provider 退役时的契约级联废弃（IFC-007，由 GOV-MOD-003 MLC-003 触发�?- 模块间运行时交互规则

**本文档与以下文件互补**（非取代关系）：
- GOV-MOD-001 MOD-P4：接口可定义性筛选——本策略定义的契约是�?MOD-P4 通过之后的工�?- GOV-MOD-003 MLC-003：退役流程——触�?IFC-007 契约级联
- GOV-MOD-005 INJ-003：注入时契约存在性检查——消费本策略定义的契约注册表

**若其他文件中出现与本策略冲突的接口契约定义，以本文档为准�?*

## 3. 受控枚举定义

本文档定义了以下受控枚举，其 SSoT 在本文件中：

| 枚举�?| 含义 | 定义位置 | 说明 |
|--------|------|---------|------|
| `draft` | 契约草稿 | §11（IFC-005�?| 可变更，�?provider 消费 |
| `frozen` | 契约冻结 | §11（IFC-005�?| 不可变更，consumer 可接入——P0 模块注入前置条件 |
| `deprecated` | 契约废弃 | §11（IFC-005�? §12（IFC-007�?| 即将移除，consumer 应迁�?|

**受控约束**：新增契约状态或修改状态转换规则需要创�?ADR（见 §17 修改条件）。GOV-MOD-005 INJ-003 的契约状态检查消费本枚举�?
## 4. 消费者注册表

以下文件直接依赖本文档——接口契约规则变更时必须同步更新�?
| 消费�?| 文件 | Tier | 依赖内容 |
|--------|------|:---:|---------|
| GOV-MOD-005 | module-injection-rules.yaml | 1 | INJ-003 检�?`cross-layer-contracts.yaml` 是否存在——消费本规范的契约注册表格式 |
| GOV-MOD-003 | module-lifecycle-policy.md | 1 | MLC-003 步骤 7（契约级联废弃）——消�?IFC-007 的级联规�?|
| GOV-MOD-001 | module-admission-policy.md | 1 | MAD-005/MOD-P4 检查接口可定义性——消费本规范的契约是否已 frozen 的判�?|
| cross-layer-contracts.yaml | `data/` | 1 | 数据文件——字段格式和必填项由 §7 IFC-003 定义 |

## 5. 接口定义要求
### IFC-001：P0 模块必须定义接口契约

所有优先级�?P0 的模块，必须�?`cross-layer-contracts.yaml` 中定义接口契约，且状态为 `frozen` 后才能注入�?
接口契约必须包含�?
| 字段 | 说明 | 是否必填 |
|------|------|:-------:|
| contract_id | 契约唯一标识 | 🔴 |
| provider | 提供�?module_id | 🔴 |
| consumers | 消费�?module_id 列表 | 🔴 |
| interface_type | 接口类型：api / event / data | 🔴 |
| schema | 请求/响应/事件的数据结构定�?| 🔴 |
| version | 契约版本号（语义化版本） | 🔴 |
| status | 契约状态：draft / frozen / deprecated | 🔴 |

### IFC-002：接口变更必须走 ADR

任何�?`frozen` 的接口契约发生变更，必须创建 KB 决策记录 记录变更决策�?
- 非破坏性变更（新增可选字段）：ADR 简要记录即�?- 破坏性变更（删除字段、修改类型）：ADR 必须包含迁移方案和影响分�?
## 6. 禁止行为

以下行为在本策略管辖范围�?*严格禁止**，违反将导致注入拒绝或契约撤销�?
| 禁止行为 | 原因 | 替代方案 |
|---------|------|---------|
| P0 模块未在 `cross-layer-contracts.yaml` 中定义接口契约就注入 | 接口未定�?�?消费者无法接�?�?运行时错�?| �?IFC-001 定义全部 7 个必填字段后注入 |
| �?`frozen` 的接口契约未�?ADR 直接变更 | 契约变更是跨模块影响——绕�?ADR 导致消费者不知情，契约与实际实现漂移 | �?IFC-002 创建 KB 决策记录，破坏性变更须含迁移方案和影响分析 |
| 破坏性变更不提供双版本并行过渡期（≥30 天） | 消费者集中迁�?�?停机窗口 �?数据不一�?| �?§8 双版本并行运�?�?0 天后再下线旧版本 |
| 跨层调用绕过 `frozen` 契约直接操作 | 绕契约即绕治�?�?接口漂移 �?架构污染不可恢复 | 通过 `cross-layer-contracts.yaml` 中的 `frozen` 契约调用 |
| 模块间形成循环调用（A �?B �?A�?| 循环依赖 �?死锁风险 + 不可测试 �?架构腐化 | 依赖注入/事件总线解耦；设计阶段 MAD-003 应捕�?|
| 手动编辑 `cross-layer-contracts.yaml` 注册�?| 注册表是脚本同步的镜像——手动编辑导致与实际契约不一�?| 使用 `validate_module_schema.py --sync-contracts` 自动同步 |
| Provider 退役时不触�?IFC-007 契约级联废弃 | 消费者引用已废弃的契�?�?运行时错�?+ 断链累积 | 退役前完成 MLC-003 全部 7 步——含契约级联废弃通知 |

## 7. 版本兼容规则

### IFC-003：语义化版本兼容�?
接口契约版本号遵循语义化版本（MAJOR.MINOR.PATCH）：

| 变更类型 | 版本变更 | 兼容�?|
|---------|---------|--------|
| 修复 bug，不改变接口 | PATCH+1 | 完全兼容 |
| 新增可选字�?端点 | MINOR+1 | 向后兼容 |
| 删除字段/修改类型/改变语义 | MAJOR+1 | 破坏性变�?|

向后兼容的变更（PATCH/MINOR）可以不通知消费方。破坏性变更（MAJOR）必须：

1. 创建 KB 决策记录
2. 通知所有消费方
3. 提供至少 30 天的迁移�?4. 迁移期内同时支持新旧版本

## 8. 破坏性变更处�?
当接口发生破坏性变更时，必须执行以下流程：

1. **创建 KB 决策记录**：记录变更原因、影响范围、迁移方�?2. **双版本并�?*：新旧接口同时运行，旧接口标�?`deprecated`
3. **通知消费�?*：向所�?`consumers` 发出迁移通知
4. **迁移�?*：至�?30 天，消费方完成迁�?5. **旧接口下�?*：迁移期结束后，旧接口标�?`deprecated`，`superseded_by` 指向新版�?6. **清理**�?0 天后物理删除旧接口定�?
## 9. 接口文档要求

每个接口契约必须附带以下文档�?
- 接口用途说明（一段话�?- 请求/响应示例
- 错误码清�?- 性能约束（P0 模块必填�?*延迟 p99 与吞吐下�?MUST 在契约进�?`frozen` 之前**，由 Owner 写入 module-registry / cross-layer-contracts（或蓝图 SLA 小节）中�?SLA 字段；本策略正文不复制具体毫秒值或 qps。非 P0 选填�?- 调用频率限制（P0 模块必填；非 P0 选填�?
## 10. 契约发现与注册表

所有接口契约必须在 `cross-layer-contracts.yaml` 中统一注册——作为契约的唯一发现入口�?
### IFC-004：cross-layer-contracts.yaml 为契约注册表

- 格式：YAML，按 contract_id 索引
- 每个条目包含：contract_id / provider / consumers / interface_type / schema_version / status
- 消费者查找契约时�?*仅从此注册表查询**，禁止扫描源码推测接�?- **生消流程**：人�?AI 在模块文件中定义契约 schema（IFC-001 六字段）�?脚本 `validate_module_schema.py --sync-contracts` 将契约条目同步至注册表。注册表�?镜像"，禁止手动编辑——所有变更在源契约文件中进行

## 11. 契约生命周期

接口契约自身也有状态流转（独立于模块生命周期）�?
```
draft �?frozen �?deprecated
```

### IFC-005：契约状态转换条�?
| 转换 | 前置条件 |
|------|---------|
| draft �?frozen | provider 模块通过 GOV-MOD-001 准入门禁 + 契约 schema �?owner 审批 |
| frozen �?deprecated | 替代契约�?frozen + 所�?consumers 已迁�?+ 至少 30 天通知�?|
| deprecated �?archived | 契约从注册表物理删除（保�?audit log�?|

- `draft` 阶段契约仅供设计讨论，不�?IFC-003 版本兼容规则约束
- `frozen` 阶段契约受完整版本兼容规则约束（§7�?- `deprecated` 阶段契约禁止新增 consumer 引用

## 12. 契约一致性验�?
### IFC-006：模块必须通过契约一致性检�?
provider 模块注入和变更时，必须通过契约一致性验证：

- 验证命令：`python scripts/governance/validate_module_schema.py --check-conformance {module_id}`
- 验证内容�?  1. provider 实际暴露的接口是否与契约声明�?schema 一�?  2. 所�?consumers 引用的接口版本是�?�?provider 当前版本
  3. 跨层调用的契约是否存在且 frozen
- 失败动作：注入暂停，等待 provider 修正实现或更新契�?
### IFC-007：Provider 退役时契约级联废弃

�?provider 模块进入 GOV-MOD-003 �?`archived` 状态时，由 GOV-MOD-003 MLC-003 触发契约级联废弃。具体规则见 GOV-MOD-003 §7 步骤 7�?
## 13. 模块间交互规�?
模块间的运行时交互受以下规则约束——这些规则补充了单模块治理（GOV-MOD-001~005）未覆盖的跨模块场景�?
1. **调用失败不扩�?*：A 调用 B 失败时，A 必须处理异常（重�?降级/报错），不得让错误向上游传播�?C
2. **循环调用禁止**：禁�?A �?B �?A 的直接或间接循环调用。循环引用应�?depends_on 设计阶段�?MAD-003 捕获
3. **跨层调用的契约强�?*：跨层调用（�?hot→cold）必须通过 frozen 契约进行，禁止绕过契约直接操�?4. **级联退役通知**：当模块退役（deprecated/archived）时，必须在 Session Log 中列出所�?consumers，并逐个确认迁移状态（GOV-MOD-003 MLC-003�?
## 14. 标准间引用规�?
### normative（必须遵守——修改这些引用源时本文档也须同步更新�?
| 引用目标 | 引用位置 | 依赖内容 |
|---------|---------|---------|
| PS-STD-001 §2.5 | frontmatter depends_on | doc_type/rule_form 一致性约束——policy 文件的元数据合法�?|
| PS-STD-003 §3 | §8 破坏性变�?| ABS 级别约束——破坏性变更的流程合规基准 |
| GOV-MOD-001 MOD-P4 | §1 概述 | 接口可定义性筛选——决定模块是否具备接口设计资�?|
| GOV-MOD-003 MLC-003 步骤 7 | §12 IFC-007 | 退役触发契约级联废弃——是 IFC-007 规则的触发器 |

### informative（仅供参考——变更时须评估影响但不强制同步）

| 引用目标 | 引用位置 | 用�?|
|---------|---------|------|
| GOV-MOD-005 INJ-003 | §12 IFC-006 | 注入时契约存在性检查——消费本策略定义的契约注册表 |
| validate_module_schema.py | §10 IFC-004 / §12 IFC-006 | 脚本实现——契约注册表同步与一致性验证的执行工具 |

## 15. AI 可消费性声�?
> 对标 Anthropic CLAUDE.md——直接向 AI 说明如何解析和执行本文档�?
**AI 可直接执行的规则**�?- IFC-001（�?）→ 7 个必填字段，机械化检�?- IFC-002（�?）→ contract_id 命名模板 `{provider_id}.{consumer_id}.{interface_name}`，可正则校验
- IFC-003（�?）→ 语义化版本号判定（MAJOR=破坏性、MINOR=新增兼容、PATCH=修复），确定性规�?- IFC-004（�?0）→ 契约注册表为结构�?YAML，脚本同�?- IFC-006（�?2）→ 一致性验证命�?`validate_module_schema.py --check-contracts`

**需人类判断的规�?*�?- IFC-005 契约生命周期 �?状态转换需人类审批（draft→frozen→deprecated →archived�?- §8 破坏性变更流�?6 �?�?步骤 2（受影响方通知）和 6（清理决策）需人类判断
- §13 模块间交互规�?�?运行时行为判断依赖上下文

**最小必读路�?*（全�?AI session）：
1. §1 目的与范�?�?知道管辖范围
2. §2 SSoT 声明 �?知道本文档权威边�?3. §3 受控枚举 �?知道契约状态的 3 个合法�?4. §5 接口定义要求 �?知道 IFC-001/002 必填字段
5. §6 禁止行为 �?知道不可触碰的红线及替代方案
6. §10 契约注册�?�?知道注册表结构和生消流程
7. §12 契约一致性验�?�?知道 IFC-006 验证命令

**Token 预算**：本文档�?2000 字（�?frontmatter），单次读取 �?3000 tokens�?
## 16. 变更同步规则

本策�?`stability: evolving`——接口契约规范会�?Phase 边界变化。以下矩阵定义变更类型与消费者同步要求：

| 变更类型 | 影响范围 | 同步动作 | 时机 |
|---------|---------|---------|------|
| 修改 IFC-001 必填字段列表 | cross-layer-contracts.yaml（Tier 1�?| 更新数据文件 schema | �?commit |
| 新增/删除契约状态（§3 枚举�?| GOV-MOD-005（Tier 1�?| 更新 INJ-003 契约状态检�?| �?commit |
| 修改 IFC-004/005 审批流程 | GOV-MOD-003（Tier 1�?| 更新 MLC-001 in_design 契约冻结时序 | �?commit |
| 修改 IFC-007 级联废弃规则 | GOV-MOD-003（Tier 1�?| 更新 MLC-003 步骤 7 | �?commit |
| 修改 IFC-002 字段类型 | 全部 Tier 1 | 数据迁移 + 脚本更新 | �?PR，不�?commit（需 migration commit 先行�?|
| frontmatter 仅变�?| �?| 不需同步 | �?|

**消费者通知机制**：上述表�?通知"动作的执行方式见 GOV-MOD-002 §10 消费者通知机制——Session Log 条目 + ADR + module-id-registry.json 三层通知体系�?
## 17. 修改条件

本策�?`ai_autonomy: human_gated`——接口契约规范不可由 AI 自主修改�?
| 级别 | 变更范围 | 审批�?| 要求 |
|:---:|---------|--------|------|
| L0 | 错别字、措辞优化、格式调�?| AI 自批 | Session Log 记录 |
| L1 | 增加非破坏性字段（如新增一个选填字段�?IFC-001 表） | AI 可建议，Owner 确认 | Session Log 提案 |
| L2 | 修改 IFC 规则内容 / 契约状态枚�?| Owner 审批 | 必须创建 KB 决策记录 |
| L3 | 删除已有 IFC 规则 / 修改契约状态转换规�?| Owner 审批 | 必须创建 KB 决策记录 + 全部 Tier 1 消费者同�?|
| �?| `cross-layer-contracts.yaml` 数据文件字段结构 | Owner 唯一 | 数据文件 schema 变更影响所有模块，�?Owner 可操�?|

## 18. 废弃流程

若本策略被更完善的接口契约治理框架取代：

1. **搜索影响**：对全部 Tier 1 消费者搜�?`IFC-001|IFC-002|...|IFC-007`——确认所有引用都有迁移路�?2. **通知�?*�?0 天提前通知全部消费者（Session Log + ADR�?3. **废弃标记**：`status: deprecated`，`superseded_by` 指向替代文件
4. **过渡�?*：至�?90 天——新旧契约规范并轨运行，数据文件逐步重写
5. **归档**：过渡期满、全部引用已迁移 �?`status: archived`

## 19. 异常豁免机制

**默认**：IFC-001（P0 必须定义契约）和 IFC-006（一致性验证）对所有模块同等约束�?
**例外通道**�?
| 豁免场景 | 豁免内容 | 约束 |
|---------|---------|------|
| scaffold 原型阶段 | �?IFC-001 强制契约要求 | Owner 审批，scaffold�? 边界自动回退，必须在 experimental 开始前补齐 |
| 安全修复热更�?| 跳过 IFC-004 审批流程 | 24h 内补�?ADR |
| 契约一致性验证临时跳�?| 因外部验证脚本不可用 | 记录 Session Log，外部依赖恢复后立即补验 |

**豁免规则**：每份豁免必须指定豁免的 IFC 编号、豁免范围、有效截止日期。过期不续�?
## 20. 字段不重复声�?
本策略定义的字段不重�?PS-STD-001 或其他标准文件中已定义的字段。以下为本策略独有的契约专用字段声明�?
| 字段 | 定义位置 | 使用�?|
|------|---------|--------|
| `contract_id` | §5 IFC-001 �?| cross-layer-contracts.yaml |
| `provider` | §5 IFC-001 �?| cross-layer-contracts.yaml |
| `consumers` | §5 IFC-001 �?| cross-layer-contracts.yaml |
| `interface_schema` | §5 IFC-002 | cross-layer-contracts.yaml |

上述字段仅在本文档中定义，不存在跨标准重复定义�?
### 跨标准字段交叉引�?
以下为本策略定义的字段被其他标准/文件引用的情况：

| 本标准字�?| 引用此字段的其他标准/文件 | 引用方式 |
|-----------|------------------------|---------|
| `contract_id` | cross-layer-contracts.yaml | 数据文件的主键——每个契约条目使用此字段 |
| `provider` | cross-layer-contracts.yaml / GOV-MOD-005 INJ-003 | 数据文件的必填列——注入时检�?provider 是否为合法模�?ID |
| `consumers` | cross-layer-contracts.yaml / GOV-MOD-005 INJ-003 | 数据文件的必填列——注入时校验所�?consumer 模块 ID 存在 |
| `interface_schema` | cross-layer-contracts.yaml / GOV-MOD-005 INJ-006 | 数据文件的必填列——INJ-006 检�?schema 字段类型与契约定义一�?|

> 字段改名时，必须�?§16 变更同步规则同步更新 `cross-layer-contracts.yaml` �?GOV-MOD-005 INJ 规则中所有引用�?
## 21. 审查周期

对标 ISO 11179 §6.2 定期审查要求，本策略应在以下时机进行审查�?
| 触发条件 | 审查内容 |
|---------|---------|
| 每次 Phase 边界 | 契约字段表是否需要扩展（如新�?security_context 字段�?|
| 新语言/框架引入 | IFC-002 的字段类型定义是否需要更�?|
| P0 模块列表变更 | IFC-001 �?P0 强制契约范围是否需要调�?|
| GOV-MOD-003 生命周期模型变更 | 契约状态映射是否需要更�?|
| 最低频率：�?6 个月 | 全量审查 |

## 22. 完整性自检清单

- [ ] §1 目的与范围：明确覆盖 P0 模块，说�?P1/P2 的选填策略
- [ ] §2 SSoT 声明：互补关系覆�?GOV-MOD-005/MOD-003/MOD-001
- [ ] §3 受控枚举�? 契约状态枚举完�?- [ ] §4 消费者注册表：全�?Tier 1 消费者已列出
- [ ] §5 接口定义要求：IFC-001 字段表完整（7 字段�?- [ ] §6 禁止行为�? 条禁止行为覆盖接口契约全部风险面——含禁止+原因+替代方案三列
- [ ] §10 契约注册表：生消流程明确（禁止手动编辑注册表�?- [ ] §11 契约生命周期：draft→frozen→deprecated 状态转换完�?- [ ] §12 契约一致性验证：IFC-006 验证命令和失败动作明�?- [ ] §13 模块间交互规则：跨模块约束补充单模块治理的空�?- [ ] §14 标准间引用：normative �?informative 分类正确
- [ ] §16 变更同步规则：每种变更类型有明确的同步动作和时机
- [ ] §18 废弃流程：覆盖本策略自身被取代的处置
- [ ] §19 异常豁免�? 场景含约束和过期回退
- [ ] §20 字段不重复声明：契约专用字段已声明且无跨标准重复
- [ ] §20.1 跨标准字段交叉引用：contract_id/provider/consumers/interface_schema 的消费者引用表完整——字段改名时可定位所有影响方

## 23. 变更记录

| 日期 | 版本 | 变更说明 |
|------|------|---------|
| 2026-05-01 | 0.6.4 | P2 补齐：�?0 新增「跨标准字段交叉引用」子节——contract_id/provider/consumers/interface_schema 四个字段的跨文件引用�?+ 改名同步规则 |
| 2026-05-01 | 0.6.3 | P1 结构性添加：§6 禁止行为�? 条——覆盖未定义契约注入/frozen 绕过 KB 决策记录/破坏性变更无过渡�?绕契约跨层调�?循环调用/手动编辑注册�?退役不级联废弃�? 全部后续章节 §7→�?…�?2→�?3 重编�?+ 自引�?§ 编号同步修正（~25 处） + §15 AI 可消费性最小必读路径更�?|
| 2026-05-01 | 0.6.2 | 消费者通知机制交叉引用：�?5→�?6 变更同步规则添加通知机制引用——消费者通知方式�?GOV-MOD-002 §10（Session Log/ADR/registry 三层体系�?|
| 2026-05-01 | 0.6.1 | 交叉引用漂移修复�?7 �?stale ref（IFC-001 §3→�?·IFC-003 §4→�?·IFC-004 §7→�?·IFC-005 §7→�?0·IFC-006/007 §9→�?1·修改条件 §14→�?6·MLC-003 引用 GOV-MOD-003 §5→�?，共 17 处）——Round 10 插入 §3/§4 后未同步�?self-ref + cross-file ref |
| 2026-05-01 | 0.6.0 | 对齐 PS-STD-002 §3.2.4（行为规则型条件性章节）：新�?§3 受控枚举定义�? 契约状态）+ §4 消费者注册表（Tier 1/2�? §15 变更同步规则 + §16 修改条件（L0~L3 分级�? §17 废弃流程 + §18 异常豁免机制�? 场景�? §19 字段不重复声明（contract_id/provider/consumers/interface_schema�? §20 审查周期（ISO 11179�? §21 完整性自检清单。修�?C9（性能约束占位�?Xms→TBD 待定标注�? C10（保留原 IFC-001 7 字段表）。全文章节重编号 §3→�?2�?|
| 2026-05-01 | 0.5.2 | Common Core 对齐 PS-STD-002 §3.2.1：新�?§2 SSoT声明 + §11 标准间引用规范（normative/informative�? §12 AI可消费性声�?+ 全文章节重编号（§2~§10 �?§3~§13�?|
| 2026-05-01 | 0.5.0 | 元规则对齐审计：frontmatter 添加 valid_from + 字段排序对齐 PS-STD-001 §2.3 + layer cross_layer→L1 + depends_on 移除 GOV-MOD-001/005/GOV-ARCH-001 同级引用对齐链深=1层死规则（PS-STD-001 §2.1�?|
| 2026-05-01 | 0.4.0 | 第三轮补缺：澄清契约注册表生消流�?+ IFC-007（Provider 退役级联废弃）+ 术语统一（移除→archived�? §9 模块间运行时交互规则 |
| 2026-05-01 | 0.3.0 | 补齐 G6/G17/G18/G23 细颗粒审查缺漏：新增契约注册表（IFC-004�? 契约生命周期（IFC-005�? 一致性验证（IFC-006�? P0 性能约束必填 |
| 2026-05-01 | 0.2.0 | #24 审批修复：frontmatter 补齐 depends_on 结构�?+ ai_autonomy: human_gated |
| 2026-04-30 | 0.1.0 | 初始版本 |
