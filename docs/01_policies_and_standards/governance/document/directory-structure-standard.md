---
module_id: GOV-DOC-002
title: 目录结构规范（docs/ + src/zephyr/ 双轨治理）
doc_type: standard
status: active
version: 3.3.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-01"
ttl: permanent
summary: "ZephyrAlpha 2.0 目录结构的唯一真源。定义 governance/operational/domains 三级治理架构、防幻觉路径映射、放置决策树。v3.0.0：合并 03_blueprints + 04_construction_plans + 05_delivery_and_construction → 03_modules（按层→模块两级组织，一个模块的所有生命周期产物在同一目录）。"
tags: [directory-structure, governance, path-mapping]
rule_form: declarative
scope: global
stability: stable
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "§2~§3", why: "字段定义+受控词表——目录路径SSoT依据"}
---

# 目录结构规范

> **目的**：定义 `docs/` 与 `src/zephyr/` 下每个子目录的用途和准入规则，使 AI 与人类协作者可以唯一、确定性地定位任何文件。
>
> **v2.0.0 变更摘要**：
> - 新增 §3 `src/zephyr/` 双轨（LPC）治理规则，锚定 ADR-0022
> - 新增 §4 新模块归属判别决策树
> - docs/ 目录重编号与小写化（Stage D 对齐 ADR-0022）
>
> **老树教训**：老树中文件散落在多个位置（`docs/01_FRAMEWORK/`、`docs/09_AUDIT/`、`docs/10_GOVERNANCE_COMPLIANCE/` 等），同类文件没有统一的存放位置，AI 无法可靠地找到文件。

---

## 〇、目的与范围

### 〇.1 目的

定义 `docs/` 与 `src/zephyr/` 下每个子目录的唯一用途和准入规则，使任何 AI 或人类协作者仅凭阅读本文件即可确定性地找到任何文件的唯一正确位置。

### 〇.2 本标准管理以下内容

| # | 内容 | 说明 |
|---|------|------|
| 1 | docs/ 全目录树结构 | 每个子目录的用途、准入规则、module_id 锚点范围 |
| 2 | src/zephyr/ 双轨（LPC）结构 | Vendor Lock-in 隔离 + AI Pair Programming 目录 |
| 3 | 新模块归属决策树 | 根据模块性质判断放在 governance/operational/domains 的哪个位置 |
| 4 | 防幻觉路径映射表 | 完整路径→职责说明的机器可读映射（§5.1.2） |
| 5 | 新增/废弃目录的审批流程 | 标准化审批步骤与合规要求 |

### 〇.3 本标准**不**覆盖以下内容

| # | 排除项 | 以哪个文件为准 |
|---|--------|-------------|
| 1 | 文件的具体命名规则 | file-naming-standard.md（GOV-DOC-003） |
| 2 | 各类文件的具体强制写入路径 | file-path-standard.md（GOV-DOC-004） |
| 3 | 文档生命周期与 TTL 设定 | document-lifecycle-standard.md（GOV-DOC-006） |
| 4 | 文件删除的安全门禁（如锚点保护） | file-operation-safety-policy.md（GOV-DOC-007） |
| 5 | 编码安全要求 | encoding-safety-standard.md（GOV-DOC-005） |
| 6 | 注册表文件的格式与维护规则 | _registry/catalogs/ 下的各注册表文件 |

### 〇.4 专业对标

| 来源 | 对标内容 |
|------|---------|
| ITIL SACM → CMDB Structure | CI 必须分类存放、分层管理——本文的 governance/operational/domains 三级架构基于此 |
| Linux FHS（Filesystem Hierarchy Standard） | 标准化分层目录结构——本文的 docs/ 子目录编号（01-19,99）借鉴了 FHS 的确定性思维 |
| K8s Resource Hierarchy | API Group → Version → Resource——本文的新模块归属决策树（§五）基于同样的"自顶向下确定归属"逻辑 |
| Google Monorepo Practices | `third_party/` 隔离 vendor 依赖——本文 src/zephyr/ 双轨的 Vendor Lock-in 隔离基于此 |

## 一、LPC 双轨架构总则（Spine-and-Wings）

本项目按 **Layered + Platform-Capabilities (LPC) 双轨架构**（ADR-0022）治理：

| 轨道 | 语义 | 编号前缀 | docs/ 镜像 | src/zephyr/ 物理位置 |
|------|------|----------|------------|----------------------|
| **C 轨（脊柱）** | Layered 业务过程（14 层 L00-L13）| **`l<NN>_`** | `docs/03_modules/l<NN>_*/` | `src/zephyr/l<NN>_*/` |
| **B 轨（双翼）** | Bounded Context 平台能力 / 横切基础设施 | **无前缀** | 蓝图→`docs/03_modules/l01_infrastructure/`（与C轨L01蓝图统一存放）；接口规范→`docs/03_modules/_b_track_interfaces/` | `src/zephyr/{llm_security,vector_memory,context_engine,orchestrator,feedback_loop,gates,db,kb,mcp,shared}/` |

