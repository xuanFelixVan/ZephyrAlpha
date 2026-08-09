---
ttl: permanent
doc_type: architecture_view
title: 设计备忘管理规范
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.2.0"
date: 2026-08-10
topic: design_memo_management_spec
scope: 07_trading_decision_architecture
---

# 设计备忘管理规范

> 本规范定义 `07_trading_decision_architecture` 下"设计备忘"类文档的创建、结构、演进规则。
> 目的：记录架构决策的 why，防止飘移与幻觉，但不锁死项目演进。

## 1. 为什么有设计备忘

### 1.1 问题
- 作战地图（battle_map）描述 "what is/will be"（当前/计划状态），不描述 "why"
- depgraph 描述 "what will be"（设计态模块），不描述 "why"
- 缺少 "why" 层会导致：未来 AI/人看到当前架构，不知道为什么是这样，"优化"成另一个样子，飘移发生

### 1.2 与 ADR 的区别（本项目已废弃 ADR）
本项目曾用 ADR，已删除。原因：项目演进极快，ADR 的"裁定"语义会锁死成长。设计备忘的不同：
- **不是裁定，是记录**：记录当前推理，可随项目演进而修订
- **永久态但可改**：ttl=permanent 但 version 可迭代，修订时升版本号
- **不强制推翻流程**：改设计备忘不需要写"推翻旧备忘"的新备忘，直接修订即可
- **仍防飘移**：防飘移靠的是 "why 写清楚了"，不是"流程锁死了"

## 2. 三层分治原则

设计备忘只解决 "why" 层。三层各司其职，不可混淆：

| 层 | 管什么 | 谁产出 | 性质 | 例子 |
|---|---|---|---|---|
| 生成器（generator） | "what is"——当前状态快照 | 机器自动生成 | 派生，禁止手编 | battle_map_01~12、micro battle map |
| 人（design memo） | "why"——决策推理 | 人手写 | 永久态，可修订 | 30_multi_strategy_concurrency |
| depgraph | "what will be"——设计态模块 | apply_depgraph.py 登记 + sync 派生其余3图 | 真源，五图对齐 | StrategyBook 节点 |

### 2.1 核心纪律
- **生成器不写 why**：生成器只能描述状态，写不出"为什么不是另一个"
- **设计备忘不写 what is 的细节**：当前状态由生成器+depgraph 维护，备忘只引用稳定 path
- **depgraph 不写 why**：depgraph 是结构真源，why 在备忘里，depgraph 只登记模块与依赖

### 2.2 三层协作流程
1. 人写设计备忘（why + 决策 + 替代方案 + 负空间）
2. 根据备忘决策，用 apply_depgraph.py 登记模块到 depgraph 设计态（what will be）
3. sync_panorama_module.py 自动派生其余 3 图，align_panoramas.py 验证五图对齐
4. 施工后 status 从 planned → production
5. 生成器（battle_map 等）从 depgraph 派生当前状态视图（what is）
6. 备言引用 depgraph 的稳定 path，形成 why ↔ what 的双向追溯

## 3. 什么时候建什么

| 需求 | 产物 | 位置 |
|---|---|---|
| 一个架构决策需要记录 why | 设计备忘 | `design_memos/<段位号>_<topic>.md` |
| 决策涉及的模块要施工 | depgraph 设计态登记 | depgraph（apply_depgraph.py） |
| 需要可视化某子系统的当前状态 | micro battle map（可选） | `battle_map/micro/`（生成器派生） |
| 单个 artifact 不建生成器 | —— | 等同类 artifact 达 3-5 个再建生成器 |

## 4. 命名与结构规范

### 4.1 文件命名（2026-08-09 起段位编号制）
- 全部文档：`<段位号>_<topic>.md`（topic 为 snake_case 主题）
- 段位语义：**0x** meta｜**1x** 地基（regime/数据特征）｜**2x** Alpha 策略｜**3x** 组合仓位与风控｜**4x** 交易执行｜**5x** 验证与可观测性｜**6x** 跨切治理｜**9x** 开放问题与远期
- 新文档按业务域入段，段内取下一个空号；不预留坑位；占用登记见 [00_index_trading_decision.md](00_index_trading_decision.md) §7.3
- 管理规范：`01_design_memo_management_spec.md`（本文件，唯一）
- 全部 snake_case，遵循项目命名铁律
- status 枚举：`active`（已定稿/已落地）/ `draft`（草案/待讨论/待施工）/ `deprecated`（废弃）

### 4.2 设计备忘 frontmatter
```yaml
---
ttl: permanent
doc_type: architecture_view
title: 文档标题（与 H1 一致，不带"讨论稿/设计备忘/文件名"等前缀）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: YYYY-MM-DD
topic: snake_case_topic
scope: 07_trading_decision_architecture
---
```
> 可选追加（按需，不改变上表字段集与顺序）：`parent`（上游文档）/ `last_updated` / `depends_on` / `related_modules` / `related_issues`（12/13/14 号工程文档范式）。
> ⚠️ `doc_type` 合法值见 doc_type_vocabulary.yaml——本目录全部文档用 `architecture_view`；`design_memo` 词表值已废止（2026-08-09 骨架工程时 23 篇骨架统一按 architecture_view 落盘）。

