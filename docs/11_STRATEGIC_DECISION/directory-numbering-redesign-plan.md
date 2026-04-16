---
module_id: STRATEGIC_DIR_NUMBERING_REDESIGN_PLAN
version: '1.0.0'
status: Active
created_date: '2026-04-16'
last_updated: '2026-04-16'
owner: Project Owner
layer: cross_layer
priority: P2
standard_type: architecture_decision
---

# 目录编号体系重新设计方案

> **用途**：消除 docs/ 下一级目录"同编号多义"冲突，建立长期可扩展的两维分离编号体系。
> **决策状态**：PROPOSED（待用户确认后升级为 APPROVED，执行迁移前不得动文件）。

---

## 一、问题诊断

### 1.1 冲突清单

当前 docs/ 一级目录中存在 **6 处同编号不同目录**：

| 前缀 | 目录 A（业务内容） | 目录 B（治理/架构基础设施） | 冲突性质 |
|------|------------------|---------------------------|----------|
| `01_` | `01_FRAMEWORK`（~332 蓝图） | `01_GOVERNANCE`（治理标准） | 同号两用 |
| `02_` | `02_FACTOR_LIBRARY`（L02 因子） | `02_ARCHITECTURE`（架构文档） | 同号两用 |
| `03_` | `03_TRADING_TACTICS`（L05 策略） | `03_BLUEPRINTS`（蓝图目标结构） | 同号两用 |
| `04_` | `04_EXECUTION`（L06 执行） | `04_CONSTRUCTION`（施工计划） | 同号两用 |
| `07_` | `07_AI_REPORTING`（L07 AI报告） | `07_RESEARCH`（研究层） | 同号两用 |
| `08_` | `08_HUMAN_AI_INTERFACE`（L08 人机） | `08_KNOWLEDGE`（知识库） | 同号两用 |

### 1.2 根因分析

编号体系混乱源于**两套逻辑叠加**：

```
系统架构层级（L00–L11）   ←→   目录编号（NN_）
        ↕ 试图对齐               ↕ 实际无法对齐
  业务内容域（L02 因子等）      治理/基础设施域（架构文档、治理标准）
```

业务内容目录试图与 Layer 编号对齐，但治理/基础设施目录（Governance、Architecture、Audit 等）不属于任何 Layer，被迫占用相同前缀，导致冲突。

### 1.3 影响

- AI 导航错误：AI 看到 `01_` 前缀不知是蓝图还是治理
- 人工认知负担：新成员必须记忆"哪个 01_ 是哪个"
- 脚本层面：`check_directory_naming.py` 无法基于编号做合规判断
- 未来扩展受阻：新增治理目录无可用编号段

---

## 二、设计目标

1. **唯一性**：每个编号前缀对应且仅对应一个目录
2. **两维分离**：治理/基础设施与业务内容用不同号段，互不干扰
3. **可读性**：看编号即知所属"门类"
4. **最小搬迁**：优先通过改名而非合并，降低 Change Propagation 成本
5. **向后兼容**：废弃旧名须在规则文件中保留废弃路径映射 ≥6 个月

---

## 三、新编号方案

### 3.1 号段分配原则

```
00–09  保留给治理/基础设施（cross-cutting，不属于某个 Layer）
10–29  对应系统架构 Layer（每个 Layer 占一个号段）
30+    保留给未来扩展
```

### 3.2 完整编号映射表