> **v3.2.0 澄清**：`07_ai_engineering/` 已废弃——其内容（5个B轨接口规范）已并入 `docs/03_modules/_b_track_interfaces/`。
> 统一理由：蓝图、接口规范、施工计划三个维度的文档统一放在 `03_modules/` 下，
> AI 冷启动只需遍历一个目录树即可获得全量模块信息——无需在两个目录间跳转。
> 对标 Google Monorepo：同一项目的所有文档在一个目录树下，不按"B轨/C轨"分裂。

两轨之间的依赖方向受 `import-linter` 规则约束：
- C 轨内部：**逐层向下依赖**（L06 可依赖 L00-L05，不得反向）
- C 轨 → B 轨：**允许**（业务层可以调用平台能力）
- B 轨 → C 轨：**禁止**（平台能力不得反向依赖业务）
- B 轨内部：受 ADR-0019 `feedback_loop` 反转规则约束（见 ADR-0019 §3）

---

## 二、`docs/` 目录结构

```
docs/
├── migration-declaration.md             # 文档体系双轨终止声明
├── index.md                             # 文档体系根索引（抽屉式导航入口）
├── 01_policies_and_standards/           # C/B 轨共享：治理规范 / 标准 / 协议
│   ├── governance/                      # 声明式治理规则（document/、ai/、task/、security/、architecture/、compliance/、data/、module/）
│   ├── operational/                     # 过程式操作手册（vibe_coding/、devops/、migration/）
│   ├── meta/                            # 元规则（关于规则体系的规则）
│   ├── _registry/                       # 注册表+契约（catalogs/、contracts/、schemas/、vocabularies/）
│   ├── domains/                         # 层域特定规则（L00/、L02/、L04/、L07/）
│   └── templates/                       # 文档模板
├── 02_enterprise_architecture/          # C/B 轨共享：企业架构（TOGAF 视图 + ADR + 架构模型）
│   ├── adr/                             # 架构决策记录（adr-nnnn-*.md）
│   ├── target-architecture/             # 目标架构视图（00-overview.md 等）
│   │   └── architecture-model/          # 架构模型 YAML（layers/、contracts/、events/ 等）
│   └── snapshots/                       # 架构快照（architecture-snapshot-*.yaml）
├── 03_modules/                          # C 轨镜像：14 层模块生命周期文档（按层→模块两级组织）
│   ├── l00_data_source/                 #   ├── <module>/blueprint.md + delivery/
│   ├── l01_infrastructure/              #   每个模块一个子目录，所有生命周期产物放在一起
│   ├── l02_alpha_factor/                #   （Google Monorepo / Linux FHS 风格：按主体分目录）
│   ├── l03_signal_generation/
│   ├── l04_risk_management/
│   ├── l05_portfolio_construction/
│   ├── l06_trade_execution/
│   ├── l07_post_trade_analytics/
│   ├── l08_human_ai_interface/
│   ├── l09_research_innovation/
│   ├── l10_compliance/
│   ├── l11_ml_platform/
│   ├── l12_system_telemetry/
│   └── l13_experimentation/
├── 08_knowledge/                        # 知识管理：项目经验教训（KE）、最佳实践、知识资产
│   └── index.md                         #   知识库抽屉索引入口（planned — M2 KMS 建成后填充）
├── 09_audit/                            # 审计报告（LATEST 覆盖写入）
│   └── reports/                         # 审计报告（全小写）
└── 99_archive/                          # 终态归档（retired-blueprints/ 等）
```

**目录编号保留策略**：04、05（已合并至 03_modules）、06（预留）、07（已合并至 03_modules/_b_track_interfaces/）、11-18（预留）、19（已移出项目至外部工作区）、20-98（预留）的编号**不被允许**临时占用。需新增目录必须走 §七 的 ADR 审批流程。

---

## 三、`src/zephyr/` 双轨结构（LPC）

见 ADR-0022 §3.1：

```
src/zephyr/
│
│  ═══════════ C 轨：14 层业务脊柱（带 l<NN>_ 前缀） ═══════════
│
├── l00_data_source/                     # L00 数据接入
├── l01_infrastructure/                  # L01 基础设施
├── l02_alpha_factor/                    # L02 因子
├── l03_signal_generation/               # L03 信号生成
├── l04_risk_management/                 # L04 风控
├── l05_portfolio_construction/          # L05 组合构建
├── l06_trade_execution/                 # L06 交易执行
├── l07_post_trade_analytics/            # L07 归因分析
├── l08_human_ai_interface/              # L08 人机界面
├── l09_research_innovation/             # L09 研究创新
├── l10_compliance/                      # L10 合规（业务层）
├── l11_ml_platform/                     # L11 ML 平台（训练/推理/模型注册）
├── l12_system_telemetry/                # L12 系统可观测（跨层支撑子系统）
│   ├── metrics/
│   ├── logs/
│   ├── traces/
│   ├── ai_behavior/                     # AI 行为遥测（幻觉率 / token / 规则触发）
│   └── archive/
├── l13_experimentation/                 # L13 自动化实验
│
│  ═══════════ B 轨：横切平台能力（无前缀） ═══════════
│
├── llm_security/                        # LSG  · ADR-0020
├── vector_memory/                       # VMS  · ADR-0016
├── context_engine/                      # CE   · ADR-0015
├── orchestrator/                        # Orc  · ADR-0017
├── feedback_loop/                       # FLE  · ADR-0019
├── gates/                               # 合规门禁（G1-GN 运行时）
├── db/                                  # SQLite schema / atomic 事务
├── kb/                                  # Phase 1-2 过渡期知识库（Phase 3 并入 vector_memory）
├── mcp/                                 # Model Context Protocol 客户端
└── shared/                              # 跨层契约 / 共享工具
```

