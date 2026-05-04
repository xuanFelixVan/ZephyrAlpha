---
module_id: "SYS-MASTER-001"
title: "ZephyrAlpha 系统总蓝图 — 三级金字塔架构与全部子系统拓扑"
doc_type: blueprint
status: approved
version: "0.1.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-04"
valid_from: "2026-05-04"
ttl: permanent
blueprint_level: system
summary: "ZephyrAlpha 系统级总蓝图（Level 0 System Master）——定义三级金字塔：Level 0 本蓝图（系统全景拓扑与架构原则）→ Level 1 MOD-MASTER-001（12基础设施系统集成契约）→ Level 2 16个模块蓝图（INF-005~017 + KB-001）。本蓝图是 PS-STD-005 定义的蓝图体系顶点——所有子系统蓝图通过 belongs_to 指向本蓝图或 MOD-MASTER-001。AI agent 冷启动第一站：先读 §0 分派表 → 定位自己负责的子系统 → 读对应模块蓝图。"
construction_progress: not_started
ai_role_instruction: >
  你是 ZephyrAlpha 系统总蓝图（SYS-MASTER-001），是整个蓝图三级金字塔的顶点。
  新 AI session 第一站——所有 agent 在开始任何任务前 MUST 读 §0 分派表定位自己负责的子系统，
  然后导航到对应的 Level 1/Level 2 蓝图。
  核心规则：(1)本项目采用三层蓝图体系——你定义"全局怎么排"，
  MOD-MASTER-001 定义"系统间怎么连"，模块蓝图定义"模块内怎么干"；
  (2)蓝图冲突裁决链：PS-STD-005 > SYS-MASTER-001 > MOD-MASTER-001 > 模块蓝图；
  (3)你不会生成代码——你定义系统边界和架构原则，实现由模块蓝图指引；
  (4)新 AI session 冷启动默认读 §0 即可（~400 tokens），按任务域升级到 §1-§4。
tags: [system-master, blueprint, three-tier-pyramid, architecture-topology, level0, ssoT]
priority: P0
depends_on:
  - {target: "PS-STD-005", at: "全篇", why: "蓝图架构标准——定义三级金字塔规范与本蓝图的合法位置"}
  - {target: "MOD-MASTER-001", at: "§一-§十二", why: "12基础设施系统集成蓝图——本蓝图的 Level 1 子蓝图"}
  - {target: "architecture-model/_index.yaml", at: "全篇", why: "架构模型拓扑——C-track 14层 + B-track 12系统"}
---

# ZephyrAlpha 系统总蓝图

> **module_id**: SYS-MASTER-001 | **version**: 0.1.0 | **level**: SYSTEM | **layer**: cross_layer

> **位置**: 三级金字塔 **Level 0 顶点**——定义系统全景拓扑、架构原则与蓝图导航。
> **对标**: TOGAF Architecture Vision Document + K8s Cluster API + C4 System Context Diagram。

---

## 零、AI Agent 冷启动分派

### 0.1 导航链

```
SYS-MASTER-001 (本蓝图, Level 0)
  ├── MOD-MASTER-001 (12基础设施集成, Level 1)
  │     ├── MOD-INF-005 脚本系统
  │     ├── MOD-INF-006 任务系统 (100%完整)
  │     ├── MOD-INF-007 门禁引擎
  │     ├── MOD-INF-008 上下文引擎 (92%完整)
  │     ├── MOD-INF-009 任务管线
  │     ├── MOD-INF-010 反馈闭环
  │     ├── MOD-INF-011 向量记忆
  │     ├── MOD-INF-012 数据库
  │     ├── MOD-INF-013 MCP服务端
  │     ├── MOD-INF-014 LLM安全
  │     ├── MOD-INF-015 系统遥测
  │     ├── MOD-INF-016 知识库 (MOD-KB-001)
  │     ├── MOD-INF-017 运行时集成
  │     └── MOD-INF-018~019 (暂未创建)
  └── L00-L13 业务层 (9层骨架, 4层实现)
```