| 新编号 | 新目录名 | 原目录名 | 迁移操作 | 原因 | Layer |
|--------|---------|---------|---------|------|-------|
| `00_OVERVIEW` | `00_OVERVIEW` | `00_OVERVIEW` | **保留不动** | 无冲突 | cross |
| `01_GOVERNANCE` | `01_GOVERNANCE` | `01_GOVERNANCE` | **保留不动** | 治理域优先占 `01_` | cross |
| `02_ARCHITECTURE` | `02_ARCHITECTURE` | `02_ARCHITECTURE` | **保留不动** | 架构文档 | cross |
| `03_BLUEPRINTS` | `03_BLUEPRINTS` | `03_BLUEPRINTS` | **保留不动** | 蓝图目标结构 | cross |
| `04_CONSTRUCTION` | `04_CONSTRUCTION` | `04_CONSTRUCTION` | **保留不动** | 施工计划 | cross |
| `05_IMPLEMENTATION` | `05_IMPLEMENTATION` | `05_IMPLEMENTATION` | **保留不动** | 实施层 | cross |
| `06_RESOURCES` | `06_RESOURCES` | `00_RESOURCES` | **重命名** | `00_` 段改为 `06_`，为治理域后续扩展让路 | cross |
| `07_KNOWLEDGE` | `07_KNOWLEDGE` | `08_KNOWLEDGE` | **重命名** | 知识库移到 `07_`，释放 `08_` 段 | cross |
| `08_AUDIT` | `08_AUDIT` | `09_AUDIT` | **重命名** | 审计中枢标准化到 `08_`（核心治理域） | cross |
| `09_STRATEGIC_DECISION` | `09_STRATEGIC_DECISION` | `11_STRATEGIC_DECISION` | **重命名** | L11 决策层移到 `09_`（治理域末位）| cross/L11 |
| `10_FACTOR_LIBRARY` | `10_FACTOR_LIBRARY` | `02_FACTOR_LIBRARY` | **重命名** | 进入业务内容段，对齐 L10 号段起点 | **L02** |
| `11_BLUEPRINTS_ACTIVE` | `11_BLUEPRINTS_ACTIVE` | `01_FRAMEWORK` | **重命名** | 蓝图主库，从 `01_` 移到内容段 `11_` | cross |
| `12_MODULE_DESIGNS` | `12_MODULE_DESIGNS` | `12_MODULE_DESIGNS` | **保留不动** | 无冲突 | cross |
| `15_TRADING_TACTICS` | `15_TRADING_TACTICS` | `03_TRADING_TACTICS` | **重命名** | L05 策略，进入 `15_` 段 | **L05** |
| `16_EXECUTION` | `16_EXECUTION` | `04_EXECUTION` | **重命名** | L06 执行层 | **L06** |
| `17_AI_REPORTING` | `17_AI_REPORTING` | `07_AI_REPORTING` | **重命名** | L07 AI 报告层 | **L07** |
| `17_AI_WORKFLOW` | `17_AI_WORKFLOW` | `10_AI_WORKFLOW` | **重命名** | L07+L03 AI 工作流，与 AI_REPORTING 同段 | **L07** |
| `18_HUMAN_AI_INTERFACE` | `18_HUMAN_AI_INTERFACE` | `08_HUMAN_AI_INTERFACE` | **重命名** | L08 人机接口层 | **L08** |
| `19_RESEARCH` | `19_RESEARCH` | `07_RESEARCH` | **重命名** | L09 研究层 | **L09** |
| `20_GOVERNANCE_COMPLIANCE` | `20_GOVERNANCE_COMPLIANCE` | `10_GOVERNANCE_COMPLIANCE` | **重命名** | L10 合规层 | **L10** |

> **注**：已 deprecated 且从磁盘删除的目录（`06_CONSTRUCTION_DOCS`、`07_GOVERNANCE_COMPLIANCE`、
> `08_ARCHIVED_BACKUP_*`、`08_KNOWLEDGE_BASE`、`11_Sentiment_Analysis`）不参与重命名，
> 仅在废弃路径表中补充映射记录即可。

### 3.3 方案可视化

