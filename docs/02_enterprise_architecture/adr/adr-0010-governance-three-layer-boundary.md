---
module_id: ADR-0010
title: 治理架构三层边界（Policy / Factory / Runtime）
doc_type: adr
status: active
version: 1.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-04-19
superseded_by: null
supersedes: null
related_rationale:
- R65
- R66
related_open_questions:
- OQ-026
- OQ-062
- OQ-063
tags:
- adr
- governance
- three-layer
- policy
- factory
- runtime
- ai-autonomy
- activation-path
summary: 采用 Policy / Factory / Runtime 三层治理分层边界作为 ZephyrAlpha 治理体系的架构终局。Policy 层定规则（写、存、版本化），Factory
  层造工具（把规则编译成可执行检查器），Runtime 层执行规则（拦截 + 审计 + 反馈回写 Policy 形成三角闭环）。三层**横切整个系统**管理所有被治理对象（src
  15 层业务代码 + docs 文档 + frontend 前端 + 契约基类 + 治理层自己）。对标 Goldman SecDB / JPM Athena /
  Two Sigma / Citadel / Microsoft Azure Policy / Netflix / Google Zanzibar / OPA Gatekeeper
  八家业界主流三层切法共识。本 ADR 同步承载 OQ-026 文件治理 7 层激活优先级拍板（方案 B 稳健分三轮：Sprint 9 发布守卫 → Sprint
  10 施工+AI Safety → Sprint 11 业务运行时 → T4 触发补齐 L7）。
date: '2026-04-22'
ttl: permanent
---

> **SRP 注意**：本 ADR 承载 5 个独立决策（D1~D4 + OQ-026），违反"一份 ADR 一个决策"原则。因 ADR 体系已冻结（2026-04-27），无法拆分，保留原状。

# ADR-0010：治理架构三层边界（Policy / Factory / Runtime）

## 1. 状态（Status）

- **当前状态**：`active`（等价于 accepted）
- **提议日期**：2026-04-19（S14-Phase2 批次 I-Reopen，直接 accepted，跳过 proposed 阶段）
- **拍板日期**：2026-04-19（用户选项 A「硬刚 OQ-026 + 起草三层边界讨论稿」一次性拍板 D1-D4 + OQ-026 五议题）
- **被谁取代**：无
- **取代了谁**：无（首次定义治理架构三层边界）

## 2. 上下文（Context）

### 2.1 触发原因

**背景**：ZephyrAlpha 2.0 架构终局阶段（S14 Phase 2），TOGAF 8 视图体系需要补齐最后一张 09 号视图——治理架构（Governance Architecture）。此前（2026-04-19 S14-Phase2-Closure）因先决条件硬不满足（`governance-three-layer-boundary-design.md` 讨论稿从未立项 + OQ-026 deferred）曾决定阶段性收口 `deferred-closure`（R65），随后用户改选**选项 A**「硬刚 OQ-026 拍板 + 起草三层边界讨论稿」一次性解决。讨论稿已落地为本 ADR（realized-as-adr），源稿归档于 `archive/reorg-2026-04-24/realized-as-adr/working-designs/governance-three-layer-boundary-design.md`（ARC-20260424-004）。

**需要决策的五议题**：
- **D1**：Runtime 层是否为独立治理系统（还是只是 Factory 工具的运行环境）？
- **D2**：三层之间的接口联动机制是什么（单向流水线 / 三角闭环 / 无边界）？
- **D3**：未来 AI 自治接入时的三层预留口子如何定义（OQ-062 衔接）？
- **D4**：39 治理系统按什么优先级激活（整合 OQ-026 文件治理 7 层激活顺序）？
- **OQ-026**：文件治理 L1-L7 激活优先级（三方案 A/B/C）？

### 2.2 问题本质

ZephyrAlpha 已识别 **39 个治理系统**（A 机构标配 21 + B 元治理 1 + C 氛围独有 16 + VIBE-BASE 1，详见 `archive/reorg-2026-04-24/draft-abandoned/working-designs/file-governance-architecture-design.md §7ter`，ARC-20260424-009），散落在 5 个物理位置：
- `scripts/governance/` + `scripts/arch_guard/` + `scripts/quality/`
- `.cursor/rules/` + `.trae/rules/`
- `docs/01_policies_and_standards/` + `docs/02_enterprise_architecture/adr/`
- `src/zephyr/l10_compliance/`
- `.pre-commit-config.yaml` + `.github/workflows/`

**缺一张总图** 告诉未来的 AI / 协作者：
1. 这 39 个治理系统**分几层、归谁管**
2. 它们之间**如何联动、接口协议**是什么
3. 未来 AI 自治时**在哪里预留位置**
4. 现在**激活哪些、以什么顺序激活**