### 0.2 AI Agent 分派表

| 任务域 | 先读 | 再读 | Token预算 |
|--------|------|------|:--:|
| 门禁/断路器 | 本蓝图 §2 | MOD-INF-007 blueprint | ~600 |
| 上下文注入 | 本蓝图 §2 | MOD-INF-008 blueprint | ~500 |
| 任务管线 | 本蓝图 §2 | MOD-INF-009 blueprint | ~500 |
| 反馈闭环 | 本蓝图 §2 | MOD-INF-010 blueprint | ~500 |
| 跨系统集成 | 本蓝图 §1-§3 | MOD-MASTER-001 CT-* | ~2000 |
| 新建模块 | PS-STD-005 §5 | blueprint-template.md | ~800 |
| 架构审查 | 本文全文 | PS-STD-005 + blueprint-registry.yaml | ~4000 |

### 0.3 令牌预算层级

| 层级 | 文档 | 首次读取Token | 触发条件 |
|------|------|:--:|------|
| 🔥 Hot Memory | AGENTS.md + 本蓝图 §0 | ~800 | 每个session |
| 📋 Domain Triggers | 对应模块蓝图 §1-§5 | ~2000 | path_pattern匹配 |
| 📚 Cold Memory | 模块蓝图全文 + MOD-MASTER-001 | ~8000 | 主动查询 |

---

## 一、系统全景拓扑

### 1.1 双轨架构

| 轨 | 计数 | 状态 | 职责 |
|:--|:--:|------|------|
| **C-Track** (业务层) | 14层 | 4实现/9骨架/1占位 | 量化交易业务——因子、信号、风控、执行 |
| **B-Track** (基础设施) | 12系统 | 12实现 | AI开发骨架——门禁、上下文、管线、反馈 |

### 1.2 C-Track 业务层

| 层 | 名称 | 代码状态 | 说明 |
|:--|------|:--:|------|
| L00 | Data Source | skeleton | 外部数据摄取 |
| L01 | Infrastructure | implemented | 脚本系统运行时 |
| L02 | Alpha Factor | implemented | 因子计算引擎 |
| L03 | Signal Generation | skeleton | 信号融合打分 |
| L04 | Risk Management | implemented | 风控止损 |
| L05 | Portfolio Construction | skeleton | 仓位分配 |
| L06 | Trade Execution | skeleton | 订单路由 |
| L07 | Post-Trade Analytics | skeleton | PnL归因 |
| L08 | Human-AI Interface | implemented | Dashboard |
| L09 | Research & Innovation | skeleton | 回测孵化 |
| L10 | Compliance | skeleton | 合规校验 |
| L11 | ML Platform | skeleton | ML生命周期 |
| L12 | System Telemetry | implemented | 全系统遥测 |
| L13 | Experimentation | skeleton | A/B实验 |

### 1.3 B-Track 基础设施层

| 系统 | 蓝图ID | 蓝图完整度 | 核心职责 |
|------|------|:--:|------|
| Script System | MOD-INF-005 | 85% | 脚本发现/执行/验证 |
| Task System | MOD-INF-006 | **100%** | 任务卡全生命周期 |
| Gate Engine | MOD-INF-007 | 33% | G0-G7+G1-G5门禁+断路器 |
| Context Engine | MOD-INF-008 | **92%** | 上下文四阶段流水线 |
| Pipeline | MOD-INF-009 | 58% | M1-M11双管线 |
| Feedback Loop | MOD-INF-010 | 42% | 系统自调节闭环 |
| Vector Memory | MOD-INF-011 | 85% | 向量化存储检索 |
| Database | MOD-INF-012 | 85% | SQLite元数据持久化 |
| MCP Servers | MOD-INF-013 | 85% | MCP协议服务端 |
| LLM Security | MOD-INF-014 | 85% | L1-L4四层安全防御 |
| System Telemetry | MOD-INF-015 | 85% | 全系统遥测采集 |
| Knowledge Base | MOD-KB-001 | 85% | 知识生命周期管理 |

