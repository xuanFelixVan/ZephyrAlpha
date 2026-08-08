---
ttl: permanent
doc_type: architecture_view
status: active
version: "1.0.0"
date: 2026-08-05
scope: 07_trading_decision_architecture 下的设计备忘管理
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
| 人（design memo） | "why"——决策推理 | 人手写 | 永久态，可修订 | design_memo_001 |
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
| 一个架构决策需要记录 why | 设计备忘 | `design_memos/design_memo_NNN_topic.md` |
| 决策涉及的模块要施工 | depgraph 设计态登记 | depgraph（apply_depgraph.py） |
| 需要可视化某子系统的当前状态 | micro battle map（可选） | `battle_map/micro/`（生成器派生） |
| 单个 artifact 不建生成器 | —— | 等同类 artifact 达 3-5 个再建生成器 |

## 4. 命名与结构规范

### 4.1 文件命名
- 设计备忘：`design_memo_NNN_topic.md`（NNN 三位序号，topic 为 snake_case 主题）
- 管理规范：`design_memo_management_spec.md`（本文件，唯一）
- 全部 snake_case，遵循项目命名铁律

### 4.2 设计备忘 frontmatter
```yaml
---
ttl: permanent
doc_type: design_memo
status: active
version: "1.0.0"
date: YYYY-MM-DD
topic: snake_case_topic
scope: 07_trading_decision_architecture
---
```

### 4.3 设计备忘推荐章节
1. 背景（项目处境 + 核心问题 + 约束条件）
2. 决策（架构定义 + 核心模块 + 关键特性）
3. 考虑过的替代方案（每个方案 + 拒绝理由）
4. 上限定义（系统上限 + 演进路径 + 为何是上限）
5. 待裁定（暂缓项 + 暂缓理由 + 重评条件）——非永久禁止，随项目演进重新裁定
6. 待定问题（需人决策的开放问题）
7. 引用（相关 battle_map + depgraph path + 需降级的现有设计）
8. 修订记录（日期 + 版本 + 改动 + 理由）

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
| 2026-08-05 | 1.0.0 | 初稿 | 建立设计备忘管理规范，配合 design_memo_001 多策略并发架构备忘 |