---
## config/ — 运行时配置目录

> `config/` 是项目根目录的第三个一级目录（与 `docs/`、`src/` 并列），存放系统运行时的声明式配置 YAML。
> 所有配置文件由对应的 `src/zephyr/` 模块在启动时一次性加载，运行期不再 IO。

```
config/
├── capabilities.yaml           # CBAC 能力注册表（Immutable Core）— AI 权限 ACL 的唯一真源
├── trigger_router.yaml         # M3 触发器路由分派表（Human-Gated）
├── compression/                # DocCompressor 压缩策略
│   └── policy.yaml             #   压缩不变量约束（Immutable Core）
├── risk/                       # （Phase 1f/1g 规划中）风控阈值配置
├── drift_thresholds.yaml       # （Phase 1f/1g 规划中）RI-07 DriftDetector 阈值
└── app.yaml                    # （Phase 2 规划中）L01 基础设施应用配置
```

### 准入规则

| 规则 | 说明 |
|------|------|
| ✅ 运行时声明式配置（YAML） | 由 src/ 代码加载的配置数据 |
| ✅ 权限 ACL（capabilities.yaml） | CBAC 能力注册表 |
| ✅ 路由/策略/阈值配置 | trigger_router、compression policy、risk thresholds |
| ✅ `.gitkeep` | 保留空目录占位 |
| ❌ 代码文件（.py） | → `src/zephyr/` |
| ❌ 治理文档（.md） | → `docs/01_policies_and_standards/` |
| ❌ 过程式配置（如 CI 脚本） | → `scripts/` 或 `.github/` |
| ❌ 数据文件（.db、.csv） | → `data/` |

### 权限层级（按 ai-autonomy-authority-registry.md）

| 文件 | 权限层级 | AI 可改？ |
|------|---------|:---:|
| `capabilities.yaml` | **Immutable Core** | ❌ |
| `trigger_router.yaml` | **Human-Gated** | ❌（Owner 审批） |
| `compression/policy.yaml` | **Immutable Core** | ❌ |
| `risk/**/*.yaml`（规划中） | Human-Gated | ❌（Owner 审批） |
| `drift_thresholds.yaml`（规划中） | Human-Gated | ❌（Owner 审批） |

### CBAC 自保规则

`capabilities.yaml` 中的 `write_config` 规则声明了 AI 对 config/ 的写权限：

```yaml
allow:
  - "config/compression/policy.yaml"    # 唯一允许 AI 修改的配置（Immutable Core 字段除外）
deny:
  - "config/capabilities.yaml"          # 自保：注册表不可改自身
  - "config/risk/**/*"                  # 风控配置不可改
  - "config/drift_thresholds.yaml"      # 漂移阈值不可改（Phase 1f/1g 规划）
```

- `capabilities.yaml` 自身禁止被 AI 修改 → 防止权限旁路
- `trigger_router.yaml` 虽不在 `write_config` deny 列表中，但其 schema 被定义为 Human-Gated（ai-autonomy-authority-registry.md §2.9），实际修改须走 Owner 审批

### 新增配置文件的流程

1. 确定权限层级（查 `ai-autonomy-authority-registry.md` → 判断 Immutable Core / Human-Gated / AI-Modifiable）
2. 在 `capabilities.yaml` 的 `write_config` 规则中添加对应的 allow / deny 条目
3. 在本文档本节更新文件清单
4. 若为 AI-Modifiable，在 `trigger_router.yaml` 或对应模块中添加 CBAC 检查

---
## 四、新模块归属判别决策树（锚定 ADR-0022 §3.2）

每个**新**模块按以下决策树自顶而下判断。若某一步的答案不确定，在 `docs/02_enterprise_architecture/open-questions-register.md` 登记后**不实施**，直到仲裁完成。

```
┌─ Q1：此模块的核心职责是"某条业务流水线的某一阶段"吗？
│    （例如"数据清洗"、"因子计算"、"信号生成"、"风控阈值检查"）
│    ├─ YES → 归入对应 l<NN>_*/ 层（C 轨）
│    └─ NO  → 进入 Q2
├─ Q2：此模块是"服务所有业务层的跨层平台能力"吗？
│    （例如 LLM 安全、向量检索、任务编排、反馈闭环）
│    ├─ NO  → 回到 Q1 重新审视业务归属
│    └─ YES → 进入 Q3
├─ Q3：此能力有"明确、稳定、文档化的业务边界（Bounded Context）"吗？
│    ├─ YES → 创建独立顶级包（B 轨，无 l<NN>_ 前缀，风格如 llm_security/）
│    │         → 同步创建 docs/03_modules/_b_track_interfaces/<name>-interface.md 接口合同
│    │         → 同步创建 ADR 决策记录（若为跨任务可复用能力）
│    └─ NO  → 进入 Q4
└─ Q4：此能力是"若干业务层共享的小工具、常量、契约、Schema"吗？
     ├─ YES → 归入 shared/ 子目录
     └─ NO  → 在 open-questions-register.md 登记，不实施
```