```
docs/
├── 00_OVERVIEW/         ← 全库导航（保留）
├── 01_GOVERNANCE/       ← 治理标准（保留）
├── 02_ARCHITECTURE/     ← 架构文档（保留）
├── 03_BLUEPRINTS/       ← 蓝图目标结构（保留）
├── 04_CONSTRUCTION/     ← 施工计划（保留）
├── 05_IMPLEMENTATION/   ← 实施（保留）
├── 06_RESOURCES/        ← 共享资源（原 00_RESOURCES）
├── 07_KNOWLEDGE/        ← 知识库（原 08_KNOWLEDGE）
├── 08_AUDIT/            ← 审计体系（原 09_AUDIT）★ 最大改动
├── 09_STRATEGIC_DECISION/ ← 战略决策（原 11_STRATEGIC_DECISION）
│
│   [业务内容段：10–29 对应 Layer]
│
├── 10_FACTOR_LIBRARY/   ← L02 因子库（原 02_FACTOR_LIBRARY）
├── 11_BLUEPRINTS_ACTIVE/ ← 蓝图主库（原 01_FRAMEWORK）
├── 12_MODULE_DESIGNS/   ← 模块设计（保留）
├── 15_TRADING_TACTICS/  ← L05 策略（原 03_TRADING_TACTICS）
├── 16_EXECUTION/        ← L06 执行（原 04_EXECUTION）
├── 17_AI_REPORTING/     ← L07 AI报告（原 07_AI_REPORTING）
├── 17_AI_WORKFLOW/      ← L07+L03 工作流（原 10_AI_WORKFLOW）
├── 18_HUMAN_AI_INTERFACE/ ← L08 人机（原 08_HUMAN_AI_INTERFACE）
├── 19_RESEARCH/         ← L09 研究（原 07_RESEARCH）
└── 20_GOVERNANCE_COMPLIANCE/ ← L10 合规（原 10_GOVERNANCE_COMPLIANCE）
```

---

## 四、迁移计划

### 4.1 前置条件（Phase 0 — 执行前必须完成）

- [ ] 本方案经用户明确确认（状态升级为 APPROVED）
- [ ] `subsystem-registry.yaml` 完成新编号预登记（status: planned_rename）
- [ ] `.cursor/rules/project-conventions.mdc` 废弃路径表预写入旧→新映射
- [ ] 确认当前无 open PR 涉及被重命名目录
- [ ] 执行 `git status` 确认工作区干净

### 4.2 执行顺序（Phase 1 — 低风险优先）

按搬迁成本从低到高排序，**每步单独 commit，commit message 格式**：

```
moved: docs/OLD_NAME -> docs/NEW_NAME | reason: 目录编号重设计 dir-numbering-v1
```

**批次 A（几乎无内链，影响最小）**

| 步骤 | 操作 | 说明 |
|------|------|------|
| A1 | `00_RESOURCES` → `06_RESOURCES` | 小目录，6 个文件 |
| A2 | `12_MODULE_DESIGNS` 保留 | 无操作 |
| A3 | `07_RESEARCH` → `19_RESEARCH` | 16 个文件 |
| A4 | `07_AI_REPORTING` → `17_AI_REPORTING` | ~8 个文件 |

**批次 B（中等影响，有少量内链）**

| 步骤 | 操作 | 说明 |
|------|------|------|
| B1 | `10_AI_WORKFLOW` → `17_AI_WORKFLOW` | ~45 个文件 |
| B2 | `10_GOVERNANCE_COMPLIANCE` → `20_GOVERNANCE_COMPLIANCE` | ~21 个文件 |
| B3 | `11_STRATEGIC_DECISION` → `09_STRATEGIC_DECISION` | ~57 个文件 |
| B4 | `03_TRADING_TACTICS` → `15_TRADING_TACTICS` | ~64 个文件 |
| B5 | `04_EXECUTION` → `16_EXECUTION` | ~40 个文件 |

**批次 C（高影响，需全库链接修复）**

| 步骤 | 操作 | 说明 |
|------|------|------|
| C1 | `02_FACTOR_LIBRARY` → `10_FACTOR_LIBRARY` | ~175 个文件，大量内链 |
| C2 | `08_HUMAN_AI_INTERFACE` → `18_HUMAN_AI_INTERFACE` | ~156 个文件 |
| C3 | `08_KNOWLEDGE` → `07_KNOWLEDGE` | ~13 个文件 |
| C4 | `09_AUDIT` → `08_AUDIT` | **~1172 个文件** ⚠️ 最大单步 |
| C5 | `01_FRAMEWORK` → `11_BLUEPRINTS_ACTIVE` | ~332 个文件，蓝图主库 |

### 4.3 每步迁移后的必要操作

1. 运行 `python scripts/governance/trace_file_provenance.py <new_path>` 确认 git 追踪
2. 更新 `docs/subsystem-registry.yaml` 中对应条目的 `canonical_path` 和 `file_count`
3. 更新 `.cursor/rules/project-conventions.mdc` 废弃路径表（旧路径 → 新路径）
4. 运行 `python scripts/hooks/check_index_links.py`（检查索引死链）
5. 运行 `python scripts/ci_audit/link_checker.py` 检查全局内链
6. 更新 `docs/SITEMAP.md`

