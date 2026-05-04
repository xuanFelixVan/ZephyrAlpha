---
module_id: ADR-0022
doc_type: adr
title: 双轨目录治理 — Spine-and-Wings (LPC) 架构范式
version: 1.0.0
status: active
date: '2026-04-25'
owner: ZephyrAlpha-Owner
ttl: permanent
related_adrs:
- ADR-0009
- ADR-0015
- ADR-0016
- ADR-0017
- ADR-0019
- ADR-0020
priority: P0
phase: Phase-0
layer: cross_layer
classification: confidential
language: zh
created_by: agent
valid_from: '2026-04-24'
superseded_by: null
supersedes: null
related_rationale: []
related_open_questions: []
tags: [adr, vibe-coding]
summary: "**双轨目录治理** Spine-and-Wings (LPC) 架构范式（C 轨业务分层 + B 轨平台能力）| accepted"
---

# ADR-0022: 双轨目录治理 — Spine-and-Wings (LPC) 架构范式

**状态**：Accepted
**日期**：2026-04-25
**决策者**：ZephyrAlpha-Owner
**优先级**：P0
**阶段**：Phase 0（架构宪法层）

---

## 1. 状态（Status）

- **当前状态**：`accepted`
- **提议日期**：2026-04-24
- **拍板日期**：2026-04-25
- **被谁取代**：—
- **取代了谁**：—

## 2. 背景与问题（Context）

### 2.1 为什么现在必须决策

Stage C 物理污染清理后进入 Stage D 结构对齐时，发现一个**治理层级的根本矛盾**：

- 14 层架构 `l<NN>_*` 是**业务过程纵向分层**（L00 数据 → L06 执行 → L11 ML 平台 → L13 实验）
- 但 5 大 AI 核心服务（LSG / VMS / CE / Orc / FLE）、`gates/`、`db/`、`kb/`、`mcp/`、`shared/` 是**横切的平台能力**（Cross-Cutting Platform Capabilities），**服务所有业务层**
- Stage C 初版 `module-relocation-matrix` 曾尝试把这些横切能力塞进 `src/zephyr/infra/`（"技术切片"反模式），违反 DDD Bounded Context 原则
- 若不形式化这条治理规则，每次遇到新模块都要临时仲裁，污染源会**持续再生**

### 2.2 两种治理方案的对立

| 方案 | 形态 | 代价 |
|------|------|------|
| **方案 A：全部入层** | 把 6 大核心服务硬塞进某一层（如 `l12_infra/`）| 破坏 Bounded Context，技术横切破坏业务分层语义，运行时环形依赖 |
| **方案 B：全部摘出** | 所有横切能力都独立于 14 层之外 | 破坏层编号连续性，业务逻辑（如 L10 合规）也被误摘出 |
| **方案 C：双轨**（本 ADR）| 按"服务边界强弱 + 跨层性"分流 | 治理规则多一条，但保留两种范式各自的语义价值 |

### 2.3 业界参照

| 实践 | 分层观 | 本项目映射 |
|------|--------|------------|
| **Domain-Driven Design (Evans 2003)** | 分层 + Bounded Context 并存 | **C 轨 = 分层，B 轨 = BC** |
| **Google Monorepo Style** | `{layer}/` vs 顶级 `infra/`、`common/`、`third_party/` | 与本 ADR 同构 |
| **Kubernetes `pkg/` 布局** | `apis/`、`kubelet/`、`scheduler/`、`controller/` 均平级，无编号前缀 | Bounded Context 平级布局 |
| **Uber Go Style Guide** | 业务领域独立包 + 共享基础设施独立包 | 同构 |

结论：**双轨治理不是本项目独创，而是大型工程化项目的事实标准**。

## 3. 决策（Decision）

### 3.1 正式命名：Spine-and-Wings Architecture（脊柱与双翼架构，简称 LPC）

- **Spine（脊柱）= L 轨 = Layered business process**（14 层量化业务流水线）
- **Wings（双翼）= B 轨 = Bounded Context platform capabilities**（AI 服务与平台基础设施）
- **简称 LPC**：**L**ayered + **P**latform-**C**apabilities 双轨

`src/zephyr/` 物理形态：

