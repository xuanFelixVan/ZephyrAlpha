---
module_id: "MOD-INF-019"
title: "可执行 Agent Spec 蓝图 — 蓝图→Skill 升级引擎"
doc_type: blueprint
status: draft
version: "0.2.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-05"
valid_from: "2026-05-05"
ttl: permanent
construction_progress: not_started
summary: "ZephyrAlpha 可执行 Agent Spec 蓝图——将 19 份静态蓝图升级为可加载、可版本化、可审计的 Agent Skill Pack。按任务类型聚合为 3 个 Skill Pack（架构师/实现者/治理员），通过 AGENTS.md 路由触发加载。对标 Codified Context 19 domain-expert agents + Anthropic Claude Skills。"
tags: [agent-spec, skill, executable-blueprint, codified-context, agent-os, infrastructure]
priority: P0
depends_on:
  - {target: "MOD-INF-007", at: "全篇", why: "Gate Engine——治理员 Skill Pack 的核心组件"}
  - {target: "MOD-INF-008", at: "全篇", why: "Context Engine——架构师 Skill Pack 的核心组件"}
  - {target: "MOD-INF-009", at: "全篇", why: "Pipeline——实现者 Skill Pack 的核心组件"}
  - {target: "MOD-INF-018", at: "§2", why: "Agent RBAC——Skill 加载时的权限检查"}
---

# 可执行 Agent Spec 蓝图 — 蓝图→Skill 升级引擎

> **module_id**: MOD-INF-019 | **version**: 0.2.0 | **status**: draft | **layer**: cross_layer

> **对标**：Codified Context (arXiv 2602.20478) 19 domain-expert agents + Anthropic Claude Skills（指令+脚本+资源打包为可加载模块）。
> **核心差距**：Codified Context 有 19 个可执行 Agent，ZephyrAlpha 有 0 个。蓝图告诉 AI "系统长什么样"，Agent Spec 告诉 AI "你该怎么干活"。

---

## 1. 概述与模块定位

### 1.1 模块身份

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-019 |
| 代码落位 | `src/zephyr/agent_spec/` |
| 运行时平面 | Warm memory（任务分配时加载对应 Skill Pack） |
| 核心职责 | 将静态蓝图转化为 AI Agent 可直接执行的"操作手册" |

### 1.2 核心职能（一句话）

**Agent Spec 是蓝图的"可执行版"**——蓝图是架构文档（AI 读了知道系统长什么样），Agent Spec 是操作手册（AI 读了知道该怎么干活）。按任务类型聚合为 Skill Pack，通过 AGENTS.md 路由自动加载。

### 1.3 运行场景约束

| 约束 | 影响 |
|------|------|
| 多 IDE 并发（TRAE/Cursor/RooCode） | Skill 加载机制必须跨 IDE 统一——AGENTS.md 是唯一所有 IDE 都读的文件 |
| 10+ 并发对话 | 不能加载全部 19 个 Skill——按需加载，控制 token 预算 |
| 1 人 + AI | AI 角色有限——架构师/实现者/治理员三种，不需要 19 种 |

### 1.4 当前痛点

| # | 痛点 | 后果 |
|---|------|------|
| 1 | 蓝图是纯文档，不是可执行指令 | AI 每次需要人类口头指挥"下一步做什么" |
| 2 | 蓝图没有加载机制 | AI 不知道该读哪份蓝图——冷启动成本高 |
| 3 | 蓝图没有版本化执行 | AI 可能用过期蓝图施工——导致代码与设计不一致 |
| 4 | 蓝图没有审计闭环 | 无法验证 AI 是否真的按蓝图执行 |

### 1.5 蓝图 vs Agent Spec 对比

| 维度 | 蓝图（当前） | Agent Spec（目标） |
|------|------------|-------------------|
| 格式 | Markdown 文档 | YAML + Python Skill Pack |
| 加载方式 | 人工指定或 MCP 搜索 | AGENTS.md 路由自动触发 |
| 聚合方式 | 1 蓝图 = 1 文档 | 1 Skill Pack = N 蓝图的操作指引聚合 |
| 执行验证 | 无 | Skill 执行后自动校验产出物 |
| 版本管理 | frontmatter version | semver + 兼容性矩阵 |
| 审计追踪 | 无 | Skill 执行记录写入 Audit Trail |

---

## 2. 核心架构

### 2.1 Skill Pack 聚合模型（决策 D-019-01）