**关键规则**：
- **前缀 `l<NN>_` 是 C 轨的语法标识**。看到它就意味着"属于 14 层业务脊柱"，反之亦然。
- **B 轨新包创建门槛**：独立顶级包 = BC 边界明确 + 至少 1 份 ADR + 至少 1 份接口合同 + 至少 1 个 Phase 路线。
- **过渡期实现**：某能力 Phase 1 可先在 C 轨实现（如当前 `kb/`），Phase 3 升级为 B 轨独立包。升级动作需 ADR 记录。

---

## 五、各目录准入规则

### 5.1 `01_policies_and_standards/`

**用途**：所有治理规范、标准、协议文档（跨 C/B 轨共享）

**准入规则**：
- ✅ 治理规范（`*-standard.md`）
- ✅ 治理协议（`*-protocol.md`）
- ✅ 治理声明（`*-declaration.md`）
- ✅ 治理注册表（`*-registry.yaml`）
- ✅ 治理契约（`*-contract.yaml`）
- ❌ 架构视图文档（→ `02_enterprise_architecture/`）
- ❌ 模块蓝图（→ `03_modules/`）
- ❌ 代码文件（→ `src/`）

#### 5.1.1 governance/operational 边界判据

> **这是 `01_policies_and_standards/` 内部 governance/ 和 operational/ 的唯一判据。**
> 所有子目录准入条件都从这个判据推导。

**判据定义**：

| 类型 | 特征 | 关键词 | 归属 |
|------|------|--------|------|
| **声明式** | 描述"什么是对的/错的"，不描述"怎么做" | 必须、禁止、不得、允许、要求 | `governance/` |
| **过程式** | 描述"怎么做"，按步骤执行 | 步骤、流程、检查清单、操作手册 | `operational/` |

**判据测试**：问一个问题——**"这个文件是在定义规则，还是在描述执行步骤？"**

| 答案 | 归属 | 例子 |
|------|------|------|
| 定义规则 → 声明式 | `governance/` | "所有 API 密钥必须存储在环境变量中" |
| 描述步骤 → 过程式 | `operational/` | "Step 1: 检查 .env → Step 2: 验证密钥格式" |

**边界案例判例表**：

| 文件 | 表面看 | 实际是 | 归属 | 理由 |
|------|--------|--------|------|------|
| module-injection-rules.yaml | YAML 配置 | **声明式** | governance/module/ | 定义"模块注入前必须满足的 6 条铁律"，不描述执行步骤 |
| ai-behavior-iron-policy.md | "AI行为铁律" | **声明式** | governance/module/ | 定义"AI 模型在任何操作中必须遵守的 7 条行为铁律"，不描述执行步骤 |
| vibe-coding-session-state-runbook.md | "状态机" | **过程式** | operational/vibe_coding/ | 描述 session 状态转换流程 |
| vibe-coding-gate-checklist.md | "可验证性" | **声明式** | operational/vibe_coding（保留） | 定义"规则必须可验证"的约束，但与 vibe coding 操作紧密耦合，按耦合豁免保留 |
| pre-commit-simplification-plan.md | "plan" | **过程式** | operational/devops/ | 描述 pre-commit 配置的简化执行步骤 |
| file-operation-safety-policy.md | "gate" | **声明式** | governance/document/ | 定义"文件操作前必须通过的安全检查"，是约束不是步骤 |

**混合内容处理原则**：

| 原则 | 说明 |
|------|------|
| **看主体** | 文件 70% 以上内容是声明式 → governance/；70% 以上是过程式 → operational/ |
| **看意图** | 文件的核心目的是"定规矩"还是"教操作"？ |
| **耦合豁免** | 如果声明式内容与某个 operational 子域紧密耦合，允许留在 operational/，但 frontmatter 必须标注 `rule_form: declarative` |

#### 5.1.2 子目录准入与防幻觉路径映射

> **设计目的**：AI 每次新会话都是零记忆，不知道上一次把文件放在哪了。
> 本节的设计目标是：**AI 只需要看这一张表，就能无歧义地判断任何文件该放哪，不需要推断任何路径。**
>
> **防幻觉机制**：
> 1. **完整路径**——每个目录都从项目根开始写完整路径，AI 不需要拼接
> 2. **真实锚点**——每个目录都列出当前已存在的真实文件，AI 可以用它来验证路径是否正确
> 3. **反向映射**——不仅写"这个目录能放什么"，还写"这类文件只能放这个目录"
> 4. **module_id 交叉引用**——每个锚点文件都标注 module_id，AI 可以通过搜索 module_id 验证文件位置

**完整路径映射表**：

