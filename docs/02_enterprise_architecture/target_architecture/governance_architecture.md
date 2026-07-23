---
module_id: VIEW-09-GOVERNANCE-ARCH
title: Target Architecture — Governance Architecture / 目标架构：治理架构
doc_type: architecture_view
status: Active
version: 2.2.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-04-21
related_rationale:
- R65
- R66
- R67
- R68
- R69
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
- target-architecture
- governance
- three-layer
- policy
- factory
- runtime
- ai-autonomy
- runtime-planes-boundary
- ssot-validator
- -gate
- 6-core-services-governance
summary: TOGAF 第 9 视图——治理架构。三层治理边界（Policy/Factory/Runtime）横切整个系统， 承载 D1-D4 + OQ-026
  拍板。46 治理系统分层归属（A21+B1+C17+VB1+D6）。 v2.0.0 重组织：物理位置树 → 合并表引用 scripts_model.yaml；接口描述
  → 表格化。
date: '2026-04-22'
ttl: permanent
---

# 09. Governance Architecture / 治理架构视图 （被恢复）

> **TOGAF 第 9 个架构视图** — 定义 ZephyrAlpha 2.0 的治理体系分层与联动机制。
>
> **状态**: `active` v2.0.0 · 2026-04-21 · Architecture-as-Code 重组织
>
> **拍板依据**: `archive/reorg-2026-04-24/realized-as-adr/working-designs/governance-three-layer-boundary-design.md` v1.0.0（ARC-20260424-004，已落地为 KBG-0010）+ KBG-0010 v1.0.0；v1.1.0 增量 KBG-0009 v1.1.0 + OQ-076/079/080/081。

---

## 1. Purpose & 与其他视图边界

### 1.1 本视图要回答的问题

| 问题 | 答案所在 |
|---|---|
| ZephyrAlpha 的治理体系分几层？每层做什么？| §2 三层边界全景 |
| 三层之间怎么联动？接口协议是什么？| §3 D2-B 三角闭环 |
| 46 个治理系统分别归哪层？| §4 分层归属表 |
| 未来 AI 自治接入时，治理架构如何演进？| §5 D3-B 三层预留口子 |
| 哪些治理能力现在激活？哪些等以后？| §6 D4 方案 B 激活路径 |

### 1.2 与其他视图的边界

本视图 **NOT** 覆盖以下内容（由其他视图承载）：

| 边界 | 落在哪个视图 | 本视图如何引用 |
|---|---|---|
| docs/ 文档抽屉治理规则 | `information_architecture.md` | §4 A-01/A-03 引用 |
| src/ 代码域分层规则 | `application_architecture.md` | §4 A-16 引用 |
| scripts/ 治理代码拓扑 | `application_architecture.md §5` | §2 Factory 层引用 |
| 数据层治理（PIT / Survivorship / Lineage）| `../04_architecture_principles_decisions/data_principles.md §6` | §4 A-07 F 函数引用 |
| 集成契约治理 | `integration_architecture.md §6` | §4 A-15 OCP 引用 |
| 安全威胁治理（IAM / KMS / Audit）| `security_architecture.md`（skeleton）| §4 A-10 引用 |
| 运维治理（监控 / Runbook / DR）| `operations_architecture.md`（skeleton）| §6 T1-T6 联动 |
| 前端治理（ESLint / TypeScript strict / A11y）| `frontend_architecture.md` | §4 A-05 扩展 |
| **运行平面切分（Hot/Warm/Cold）** | **`runtime_planes.md`** | **§1.2bis 铁律** |

### 1.2bis Runtime Plane 边界铁律（v1.2.0，R69 / J1 批次）

