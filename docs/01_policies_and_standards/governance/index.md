---
module_id: GOV-IDX-001
title: "治理域总索引"
doc_type: index
status: active
version: "1.3.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
ai_autonomy: human_gated
rule_form: declarative
created_by: human_plus_agent
date: "2026-05-04"
valid_from: "2026-05-01"
ttl: permanent
summary: "governance/ 目录的顶层导航索引。列出全部 8 个治理子域的目录结构、职责边界、文件清单和索引入口。新 AI session 进入治理域时，应首先读取本文件以建立全局认知。"
tags: [index, governance, navigation, root]
depends_on:
  - target: PS-STD-001
    at: "§5.8"
    why: "metadata-registry.md 定义 GOV 前缀 module_id 的分配规则"
---

# 治理域总索引

> **module_id**: GOV-IDX-001 | **version**: 1.3.0 | **status**: active

本文件是 `governance/` 的顶层导航入口。**新 AI session 进入治理域的第一站**——读完此文件即理解全部 8 个治理子域的职责边界和文件布局，无需遍历 50 个文件。

> **对标**：ITIL v4 Service Management 要求治理体系有明确的服务目录（Service Catalog）作为入口。蓝图的 D-001 决策要求 governance/ 的每个子目录必须声明正向/负向责任。AGENTS.md §5.1 零记忆重启标准：AI 每次都是"新员工"，必须有一个文件让它 3 分钟内理解目录结构。

---

## §1 本目录的责任

`governance/` 是 ZephyrAlpha 的**声明式全局规则中心**。这里管的是"全项目通用的期望状态"——什么必须做、什么禁止做、操作之间是什么关系。

**核心判据**（对齐 PS-IDX-001 §三）：
- **governance/** = 声明式（declarative）：描述期望状态——"架构变更必须经过评审"（不是步骤，是规则）
- **operational/** = 过程式（imperative）：描述执行步骤——"打开 Pre-commit 检查→运行 validate_architecture.py→修复错误→提交"

### §1.1 正向责任（本目录管的事）

| 治理域 | 职责 | 文件数 |
|--------|------|:-----:|
| `architecture/` | 架构治理——ADR 协议、评审门控、版本化策略 | 7 |
| `security/` | 安全治理——密钥管理、访问控制、安全事件响应 | 3 |
| `data/` | 数据治理——数据质量、数据血缘、数据保留 | 3 |
| `compliance/` | 合规治理——监管分类、审计追踪 | 3 |
| `document/` | 文档治理——命名、路径、结构、生命周期 | 9 |
| `ai/` | AI 治理——自治权限、幻觉自检、协同规则 | 8 |
| `task/` | 任务治理——任务卡、生命周期、关闭标准 | 3 |
| `module/` | 模块治理——准入门禁、生命周期、接口契约 | 6 |

### §1.2 负向责任（本目录不管的事，去对应目录找）

- 元规则（"规则怎么写"）→ `meta/`
- 过程式操作步骤（"怎么执行"）→ `operational/`
- 层域专属规则 → `domains/Lxx/`
- 代码实现的 Schema 定义 → `src/zephyr/shared/contracts/`
- 架构决策记录（ADR）→ `docs/02_enterprise_architecture/adr/`

---

## §2 子域导航速览

| 子域 | module_id 范围 | 索引文件 | 状态 |
|------|:---:|---|---|
| `architecture/` | GOV-ARCH-001~006 | [architecture/index.md](architecture/index.md) | ✅ active |
| `security/` | GOV-SEC-001~003 | [security/index.md](security/index.md) | ✅ active |
| `data/` | GOV-DATA-001~003 | [data/index.md](data/index.md) | ✅ active |
| `compliance/` | GOV-CMP-001~003 | [compliance/index.md](compliance/index.md) | ✅ active |
| `document/` | GOV-DOC-001~010 | [document/index.md](document/index.md) | ✅ active |
| `ai/` | GOV-AI-001~009 | [ai/index.md](ai/index.md) | ✅ active |
| `task/` | GOV-TASK-001~005 | [task/index.md](task/index.md) | ✅ active |
| `module/` | GOV-MOD-001~007 | [module/index.md](module/index.md) | ✅ active |

> **图例**：✅ active = 索引已建、目录已激活 | 本表所有索引文件均已创建并激活（2026-05-01 审查后修复 3 个待建索引）

---

## §3 跨域依赖关系速览

```
architecture/ ←→ security/     (架构评审门控 ←→ 密钥泄露触发安全事件)
    │                │
    └──── data/ ←────┘          (架构版本化 ←→ 数据质量依赖)
              │
         compliance/            (审计追踪引用数据保留期限+访问控制)
              │
         ai/                    (AI日志保留 → data/数据保留策略)
```

关键跨域引用链：
- `compliance/audit-trail → data/retention → ai/session-log-schema`（审计→保留→日志，3 域链）
- `security/access-control → ai/autonomy-registry`（访问控制 → AI 代理权限注册表）

---

## §4 对 AI 的使用指引

每个新 AI session 进入 `governance/` 后，应按以下顺序建立认知：

1. **先读本文件**（你正在读的这个）——理解 8 个治理域的职责边界
2. **根据任务类型选择子域**：
   - 涉及架构评审/ADR → `architecture/`
   - 涉及密钥/访问/安全事件 → `security/`
   - 涉及数据质量/血缘/保留 → `data/`
   - 涉及合规/审计/监管 → `compliance/`
   - 涉及文档规范 → `document/`
   - 涉及 AI 行为 → `ai/`
   - 涉及任务管理 → `task/`
   - 涉及模块接入 → `module/`
3. **进入子域后，先读子域的 index.md**（如果有），再读具体文件

所有治理文件标记 `ai_autonomy: human_gated` —— AI 可以读取和应用这些规则，但**不得单方面修改**。任何修改必须由 Owner 审批。

---

## §5 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.3.0 | 2026-05-04 | 审计修复。(1) body文本：38→50 个文件（全部 governance/ 递归文件数 51 - 1 索引文件自己 = 50）。(2) §1.1 文件数：architecture/ 5→7、compliance/ 2→3——对齐实际磁盘文件数。版本号 minor +1。 |
| 1.1.0 | 2026-05-02 | 审计修复。(1) §1.1 文件数对账：architecture/ 3→6、security/ 3→4、data/ 3→4、compliance/ 2→3、task/ 6→4（handoff-protocol 已迁至 ai/、bootstrap-plans 已废除）。版本号 minor +1。 |
| 1.0.0 | 2026-05-01 | 初始创建。(1) §1 责任声明——正向 8 域 + 负向 5 类。(2) §2 子域导航——8 域 module_id 范围、索引、状态。(3) §3 跨域依赖关系——关键引用链。(4) §4 AI 使用指引——三步认知建立。(5) 对齐 task/index.md 模板 + PS-IDX-001 边界判据。 |
