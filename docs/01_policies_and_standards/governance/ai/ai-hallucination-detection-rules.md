---
module_id: GOV-AI-009
title: AI 幻觉自动检测规则集
doc_type: policy
status: active
version: 1.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-04"
valid_from: "2026-05-04"
ttl: permanent
summary: "10 条 AI 代码产出物的自动化幻觉检测规则，含检测方式、严重级别、拦截行为和升级策略。与 GOV-AI-003（手动自检清单）互补——本文档定义可脚本化的自动检测，GOV-AI-003 定义 AI Session 开始前的自我审查。"
tags: [ai, hallucination, detection-rules, automated-gate, governance]
rule_form: procedural
scope: global
stability: stable
verifiability: automated
ai_autonomy: human_gated
depends_on:
  - {target: GOV-AI-003, at: "$", why: "互补文档——手动自检清单与本自动化规则形成双层防护"}
  - {target: PS-STD-001, at: "§2.5", why: "frontmatter 字段真源"}
  - {target: ADR-0014, at: "$", why: "模块准入原则——HC-1/HC-2/HC-3 基于准入铁律"}
supersedes: null
source:
  origin_doc: "模块候选池/开发流程/开发流程七合一方案.md"
  origin_section: "§7.4 AI 幻觉检测启发式规则集"
  origin_version: "v2.2.0"
  extraction_date: "2026-05-04"
---

# AI 幻觉自动检测规则集

> **目的**：定义可被 pre-commit hook / CI gate / 架构门禁脚本自动执行的 AI 幻觉检测规则。与 `ai-hallucination-self-check-policy.md`（GOV-AI-003）的手动自检清单形成双层防护——GOV-AI-003 在 session 开始前由 AI 自检，本文档在代码提交时自动拦截。
>
> **来源**：提取自《开发流程七合一方案 v2.2.0》§7.4。基于七方审计融合报告的 35 条修改建议，将核心规则从 WARNING 升级为 ERROR，并扩展覆盖遗漏的幻觉模式。

---

## 一、与 GOV-AI-003 的分工

| 维度 | GOV-AI-003（手动自检） | GOV-AI-009（自动检测） |
|------|----------------------|----------------------|
| 触发时机 | Session 开始前 | 代码提交时（pre-commit/CI） |
| 执行者 | AI 自身 | 脚本/钩子自动执行 |
| 检测方式 | 问答式逐项确认 | AST 解析/依赖图分析/注册表比对 |
| 覆盖范围 | 路径/ID/接口/依赖/SSOT/编号/权限/编码/任务/引用 | 注册/依赖/跨层/契约/配置/不变/平面/数据流/幂等/PIT |
| 失败后果 | 停止操作/标注不确定性/请求 Owner | ERROR=阻断提交 / WARNING=标注不阻断 |

---

## 二、五层门禁架构（规则执行上下文）

```
┌─────────────────────────────────────────────────────────────┐
│  GATE 0 │  生成前门禁（Pre-Generation Gate）                  │
│         │  触发时机：AI Session Step 2（对话开发）开始前       │
│         │  不通过 → AI 只能做只读操作，不能生成代码            │
├─────────────────────────────────────────────────────────────┤
│  GATE 4 │  发布门禁（Release Gate）                           │
│         │  能力成熟度评分 ≥ 3 / Sim-to-Real 验证 / 性能门禁   │
├─────────────────────────────────────────────────────────────┤
│  GATE 3 │  集成门禁（Integration Gate）                       │
│         │  契约兼容性 / 跨平面通信 / 断链检测 / 文档完整性     │
├─────────────────────────────────────────────────────────────┤
│  GATE 2 │  代码门禁（Code Gate）                             │
│         │  Lint / Type check / 测试覆盖 / Frontmatter / 编码  │
├─────────────────────────────────────────────────────────────┤
│  GATE 1 │  架构门禁（Architecture Gate）— ♨️ 本文档核心规则    │
│         │  模块ID校验 / 运行平面 / ADR引用 / 变更影响分析      │
│         │  ♨️ AI 幻觉检测（10条 HC 规则）                     │
│         │  依赖漂移检测 / 不变量合规 / 知识完整性             │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、10 条自动检测规则

### 3.1 核心规则表

| 规则 ID | 规则 | 检测方式 | 严重级别 | 拦截行为 |
|---------|------|---------|:------:|---------|
| **HC-1** | 新增类/接口未在 `module_id_registry.json` 中登记 | AST 解析 + 注册表比对 | **ERROR** | 阻断提交 |
| **HC-2** | 代码中引入的依赖未在 `technology-landscape.yaml` 的 Adopt/Assess 象限 | import 解析 + Tech Radar 比对 | WARNING | 标注，不阻断 |
| **HC-3** | 跨层直接调用（绕过 `shared/contracts/`） | 依赖图分析 | **ERROR** | 阻断提交，资金执行安全红线 |
| **HC-4** | 修改 frozen 契约（`cross-layer-contracts.yaml` 中 `status=frozen`） | 契约文件 diff | **ERROR** | 阻断提交，架构稳定性保护 |
| **HC-5** | 新增配置项未在 `system-configuration.yaml` 登记 | 配置文件 diff + 注册表比对 | WARNING | 标注，不阻断 |
| **HC-6** | 不变量违反 — AI 生成的代码违反架构不变量 | `invariant_check.py` | **ERROR** | 阻断提交 |
| **HC-7** | 运行平面错配 — AI 将 Cold Path 逻辑写入 Hot Path 模块 | 运行平面标签比对 | **ERROR** | 阻断提交 |
| **HC-8** | 数据流方向违反 — 违反 L00→L02→L03 单向数据流 | 依赖方向分析 | **ERROR** | 阻断提交 |
| **HC-9** | 幂等性缺失 — L06 执行层代码缺少幂等 Key | AST 解析 + 层标签比对 | WARNING | 标注，不阻断 |
| **HC-10** | PIT 铁律绕过 — 回测代码访问了未来数据 | PIT 合规检查 | **ERROR** | 阻断提交 |

### 3.2 补充规则

| 规则 ID | 规则 | 检测方式 | 严重级别 |
|---------|------|---------|:------:|
| **HC-6b** | 语义一致性校验 — 关键子类（FactorBase/StrategyBase/BrokerInterface）必须附带属性测试 | AST 解析 + 测试文件检测 | WARNING |
| **HC-7b** | 跨模块变更隔离 — 同一 commit 禁止跨 2 层修改契约文件 | Git diff 层标签分析 | WARNING |

---

## 四、升级策略

```
Sprint 9-10（当前执行）:
  ERROR（自动拦截）：HC-1 / HC-3 / HC-4 / HC-6 / HC-7 / HC-8 / HC-10
  WARNING（标注不阻断）：HC-2 / HC-5 / HC-9 / HC-6b / HC-7b
  WARNING 累计超过 5 条则禁止 commit