| # | 目录完整路径 | 定位 | 当前真实文件（锚点） | ✅ 能放 | ❌ 不能放（→ 正确位置） |
|---|------------|------|-------------------|--------|---------------------|
| 1 | `docs/01_policies_and_standards/meta/` | 元标准层 | PS-STD-000 ~ PS-STD-007, PS-REG-001 | 元标准（关于规则体系本身的规则） | 领域治理规则（→ #2）、操作步骤（→ #10）、层域规则（→ #14~#17） |
| 2 | `docs/01_policies_and_standards/governance/document/` | 文档治理 | GOV-DOC-001~010 | 文档命名/路径/编码/生命周期/安全规则 | AI 治理（→ #3）、任务治理（→ #4） |
| 3 | `docs/01_policies_and_standards/governance/ai/` | AI 治理 | GOV-AI-001~007 | AI 自治/入职/幻觉/模型契约/操作预算 | 任务卡（→ #4）、VC 操作步骤（→ #10） |
| 4 | `docs/01_policies_and_standards/governance/task/` | 任务治理 | GOV-TASK-001~003 | 任务卡/交接/裁定/生命周期 | AI 操作预算（→ #3）、VC 操作（→ #10） |
| 5 | `docs/01_policies_and_standards/governance/security/` | 安全治理 | （Phase 1 新建）GOV-SEC-001~003 | 密钥管理/访问控制/安全事件策略 | 安全操作手册（→ #11 或 #10） |
| 6 | `docs/01_policies_and_standards/governance/compliance/` | 合规治理 | （Phase 1 新建）GOV-CMP-001~002 | 监管分类法/审计追踪策略 | 合规操作手册（→ #11）、L10 特定规则（→ #14 L10） |
| 7 | `docs/01_policies_and_standards/governance/architecture/` | 架构治理 | （Phase 1 新建）GOV-ARCH-001~003 | ADR 协议/架构评审/架构版本化 | 架构视图（→ 02_enterprise_architecture/）、模块文档（→ 03_modules/） |
| 8 | `docs/01_policies_and_standards/governance/data/` | 数据治理 | （Phase 1 新建）GOV-DATA-001~003 | 数据质量/血缘/保留策略 | 数据操作手册（→ #11）、L00 特定规则（→ #14 L00） |
| 9 | `docs/01_policies_and_standards/governance/module/` | 模块治理 | （Phase 1 新建）GOV-MOD-001~005 | 模块准入/生命周期/接口契约/注入规则 | 模块文档（→ 03_modules/）、模块代码（→ src/zephyr/） |
| 10 | `docs/01_policies_and_standards/operational/vibe_coding/` | VC 操作 | OPS-VC-001~003 | VC 上下文规则/session 状态机/可验证性操作 | VC 声明式约束（→ governance/ 对应子域） |
| 11 | `docs/01_policies_and_standards/operational/devops/` | DevOps 操作 | OPS-DEV-001 | pre-commit/CI/部署流程 | DevOps 策略（→ governance/ 对应子域） |
| 12 | `docs/01_policies_and_standards/operational/migration/` | 迁移操作 | OPS-MIG-001 | 迁移审计/迁移步骤 | 迁移策略（→ governance/ 对应子域） |
| 13 | `docs/01_policies_and_standards/domains/L00_data_source/` | L00 层域 | （Phase 2 新建）DOM-L00-001~002 | L00 层的 governance/ + operational/ | 全局规则（→ governance/） |
| 14 | `docs/01_policies_and_standards/domains/L02_alpha_factor/` | L02 层域 | （Phase 2 新建）DOM-L02-001~002 | L02 层的 governance/ + operational/ | 全局规则（→ governance/） |
| 15 | `docs/01_policies_and_standards/domains/L04_risk_management/` | L04 层域 | （Phase 2 新建）DOM-L04-001~002 | L04 层的 governance/ + operational/ | 全局规则（→ governance/） |
| 16 | `docs/01_policies_and_standards/domains/L07_post_trade_analytics/` | L07 层域 | （Phase 2 新建）DOM-L07-001~002 | L07 层的 governance/ + operational/ | 全局规则（→ governance/） |
| 17 | `docs/01_policies_and_standards/_registry/contracts/` | 验证契约 | （Phase 4 新建） | CI 消费的 YAML 契约 | .md 文件（→ governance/） |
| 18 | `docs/01_policies_and_standards/_registry/catalogs/` | 自动注册表 | （Phase 2 新建） | 脚本生成的 YAML 注册表 | **手动编辑的文件** |
| 19 | `docs/01_policies_and_standards/_registry/vocabularies/` | 受控词表 | （Phase 2 新建） | AI 消费的 YAML 词表 | .md 文件（→ governance/） |
| 20 | `docs/01_policies_and_standards/_registry/schemas/` | JSON Schema | （Phase 4 新建） | 脚本生成的 JSON Schema | **手动编辑的文件** |
| 21 | `docs/01_policies_and_standards/templates/` | 模板 | blueprint-template.md（已合并施工指引） | policy/standard/runbook/playbook 模板 | 正式规则文件（→ governance/ 或 operational/） |

**反向映射表（文件类型 → 唯一目标目录）**：

> AI 判断"这类文件该放哪"时，查这张表。每种文件类型**只有一个**目标目录。