### 4.4 批次 C4（`09_AUDIT → 08_AUDIT`）特殊处置

这是影响最大的单步。在执行 C4 前额外要求：

- 更新所有在 `.cursor/rules/` 和 `project-conventions.mdc` 中对 `09_AUDIT/` 的引用
- 更新 `governance-asset-inventory.yaml` 中所有 `09_AUDIT` 路径引用
- 更新所有 `scripts/audit/`、`scripts/ci_audit/`、`scripts/governance/` 脚本中硬编码的 `09_AUDIT` 路径
- 更新 `.github/workflows/` 中所有 `09_AUDIT` 路径引用
- **建议**：C4 单独作为一个 PR，包含完整的路径替换脚本并在 CI 通过后合并

---

## 五、决策记录

### 5.1 重大决策

| 决策 | 选项A（采用） | 选项B（放弃） | 理由 |
|------|------------|------------|------|
| 治理域号段 | `00–09`（保留/接近现有） | 高位号段（`80–89`） | 治理文档是每次 AI 会话的"必读"入口，低号段在目录排序中更靠前，一眼可见 |
| 业务内容段起点 | `10`（与 Layer 编号对齐） | `20`（与 Layer 错开） | `10_` 对应 Layer 序号，认知负担最低 |
| `09_AUDIT` 迁移 | 改名为 `08_AUDIT` | 保持 `09_AUDIT` | `09_` 在新方案中保留给战略决策，若不改则仍有冲突 |
| `01_FRAMEWORK` 改名 | `11_BLUEPRINTS_ACTIVE` | 保持原名 | 与 `03_BLUEPRINTS`（目标结构）区分，"ACTIVE"表明它是当前真源 |

### 5.2 保留不动的目录（零迁移成本）

`00_OVERVIEW`、`01_GOVERNANCE`、`02_ARCHITECTURE`、`03_BLUEPRINTS`、`04_CONSTRUCTION`、`05_IMPLEMENTATION`、`12_MODULE_DESIGNS` — 这 7 个目录在新方案中无需改名，覆盖治理域核心，**本次零成本收益最高**。

---

## 六、风险与缓解

| 风险 | 等级 | 缓解措施 |
|------|------|---------|
| 批量重命名导致大量链接失效 | 高 | 分批执行（A→B→C），每批后运行链接检查才继续 |
| AI 会话引用旧路径 | 中 | `.cursor/rules/` 废弃路径表同步维护 |
| `09_AUDIT → 08_AUDIT` 影响脚本硬编码 | 高 | C4 单独 PR + 专门路径替换脚本 |
| 迁移期间两个名字共存导致混淆 | 中 | 迁移期在旧目录保留 `MOVED.md` 指针文件（72 小时后删除） |

---

## 七、本方案不执行的内容

以下在本次重设计**范围之外**（避免范围蔓延）：

- 合并 `17_AI_REPORTING` 与 `17_AI_WORKFLOW`（同号段，Phase D 再议）
- 拆分 `05_IMPLEMENTATION` 中的混杂内容
- 迁移 `docs/01_FRAMEWORK` 蓝图到 `docs/03_BLUEPRINTS` 的子目录（Phase D）

---

## 八、下一步行动

1. **用户决策**：对方案进行审阅，批注意见，输出 APPROVED 或 MODIFIED 状态
2. **方案批准后**：升级 `status` 为 APPROVED，将本文路径写入 `TECH_DECISION_RECORDS.md`
3. **执行批次 A**（最低风险入手，建立执行信心）：T0，Composer 2，无需 Thinking
4. **执行批次 B**：T1，Gemini 2.5 Flash，批量路径替换
5. **执行批次 C1–C3**：T1，Gemini 2.5 Flash，含链接修复
6. **执行批次 C4（09_AUDIT 单独 PR）**：T1 + T3 审查，最大风险步骤
7. **执行批次 C5**：T1，蓝图主库重命名

---

## 变更历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-04-16 | 初始设计，Proposed 状态 |