### 1.4 运行时平面（正交视图）

| 平面 | 覆盖系统 | 职责 |
|------|------|------|
| 任务执行平面 | Orc + Pipeline + Script System | 任务调度执行 |
| 知识平面 | KB + VMS + Context Engine | 记忆检索注入 |
| 安全平面 | Gate Engine + LSG + Sandbox | 门禁校验沙箱 |
| 反馈平面 | Feedback Loop + Telemetry | 自调节监控 |
| 数据平面 | Database + Shared/Contracts | 持久化契约 |

---

## 二、架构原则

### 2.1 不可变核心

| 原则 | 陈述 | 来源 |
|------|------|------|
| P1: SSoT | 每个架构事实只有一个 canonical source | ADR-0001 |
| P2: YAML Schema | 结构化数据用YAML+JSON Schema，不用MD | ADR-0002 |
| P3: Dual AI | Writer+Reviewer双角色协作 | ADR-0003 |
| P4: OCP | 通过抽象基类扩展，不修改现有代码 | ADR-0004 |
| P5: Blueprint First | 任何代码变更前必须读对应蓝图（G6强制） | G6 |

### 2.2 蓝图体系铁律

| # | 铁律 | 执行者 |
|:--|------|------|
| 1 | 三级金字塔不可扁平化——Level 0/1/2 职责分明 | PS-STD-005 |
| 2 | belongs_to 必填——每个模块蓝图必须声明归属 | PS-STD-005 §5 |
| 3 | 蓝图与代码双向对齐——GATE-A (代码↔YAML) + GATE-B (YAML↔MD) | AGENTS.md §6.10 |
| 4 | G6 硬合规——AI 未读蓝图则代码变更 REJECT | g6_blueprint_compliance.yaml |
| 5 | blueprint_routing.yaml 是路由 SSoT——新模块必须登记 | MOD-INF-009 §8 |

---

## 三、关键架构决策索引

| ADR | 标题 | 决策 |
|------|------|------|
| ADR-0001 | Canonical SSoT | YAML=真源, MD=衍生视图 |
| ADR-0002 | 单Schema Phased Required Fields | 一个JSON Schema渐进式必填 |
| ADR-0003 | Dual AI Collaboration | Writer/Reviewer双角色 |
| ADR-0004 | OCP Extension Points | 开闭原则扩展点 |
| ADR-0015 | Context Engine | 四阶段流水线 |
| ADR-0016 | Vector Memory | ChromaDB+BGE-M3 |
| ADR-0017 | Agent Orchestrator | SQLite+asyncio |
| ADR-0018 | Agent Sandbox | Windows ACL |
| ADR-0019 | Feedback Loop | 三阶段闭环 |
| ADR-0020 | LLM Security | 四层防御 |
| R90 | 三级金字塔 | 本蓝图的架构基础 |

---

## 四、跨模块数据流

```
用户意图 → IntentParser → TriggerRouter → Orchestrator
  → ContextEngine(构建上下文) → GateEngine(G6检查→G1-G5门禁)
  → Pipeline(分配M1-M11) → ScriptSystem(执行脚本)
  → FeedbackLoop(收集结果) → VectorMemory(记忆更新)
  → Telemetry(遥测记录)
```

**关键集成点**:
- G6 gate 在 Pipeline 分配前运行——确保 AI 已读蓝图
- Context Engine 通过 `blueprint_routing.yaml` 确定上下文范围
- Feedback Loop 触发 AutoEvolution 调整蓝图索引权重

---

## 五、依赖关系

| 本蓝图依赖 | 关系 | 为什么 |
|------|:--:|------|
| PS-STD-005 | governs | 定义本蓝图的合法位置 |
| MOD-MASTER-001 | delegates_to | 12系统集成契约 |
| architecture-model/_index.yaml | reads_from | 拓扑数据 |
| blueprint-registry.yaml | monitors | 蓝图健康度 |