### 2.3 机构对标

| 机构/平台 | Policy 层 | Factory 层 | Runtime 层 | 关键启发 |
|---|---|---|---|---|
| **Goldman Sachs（SecDB）** | Slang 规则库 | SecView IDE | 运行时拦截（risk/regulatory controls）| 三层独立 + 执行嵌入业务 |
| **JPMorgan（Athena）** | Control Plane | 规则编译器 | Data Plane + Audit Plane | 三平面分离 + 审计独立 |
| **Two Sigma** | Governance-as-Code | Governance-Tooling | Governance-Runtime | 三层术语标准化 |
| **Citadel** | Policy Registry | Compliance Engine | Monitoring Layer | 登记 / 引擎 / 监控分离 |
| **Microsoft（Azure Policy）** | Definition | Assignment | Evaluation | 定义 / 分配 / 评估清晰分工 |
| **Netflix** | Policy Definition | Policy Compilation | Policy Execution + 混沌反馈 | 带反馈环的三角闭环 |
| **Google（Zanzibar + OPA）** | Schema | Tuples | Check API | 三层 API 化 |
| **OPA Gatekeeper 2026** | ConstraintTemplate | Constraint | Admission Webhook（deny/dryrun/warn/disabled 四档）| 四档执行约定 |

**共性**：**大型机构从不用"一套代码管一切治理"**，全部是三层分离（Policy / Factory / Runtime），只是叫法不同。

**2026 新趋势**（WebSearch 补充）：
1. **"Embedded, not paper"** —— 2026 年监管要求规则必须"被执行"不是"被写下来"
2. **AI Governance Formalization** —— 2026 新监管要求 formal ownership + documented oversight + sign-offs
3. **Full-Stack Policy-as-Code** —— Pulumi OPA v1.1.0（2026）把 Gatekeeper 扩展到 full-stack governance

## 3. 候选方案

### 方案 A：合并为二层（Policy + Runtime，Factory 融入 Runtime）

- 把 Factory 工具作为 Runtime 的一部分（工具在 CI 里动态编译）
- **否决理由**：
  - 业界零先例（8 家机构全部三层独立）
  - Factory 与 Runtime 变更节奏不同（Factory 脚本变化快，Runtime hook 稳定）
  - 违反单一职责原则

### 方案 B：单向流水线（Policy → Factory → Runtime，无反馈）

- Policy 定义规则 → Factory 编译 → Runtime 执行，**不反馈**
- **否决理由**：
  - fitness functions 拿不到运行时数据 → 规则会静态化、过时
  - 2026 监管新要求 "embedded practice" 强调审计必须反馈
  - AI 治理演进时无法闭环（新规则无法通过实测数据迭代）

### 方案 C：【推荐】三层 + 三角闭环

- Policy / Factory / Runtime 三层独立
- Runtime 审计数据定期回写 Policy 驱动规则演进（闭环）
- 39 治理系统按主归属层归类，允许跨层次归属
- 为 AI 自治三层预留命名空间 + 接口协议 + 审计 schema
- 激活按 OQ-026 方案 B 分三轮（Sprint 9/10/11 + T4 触发）

### 方案 D：四层架构（加独立 AI 层）

- Policy + Factory + Runtime + AI 独立层
- **否决理由**：
  - AI 治理活动应**嵌入**三层内部（Policy 层管 AI 规则 / Factory 层管 AI 工具 / Runtime 层管 AI 审计）
  - 单独加 AI 层会产生双重治理结构，增加复杂度
  - OQ-063 已决议 AI 员工口子**分散在三层预留**

## 4. 决策（Decision）

**采用方案 C：三层 + 三角闭环**。

### 4.1 五议题拍板结论

| 议题 | 拍板结论 | 用户决策原话（ipsissima verba） |
|---|---|---|
| **D1 Runtime 是否独立** | **D1-B 独立** | "D1-B（推荐），作为独立层，这是否可以未来 AI 治理铺路？" |
| **D2 三层接口联动** | **D2-B 三角闭环带反馈环** | "三角闭环：Policy → Factory → Runtime → 审计回写 Policy（带反馈环）形成完美闭环最好，相当于最后有检查步骤。" |
| **D3 AI 自治规划** | **D3-B 三层都预留 AI 员工口子** | "D3：合规层 AI 员工规划（对标 OQ-062 AI 自治）这个肯定现在就要讨论清楚，不然给未来埋雷，选 D3-B（推荐）。" |
| **D4 激活路径 / OQ-026** | **方案 B 稳健分三轮** | "我的逻辑是分阶段，先激活能保证正常发布任务的，然后是施工，最后是业务。" |

### 4.2 三层定义与物理位置

