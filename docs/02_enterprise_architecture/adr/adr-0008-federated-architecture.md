---
module_id: ADR-0008
title: 四架构联邦制（Federated-Light）与 Metamodel 桥梁
doc_type: adr
status: active
version: 1.1.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-04-18
superseded_by: null
supersedes: null
related_rationale:
- R29
- R30
- R64
related_open_questions:
- OQ-045
- OQ-046
tags:
- adr
- federated-architecture
- metamodel
- governance
- scalability
- togaf
- architecture-axes
summary: 采用轻量联邦制（Federated-Light）管理 ZephyrAlpha 的四个独立架构域（文档架构 docs/、后端代码架构 src/zephyr/、前端代码架构
  frontend/、治理架构 scripts/），通过 .metadata/ 下的 Metamodel 桥梁（entity-graph.json + catalogs/
  + cross-references.yaml）实现跨域可追溯性。对标 Two Sigma / Citadel / Goldman Sachs 等大型机构的架构管理实践。**2026-04-19
  批次 H 追溯性从 ADR-DRAFT-0008 升格为 accepted**，与 ADR-0007 成对落地。
date: '2026-04-22'
ttl: permanent
---

# ADR-0008：四架构联邦制（Federated-Light）与 Metamodel 桥梁

## 1. 状态（Status）

- **当前状态**：`accepted`
- **提议日期**：2026-04-18（作为 ADR-DRAFT-0008 起草）
- **拍板日期**：2026-04-18（OQ-045 会话 10 由用户拍板）
- **升格日期**：2026-04-19（批次 H 追溯性从 `adr-drafts/` 搬至 `adr/`，status `proposed` → `accepted`）
- **被谁取代**：无
- **取代了谁**：无（首次显式定义架构间关系）

## 2. 上下文（Context）

### 2.1 规模增长预测

| 维度 | 当前（2026-04 Sprint 8） | 预计 6 个月内（Sprint 20） | 风险 |
|-----|------------------------|--------------------------|------|
| docs/ 文档数 | ~150 | 500+ | 交叉引用断裂、孤儿文档积累 |
| ADR 数量 | 6 | 30-50 | 超越人类跟踪能力 |
| src/ 代码模块 | 11 层 + shared | 15 层 + 60-80 子模块 | 层间依赖隐性化 |
| frontend/ App 数 | 0 | 10+ | 与后端 API 契约漂移 |
| scripts/ 治理脚本 | ~10 | 30+ | 规则间冲突 |
| OSS Catalog 条目 | 42 | 500-2000 | Catalog 与代码层映射失联 |

### 2.2 问题本质

当系统跨过 "200 份 docs / 50 条 ADR" 阈值后，单一线性治理无法维持一致性。需要：
1. 各域独立演进，减少全局锁
2. 跨域关系可机器查询，不依赖人脑记忆
3. 新增实体自动注册，防止"架构暗物质"

### 2.3 机构对标

| 机构 | 做法 | 关键特征 |
|-----|------|---------|
| **Two Sigma** | 内部"平台即产品"，每个平台有独立的架构和文档 | 独立域 + 中央注册表 |
| **Citadel** | 技术与业务架构分治，中央 ADR 委员会仅审跨域 | 联邦审批 + 局部自治 |
| **Goldman Sachs** | Marquee 平台独立前端架构，SecDB 独立后端架构 | 物理隔离 + API 标准化 |
| **Netflix**（工程对标） | 四域分治（平台/流媒体/内容/游戏），Backstage 做注册中心 | 联邦制 + 软件目录 |

**共性**：大型机构从不用"一本大书管一切"，而是联邦制 + 中央注册/索引。

## 3. 候选方案

### 方案 Mono：维持单一架构体系（当前现状）

- 所有架构知识集中在 `docs/02_enterprise_architecture/` 和 taskbook
- **否决理由**：已出现文档引用断裂、ADR 与代码映射丢失、taskbook 膨胀至 900+ 行