Sprint 11+（基于误报数据调优）:
  评估 HC-2 / HC-5 是否需要升级
  评估 HC-9 全局升级为 ERROR
```

---

## 五、人工确认机制

### 5.1 强制人工确认（必触发）

| 规则 | 原因 |
|------|------|
| **HC-3** | 跨层直接调用 — 资金执行安全红线 |
| **HC-4** | 修改 frozen 契约 — 架构稳定性保护 |
| **HC-10** | PIT 铁律绕过 — 回测有效性红线 |

### 5.2 条件人工确认

| 规则 | 触发条件 |
|------|---------|
| **HC-1** | 新增类属于 L04/L06 层（风控/执行） |
| **HC-2** | 引入技术不在 Tech Radar Adopt 象限 |

### 5.3 SLA 与格式要求

```yaml
sla:
  max_delay_hours: 24
  escalation: block_further_work
  reminder_after_hours: 12
format_requirements:
  - Owner 在 Session Log 的 confirmation_section 签字
  - Git commit message 必须包含 "Confirmed-By: Owner"
warning_review:
  - 每次 commit 前必须展示 WARNING 清单，强制 AI 阅读并确认
  - Owner 必须在 Session Log 中确认已审阅，作为 DoD 的一部分
  - WARNING 累计超过 5 条则禁止 commit
```

---

## 六、与现有基础设施的集成

| 基础设施 | 关系 |
|---------|------|
| `ai-hallucination-self-check-policy.md` (GOV-AI-003) | 互补——手动自检清单，本文档为自动化规则 |
| `scripts/governance/d11_compliance/` | HC 规则的目标执行位置（pre-commit hook） |
| `module-id-registry.yaml` | HC-1 校验的数据源 |
| `ssot-authority-map.md` | HC-5/HC-6 校验的权威来源映射 |
| `architecture-contract.yaml` | HC-3/HC-4/HC-7/HC-8 的结构化约束 |
| `ADR-0014` (模块准入原则) | HC-1/HC-2/HC-3 的策略依据 |

---

## 附录：规则对应的检测实现状态

| 规则 | 检测脚本 | 路径 | 状态 |
|------|---------|------|:--:|
| HC-1 | AST注册表比对 | 待实现 | ⬜ |
| HC-2 | Tech Radar 比对 | 待实现 | ⬜ |
| HC-3 | 依赖图跨层分析 | 待实现 | ⬜ |
| HC-4 | 契约文件 diff | 待实现 | ⬜ |
| HC-5 | 配置注册表比对 | 待实现 | ⬜ |
| HC-6 | `invariant_check.py` | 待创建 | ⬜ |
| HC-7 | 运行平面标签比对 | 待实现 | ⬜ |
| HC-8 | 数据流方向分析 | 待实现 | ⬜ |
| HC-9 | AST幂等检查 | 待实现 | ⬜ |
| HC-10 | PIT合规检查 | 待实现 | ⬜ |