| 文件类型 | 唯一目标目录 | 完整路径 |
|---------|------------|---------|
| 元标准（关于规则体系的规则） | meta/ | `docs/01_policies_and_standards/meta/` |
| 文档命名/路径/编码规则 | governance/document/ | `docs/01_policies_and_standards/governance/document/` |
| AI 自治/入职/幻觉/模型契约 | governance/ai/ | `docs/01_policies_and_standards/governance/ai/` |
| 任务卡/交接/裁定 | governance/task/ | `docs/01_policies_and_standards/governance/task/` |
| 密钥/访问控制/安全事件策略 | governance/security/ | `docs/01_policies_and_standards/governance/security/` |
| 监管分类/审计追踪策略 | governance/compliance/ | `docs/01_policies_and_standards/governance/compliance/` |
| ADR 协议/架构评审/版本化 | governance/architecture/ | `docs/01_policies_and_standards/governance/architecture/` |
| 数据质量/血缘/保留策略 | governance/data/ | `docs/01_policies_and_standards/governance/data/` |
| 模块准入/生命周期/注入规则 | governance/module/ | `docs/01_policies_and_standards/governance/module/` |
| VC 上下文/session 状态机 | operational/vibe_coding/ | `docs/01_policies_and_standards/operational/vibe_coding/` |
| pre-commit/CI/部署流程 | operational/devops/ | `docs/01_policies_and_standards/operational/devops/` |
| 迁移审计/迁移步骤 | operational/migration/ | `docs/01_policies_and_standards/operational/migration/` |
| 模块文档（蓝图/交付） | 03_modules/l<NN>_<layer>/<module>/ | `docs/03_modules/` |
| L00 层特定规则 | domains/L00_data_source/ | `docs/01_policies_and_standards/domains/L00_data_source/` |
| L02 层特定规则 | domains/L02_alpha_factor/ | `docs/01_policies_and_standards/domains/L02_alpha_factor/` |
| L04 层特定规则 | domains/L04_risk_management/ | `docs/01_policies_and_standards/domains/L04_risk_management/` |
| L07 层特定规则 | domains/L07_post_trade_analytics/ | `docs/01_policies_and_standards/domains/L07_post_trade_analytics/` |
| 验证契约 YAML | _registry/contracts/ | `docs/01_policies_and_standards/_registry/contracts/` |
| 自动注册表 YAML | _registry/catalogs/ | `docs/01_policies_and_standards/_registry/catalogs/` |
| 受控词表 YAML | _registry/vocabularies/ | `docs/01_policies_and_standards/_registry/vocabularies/` |
| JSON Schema | _registry/schemas/ | `docs/01_policies_and_standards/_registry/schemas/` |
| 文档模板 | templates/ | `docs/01_policies_and_standards/templates/` |

**防幻觉验证流程**：

> AI 在放置文件前，**必须**执行以下验证步骤。跳过任何一步都可能导致路径幻觉。

```
Step 1: 查反向映射表，确定文件类型对应的唯一目标目录
Step 2: 查完整路径映射表，确认目标目录的完整路径
Step 3: 用锚点文件验证路径是否存在——搜索锚点文件的 module_id，
        如果能找到，说明路径正确；如果找不到，说明路径可能有误
Step 4: 用 §5.1.1 核心判据二次验证——文件是声明式还是过程式？
        声明式文件不能放 operational/，过程式文件不能放 governance/
Step 5: 放置文件
```

**锚点验证示例**：

AI 要创建一个安全策略文件，按反向映射表应该放 `governance/security/`。
验证步骤：搜索 `GOV-SEC-001`（governance/security/ 的锚点文件），如果能找到，说明路径正确。

**domains/ 内部防幻觉规则**：

```
domains/L{XX}_{layer_name}/
├── governance/       ← 该层的声明式规则（完整路径：.../domains/L{XX}_{layer_name}/governance/）
└── operational/      ← 该层的过程式规则（完整路径：.../domains/L{XX}_{layer_name}/operational/）
```

| 规则 | 说明 |
|------|------|
| 每个层域目录下**必须**有 governance/ 和 operational/ 两个子目录 | 不允许只有其中一个 |
| governance/ 下只放声明式，operational/ 下只放过程式 | 同 §5.1.1 核心判据 |
| 全局规则放 `governance/`（#2~#9），层域规则放 `domains/L{XX}_*/`（#14~#17） | 判断标准：影响所有层 → 全局；只影响一个层 → 层域 |

**放置决策树**：

```
Q1: 文件是关于"规则体系本身"的元规则吗？
    → 是: meta/
    → 否: Q2

Q2: 文件是声明式还是过程式？
    → 声明式: Q3
    → 过程式: Q4
    → 混合: 看主体（70%）+ 看意图

Q3: 这条声明式规则影响所有层，还是只影响特定层？
    → 所有层: governance/{领域}/
    → 特定层: domains/L{XX}_*/governance/

Q4: 这条过程式规则影响所有层，还是只影响特定层？
    → 所有层: operational/{领域}/
    → 特定层: domains/L{XX}_*/operational/
```

### 5.2 `02_enterprise_architecture/`

**用途**：企业架构文档（TOGAF 视图 + ADR + 架构模型 YAML）

**准入规则**：
- ✅ TOGAF 架构视图（`0X-*-architecture.md`）
- ✅ ADR（`adr-nnnn-*.md`，**文件名全小写**；frontmatter 内 `doc_id: ADR-NNNN` 保持大写）
- ✅ 架构模型 YAML（`layers/l<NN>-*.yaml`、`contracts/*.yaml`、`events/*.yaml` 等）
- ✅ 架构快照（`snapshots/architecture-snapshot-*.yaml`）
- ❌ 治理规范（→ `01_policies_and_standards/`）
- ❌ 模块蓝图（→ `03_modules/`）

### 5.3 `03_modules/` (C 轨镜像)