> **决策 D-019-01**：不创建 19 个独立 Skill，而是按 AI 角色聚合为 3 个 Skill Pack（架构师/实现者/治理员）。每个 Skill Pack 聚合多个蓝图的关键操作指引，按需加载。
>
> **决策依据**：1人+AI场景，AI 角色只有 3 种，不需要 19 种。10+ 并发对话，加载 19 个 Skill 会耗尽 token 预算。3 个 Skill Pack 覆盖所有场景。

```yaml
skill_packs:
  architect:
    skill_id: "SKILL-PACK-ARCH-001"
    name: "架构师 Skill Pack"
    description: "读蓝图 + 设计接口 + 写代码 + 跑门禁"
    derived_from:
      - "MOD-MASTER-001"  # 总蓝图——集成契约
      - "MOD-INF-008"     # Context Engine——上下文注入
      - "MOD-INF-009"     # Pipeline——路由设计
      - "MOD-INF-007"     # Gate Engine——门禁设计
    trigger_keywords: ["设计", "架构", "接口", "蓝图", "新模块"]
    token_budget: 3000
    instructions:
      - "读蓝图 §3 接口契约 → 生成 Pydantic 模型骨架"
      - "读蓝图 §2 核心架构 → 生成类/方法签名"
      - "写代码后跑 G0-G7 门禁 → 门禁 FAIL 则按 fix_hint 修复"
      - "修改架构 YAML 后触发 auto_guard 后验"

  implementer:
    skill_id: "SKILL-PACK-IMPL-001"
    name: "实现者 Skill Pack"
    description: "读蓝图 §3 + 写代码 + 跑测试 + 修 lint"
    derived_from:
      - "MOD-INF-006"     # Task System——任务执行
      - "MOD-INF-012"     # Database——数据层
      - "MOD-INF-011"     # Vector Memory——向量层
      - "MOD-INF-013"     # MCP Servers——接口层
    trigger_keywords: ["实现", "编码", "修复", "测试", "lint"]
    token_budget: 2000
    instructions:
      - "读蓝图 §3 接口契约 → 按契约实现类/方法"
      - "写代码后跑 pytest + ruff → FAIL 则修复"
      - "修改文件后触发 pre-commit 门禁"
      - "创建新文件后更新蓝图 §5 路径索引"

  governor:
    skill_id: "SKILL-PACK-GOV-001"
    name: "治理员 Skill Pack"
    description: "跑审计脚本 + 修漂移 + 写审计日志 + 检查合规"
    derived_from:
      - "MOD-INF-007"     # Gate Engine——门禁评估
      - "MOD-INF-005"     # Script System——审计脚本
      - "MOD-INF-023"     # Drift Detector——漂移检测
      - "MOD-INF-020"     # Audit Trail——审计日志
      - "MOD-INF-018"     # Agent RBAC——权限检查
    trigger_keywords: ["审计", "门禁", "漂移", "合规", "治理", "校验"]
    token_budget: 2000
    instructions:
      - "运行治理脚本 → 收集 Findings → 按严重度排序"
      - "检测到漂移 → 尝试自动对账 → 失败则生成修复建议"
      - "门禁评估 → FAIL 则返回 fix_hint 给调用方"
      - "所有操作写入审计日志"
```

### 2.2 AGENTS.md 路由触发（决策 D-019-02）

> **决策 D-019-02**：Skill Pack 通过 AGENTS.md 路由触发加载，而非独立加载机制。AGENTS.md 是所有 IDE（TRAE/Cursor/RooCode）都会读取的文件，是跨 IDE 统一的唯一入口。
>
> **决策依据**：多 IDE 并发场景，不能依赖单一 IDE 的加载机制。AGENTS.md 是所有 IDE 的共同入口。

```yaml
# AGENTS.md 中新增的 Skill Pack 路由章节
skill_routing:
  description: "根据任务类型自动加载对应的 Skill Pack"
  rules:
    - trigger: "任务涉及 设计/架构/接口/新模块"
      load: "SKILL-PACK-ARCH-001"
      path: "src/zephyr/agent_spec/skills/architect/"

    - trigger: "任务涉及 实现/编码/修复/测试"
      load: "SKILL-PACK-IMPL-001"
      path: "src/zephyr/agent_spec/skills/implementer/"

    - trigger: "任务涉及 审计/门禁/漂移/合规"
      load: "SKILL-PACK-GOV-001"
      path: "src/zephyr/agent_spec/skills/governor/"
```

### 2.3 渐进式 Skill 演进（决策 D-019-03）