### 4.3 设计备忘推荐章节
1. 背景（项目处境 + 核心问题 + 约束条件）
2. 决策（架构定义 + 核心模块 + 关键特性）
3. 考虑过的替代方案（每个方案 + 拒绝理由）
4. 上限定义（系统上限 + 演进路径 + 为何是上限）
5. 待裁定（暂缓项 + 暂缓理由 + 重评条件）——非永久禁止，随项目演进重新裁定
6. 待定问题（需人决策的开放问题）
7. 引用（相关 battle_map + depgraph path + 需降级的现有设计）
8. 修订记录（日期 + 版本 + 改动 + 理由）

> 骨架期（status=draft 占位文档）在最前加「主题组信息」节（G 组编号/依赖/优先级/正交性，供多 AI 认领导航），后续章节顺延编号；讨论定型（→active）时可移除该节并重编号，或保留作导航。

### 4.4 文档种类适配（章节结构不强制统一）

§4.3 的 8 节模板是**决策备忘**（记录"为什么选 A 不选 B"）的推荐结构。本目录存在多种文档种类，结构按种类适配，不强制套同一模板：

| 种类 | 典型文档 | 结构原则 |
|---|---|---|
| 决策备忘 | 20/30/31/40 | 按 §4.3 八节模板 |
| spec / 工程详设 | 10/11/12/13 | 按对象内在结构组织（如 10 号按"范围→12 态清单→状态机→Shrinkage"），章节由内容决定 |
| 诊断报告 | 14 | 按因果时间线组织（背景→诊断→裁定→落地→详设），"替代方案"并入裁定节不单列 |
| 施工计划 | 50/51 | 按施工流程组织（目标→现状→改动→验证→不做） |
| 索引 / 规范 / 清单 | 00/01/90/91 | 按各自职能组织 |

**两条硬约束（不论种类都必须有）**：
1. **末尾必须有「修订记录」节**——升版本可追溯的底线
2. **必须有「开放问题」或等价节**（待定问题/待裁定/开放问题）——标明哪些需人决策，AI 不擅自发挥

**不做什么**：
- 不为"结构统一"重排已有章节——交叉引用（含带行号锚点 `#L1525`）会断裂，遗漏风险大于外观统一收益
- 不加"AI 施工导航"前置节——派生于正文的摘要必然与正文漂移，错误导航比无导航更坑 AI；AI 读 frontmatter（status/depends_on/related_issues）+ 扫 H2 即可建立心理地图
- 章节编号风格（阿拉伯/中文数字/带 0 前缀）不强制统一——对 AI 施工零影响，仅外观

## 5. 防飘移机制

### 5.1 三重锚点
1. **设计备忘是 why 的锚**：任何未来 AI/人想改架构，先读备忘，知道为什么现在是这样
2. **depgraph 是 what 的锚**：五图对齐铁律强制施工前先登记设计态，备忘决策的模块必须在 depgraph 里找得到
3. **备忘引用 depgraph 的 path**：双向可追溯，从备忘能找到模块，从模块 blueprint 能回溯到备忘

### 5.2 引用纪律
- 设计备忘引用 depgraph **只用稳定标识**（path / module_id / blueprint_id）
- **禁止用 node_id / edge_id**（易变，每次 regenerate 会变）
- 这遵循项目文档引用铁律（TRAE-083）

### 5.3 修订规则
- 修订设计备忘 = 升 version（1.0.0 → 1.1.0 小改，2.0.0 大改）
- 修订不需要写"推翻"新备忘，直接改原文
- 但修订时 MUST 在文末"修订记录"小节记录：日期 + 改了什么 + 为什么改

## 6. 不做什么

| 不做 | 理由 |
|---|---|
| 不叫 ADR | ADR 的"裁定"语义锁死项目，已废弃 |
| 不为单个 artifact 建生成器 | 过度工程；等同类 artifact 达 3-5 个再建 |
| 不在设计备忘里写当前状态细节 | 当前状态由生成器+depgraph 维护，备忘只写 why |
| 不让生成器写 why | 生成器写不出推理过程 |
| 不用 node_id 引用 depgraph | node_id 易变，用 path |
| 不强制推翻流程 | 项目演进快，修订即可，不锁死 |

## 7. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-05 | 1.0.0 | 初稿 | 建立设计备忘管理规范，配合 30_multi_strategy_concurrency 多策略并发架构备忘 |
| 2026-08-09 | 1.1.0 | §4.1 命名规则改段位编号制（0x/1x/2x/.../9x）；§3 路径更新；§2 引用更新；加 status 枚举说明 | 文档体系重排，design_memo_NNN/discussion_NNN 双前缀废止 |
| 2026-08-09 | 1.1.1 | §4.2 frontmatter 示例修正（doc_type: design_memo→architecture_view，补 title/owner/language 字段 + 可选追加说明）；§4.3 补骨架期「主题组信息」节说明；自身文档头同步统一（补 title/owner/language/topic，scope 值归一） | design_memo 词表值已废止（23 篇骨架按 architecture_view 落盘），规范示例须与词表/现状一致；15 篇有内容文档文档头统一（仅动 frontmatter/H1/修订记录，章节编号与正文零变更） |
| 2026-08-10 | 1.2.0 | 新增 §4.4「文档种类适配」：明确 §4.3 八节模板是决策备忘专用，spec/诊断/施工计划/索引按各自种类适配；两条硬约束（必须有修订记录 + 必须有开放问题等价节）；三条不做（不重排已有章节、不加 AI 施工导航、不强制编号风格） | 15 篇有内容文档结构本就按种类分化（决策备忘 4 篇已统一、spec/诊断/施工各自合理），强求统一会打断交叉引用（含 #L1525 行号锚点）且对 AI 施工无实质收益；错误导航比无导航更坑 AI，故不加导航节 |