**关键澄清**：04bis 的**三运行平面**（Hot/Warm/Cold）与本视图的**治理三层**（Policy/Factory/**Runtime**）**名字都叫 "Runtime" 但意义完全不同**，二者正交独立：

| 维度 | 09-GOV Runtime 层 | 04bis Runtime Plane |
|---|---|---|
| **切片维度** | 治理维度（谁管规则）| 执行维度（代码何时以什么延迟跑）|
| **切片方式** | 按规则生命周期切（Policy/Factory/**Runtime**）| 按延迟预算切（Hot<10ms / Warm / Cold>1s）|
| **所有 Plane 都有治理 Runtime？** | — | **是**（Hot=C++ OPA / Warm=Python 拦截 / Cold=Airflow hook）|
| **Policy 层的 Plane？** | — | **无**（规则文本不执行）|
| **Factory 层的 Plane？** | — | **Cold**（linter/编译器在构建期批量执行）|

**联合引用必须使用双标签语法**（详见 04bis §7.3）：`[GOV:Runtime] × [Plane:Hot]`

**禁止**：单独使用 "Runtime" 一词——必须带限定词（"Runtime 层" 指治理 / "Runtime Plane" 指执行）。

### 1.3 本视图的三层治理**管什么？**

**核心澄清**：治理三层**横切整个系统的所有域**——业务层（src/ 52 域）、文档层（docs/ 21 抽屉）、前端层（frontend/）、治理层自己（scripts/ + .cursor/rules/）。治理三层和业务域是**平级正交**的"尺子 + 纪委 + 审计处"。

| 被管对象 | 管的规矩 | 涉及治理层 |
|---|---|---|
| `src/zephyr/*/*.py` 业务代码（按 52 域组织） | ruff/mypy/bandit/PIT/fitness functions | Policy→Factory→Runtime |
| `docs/**/*.md` 文档 | frontmatter schema/INDEX/孤儿检查 | Policy→Factory→Runtime |
| `frontend/**/*.tsx` 前端代码 | ESLint/TypeScript strict/A11y | Policy→Factory→Runtime |
| KB:decisions namespace 架构决策 | append-only/14 天实现 Gate | Policy→Factory→Runtime |
| `shared/contracts/*.py` 契约基类 | OCP 冻结（release 后不可改）| Policy→Factory→Runtime |
| **治理层自己** | 治理规则变更 review/治理脚本测试 | Policy→Factory→Runtime（自治）|

---

## 2. 三层边界全景（Policy / Factory / Runtime）

### 2.1 三层定义速查

| 层 | 大白话定位 | 职责 | 典型产物 |
|---|---|---|---|
| **Policy 层** | 规章制度部门 | 定规则/存规则/版本化/append-only review | Markdown 规则、KB 决策记录、folder-charters、Rego |
| **Factory 层** | 纪委工具组 | 把规则编译成可执行检查器 + 工具链管理 | ruff/mypy 配置、fitness function、arch_guard |
| **Runtime 层** | 巡查队+审计处+档案室 | 拦截+审计+反馈回写 Policy | pre-commit、CI、OPA sidecar、audit-log |

### 2.2 三层物理位置速查

> **详细路径清单** → 查询 depgraph: `SELECT path FROM nodes WHERE domain_id IN ('D_GOVERNANCE','D_GOV_AUDIT','D_GOV_RULE')`（governance/arch_guard/quality 三域）

| 层 | 关键物理位置 | 代表产物 |
|---|---|---|
| **Policy** | `docs/01_policies_and_standards/` · KB:decisions namespace · `.cursor/rules/` · `.trae/rules/` · `AGENTS.md` | 规则文档、KBG-0001~0041（33 VERIFIED）、AI 协作规则 |
| **Factory** | `scripts/arch_guard/` · `scripts/governance/` · `scripts/quality/` · `pyproject.toml` | 25 条 F 函数、import_linter、ruff.toml/mypy.ini/bandit.yaml |
| **Runtime** | `.pre-commit-config.yaml` · `.github/workflows/` · `src/zephyr/compliance/` · `scripts/governance/audit_log/` · `scripts/governance/opa/` · `.metadata/` | pre-commit hooks、CI Gate、kill_switch、OPA policies |

### 2.3 三层架构全景图（Mermaid）

> **📊 治理三层全景图**：见 [`diagrams/governance_three_layers.mmd`](diagrams/governance_three_layers.mmd)

**关键理解**：
- 治理三层与业务层是**平级正交**的横切关系（不是"上下层"）
- 治理三层**管所有层**，包括治理层自己（自治）
- Policy → Factory → Runtime → 审计回写 Policy 构成**三角闭环**（D2-B）

---

## 3. 三层接口联动机制（D2-B 三角闭环）

### 3.1 D2-B 拍板结论

**拍板**：**D2-B 三角闭环：Policy → Factory → Runtime → 审计回写 Policy**

**用户决策原话**（2026-04-19）：
> "三角闭环：Policy → Factory → Runtime → 审计回写 Policy（带反馈环）形成完美闭环最好，相当于最后有检查步骤。"

### 3.2 四条核心接口

> **📊 D2-B 闭环接口图**：见 [`diagrams/governance_d2b_loop.mmd`](diagrams/governance_d2b_loop.mmd)

| 接口 | 触发时机 | 协议 | 当前状态 |
|---|---|---|---|
| **① Policy→Factory** | Policy 规则新增/变更（git commit） | policy_compiler：Markdown/YAML → 检查器配置 | 手动（Sprint 10/11 自动化） |
| **② Factory→Runtime** | git commit / CI push / 交易执行 / AI 决策 | pre-commit hook / GitHub Actions / 函数调用 | L3 三件套就位（Sprint 9） |
| **③ Runtime→Audit** | 每次检查器执行后 | append-only 写入 `policy_decision_ledger.jsonl`（OQ-063 §4.3 28 字段） | Sprint 10 |
| **④ Audit→Policy** | 定期（周/月）+ 事件驱动 | `feedback_to_policy.py` 聚合 → PR 提案 | Sprint 10/11 |

### 3.3 四档执行约定（对标 OPA Gatekeeper 2026）

| 档位 | 行为 | 使用场景 |
|---|---|---|
| **deny** | 直接拒绝 | L3 三件套 / 量化红线 / OCP 冻结 |
| **dryrun** | 仅记录不拦截 | 新规则过渡期（7-14 天观察） |
| **warn** | 警告但放行 | 非强制规则 / 建议项 |
| **disabled** | 临时关闭 | 紧急场景 / 故障诊断 |

**档位升级路径**：dryrun（7-14d）→ warn（7d）→ deny → 紧急时降 disabled → retrospective 决定回滚。

---

## 4. 46 治理系统分层归属表（v1.2.0：原 45 + GATE-SUM 校正 1）

> **概算归属**（Opus 粗分类），多数系统跨层，按"主归属层"归类。精确分层由施工 Sprint 0 细化。
>
> **v1.0.0**：39 系统（A21+B1+C17+VB1）。**v1.1.0 J0-sync**：+D 家族 6 = 45 系统。**v1.2.0 GATE-SUM**：C 家族 16→17（VIB-17 之前遗漏），总计 46。

### 4.1 A 家族：机构标配（21 个）

| ID | 系统名 | 主层 | 次层 | 激活 Sprint |
|---|---|---|---|---|
| A-01 | KB 决策记录 架构决策治理 | Policy | — | 已就位 |
| A-02 | folder-charters 目录契约 | Policy | — | 已就位 |
| A-03 | index.md 索引治理 | Policy | (Runtime 孤儿检查) | Sprint 9（F21）|
| A-04 | Frontmatter schema | Policy | (Factory 编译) | 已就位 |
| A-05 | 编码规范（ruff/mypy/bandit）| Factory | (Runtime pre-commit/CI) | Sprint 9（L3）|
| A-06 | 架构守卫（import-linter）| Factory | (Runtime CI) | Sprint 9（L4）|
| A-07 | Fitness Functions 25 条 | Factory | (Runtime CI) | Sprint 9（L4，OQ-027）|
| A-08 | Pre-commit hooks | Runtime | — | Sprint 9 |
| A-09 | CI workflows | Runtime | — | Sprint 9 |
| A-10 | Audit log（append-only）| Runtime | — | Sprint 10（L10）|
| A-11 | Decision provenance | Runtime | — | Sprint 10（F25）|
| A-12 | Policy-as-Code（OPA）| Runtime | (Factory Rego 编译) | Sprint 11（L6）|
| A-13 | SBOM（供应链）| Factory | (Runtime 扫描) | **T4 触发**（L7）|
| A-14 | Kill switch | Runtime | — | Sprint 9（compliance）|
| A-15 | OCP 契约冻结 | Policy | (Factory 签名, Runtime 守卫) | Sprint 10（L5，F24）|
| A-16 | 跨层依赖治理 | Factory | (Runtime CI) | Sprint 9 |
| A-17 | 目录预算 | Policy | (Factory) | Sprint 9 |
| A-18 | 文件名治理 | Factory | (Runtime) | Sprint 9（F22）|
| A-19 | KB 决策记录 14 天实现 Gate | Factory | (Runtime) | Sprint 10（F23）|
| A-20 | 状态快照治理 | Runtime | — | Sprint 10 |
| A-21 | 报告归档 | Runtime | — | Sprint 9 |

### 4.2 B 家族：元治理（1 个）

| ID | 系统名 | 主层 | 次层 | 激活 Sprint |
|---|---|---|---|---|
| B-01 | Meta-Governance 元治理 | **全三层** | — | Sprint 10 |

B-01 是"治理治理系统的系统"（对标 Goldman GRB）：Policy 元规则 + Factory 治理脚本检查 + Runtime 元治理审计。

### 4.3 C 家族：氛围编程独有（17 个 VIB）

| ID | 系统名 | 主层 | 次层 | 激活 Sprint |
|---|---|---|---|---|
| VIB-01 | Session 协作治理 | Policy | (Runtime SessionRegistry/handoff-log) | 已落地（SessionRegistry/Handoff/ConflictDetector，P2-SES；commit 路径接入待 P4-T1） |
| VIB-02 | 多 AI 工具规则单源 | Policy | — | 已就位 |
| VIB-03 | 模型调用治理（6 子系统）| Policy | (Factory token 预算, Runtime 监控) | Sprint 10 |
| VIB-04 | Prompt 资产治理 | Policy | — | Sprint 11 |
| VIB-05 | AI 输出验收治理 | Runtime | — | Sprint 10 |
| VIB-06 | 知识连续性（Transcript 索引）| Runtime | — | Sprint 11 |
| VIB-07 | 人机信任校准 | Policy | — | 已就位 |
| VIB-08 | AI 并发执行治理 | Runtime | (Factory 限流器) | Sprint 10 |
| VIB-09 | 反向氛围编程（AI 防放水）| Runtime | — | Sprint 10 |
| VIB-10 | 氛围工作节奏 | Policy | — | 已就位 |
| VIB-11 | AI 成本治理 | Factory | (Runtime 监控) | Sprint 10 |
| VIB-12 | 决策溯源（provenance）| Runtime | — | Sprint 10（与 A-11 合并）|
| VIB-13 | AI 知识边界治理 | Policy | — | Sprint 11 |
| VIB-14 | AI 行为审计 | Runtime | — | **T3 触发** |
| VIB-15 | 漂移检测 | Runtime | — | Sprint 11 |
| VIB-16 | 信息时效自刷新 | Runtime | — | Sprint 11 |
| VIB-17 | 反讨好（红队模式）| Runtime | — | Sprint 10 |

### 4.4 VIBE-BASE 家族：共享底座（1 个）

| ID | 系统名 | 主层 | 次层 | 激活 Sprint |
|---|---|---|---|---|
| VB-01 | 氛围编程共享规则 | Policy | — | 已就位 |

### 4.5 D 家族：AI 治理基础设施（6 个）· v1.1.0 新增（J0-sync）

> D = Defense / Data-Intelligence / Decision。6 个**超越 A/B/C/VB 分类**的 AI 治理新系统——"给 AI 员工准备的办公场所 + 保密室 + 情报部 + 决策核心"。与原 39 系统不冲突、不重叠。
>
> **Runtime Plane 列**（R69/J1 批次）：09-GOV 治理维度（主层/次层）与 04bis 执行维度（Plane）正交独立，详见 §1.2bis。

| ID | 系统名 | 主层 | 次层 | Runtime Plane | 激活 | 源 OQ | 代码归属 |
|---|---|---|---|---|---|---|---|
| **D-01** | **AISG 防泄密（AI Security Gateway）** | **全三层** | — | Warm 主 + `security_gateway` Hot-adj + Factory Cold | **OQ-081 硬闸门（Sprint 0 前 P0）** | OQ-076 | `compliance/ai_security/` |
| **D-02** | **Scout Agent（AI 情报员）** | Runtime | (Policy 白名单 / Factory scraper) | Cold（每日 cron） | Sprint 9 简易→11+ 完整 | OQ-079 | `ml_train/scout/` |
| **D-03** | **Decision Engine**（占位）| Runtime | — | Warm | K2 批次 | OQ-080 | `frontend/` |
| **D-04** | **Capital Allocation Engine**（占位，G2 最高）| Runtime | — | Warm 主 + Cold 回测 | K2 批次 | OQ-080 | `pf_core/` |
| **D-05** | **Failure Learning Engine**（占位，G3 最后）| Runtime | — | Cold 主 | K2 批次 | OQ-080 | `compliance/` + KMS L5 |
| **D-06** | **Market Regime Engine**（占位，G4 第二）| Runtime | — | Warm 主 + Cold 训练 | K2 批次 | OQ-080 | `research/` |

**D 家族与原 39 系统关系**：独立分类（AI 治理基建层 vs 业务治理）；共享三层边界方法论；D-01 与 B-01 正交（B-01=治理治理 vs D-01=防泄密）；D-01 是 VIB-03 上游（先脱敏再调度）；D-01 audit ≠ VIB-14（数据流审计 vs 业务决策审计）。

**D-01 AISG 全三层展开**：Policy（`ai_security_gateway_policy.md` + `.cursorignore` + `.cursorrules`）→ Factory（`compile_desensitize_rules.py`）→ Runtime（`compliance/ai_security/` 六大模块 + `aisg/audit_log.jsonl`）。

**D-02 Scout 全三层展开**：Policy（`scout_agent_whitelist.md`）→ Factory（`compile_scraper.py`）→ Runtime（`ml_train/scout/` + `kms/daily_digest/` + **强制走 AISG**）。

### 4.6 分层汇总（39→45）

| 层 | 主归属系统数 | 占比 |
|---|---|---|
| **Policy 层** | 16 | 36% |
| **Factory 层** | 7 | 16% |
| **Runtime 层** | 20 | 44% |
| **全三层**（B-01 + D-01） | 2 | 4% |
| **总计** | **45** | 100% |

### 4.7 激活时间轴分布

| 时间窗 | 系统数 | 备注 |
|---|---|---|
| 已就位 | 8 | Policy 层基础（KB 决策记录/folder-charters/.cursor/rules 等）|
| **Sprint 0 前硬闸门** | **1** | D-01 AISG scaffold 最小集 5 件套（~21h） |
| Sprint 9（L3+L4）| 11 | A-05~09/14/16~18/21 + D-02 简易版 |
| Sprint 10（AI Safety+L5）| 13 | A-10/11/15/19/20 + B-01 + VIB-03/05/08/09/11/17 + VIB-12 |
| Sprint 11（L6 OPA）| 6 | A-12 + VIB-04/06/13/15/16 |
| Sprint 11+ | 1 | D-02 完整版 |
| **K2 批次** | **4** | D-03~06 四引擎（G2→G4→G1→G3 优先级）|
| T3/T4 触发 | 2 | VIB-14（T3）+ A-13 SBOM（T4）|

---

## 5. AI 自治规划（D3-B 三层预留口子）

### 5.1 D3-B 拍板结论

**拍板**：**D3-B 三层都预留 AI 员工口子**（Policy 花名册 + Factory 命名空间 + Runtime 审计 schema）

**用户决策原话**（2026-04-19）：
> "D3：合规层 AI 员工规划（对标 OQ-062 AI 自治）这个肯定现在就要讨论清楚，不然给未来埋雷，选 D3-B。"

**关键原则**：**只预留不实施**——只定义命名规则 + 路径规则 + 接口名。激活时机由 §6 T3 触发。

### 5.2 三层 AI 员工口子清单

| 层 | 口子 | 物理位置（未来）|
|---|---|---|
| **Policy** | AI 员工花名册 | `docs/01_policies_and_standards/ai-operators-registry.md`（Stage K 待建） |
| **Policy** | AI 行为规则 | `docs/01_policies_and_standards/ai-operator-guidelines.md`（Stage K 待建） |
| **Policy** | AI 决策记录模板 | KB:decisions namespace（Session Log decisions 结构化字段） |
| **Policy** | AISG 红线过滤 | `.cursorignore` + `.cursorrules`（OQ-081 硬闸门）|
| **Policy** | AISG 策略文档 | `docs/01_policies_and_standards/ai-security-gateway-policy.md`（Stage K 待建） |
| **Policy** | Scout 抓取白名单 | `docs/01_policies_and_standards/scout-agent-whitelist.md`（Stage K 待建） |
| **Factory** | AI Operator 命名空间 | `src/zephyr/{domain}/_ai_operator/` · `vib/_ai_operator/` · `b01/_ai_operator/` |
| **Factory** | AI Operator 接口协议 | `shared/contracts/ai_operator_contract.py` |
| **Factory** | AISG 脱敏编译器 | `scripts/governance/aisg/compile_desensitize_rules.py` |
| **Factory** | Scout scraper 编译器 | `scripts/governance/scout/compile_scraper.py` |
| **Runtime** | AI 决策日志 schema + ledger | `scripts/audit_log/ai_decision_schema.py` + `ai_decision_ledger.jsonl`（OQ-063 28 字段）|
| **Runtime** | AI 行为审计（VIB-14）| `scripts/audit_log/vib14_ai_behavior_audit.py` |
| **Runtime** | AISG 六大模块 | `src/zephyr/compliance/ai_security/`（D-01 P0 红线）|
| **Runtime** | Scout Agent 运行态 | `src/zephyr/ml_train/scout/` + `kms/daily_digest/` |
| **Runtime** | 四大引擎 K2 占位 | `D_FRONTEND/decision_engine/` · `D_PF_CORE/capital_allocation/` · `D_GOV_AUDIT/failure_learning/` · `D_SIMULATION/market_regime/` |

### 5.3 AI 员工规划总数（v1.2.0：39→46 系统，~39 AI 员工）

| 家族 | 系统数 | AI 员工规划 |
|---|---|---|
| A 机构标配 | 21 | 10 planned + 11 其他 |
| B 元治理 | 1 | 3（GRB 主席 / 治理债预测 / 冲突仲裁）|
| C 氛围独有 | 16 | 10 planned + 6 reserved |
| VIBE-BASE | 1 | 2 reserved |
| **D AI 治理基建** | **6** | **~7**（D-01=2 / D-02=1 / D-03~06≥4）|
| **总计** | **45** | **~38 AI 员工** |

**预留 ≠ 过度抽象**：不建目录、不写代码、不激活系统——只标好"空屋子门牌号"，防止未来搬入时发现门开错了。

---

## 6. 激活条件 + 治理升级路径（D4 方案 B）

### 6.1 D4 拍板结论

**拍板**：**OQ-026 方案 B 稳健分三轮激活**

**用户决策原话**（2026-04-19）：
> "我的逻辑是分阶段，先激活能保证正常发布任务的，然后是施工，最后是业务。"

| 用户逻辑 | 方案 B 对应 | 激活内容 |
|---|---|---|
| 先激活发布守卫 | **Sprint 9** | L3 三件套 + L4 架构守卫（import-linter + 25 F 函数）|
| 然后施工 | **Sprint 10** | AI Safety 三件套 + L5 OCP 契约冻结 |
| 最后业务 | **Sprint 11** | L6 OPA Policy-as-Code |
| T4 触发补齐 | **T4** | L7 SBOM（真实资金/外部审计）|

### 6.2 激活路径时间表

> **📊 治理系统激活时间表**：见 [`diagrams/governance_activation_gantt.mmd`](diagrams/governance_activation_gantt.mmd)

### 6.3 七条激活触发条件（T0-T6）

> 本视图已 active v2.1.0。T0 为 scaffold 强制门禁（最先激活），T1-T6 为后续局部子系统升级。

| 触发条件 | 触发后的动作 |
|---|---|
| **T0 scaffold 基础奠基完成**（前置门禁）| **SSoT Validator 激活**（KBG-0021）：阻塞 experimental 下游任务直至全库 frontmatter + 路径 + 跨引用一致性 100% 通过 |
| **T1 真实资金接入** | L7 SBOM + 06-SEC/08-OPS 从 skeleton→active |
| **T2 多人协作** | VIB-01 升级 + B-01 GRB 激活 |
| **T3 AI 自治升格** | D3-B 口子从"预留"→"实施" + VIB-14 激活 |
| **T4 外部审计合规** | L7 SBOM + 06-SEC/08-OPS 实质化 |
| **T5 F 函数 ≥25 条** | 25 条 F 函数进 CI Gate + 数据层 OQ-075 3 条合并 |
| **T6 用户主动激活** | 按需激活对应子系统 |
| **T7 6 大核心服务 D6 ≥ 5.5/10**（experimental 出口）| LSG + Sandbox + Scanner 红队评估通过 → 允许接入外部协作 |

### 6.4 T0 — SSoT Validator（scaffold 唯一治理任务）

**定位**：KBG-0021 定义，是 scaffold → experimental 的**强制门禁**。没有 SSoT Validator 通过，任何 experimental 核心服务（LSG/CE/VMS/Orc/FLE）落地任务都被阻塞。

**治理归属**：

| 层 | 产物 | 物理位置 |
|---|------|---------|
| **Policy** | SSoT 一致性规则集 | `docs/01_policies_and_standards/ssot-validation-rules.md`（Stage J 待建） |
| **Factory** | Validator 实现 | `scripts/governance/d5_architecture/validate_ssot.py`（复用 11 维审计器骨架）|
| **Runtime** | 每日/每 PR 扫描 | CI `ci_audit/ssot_daily.py` + pre-commit hook |

**检查清单（scaffold 出口必须 100% 通过）**：

- [ ] 所有 frontmatter schema 符合 KBG-0002
- [ ] 所有跨文档引用链接 Valid（无死链）
- [ ] 所有 `module_id` 在全库唯一（无重复）
- [ ] 所有文件在 `directory-keep-whitelist.yaml` 或有明确 owner
- [ ] `reference-remap-table.yaml` 审计日志完整（本次重组的 10+ 条 change_log）
- [ ] 域分层无越界引用（D_FACTOR 不得 import D_PF_CORE，域边界由 depgraph 定义）
- [ ] 6 大核心服务接口规范已全部在 `docs/03_modules/_b_track_interfaces/` 就位

### 6.5 6 大核心服务的治理归属

> 新增于 v2.1.0（2026-04-24）。6 大核心服务（LSG/CE/VMS/Orc/FLE/KB）在三层治理边界中的归属：

| 服务 | Policy 层治理 | Factory 层治理 | Runtime 层治理 |
|------|--------------|--------------|---------------|
| **LSG** | `ai_security_gateway_policy.md` + 四层防御规则集 | `scripts/governance/aisg/` 策略编译器 | Session Log `security_events` 表 + 红队评估季度报告 |
| **CE** | Context 策略白名单 + 压缩质量 SLO | `ContextEngineProtocol` 抽象基类 | FLE `llm_calls` 表 + 压缩质量周报 |
| **VMS** | Collection 元数据契约 + 级联语义表 | `VectorMemoryProtocol` 抽象基类 | Session Log `vms_operations` 表 + 去重检测月报 |
| **Orc** | 任务状态机 + Agent 白名单 | `OrchestratorProtocol` + Sandbox ACL 模板 | `agent_actions` + `sandbox_violations` 表 + 幻觉检测月报 |
| **FLE** | 异常阈值策略 + 动作分派规则 | `FeedbackLoopProtocol` + EMA 参数 | FLE 自监控 anomaly_ledger + 阈值触发审计 |

**治理一致性约束**：6 大核心服务的 Policy 文档必须在 experimental 末全部就位，否则 T7 门禁不通过。

### 6.6 边界声明

**本视图只做**：定义三层分层边界 + 承载 D1-D4 拍板 + 关闭 OQ-026 + 预留 AI 口子 + 锁定激活时间表 + 作为 KBG-0010 + KBG-0021 同源视图 + 定义 6 大核心服务治理归属。

**本视图不做**：不新建目录、不写脚本、不激活检查器、不实施 D3-B 口子、不动 39 系统内部结构、不动 src/ 52 域、不动 KBG-0001~0009。

### 6.7 CL-023 V-15 TruthSourceCascadeValidator 启动记录

> 新增于 v2.2.0（2026-04-27）。Wave 1 R82 兜底缺口 V-15 启动条件已满足。

**启动条件**（全部满足）：
- [x] Wave 1 R80~R85 已写入 rationale-log
- [x] B6 + B1-B5 蓝图已稳定 + V-12 门禁已运行
- [x] `scripts/governance/validate_truth_source_cascade.py` 已实施（T-V2-012 Sonnet）

**Runtime 层归属**：

| 组件 | 物理路径 | 权限 | 说明 |
|------|---------|------|------|
| V-15 骨架 | `scripts/governance/validate_truth_source_cascade.py` | AI-Modifiable | 真源连锁回溯校验器 |
| 影响追踪报告 | `.runtime/reports/truth_source_cascade_<date>.md` | AI-Modifiable | 运行时输出 |
| 阈值告警 | 同上，CASCADE-WARN 输出 | Human-Gated | experimental warn-only |

**experimental 约束**：仅扫描 R-86 起，warn-only 模式（exit code = 0），不阻塞流程。

---

## 7. Revision history / 修订记录

| Date | Version | Description |
|---|---|---|
| 2026-04-27 | **v2.2.0** | CL-023 V-15 TruthSourceCascadeValidator 启动记录（§6.7）：R82 兜底缺口已实施，experimental warn-only 模式。T-V2-012 Step 8 GLM-5.1 文档。 |
| 2026-04-24 | **v2.1.0** | B-d-6 — 新增 T0 "scaffold 基础奠基"强制门禁（KBG-0021 SSoT Validator）+ T7 "6 大核心服务 D6 ≥ 5.5"（experimental 出口）。新增 §6.4 SSoT Validator 三层归属与 scaffold 出口检查清单（7 项）+ §6.5 6 大核心服务治理归属表（每个服务的 Policy/Factory/Runtime 三层产物）。激活条件从 6 条扩至 8 条（T0-T7）。|
| 2026-04-21 | **v2.0.0** | Architecture-as-Code 重组织：物理位置树→合并表引用 scripts_model.yaml；接口描述→表格化；frontmatter 精简。615→~490 行。 |
| 2026-04-19 | v1.2.0 | J1 批次 R69/KBG-0011：§1.2bis Runtime Plane 正交标注。 |
| 2026-04-19 | v1.1.0 | J0-sync：§4.5 D 家族 6 个 AI 治理基建。39→45 系统。 |
| 2026-04-19 | v1.0.0 | 首次发布：D1-D4 + OQ-026 拍板。三层边界 + 45 系统 + AI 预留 + 激活路径。 |

> 完整修订历史：`git log --oneline -- governance_architecture.md`