### 方案 Heavy-Fed：完整联邦制（四域 + 中央 ARB + 独立版本管理）

- 每个域有独立的 Architecture Board、独立的 ADR 编号空间、独立的版本标签
- **否决理由**：治理开销过大，当前团队 1 人 + AI，无法维持四个 Board

### 方案 Federated-Light：【推荐】轻量联邦制

- 四个域独立演进，但共享同一 ADR 编号空间和同一治理标准
- `.metadata/` Metamodel 提供跨域可追溯性
- 无 Architecture Board 实体（AI 代行审查职能）

## 4. 决策（Decision）

**采用方案 Federated-Light**。

### 4.1 四个架构域

| 域 | 物理根目录 | 独立产物 | 治理方式 |
|----|----------|---------|---------|
| **Documentation Architecture** | `docs/` | TOGAF 视图（01-10）、ADR、Blueprint、Catalog | doc_guard 7 层 + 文档标准 |
| **Backend Code Architecture** | `src/zephyr/` | 15 层 Python 模块 + shared | Import-Linter + mypy + ruff |
| **Frontend Code Architecture** | `frontend/` | platform + 10 apps + packages + tools | ESLint + 微前端约束 + Playwright |
| **Governance Code Architecture** | `scripts/` | doc_guard / hooks / CI 管线 / 自动化脚本 | 脚本自身的单测 + 版本化 |

### 4.2 共享层（不独立为域）

| 共享资源 | 物理位置 | 说明 |
|---------|---------|------|
| ADR 编号空间 | `docs/02_enterprise_architecture/adr-drafts/` | 统一编号，跨域决策用同一序列 |
| 治理标准 | `docs/01_policies_and_standards/` | frontmatter 字段规范、文档分层标准 |
| Metamodel | `.metadata/` | 实体注册表 + 跨域交叉引用（见 §4.3） |

### 4.3 Metamodel 桥梁

`.metadata/` 目录结构：

```
.metadata/
├── entity-graph.json           # 全局实体注册表
├── catalogs/                   # 实体目录索引
│   ├── adr-catalog.yaml        # ADR ID → 文件路径 → 影响代码模块
│   ├── blueprint-catalog.yaml  # Blueprint → 目标代码模块 → 依赖 ADR
│   ├── module-catalog.yaml     # 代码模块 → API 契约 → 依赖上游模块
│   └── oss-catalog-ref.yaml    # OSS 条目 → 目标代码层 → BvB 决策
├── cross-references.yaml       # 跨域引用映射（who → whom）
└── schema/
    └── metamodel-schema.json   # Metamodel 的 JSON Schema 定义
```

#### Entity Types（实体类型）

| 类型 | 命名空间前缀 | 示例 |
|-----|-----------|------|
| ADR | `adr:` | `adr:0007` |
| Blueprint | `bp:` | `bp:feature-store` |
| CodeModule | `mod:` | `mod:l04_ml_engine/feature_store` |
| Catalog | `cat:` | `cat:oss-catalog` |
| Policy | `pol:` | `pol:file-governance-l3` |
| FrontendApp | `app:` | `app:strategy-ide` |
| OQ | `oq:` | `oq:043` |

#### Relationship Types（关系类型）

| 关系 | 方向 | 示例 |
|-----|------|------|
| `implements` | Blueprint → CodeModule | `bp:feature-store` → `mod:l04/feature_store` |
| `governs` | Policy → CodeModule/FrontendApp | `pol:file-governance-l4` → `mod:*` |
| `decides` | ADR → Blueprint/CodeModule | `adr:0007` → `app:*` |
| `depends_on` | CodeModule → CodeModule | `mod:l05` → `mod:l04` |
| `supersedes` | ADR → ADR | `adr:0008` supersedes nothing |
| `evaluates` | Catalog → CodeModule | `cat:oss:zipline` → `mod:l05` |

#### 自动生成 vs 手工维护