> **决策 D-019-03**：scaffold 先做 3 个 Skill Pack（架构师/实现者/治理员），验证可行后再考虑细化。不追求一步到位的 19 个 Skill。
>
> **决策依据**：先验证 3 个 Skill Pack 的效果，再决定是否需要更细粒度的拆分。过早细化 = 过度工程。

```yaml
evolution_roadmap:
  phase_0:
    description: "3 个 Skill Pack 验证"
    deliverables:
      - "SKILL-PACK-ARCH-001（架构师）"
      - "SKILL-PACK-IMPL-001（实现者）"
      - "SKILL-PACK-GOV-001（治理员）"
    validation: "3 个 Skill Pack 覆盖 80% 常见任务类型"

  phase_1:
    description: "按需细化——如果 3 个 Skill Pack 不够用"
    trigger: "某个 Skill Pack 的 token_budget 经常超限，或 AI 经常加载错误的 Skill Pack"
    possible_splits:
      - "架构师 → 系统架构师 + 模块架构师"
      - "实现者 → 后端实现者 + 前端实现者"
      - "治理员 → 审计员 + 运维员"

  phase_2:
    description: "Skill 自动派生——蓝图变更 → Skill Pack 自动更新"
    trigger: "蓝图更新频繁导致 Skill Pack 漂移"
```

### 2.4 Skill Pack 文件结构

```yaml
# 每个 Skill Pack 的目录结构
skills/
  architect/
    skill_pack.yaml       # Skill Pack 配置——指令+触发词+token预算
    instructions.md       # 操作手册——AI 读这个就知道怎么干活
    resources.yaml        # 资源索引——需要加载的蓝图/代码/配置
    scripts/              # 可执行脚本——门禁/校验/生成
  implementer/
    skill_pack.yaml
    instructions.md
    resources.yaml
    scripts/
  governor/
    skill_pack.yaml
    instructions.md
    resources.yaml
    scripts/
```

---

## 3. 文件组成

| 文件 | 职责 |
|------|------|
| `skill_model.py` | Skill Pack 数据模型——Pydantic V2 模型 |
| `skill_loader.py` | Skill Pack 加载器——从 AGENTS.md 路由触发加载 |
| `skill_executor.py` | Skill Pack 执行器——调用 Skill 中的脚本并验证结果 |
| `skill_registry.yaml` | Skill Pack 注册表——3 个 Pack 的索引 |
| `skills/` | Skill Pack 存放目录——3 个子目录 |

---

## 4. 施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| scaffold | 3 个 Skill Pack（架构师/实现者/治理员）+ AGENTS.md 路由 + SkillLoader | 📋 Backlog |
| experimental | 按需细化 + Skill 执行验证 + 审计闭环 | 📋 Backlog |
| beta | Skill 自动派生（蓝图变更 → Skill Pack 自动更新）+ 兼容性矩阵 | 📋 Backlog |

---

## 5. 风险与缓解

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|:---:|:---:|------|
| R1 | Skill Pack 与蓝图漂移——蓝图更新但 Skill Pack 未同步 | 高 | 高 | CI 门禁：蓝图 version 变更 → 触发 Skill Pack 重新审查 |
| R2 | Skill Pack token 预算不足——3 个 Pack 覆盖不够 | 中 | 中 | 渐进加载：先加载 instructions.md，按需加载 resources |
| R3 | AGENTS.md 膨胀——路由规则越来越多 | 低 | 中 | 路由规则保持在 10 条以内，超出则拆分为独立路由文件 |

---

## 决策记录

| 决策 ID | 决策内容 | 日期 | 依据 |
|---------|---------|------|------|
| D-019-01 | 3 个 Skill Pack 聚合（非 19 个独立 Skill） | 2026-05-05 | 1人+AI，AI 角色只有 3 种；10+ 并发对话，19 个 Skill 耗尽 token |
| D-019-02 | AGENTS.md 路由触发加载 | 2026-05-05 | 多 IDE 并发，AGENTS.md 是唯一跨 IDE 统一入口 |
| D-019-03 | scaffold 先做 3 个 Skill Pack 验证 | 2026-05-05 | 先验证再细化，避免过度工程 |

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-05 | 0.2.0 | 三项决策写入：D-019-01 3个Skill Pack聚合 + D-019-02 AGENTS.md路由 + D-019-03 渐进式演进；重构为 Skill Pack 模型 |
| 2026-05-05 | 0.1.0 | 初始创建——Skill 结构 + SkillLoader + 三阶段路线图 |