| 层 | 定位 | 物理位置 |
|---|---|---|
| **Policy 层**（规章制度部门）| 定规则 / 存规则 / 版本化规则 | `docs/01_policies_and_standards/` + `docs/02_enterprise_architecture/adr/` + `.cursor/rules/` + `.trae/rules/` + `AGENTS.md` |
| **Factory 层**（纪委工具组）| 把规则编译成可执行检查器 | `scripts/arch_guard/` + `scripts/governance/` + `scripts/quality/` + `pyproject.toml` |
| **Runtime 层**（巡查队 + 审计处 + 档案室）| 拦截 + 审计 + 反馈回写 | `.pre-commit-config.yaml` + `.github/workflows/` + `src/zephyr/l10_compliance/` + `scripts/audit_log/` + `scripts/opa/` + `.metadata/` |

### 4.3 被治理对象（三层管什么）

**核心原则**：治理三层**横切整个系统**，管所有被治理对象：
- `src/zephyr/l00-l14/*.py` 业务代码（15 层）
- `docs/**/*.md` 所有文档
- `frontend/**/*.tsx` 前端代码
- `adr/*.md` 架构决策
- `shared/contracts/*.py` 契约基类
- **治理层自己**（scripts/governance/ + .cursor/rules/）—— 自治

### 4.4 D2-B 三角闭环接口协议

```
① Policy → Factory：policy_compiler（未来实现）把 Markdown/YAML 规则编译成 Factory 检查器配置
② Factory → Runtime：pre-commit hook / GitHub Actions / 函数调用绑定
③ Runtime → Audit：append-only 写入 scripts/audit_log/policy_decision_ledger.jsonl
④ Runtime → Policy（反馈）：feedback_to_policy.py 聚合 ledger → 生成 Policy 演进 PR
```

**四档执行约定**（对标 OPA Gatekeeper 2026）：
- **deny**：直接拒绝（L3 三件套 / 量化红线 / OCP 契约冻结）
- **dryrun**：仅记录不拦截（新规则 7-14 天观察窗口）
- **warn**：警告但放行（非强制规则）
- **disabled**：临时关闭（紧急 / 故障诊断）

### 4.5 D3-B AI 员工三层口子清单

| 层 | 口子名 | 物理位置（未来）| 激活时机 |
|---|---|---|---|
| Policy | AI 员工花名册 | `docs/01_policies_and_standards/ai-operators-registry.md`（Stage K 待建） | T3 触发 |
| Policy | AI 行为规则 | `docs/01_policies_and_standards/ai-operator-guidelines.md`（Stage K 待建） | T3 触发 |
| Policy | AI 决策 ADR 模板 | `adr/_template_ai_decision.md` | T3 触发 |
| Factory | AI Operator 命名空间 | `src/zephyr/{l00-l14}/_ai_operator/` + `vib/{vib}/_ai_operator/` + `scripts/b01_meta_governance/_ai_operator/` | T3 触发 |
| Factory | AI Operator 接口协议 | `shared/contracts/ai_operator_contract.py` | T3 触发 |
| Runtime | AI 决策日志 schema（28 字段）| `scripts/audit_log/ai_decision_schema.py` | T3 触发 |
| Runtime | AI 决策 append-only ledger | `scripts/audit_log/ai_decision_ledger.jsonl` | T3 触发 |
| Runtime | VIB-14 AI 行为审计 | `scripts/audit_log/vib14_ai_behavior_audit.py` | T3 触发 |

**关键原则**：**只预留不实施**——本 ADR 不新建任何目录不写任何代码，只定义命名规则 + 路径规则 + 接口名。

### 4.6 D4 激活路径（方案 B）

| Sprint / 触发 | 激活内容 | 对应用户分阶段逻辑 |
|---|---|---|
| **Sprint 9** | L3 三件套（ruff/mypy/bandit）+ L4 架构守卫（import-linter + 25 条 fitness functions + arch_guard）+ 量化红线（kill switch / PIT 校验 / lookahead）| **先激活能保证正常发布任务的** |
| **Sprint 10** | L5 OCP 契约冻结 + AI Safety 三件套 + A-10 audit_log + A-11 decision_provenance（F25）+ A-19 ADR 14 天 Gate（F23）| **然后是施工** |
| **Sprint 11** | L6 OPA Gatekeeper + Rego 策略库 + D2-B 反馈回写闭环 | **最后是业务** |
| **T4 触发**（真实资金 / 外部审计）| L7 SBOM + `06-security-architecture.md` 从 skeleton → active + `08-operations-architecture.md` 从 skeleton → active | 业务上线合规铁律 |

## 5. 影响（Consequences）

### 5.1 正面影响