```
src/zephyr/
├── # ========= C 轨：14 层业务脊柱（带 l<NN>_ 前缀） =========
├── l00_data_source/
├── l01_infrastructure/
├── l02_alpha_factor/
├── l03_signal_generation/
├── l04_risk_management/
├── l05_portfolio_construction/
├── l06_trade_execution/
├── l07_post_trade_analytics/
├── l08_human_ai_interface/
├── l09_research_innovation/
├── l10_compliance/               # L10：合规业务层
├── l11_ml_platform/              # L11：ML 平台（训练/推理/模型注册）
├── l12_system_telemetry/         # L12：系统可观测子系统（跨层支撑）
├── l13_experimentation/          # L13：自动化实验
│
├── # ========= B 轨：横切平台能力（无 l<NN>_ 前缀） =========
├── llm_security/                 # LSG · ADR-0020
├── vector_memory/                # VMS · ADR-0016
├── context_engine/               # CE  · ADR-0015
├── orchestrator/                 # Orc · ADR-0017
├── feedback_loop/                # FLE · ADR-0019
├── gates/                        # 合规门禁（G1-GN 运行时）
├── db/                           # SQLite schema / atomic 事务
├── kb/                           # Phase 1-2 过渡期知识库（Phase 3 并入 VMS）
├── mcp/                          # Model Context Protocol 客户端
└── shared/                       # 跨层契约 / 工具
```

### 3.2 归属判别流程（决策树）

每个新模块按以下树自顶而下判断：

```
┌─ Q1：此模块的核心职责是"某条业务流水线的某一阶段"吗？
│    ├─ YES → 归入对应 l<NN>_*/ 层（C 轨）
│    └─ NO  → 进入 Q2
├─ Q2：此模块是"服务所有业务层的跨层平台能力"吗？
│    ├─ NO  → 回到 Q1 重新审视
│    └─ YES → 进入 Q3
├─ Q3：此能力有"明确、稳定、文档化的业务边界"（Bounded Context）吗？
│    ├─ YES → 创建独立顶级包（B 轨：llm_security/ 风格，无 l<NN>_ 前缀）
│    └─ NO  → 进入 Q4
└─ Q4：此能力是"若干业务层共享的小工具、常量、契约、Schema"吗？
     ├─ YES → 归入 shared/ 子目录
     └─ NO  → 先在 open-questions-register.md 登记，不实施
```

### 3.3 编号前缀规则

| 类型 | 前缀 | 原因 |
|------|------|------|
| C 轨 · 业务层（L00-L13）| **`l<NN>_`** | 14 层有顺序、有依赖图、有 fitness function 约束 |
| C 轨 · 层内子系统（如 `l12_system_telemetry/logs/`）| **无**（子目录不再加前缀）| 子目录已被父层 `l<NN>_` 隔离命名空间 |
| B 轨 · Bounded Context（如 `llm_security/`）| **无** | BC 是功能模块，不是层；加前缀反而暗示"层序"误导 |
| B 轨 · 共享工具（`shared/`）| **无** | 横切基础设施 |

**特殊说明 · L12 的双重身份**：
- `src/zephyr/l12_system_telemetry/` 是 C 轨（系统可观测业务线）
- 5 大 AI 服务（LSG/VMS/CE/Orc/FLE）也曾被误称"L12 服务"，实为 B 轨（无 `l12_` 前缀）
- 两者只是"都为所有层提供支撑"的相似性，治理范式不同

### 3.4 docs/ 镜像规则

`docs/` 目录对 `src/zephyr/` 两轨**结构同构**：

- C 轨镜像：`docs/03_blueprints/l<NN>_*/`（14 层蓝图）
- B 轨镜像：`docs/03_modules/_b_track_interfaces/` 下的 6 大核心服务接口合同 + `docs/10_compliance/`（B/C 轨共享合规规范）

### 3.5 归属仲裁权

- **默认仲裁人**：Owner（ZephyrAlpha-Owner）
- **建议起草人**：Agent（基于决策树 §3.2 生成归属建议）
- **争议记录**：所有归属仲裁记入 `docs/02_enterprise_architecture/architecture-rationale-log.md`

## 4. 后果（Consequences）

### 4.1 正面后果

- 新模块落位有**确定性判别流程**，无需每次临时仲裁
- C 轨/B 轨分野使 `import-linter` 规则可精确表达：
  - C 轨：严格"下层不得依赖上层"（业务 DAG）
  - B 轨：只允许"C 轨依赖 B 轨"+ B 轨内受限依赖图（VMS/LSG 为叶子，CE/Orc/FLE 为中间层，见 ADR-0019）
- 与业界 DDD / Google / Kubernetes 实践对齐，新人上手曲线降低
- 14 层业务语义与横切能力语义**不再互相污染**

### 4.2 负面后果

- 治理规则复杂度 +1 条（需要新人理解"为什么 `llm_security` 不加 `l12_`"）
  → **缓解**：本 ADR + `directory-structure-standard.md` v2.0.0 显式说明决策树
- `src/zephyr/` 第一层子目录数量从原 11 个（纯 L0-L10）增到 19+ 个
  → **缓解**：IDE 文件树树形渲染天然分组；`ls` 按首字母排序自然把 `l<NN>_*` 聚到一起，`llm_security/vector_memory/...` 聚到另一起

### 4.3 兼容性影响

