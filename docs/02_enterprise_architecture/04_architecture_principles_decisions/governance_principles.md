---
module_id: VIEW-04PRINC-GOVERNANCE
title: Architecture Principles — Governance / 架构原则：治理
doc_type: architecture_view
status: Active
version: 1.0.1
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-07-19
superseded_by: null
supersedes: VIEW-09-GOVERNANCE-ARCH
related_rationale: R65, R66, R67, R68, R69
related_open_questions:
- OQ-076
- OQ-079
- OQ-080
- OQ-081
- OQ-083
related_kb:
- KBG-0009
- KBG-0010
- KBG-0011
- KBG-0021
tags:
- governance-principles
- togaf
- three-layer
- policy
- factory
- runtime
- ai-autonomy
- runtime-planes-boundary
- ssot-validator
- 5-core-services-governance
summary: 治理架构永恒原则文档。timeless 方法论——三层治理边界（Policy/Factory/Runtime）、D2-B 三角闭环（Policy→Factory→Runtime→Audit→Policy）、四档执行约定（deny/dryrun/warn/disabled）、D3-B AI 自治三层预留口子、D4 方案 B 稳健分三轮激活、T0-T7 激活触发条件、Runtime Plane 边界铁律（治理 Runtime 层 vs 执行 Runtime Plane 正交独立）。派生数据（46 治理系统分层归属表、激活 Sprint、5 大核心服务治理归属）不在本文档，由 depgraph + 治理系统注册表维护。
date: '2026-07-19'
ttl: permanent
---

# Architecture Principles — Governance
# 架构原则：治理（Governance Principles）

---

## §1 定位 / Position

本文档是**治理架构的永恒指导原则**。

**保留内容**：方法论、设计原则、不变约束——三层治理边界、D2-B 三角闭环、四档执行约定、D3-B AI 自治预留、D4 激活路径、T0-T7 触发条件、Runtime Plane 边界铁律。

**不保留内容**（派生/动态数据，由各自自动化系统维护）：
- 46 治理系统分层归属表 → depgraph + 治理系统注册表
- 激活 Sprint 时间表 → 治理系统注册表
- 5 大核心服务治理归属 → depgraph
- D 家族 6 系统详细展开 → 各域蓝图

**与其他原则文档关系**：
- [capability_maturity_principles.md](capability_maturity_principles.md)：能力成熟度方法论
- [data_principles.md](data_principles.md)：数据架构原则
- [security_principles.md](security_principles.md)：安全架构原则
- [integration_principles.md](integration_principles.md)：集成架构原则
- [business_principles.md](business_principles.md)：业务架构原则
- [information_principles.md](information_principles.md)：信息架构原则
- [application_principles.md](application_principles.md)：应用架构原则
- [technology_principles.md](technology_principles.md)：技术架构原则
- 本文：治理架构原则（三层边界/D2-B 闭环/D3-B 预留/D4 激活）

---

## §2 三层治理边界（Policy / Factory / Runtime）

### 2.1 三层定义（永恒框架）

治理三层**横切整个系统的所有域**——业务层（src/ 全域）、文档层（docs/ 6 顶级目录）、前端层（frontend/）、治理层自己（scripts/ + .cursor/rules/）。治理三层和业务域是**平级正交**的"尺子 + 纪委 + 审计处"。

| 层 | 大白话定位 | 职责 | 典型产物 |
|---|---|---|---|
| **Policy 层** | 规章制度部门 | 定规则/存规则/版本化/append-only review | Markdown 规则、KB 决策记录、folder-charters、Rego |
| **Factory 层** | 纪委工具组 | 把规则编译成可执行检查器 + 工具链管理 | ruff/mypy 配置、fitness function、arch_guard |
| **Runtime 层** | 巡查队+审计处+档案室 | 拦截+审计+反馈回写 Policy | pre-commit、CI、OPA sidecar、audit-log |

### 2.2 三层物理位置框架（永恒分类）

> **注**：具体物理路径清单由 depgraph 维护（`SELECT path FROM nodes WHERE domain_id IN ('D_GOVERNANCE','D_GOV_AUDIT','D_GOV_RULE')`），不在本文档硬编码。

| 层 | 关键物理位置（框架） | 代表产物 |
|---|---|---|
| **Policy** | `docs/01_policies_and_standards/` · KB:decisions namespace · `.cursor/rules/` · `.trae/rules/` · `AGENTS.md` | 规则文档、KBG 决策记录、AI 协作规则 |
| **Factory** | `scripts/arch_guard/` · `scripts/governance/` · `scripts/quality/` · `pyproject.toml` | F 函数、import_linter、ruff/mypy/bandit 配置 |
| **Runtime** | `.pre-commit-config.yaml` · `.github/workflows/` · `src/zephyr/compliance/` · `scripts/governance/audit_log/` · `scripts/governance/opa/` | pre-commit hooks、CI Gate、kill_switch、OPA policies |

### 2.3 三层架构关键理解（永恒）