**用途**：14 层模块生命周期文档。每个模块一个子目录，所有生命周期产物（蓝图含施工指引 → 交付记录）放在同一模块目录下（Google Monorepo / Linux FHS 风格：按主体分目录，不按文档类型分目录）。

> **2026-05-02 更新**：蓝图和施工指引已合并为一份 `blueprint.md`（§1-§11 架构设计 + §12 施工指引）。不再需要独立的 `construction-plan.md`。历史施工图保留在 `delivery/` 下作为审计证据。

**内部结构**：
```
03_modules/
├── l00_data_source/          # L00 层
│   ├── <module-name>/        # 每个模块一个子目录
│   │   ├── blueprint.md      # 蓝图：模块架构设计
│   │   ├── construction-plan.md  # 施工图：实施步骤与验收标准
│   │   └── delivery/         # 交付记录（按版本）
│   │       └── v1.0.0.md
│   └── ...
├── l01_infrastructure/       # L01 层
└── ...（共 14 层 L00-L13）
```

**准入规则**：
- ✅ `l<NN>_*/` 子目录下的模块目录
- ✅ 模块目录下 `blueprint.md` / `delivery/`
- ❌ 非 C 轨业务层的文档
- ❌ 5 大 AI 服务的接口文档（→ `03_modules/_b_track_interfaces/`）
- ❌ 项目级元计划（→ `01_policies_and_standards/operational/devops/`）

**与 GOV-DOC-002 v2.x 的变化**：

| v2.x（旧） | v3.0.0（新） |
|-----------|-------------|
| `03_blueprints/` 只有蓝图、`04_construction_plans/`、`05_delivery_and_construction/` | 合并为 `03_modules/`；蓝图和施工指引统一为一份 `blueprint.md` |
| 蓝图+施工图分为两份文件 | 一份 `blueprint.md` 覆盖全流程（§1-§11 架构 + §12 施工指引） |
| 平铺施工图目录（1500 个文件不可行） | 模块子目录隔离（每个目录 3-5 个文件） |

### 5.4 `03_modules/_b_track_interfaces/` — 原 07_ai_engineering（已合并）

> **v3.2.0**：`07_ai_engineering/` 目录已删除，其内容（5 个 B 轨接口规范）已并入 `03_modules/_b_track_interfaces/`。
> 蓝图、接口规范、施工计划统一在 `03_modules/` 下——AI 冷启动只需遍历一个目录树。

**用途**：5 大 AI 核心服务（LSG/VMS/CE/Orc/FLE）接口合同

**准入规则**：
- ✅ `<service>-interface.md`（如 `llm-security-gateway-interface.md`）
- ❌ 业务层蓝图（→ `03_modules/l01_infrastructure/<module>/`）

### 5.5 `09_audit/`

**用途**：审计报告与审计状态数据（Ex-post——"执行得怎样"）。

**准入规则**：
- ✅ 架构合规性审计报告、SSoT 验证扫描报告、审计状态数据
- ❌ 任何形式的治理规则、合规规范、标准文件（→ `01_policies_and_standards/`）

---

## 六、禁止操作

| 禁止操作 | 原因 |
|---------|------|
| 在 `docs/`（老树体系）下新建文件 | 只读遗留体系（见 `migration-declaration.md`） |
| 在 `docs/` 根目录下新建 `.md` 文件（`migration-declaration.md` 和 `index.md` 除外）| 根目录只允许声明文件和索引文件 |
| 将治理规范放入 `02_enterprise_architecture/` | 类型不匹配（→ `01_policies_and_standards/`） |
| 将架构视图放入 `01_policies_and_standards/` | 类型不匹配（→ `02_enterprise_architecture/`） |
| 新建顶级目录（未在本文档中定义的）| 必须先走 §七 ADR 审批流程 |
| **把 B 轨平台能力放入某一 C 轨层**（例如 `l12_llm_security/`）| 违反 ADR-0022 §3.3；BC 语义会被层语义污染 |
| **把 C 轨业务层改成 B 轨平级形式**（例如把 `l06_trade_execution/` 改成 `execution/`）| 失去 14 层依赖图的编号约束 |
| **混用大小写（ADR_0009 vs adr-0009）** | 所有文件名全小写 kebab-case；ADR id 大写保留在 frontmatter 内 |
| 在 `01_policies_and_standards/governance/` 下放过程式文件 | 违反 §5.1.1 核心判据——声明式/过程式边界 |
| 在 `01_policies_and_standards/operational/` 下放声明式文件 | 违反 §5.1.1 核心判据（耦合豁免除外） |
| 在 `01_policies_and_standards/domains/` 下创建空目录 | 至少 1+1 规则（governance/ + operational/）才允许创建 |
| 手动编辑 `_registry/catalogs/` 和 `_registry/schemas/` | 脚本生成文件，手动编辑会被覆盖 |
| 在 `governance/` 子目录下再建子目录（除非文件数 >20） | 扁平化原则 |
| 把全局规则放入 `domains/` | 全局规则放 `governance/` |
| 把层域规则放入 `governance/` | 层域规则放 `domains/` |

---

## 七、新增目录的审批流程

### 7.1 新增 `docs/` 顶级目录