---

## 六、产出物存放目录

| 产出物 | 路径 |
|------|------|
| 本蓝图 | `docs/03_modules/_sys-master/blueprint.md` |
| 集成蓝图 | `docs/03_modules/_master-blueprint/blueprint.md` |
| 全部模块蓝图 | `docs/03_modules/l01_infrastructure/*/blueprint.md` |
| 架构标准 | `docs/01_policies_and_standards/meta/blueprint-architecture-standard.md` |
| 架构模型 | `architecture-model/layers/*.yaml` |
| 业务层代码 | `src/zephyr/l00_data_source/` ~ `l13_experimentation/` |
| 基础设施代码 | `src/zephyr/gates/`, `src/zephyr/context_engine/`, ... |
| 门禁定义 | `src/zephyr/gates/*.yaml` |

---

## 七、集成目标

| 目标 | 状态 | Phase |
|------|:--:|:--:|
| 三级金字塔全部就位 | SYS-MASTER-001 已创建 | beta ✓ |
| 蓝图完整度 ≥80% | 当前 ~62%, INF-007~010补齐中 | beta |
| G6 硬合规 REJECT <10% | 当前 33.3% | beta-stable |
| C-Track 业务蓝图 (L00-L13) | 0/14 已创建 | stable+ |
| Domain Expert Agent | Gate/Context/Pipeline 3个 | beta |

---

## 八、需要更新的相关内容

当本文变更时，同步更新：
1. `docs/03_modules/blueprint-registry.yaml` —— 新增 SYS-MASTER-001 登记行
2. `docs/01_policies_and_standards/meta/blueprint-architecture-standard.md` —— 若 Level 0 定义调整
3. `architecture-rationale-log.md` —— 追加 beta 相关决策

---

## 九、已知风险与缓解

| 风险 | 影响 | 缓解 |
|------|------|------|
| SYS-MASTER → MOD-MASTER → 模块蓝图 三层不一致 | AI 读错蓝图 | GATE-A + GATE-B 对齐检查 |
| 本蓝图过长导致 AI 不读 | 冷启动失败 | §0 分派表 + 按需阅读设计 |
| C-Track 业务蓝图缺失 | 业务开发缺指引 | stable 创建 L02/L04/L08/L12 |
| SYS-MASTER 与 MOD-MASTER 边界模糊 | 契约重复定义 | 铁律：SYS-MASTER 定义"谁有什么"，MOD-MASTER 定义"之间怎么连" |

---

## 十、后果

- AI agent 现在有明确的 Level 0 入口——冷启动不再迷茫
- 蓝图冲突有明确裁决链——不再需要猜测谁的优先级更高
- C-Track 业务蓝图缺失被显式记录——可追踪的技术债务
- 三级金字塔从"只有概念"变成"有代码/文档载体"——PS-STD-005 的设计得到完整实现

---

## 十一、施工指引

| 步骤 | 说明 | Phase |
|------|------|:--:|
| 1 | 在 blueprint-registry.yaml 中登记 SYS-MASTER-001 | beta |
| 2 | 为 INF-007~010 补齐 §5-§11 | beta |
| 3 | 为 Gate/Context/Pipeline 创建 domain-expert agent spec | beta |
| 4 | 运行 beta 30 session 验证 | beta |
| 5 | 创建 C-Track L02/L04/L08/L12 业务蓝图 | stable |
| 6 | 补齐剩余 C-Track 蓝图 | Phase 5+ |

---

## 十二、变更记录

| 版本 | 日期 | 变更内容 |
|------|------|------|
| 0.1.0 | 2026-05-04 | beta 创建——系统总蓝图初版。三级金字塔顶点就位：系统全景拓扑（14C+12B）、架构原则（5项+5铁律）、ADR索引、跨模块数据流、蓝图导航链、令牌预算层级、运行时平面视图。 |