- 治理三层与业务层是**平级正交**的横切关系（不是"上下层"）
- 治理三层**管所有层**，包括治理层自己（自治）
- Policy → Factory → Runtime → 审计回写 Policy 构成**三角闭环**（D2-B）

---

## §3 D2-B 三角闭环（三层接口联动机制）

### 3.1 D2-B 拍板结论（永恒）

**拍板**：**D2-B 三角闭环：Policy → Factory → Runtime → 审计回写 Policy**

**用户决策原话**（2026-04-19）：
> "三角闭环：Policy → Factory → Runtime → 审计回写 Policy（带反馈环）形成完美闭环最好，相当于最后有检查步骤。"

### 3.2 四条核心接口（永恒框架）

| 接口 | 触发时机 | 协议 |
|---|---|---|
| **① Policy→Factory** | Policy 规则新增/变更（git commit） | policy_compiler：Markdown/YAML → 检查器配置 |
| **② Factory→Runtime** | git commit / CI push / 交易执行 / AI 决策 | pre-commit hook / GitHub Actions / 函数调用 |
| **③ Runtime→Audit** | 每次检查器执行后 | append-only 写入 `policy_decision_ledger.jsonl` |
| **④ Audit→Policy** | 定期（周/月）+ 事件驱动 | `feedback_to_policy.py` 聚合 → PR 提案 |

### 3.3 四档执行约定（永恒，对标 OPA Gatekeeper 2026）

| 档位 | 行为 | 使用场景 |
|---|---|---|
| **deny** | 直接拒绝 | L3 三件套 / 量化红线 / OCP 冻结 |
| **dryrun** | 仅记录不拦截 | 新规则过渡期（7-14 天观察） |
| **warn** | 警告但放行 | 非强制规则 / 建议项 |
| **disabled** | 临时关闭 | 紧急场景 / 故障诊断 |

**档位升级路径（永恒）**：dryrun（7-14d）→ warn（7d）→ deny → 紧急时降 disabled → retrospective 决定回滚。

---

## §4 D3-B AI 自治规划（三层预留口子）

### 4.1 D3-B 拍板结论（永恒）

**拍板**：**D3-B 三层都预留 AI 员工口子**（Policy 花名册 + Factory 命名空间 + Runtime 审计 schema）

**用户决策原话**（2026-04-19）：
> "D3：合规层 AI 员工规划（对标 OQ-062 AI 自治）这个肯定现在就要讨论清楚，不然给未来埋雷，选 D3-B。"

### 4.2 三层 AI 员工口子框架（永恒）

| 层 | 口子类型 |
|---|---|
| **Policy** | AI 员工花名册 / AI 行为规则 / AI 决策记录模板 / AISG 红线过滤 / AISG 策略文档 / Scout 抓取白名单 |
| **Factory** | AI Operator 命名空间 / AI Operator 接口协议 / AISG 脱敏编译器 / Scout scraper 编译器 |
| **Runtime** | AI 决策日志 schema + ledger / AI 行为审计 / AISG 六大模块 / Scout Agent 运行态 / 四大引擎 K2 占位 |

### 4.3 预留原则（永恒铁律）

**只预留不实施**——只定义命名规则 + 路径规则 + 接口名。激活时机由 §5 T3 触发。

**预留 ≠ 过度抽象**：不建目录、不写代码、不激活系统——只标好"空屋子门牌号"，防止未来搬入时发现门开错了。

---

## §5 D4 激活路径（方案 B 稳健分三轮激活）

### 5.1 D4 拍板结论（永恒）

**拍板**：**OQ-026 方案 B 稳健分三轮激活**

**用户决策原话**（2026-04-19）：
> "我的逻辑是分阶段，先激活能保证正常发布任务的，然后是施工，最后是业务。"

| 用户逻辑 | 方案 B 对应 | 激活内容 |
|---|---|---|
| 先激活发布守卫 | **Sprint 9** | L3 三件套 + L4 架构守卫 |
| 然后施工 | **Sprint 10** | AI Safety 三件套 + L5 OCP 契约冻结 |
| 最后业务 | **Sprint 11** | L6 OPA Policy-as-Code |
| T4 触发补齐 | **T4** | L7 SBOM（真实资金/外部审计）|

### 5.2 T0-T7 激活触发条件（永恒框架）

| 触发条件 | 触发后的动作 |
|---|---|
| **T0 scaffold 基础奠基完成**（前置门禁）| **SSoT Validator 激活**（KBG-0021）：阻塞 experimental 下游任务直至全库 frontmatter + 路径 + 跨引用一致性 100% 通过 |
| **T1 真实资金接入** | L7 SBOM + SEC/OPS 从 skeleton→active |
| **T2 多人协作** | VIB-01 升级 + B-01 GRB 激活 |
| **T3 AI 自治升格** | D3-B 口子从"预留"→"实施" + VIB-14 激活 |
| **T4 外部审计合规** | L7 SBOM + SEC/OPS 实质化 |
| **T5 F 函数 ≥25 条** | 25 条 F 函数进 CI Gate |
| **T6 用户主动激活** | 按需激活对应子系统 |
| **T7 5 大核心服务 ≥ 5.5/10**（experimental 出口）| LSG + Sandbox + Scanner 红队评估通过 → 允许接入外部协作 |