1. 在本文档 §二 提出新目录编号、用途和准入规则
2. 起草 ADR（若涉及架构性归属）或直接修订本文档
3. 获得 Owner 批准
4. 创建目录 + `README.md`
5. 重新生成 `document-metadata-index.yaml`（`python scripts/governance/d3_metadata/generate_rule_catalog.py`）

### 7.2 新增 `src/zephyr/` 包（C 轨 or B 轨）

1. 运行 §四 归属决策树，明确归属 C 轨或 B 轨
2. 若为 **C 轨新层**（L14+）：需要 ADR + 14 层总数变更的冲击评估
3. 若为 **B 轨新独立包**：需要 ADR + 接口合同 + Phase 路线
4. 在本文档 §三 记录新包
5. 创建骨架（`__init__.py` 带 docstring 说明轨道归属与架构真源）
6. Owner 批准后合入

### 7.3 废弃/合并目录

1. 登记到 `module-relocation-matrix.yaml`（next reorg event）
2. 归档到 `archive/reorg-<YYYY-MM-DD>/superseded/` 并在 `MANIFEST.yaml` 登记
3. 保留最少 12 个月后才可永久删除（ARMA GARP 留存期）

---

## 附录 A：与既有文档的对应关系

| 本规范章节 | 详细定义来源 |
|------------|--------------|
| §一 LPC 双轨架构 | ADR-0022（治理宪法）|
| §三 src/zephyr 结构 | `docs/02_enterprise_architecture/target-architecture/03-application-architecture.md` §4 |
| §四 归属决策树 | ADR-0022 §3.2 |
| §五 `03_modules/_b_track_interfaces/` 准入 | `docs/03_modules/_b_track_interfaces/index.md` |
| §五 ADR 文件名规则 | `file-naming-standard.md`（Stage F 升级到 v2.0.0 后完整定义）|

---

*本规范是 ZephyrAlpha 2.0 目录治理的**执行层文件**（宪法层是 ADR-0022）。所有目录创建、归属、合并、废弃操作必须先过本规范，再过工具链（pre-commit / CI）。*

---

## 八、与其他规则的关系

| 规则 | 与本标准的关系 |
|------|-------------|
| file-naming-standard.md（GOV-DOC-003） | 文件命名规范规定了子目录下的文件命名格式（如 governance/ 下用 `-standard.md`，operational/ 下用 `-runbook.md`） |
| file-path-standard.md（GOV-DOC-004） | 路径规范以本标准的目录定义为锚——每种文件类型的强制路径必落在本标准定义的某个子目录下 |
| document-lifecycle-standard.md（GOV-DOC-006） | 生命周期管理中的归档路径（如 09_audit/archive/）由本标准定义 |
| file-operation-safety-policy.md（GOV-DOC-007） | 不可触碰锚点文件清单与本标准的 §5.1.2 锚点文件表对齐 |
| document-discovery-policy.md（GOV-DOC-010） | 本标准的 §5.1.2 防幻觉路径映射是文档发现路径 1（index → 目录树）的基础数据 |
| unified-numbering-standard.md（GOV-DOC-001） | 编号前缀决定了每个目录下文件的 module_id 格式 |

## 九、变更记录

| 日期 | 版本 | 修改内容 |
|------|------|---------|
| 2026-04-22 | 2.1.0 | 新增 19_development_workspace/ 5 个子目录（Wave 0 R71/R72）：drafts-and-audits/、pending-arbitration/、migrated-from-pool/、cleanup-todos/ |
| 2026-04-26 | 2.2.0 | A/B 双区合并：取消 pending-arbitration/（B 区），合并入 drafts-and-audits/（草稿区）——锚定 R80 决策 |
| 2026-04-27 | 2.3.0 | 新增 §3 src/zephyr/ 双轨治理 + §4 决策树 |
| 2026-05-01 | 2.4.0 | frontmatter 清理 + 结构对齐。（1）移除非标准字段 `related_adrs`/`supersedes`/`v2_*_changes` → 标准化 depends_on + 变更记录；（2）新增 §〇 目的与范围（§〇.2 管理内容 + §〇.3 不覆盖内容 + §〇.4 专业对标）；（3）新增 §八 与其他规则的关系 + §九 变更记录；（4）修正树形图中虚构的 `document-standards/` → 实际子目录；（5）锚点范围修正：GOV-DOC-001~008 → GOV-DOC-001~010。对齐 templates/policy-template.md 强制结构。 |
| 2026-05-01 | 3.0.0 | **架构合并**：删除 `03_blueprints/`、`04_construction_plans/`、`05_delivery_and_construction/`，合并为 `03_modules/`（按层→模块两级组织，一个模块的所有生命周期产物在同一目录）。对齐 Google Monorepo / Linux FHS 的"按主体分目录，不按文档类型分目录"实践。`04_construction_plans/` 下 4 个项目级元计划迁移到 `01_policies_and_standards/operational/devops/bootstrap-plans/`。 |
| 2026-05-02 | 3.1.0 | 删除 `19_development_workspace/`（开发工作区已迁至项目外部独立目录，项目内仅保留真源文件）。 |
| 2026-05-03 | 3.3.0 | **07_ai_engineering 删除**：目录已物理删除，所有残留引用（树形图、决策树、准入规则、附录A）全部更新为 `03_modules/_b_track_interfaces/`。编号 07 加入保留策略清单。 |