1. **TOGAF 8 视图体系收口 10/10**——09 号视图补齐，架构系统图 100% 完成
2. **治理体系架构一致性**——39 个治理系统有明确归属层，未来扩展有章可循
3. **AI 自治铺路**——D3-B 三层口子定义好，OQ-062 升格时零重构接入
4. **闭环治理**——D2-B 反馈环让规则随运行时数据演进，防止规则过时
5. **OQ-026 关闭**——deferred 5 个月的文件治理激活优先级正式拍板
6. **对标业界共识**——与 8 家主流机构/平台一致，后续协作者零学习曲线

### 5.2 负面影响（风险）

1. **激活延迟风险**——Sprint 9/10/11 激活节奏依赖架构终局完成时间，若架构终局延期 → 治理激活连带延期
2. **Factory 层工具链选型风险**——L6 OPA 有学习曲线（Rego 语法），Sprint 11 需预留充足学习时间
3. **反馈回写接口未定稿**——D2-B 闭环的 feedback_to_policy.py 具体实现方式留到 Sprint 10/11 细化，存在接口变更可能
4. **39 系统分层概算**——本 ADR §4 分层归属为概算版，精确版留到施工 Sprint 0，可能有 1-2 个系统层归属调整

### 5.3 缓解措施

1. **激活延迟**：每 Sprint 有明确 exit criteria，未达标不进入下一 Sprint
2. **OPA 学习曲线**：Sprint 11 预留 5-7 天（比 Sprint 9/10 多），期间允许 dryrun 模式
3. **反馈接口**：Sprint 10 先实现 ledger write（必须），Sprint 11 再补 feedback_to_policy（可延迟 1 个 Sprint）
4. **分层调整**：本 ADR **不锁死** 39 系统分层归属，施工 Sprint 0 可通过 "append-only" 方式新增 R 号记录调整

## 6. 元数据（Metadata）

### 6.1 Related Rationale

- **R65**（2026-04-19 S14-Phase2-Closure）：批次 I 阶段性收口决策，将 09 号视图定性为 `deferred-closure`。**被本 ADR 实质性超越**：用户后续改选选项 A 硬刚拍板，R65 的 T1-T6 触发条件降级为"局部子系统未来升级触发器"，不是本 ADR 整体激活触发器（本 ADR 已 accepted）。
- **R66**（2026-04-19 S14-Phase2 批次 I-Reopen）：本 ADR 落地决策，9 张视图主线完成。

### 6.2 Related Open Questions

- **OQ-026**（deferred → **closed**，本 ADR 同步关闭）：文件治理 7 层激活优先级，方案 B 拍板
- **OQ-062**（P4 保留）：AI 自治公司终局，本 ADR D3-B 为其预留三层口子
- **OQ-063**（closed）：AI 自治三层口子，本 ADR D3-B 与之完全对齐

### 6.3 Related Work

- `archive/reorg-2026-04-24/realized-as-adr/working-designs/governance-three-layer-boundary-design.md` v1.0.0（ARC-20260424-004，realized-as-adr）—— 本 ADR 的讨论稿与完整论证（§2 八家业界对标 / §5 39 系统概算分层 / §8 拍板路径溯源）
- `target-architecture/09-governance-architecture.md` v1.0.0 active —— 本 ADR 的同源治理架构视图
- `archive/reorg-2026-04-24/draft-abandoned/working-designs/file-governance-architecture-design.md §7ter`（ARC-20260424-009）—— 39 系统总表（本 ADR §4 分层归属的输入）
- `archive/reorg-2026-04-24/draft-abandoned/working-designs/governance-system-internal-structure-convention.md`（ARC-20260424-010）—— 39 系统内部 4 层骨架约定（AI 自治口子预留规则，本 ADR D3-B 的前置约定）
- `archive/reorg-2026-04-24/draft-abandoned/working-designs/ai-autonomous-company-endgame-design.md`（ARC-20260424-006）—— OQ-062 专题稿

## 7. 修订记录（Revision History）

| 日期 | 版本 | 说明 |
|---|---|---|
| 2026-04-19 | 1.0.0 | **首次发布 accepted**（S14-Phase2 批次 I-Reopen）。承载 D1-D4 + OQ-026 五议题一次性拍板。用户选项 A「硬刚 OQ-026 拍板 + 起草三层边界讨论稿」拍板路径。同步产出 `09-governance-architecture.md` v1.0.0 + `working-designs/governance-three-layer-boundary-design.md` v1.0.0。同步关闭 OQ-026（deferred → closed）。对标 8 家业界主流三层切法（Goldman SecDB / JPM Athena / Two Sigma / Citadel / Microsoft Azure Policy / Netflix / Google Zanzibar / OPA Gatekeeper 2026）。|