### 5.3 T0 SSoT Validator 检查清单（永恒 scaffold 出口）

scaffold → experimental 的**强制门禁**，必须 100% 通过：

- 所有 frontmatter schema 符合 KBG-0002
- 所有跨文档引用链接 Valid（无死链）
- 所有 `module_id` 在全库唯一（无重复）
- 所有文件在 `directory-keep-whitelist.yaml` 或有明确 owner
- 域分层无越界引用（D_FACTOR 不得 import D_PF_CORE，域边界由 depgraph 定义）
- 5 大核心服务接口规范已全部在 `docs/03_modules/_cross_layer/_b_track_interfaces/` 就位

---

## §6 Runtime Plane 边界铁律（关键澄清）

### 6.1 同名不同义问题（永恒澄清）

**问题**：09-GOV 三层叫 Policy / Factory / **Runtime**，04bis 三平面叫 Hot / Warm / **Cold**（没有叫 Runtime），但在交流中经常被误解为"Runtime 平面 = GOV Runtime 层"。**这是错误的**。

### 6.2 边界对照表（永恒）

| 维度 | 治理 Runtime 层 | 执行 Runtime Plane（Hot/Warm/Cold）|
|---|---|---|
| **切片维度** | 治理维度（谁管规则）| 执行维度（代码何时以什么延迟跑）|
| **切片方式** | 按"规则生命周期"切（定规则 Policy / 造工具 Factory / 执行拦截 Runtime）| 按"延迟预算 + 技术栈"切（Hot / Warm / Cold）|
| **所有 Plane 都有治理 Runtime？** | — | **是**（Hot=C++ OPA / Warm=Python 拦截 / Cold=Airflow hook）|
| **Policy 层的 Plane？** | — | **无**（规则文本不执行）|
| **Factory 层的 Plane？** | — | **Cold**（linter/编译器在构建期批量执行）|

### 6.3 复合命名规则（永恒——当二者联合引用时）

当需要联合描述"某代码的治理层 + 运行平面"时，使用**双标签语法**：

```
[GOV:<Policy|Factory|Runtime>] × [Plane:<Hot|Warm|Cold|—>]
```

示例：
- `d_risk.limits.hard_cut.py` → `[GOV:Runtime] × [Plane:Hot]`
- `d_factor.pipeline.batch.py` → `[GOV:Runtime] × [Plane:Cold]`
- `docs/01_policies_and_standards/ai-security-gateway-policy.md` → `[GOV:Policy] × [Plane:—]`

### 6.4 命名约束（永恒铁律）

**在任何文档中禁止单独使用 "Runtime" 一词**——必须带限定词：
- ✅ **Runtime Plane** = 运行平面（执行维度）
- ✅ **Governance Runtime Layer** = 治理 Runtime 层（治理维度）
- ❌ **Runtime**（单独）= 歧义

---

## §7 视图边界 / Boundaries

### 7.1 本文档覆盖

- 三层治理边界定义（Policy/Factory/Runtime）（§2）
- D2-B 三角闭环与四档执行约定（§3）
- D3-B AI 自治三层预留口子（§4）
- D4 方案 B 激活路径与 T0-T7 触发条件（§5）
- Runtime Plane 边界铁律（§6）

### 7.2 本文档不覆盖（由其他系统维护）

| 内容 | 真源 |
|------|------|
| 46 治理系统分层归属表 | depgraph + 治理系统注册表 |
| 激活 Sprint 时间表 | 治理系统注册表 |
| 5 大核心服务治理归属 | depgraph |
| D 家族 6 系统详细展开 | 各域蓝图 |
| 三层物理位置详细路径 | depgraph |
| docs/ 文档抽屉治理规则 | `information_principles.md` |
| src/ 代码域分层规则 | `application_principles.md` |
| 数据层治理（PIT/Survivorship/Lineage）| `data_principles.md` |
| 集成契约治理 | `integration_principles.md` |
| 安全威胁治理 | `security_principles.md` |
| 运行平面详细映射 | `runtime_planes_principles.md` |

### 7.3 与其他原则文档关系

- [capability_maturity_principles.md](capability_maturity_principles.md)：能力成熟度方法论
- [data_principles.md](data_principles.md)：数据架构原则
- [security_principles.md](security_principles.md)：安全架构原则
- [integration_principles.md](integration_principles.md)：集成架构原则
- [business_principles.md](business_principles.md)：业务架构原则
- [information_principles.md](information_principles.md)：信息架构原则
- [application_principles.md](application_principles.md)：应用架构原则
- [technology_principles.md](technology_principles.md)：技术架构原则
- 本文：治理架构原则（三层边界/D2-B 闭环/D3-B 预留/D4 激活）

---

> **文档维护原则**：本文档只包含永恒指导原则。任何随治理系统激活、Sprint 演进、5 大核心服务治理归属变化的内容，均不应写入本文档——它们由各自自动化系统维护。