| 文件 | 维护方式 | 触发 |
|-----|---------|------|
| `entity-graph.json` | **脚本自动生成** | `scripts/meta/build-entity-graph.py` 扫描 frontmatter |
| `catalogs/*.yaml` | **脚本自动生成 + 手工补全** | 自动从 frontmatter 提取，手工补 cross-reference |
| `cross-references.yaml` | **手工维护**（初期）→ 脚本辅助（后期） | ADR 新增/Blueprint 变更时更新 |
| `schema/` | **手工维护** | Metamodel Schema 变更时更新 |

### 4.4 演进路线

| 阶段 | 触发条件 | 动作 |
|-----|---------|------|
| **Phase 0**（当前） | ADR-0008 approved | 建 `.metadata/` 骨架 + `schema/metamodel-schema.json` 定义稿 |
| **Phase 1** | docs > 200 且 ADR > 15 | 脚本自动生成 `entity-graph.json`，手工补 `cross-references.yaml` |
| **Phase 2** | docs > 500 且 frontend/ 投产 | 全自动 CI 校验（entity 未注册则 CI fail），Backstage 重评估（见 OQ-040） |

### 4.5 与 ADR-0007 的关系

ADR-0007（前端平台层）定义了 `frontend/` 的内部结构。ADR-0008 定义了 `frontend/` 作为四个域之一如何与其他三域协作、如何在 Metamodel 中注册实体。两者互补：

- ADR-0007 回答 "前端怎么建"
- ADR-0008 回答 "四个域怎么连"

## 5. 后果（Consequences）

### 5.1 收益

- **独立演进**：后端可独立升级 L12/L13，前端可独立加 App，docs 可独立扩视图，互不阻塞
- **跨域可追溯**：任何实体（ADR/Blueprint/Module/App）都能在 Metamodel 中查到上下游关系
- **AI 友好**：entity-graph.json 是结构化 JSON，AI 可直接解析而不需要阅读 500 份 md
- **渐进式**：Phase 0 仅需建骨架目录，不需重构现有内容

### 5.2 代价

- 新增 `.metadata/` 顶级目录
- Phase 1 需开发 `build-entity-graph.py` 脚本（Sonnet 可完成）
- `cross-references.yaml` 手工维护有遗漏风险（Phase 2 CI 校验可缓解）

### 5.3 风险

| 风险 | 缓解 |
|-----|------|
| Metamodel 维护被遗忘 | Phase 1 加入 doc_guard pre-commit 校验 |
| entity-graph.json 与实际不一致 | 每次 `git push` 自动 rebuild |
| 四域标准不一致 | 共享治理标准（ADR 编号 / frontmatter 字段 / 文档分层）|

## 6. 回滚条件（Rollback）

若 12 个月内系统未跨过 "200 docs / 15 ADR" 阈值，且跨域追溯需求极低，可降级回 Mono 方案（删除 `.metadata/`，回到集中式文档管理）。

## 7. 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-04-18 | 1.0.0 | 初版（作为 `adr-drafts/ADR-DRAFT-0008`）。会话 10（Opus 47）AX-1 四架构联邦制讨论产出。对标 Two Sigma/Citadel/Goldman/Netflix，选定 Federated-Light。status `proposed`。 |
| 2026-04-19 | 1.1.0 | **追溯性升格为 accepted**（与 ADR-0007 成对落地）：拍板日期仍为 2026-04-18（OQ-045 关闭日），升格日期为 2026-04-19（批次 H S14-Phase2-BatchH）。文件物理位置从 `adr-drafts/ADR-DRAFT-0008-federated-architecture.md` 搬至 `adr/adr-0008-federated-architecture.md`，草稿原件删除。module_id 从 `EA-ADR-DRAFT-0008` 改为 `ADR-0008`，status `proposed` → `accepted`，related_rationale 追加 R64（本次升格的治理决策登记）。`adr/index.md` 同步登记。|