- Phase 0 一次性迁移：见 `module-relocation-matrix.yaml` v2.0.0（Stage E 执行）
- Phase 1 之后：新增模块直接按 §3.2 决策树落位
- 现有 `kb/` 作为 Phase 1-2 过渡期实现，Phase 3 并入 `vector_memory/`

## 5. 替代方案（Alternatives）

### 5.1 方案 A：全部入层（已否决）

将 6 大核心服务硬塞进 `l12_infra/`（或类似单一层），继续沿用纯 C 轨。

**否决理由**：
- 6 大核心服务的 Bounded Context 边界强、独立演进、各自有 ADR（ADR-0015/16/17/19/20），强行合并为单层破坏 BC 完整性
- LSG/VMS 等依赖关系**不符合"层内无环 + 逐层向下"** 的 L-约束（例如 CE 同时依赖 VMS + LSG，FLE 依赖所有人）
- 违反 DDD、Google、Kubernetes 的实际工程经验

### 5.2 方案 B：全部摘出（已否决）

取消 `l<NN>_` 分层，所有包平级。

**否决理由**：
- 业务过程（L00 数据 → L01 基建 → L02 因子 ... → L07 归因）天然有**严格顺序和依赖图**，失去编号无法表达该约束
- fitness functions / import-linter 规则无法精确表达"层级依赖方向"
- 量化系统"数据流 → 因子 → 信号 → 风控 → 组合 → 执行 → 归因"的管线语义是项目**本质差异化特征**，不应抹平

### 5.3 方案 C：双轨（本 ADR · 已采纳）

C 轨保持 14 层业务脊柱，B 轨独立为平台能力翼。

**采纳理由**：§3 已详述。

## 6. 相关决策（Related）

- **ADR-0009**：src/ 14 层架构升级（本 ADR 的 C 轨来源）
- **ADR-0015**：Context Engine 架构（B 轨 · CE）
- **ADR-0016**：Vector Memory Service 架构（B 轨 · VMS）
- **ADR-0017**：Agent Orchestrator 架构（B 轨 · Orc）
- **ADR-0019**：Feedback Loop Engine 架构（B 轨 · FLE · 定义了 B 轨内依赖反转规则）
- **ADR-0020**：LLM Security Gateway 架构（B 轨 · LSG）
- **ADR-0021**：SSoT Validator Phase 0 门禁（本 ADR 的治理落地执行者）

## 7. 执行清单（Implementation Checklist）

- [x] Stage D-a：创建 B 轨 6 大核心服务骨架（`src/zephyr/{llm_security,vector_memory,context_engine,orchestrator,feedback_loop}/`）
- [x] Stage D-a：创建 C 轨 L12/L13 骨架（`l12_system_telemetry/` + `l13_experimentation/`）
- [x] Stage D-b：L10/L11 重命名（`l10_governance_compliance` → `l10_compliance`；`l11_strategic_decision` → `l11_ml_platform`）
- [x] Stage D-d：归档 v1.0 层定义（MANIFEST ARC-017）
- [x] Stage D-e：本 ADR 起草
- [ ] Stage D-f：`directory-structure-standard.md` v2.0.0 嵌入 §3.2 决策树
- [ ] Stage E：物理代码迁移（`src/zephyr/infra/` 解构到 6 大核心服务 + `gates/`）
- [ ] Stage G：`import-linter` 规则新增 **track_c_layering** 与 **track_b_bounded_context** 两套约束

---

## 附录 A：决策树的 5 个已解个案

| 模块 | Q1 | Q2 | Q3 | Q4 | 归属 |
|------|----|----|----|-----|------|
| `llm_security/` | NO（非业务阶段）| YES（所有 LLM 交互都过它）| YES（有 LSG ADR + 接口合同）| — | **B 轨独立包** |
| `l12_system_telemetry/` | NO | YES | YES（BUT 业务边界弱 + 多层分片）| — | **C 轨带 `l12_` 前缀** |
| `gates/g2_triage.yaml` | NO（非业务阶段）| YES（跨所有 ADR 的门禁规则）| YES（有 gate-strategy.md）| — | **B 轨独立包 `gates/`** |
| `db/sqlite_schema.py` | NO | YES | 部分（schema 是契约，但无独立接口合同）| YES（shared 工具）| **B 轨独立包 `db/`**（边界够强可升为独立 BC）|
| `shared/types.py` | NO | NO（非能力）| — | YES | **B 轨 `shared/`** |

## 附录 B：LPC 缩写说明

- **L** = **L**ayered（分层，脊柱，C 轨）
- **P** = **P**latform（平台，横切，B 轨的"翼"侧）
- **C** = **C**apabilities（能力，强调"可复用的跨层功能"而非"服务"一词的歧义）

可读作：**"以分层（L）业务为脊柱，以平台能力（PC）为双翼，分别治理"**。

---

*本 ADR 是 ZephyrAlpha 2.0 目录治理的**宪法级决策**，取代所有历史的临时归属仲裁。*
