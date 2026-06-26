---
module_id: KE-WORKING-ttl_rca_report
title: "ttl 字段全量缺失根因调研报告 + 裁定 + 治本施工方案"
category: investigation_report
status: active
version: "1.0.0"
created: "2026-06-26"
updated: "2026-06-26"
owner: ZephyrAlpha-Owner
doc_type: report
ttl: task_bound
---

# ttl 字段全量缺失根因调研报告

> **报告性质**：过程性调研文档（ttl=task_bound），任务完成即归档
> **调研范围**：全项目 `.md` 文件 ttl 字段合规性
> **调研时间**：2026-06-26
> **调研方法**：全量静态扫描 + 真源代码核实 + 业界实践对标 + 100% AI 开发场景适配分析

---

## 一、执行摘要（Executive Summary）

GATE-15（frontmatter ttl 校验门禁）全量扫描发现 **4821 个 `.md` 文件缺失 ttl 字段**，占全项目带 frontmatter 文档的 **94.5%**（4821/5104）。这是一次**系统性注入缺口**，而非个别文件疏漏——病根在于多个文档生成入口（bootstrap 引擎、ingest 门禁、index 生成器）在创建文件时**统一不注入 ttl 字段**，叠加 GATE-15 长期以增量模式运行导致存量违规从未被扫描。

**核心裁定**：这不是"AI 不遵守规则"的纪律问题，而是**生成器代码层缺陷** + **门禁执行模式缺陷**的双重系统性故障。治本须从代码注入端修复（而非靠 AI 每次"记得加 ttl"），辅以批量回填 + 门禁升级。

---

## 二、数据概览（Data Overview）

> 数据来源：2026-06-26 10:31 全量静态扫描，脚本 `_tmp_ttl_verify.py`（机械可复现）

### 2.1 总量

| 指标 | 数量 | 占比 |
|------|------|------|
| 全项目 `.md` 文件总数 | 5,141 | 100% |
| 有 frontmatter + 有 ttl（合规） | 283 | 5.5% |
| 有 frontmatter + 无 ttl（**违规**） | **4,821** | **93.7%** |
| 无 frontmatter（GATE-15 跳过） | 37 | 0.7% |

### 2.2 违规文件分布（按目录）

| 目录 | 违规数 | 占比 | 性质 |
|------|--------|------|------|
| `docs/08_knowledge/01_raw_intake/` | 3,238 | 67.2% | KB 冷启动引导自动生成 |
| `docs/08_knowledge/04_archived/` | 1,399 | 29.0% | KB 归档（raw_intake 流转） |
| `docs/03_modules/_cross_layer/` | 48 | 1.0% | 蓝图/手工文档 |
| `docs/03_modules/_domain_governance/` | 14 | 0.3% | 蓝图/手工文档 |
| `docs/03_modules/_manifests/` | 13 | 0.3% | index.md 自动生成 |
| `docs/03_modules/` 其他子目录 | ~56 | 1.2% | 混合 |
| `docs/02_enterprise_architecture/` | ~44 | 0.9% | index.md + 手工文档 |
| `docs/01_policies_and_standards/` | ~7 | 0.1% | index.md |
| `docs/09_audit/research_notes/` | 5 | 0.1% | 过程笔记 |
| **合计** | **4,821** | 100% | — |

### 2.3 区位分布

| 区位 | 违规数 | 占比 |
|------|--------|------|
| 永久区（4 条路径） | 4,813 | 99.8% |
| 非永久区 | 8 | 0.2% |

### 2.4 现存 frontmatter 字段频次（5104 个有 frontmatter 的文件）

| 字段 | 出现次数 | 覆盖率 | 说明 |
|------|----------|--------|------|
| `title` | 5,075 | 99.4% | 近乎全覆盖 |
| `module_id` | 4,956 | 97.1% | 近乎全覆盖 |
| `category` | 4,626 | 90.6% | KB 文件必备 |
| `status` | 2,249 | 44.1% | 部分文档有 |
| `doc_type` | 393 | 7.7% | 少数文档有 |
| `version` | 372 | 7.3% | 少数文档有 |
| **`ttl`** | **283** | **5.5%** | **极度稀疏** |

**关键观察**：`title`/`module_id`/`category` 覆盖率 90%+，而 `ttl` 仅 5.5%——三个高频字段均由生成器统一注入，`ttl` 从未被任何生成器注入。这印证了"系统性注入缺口"而非"个别疏漏"的判断。

---

## 三、根因分析（Root Cause Analysis）

> 调研方法：逐一核实每个文档生成入口的代码真源（`<脚本> --help` / 直读源码），不采信上一轮 AI 结论。

### 3.1 病根一：bootstrap.py 创建时注入缺口（影响 4,637 文件，占 96.2%）

**真源代码**：[`bootstrap.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/kb/bootstrap.py#L313-L323) L313-323

```python
def _build_frontmatter_text(self, ke_id: str, chunk: BootstrapChunk) -> str:
    head = chunk.heading.strip() or ke_id
    return (
        f"---\n"
        f"module_id: {ke_id}\n"
        f"title: {head[:80]}\n"
        f"category: {chunk.category}\n"   # ← 只写 3 字段，无 ttl
        f"---\n\n"
        f"# {head}\n\n"
        f"{chunk.content[:4000]}\n"
    )
```

**影响范围**：KB 冷启动引导引擎从存量文档自动生成 KE（Knowledge Element）文件，全部写入 `docs/08_knowledge/01_raw_intake/`，流转后到 `04_archived/`。3238 + 1399 = 4637 个文件，占违规总量 96.2%。

**病根定性**：**生成器代码缺陷**。bootstrap 作为自动化批量生成入口，其模板硬编码了 3 个字段，从一开始就没把 ttl 纳入。这不是"AI 忘了加"，而是"生成器不生产这个字段"。

### 3.2 病根二：ingest.py 门禁字段清单不含 ttl

**真源代码**：[`ingest.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/kb/ingest.py#L63) L63

```python
REQUIRED_FRONTMATTER_FIELDS = ["module_id", "title", "category"]  # 无 ttl
```

**影响范围**：IngestGate 是 KB 系统的入库门禁，它校验必填字段但不要求 ttl。这意味着即使手工/AI 摄入文档，也不会被强制要求 ttl。

**病根定性**：**门禁清单缺陷**。与 bootstrap 形成双重缺口——生成器不注入 + 门禁不校验 = ttl 在 KB 系统中完全无约束。

### 3.3 病根三：generate_missing_index_md.py 索引生成器不注入 ttl

**真源代码**：[`generate_missing_index_md.py`](file:///d:/ZephyrAlpha/scripts/governance/d1_structure/generate_missing_index_md.py#L59-L69) L59-69

```python
INDEX_TEMPLATE = (
    "---\n"
    "doc_type: index\n"
    "status: active\n"
    'title: "{dir_name} — 目录索引"\n'
    'module_id: "{module_id}"\n'
    'blueprint_id: "{blueprint_id}"\n'
    'version: "{version}"\n'
    'created: "{today}"\n'
    'updated: "{today}"\n'   # ← 8 字段，无 ttl
    "---\n\n"
    ...
)
```

**影响范围**：该脚本自动为每个缺少 index.md 的目录生成索引文件，遍布 `docs/01_policies_and_standards/_registry/index.md`、`docs/02_enterprise_architecture/index.md`、`docs/03_modules/specs/index.md` 等数十个 index.md。

**病根定性**：**第三个生成器注入缺口**。index 生成器模板有 8 个字段但无 ttl，导致自动生成的索引文件全部违规。

### 3.4 病根四：GATE-15 长期增量模式，存量违规从未被扫描

**真源代码**：[`.pre-commit-config.yaml`](file:///d:/ZephyrAlpha/.pre-commit-config.yaml) GATE-15 配置段 + [`check_frontmatter_metadata.py`](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_frontmatter_metadata.py#L82-L84) L82-84

**配置**：
```yaml
- id: check-frontmatter-metadata
  name: GATE-15 (Frontmatter ttl)
  entry: python scripts/governance/d3_metadata/check_frontmatter_metadata.py
  language: system
  files: ^docs/.*\.md$
  pass_filenames: true   # ← 增量模式：只校验 staged 文件
```

**校验逻辑**（L82-84）：
```python
# 无 frontmatter 的文档跳过（不校验 ttl）
if not metadata:
    return issues
```

**病根定性**：**门禁执行模式缺陷**。`pass_filenames: true` 意味着 GATE-15 只在校验"本次 commit 涉及的文件"时触发。4821 个存量违规文件如果不被再次修改并 commit，永远不会被 GATE-15 扫描到。增量门禁防增量违规，不治存量违规——这是 pre-commit 钩子的固有特性，但项目未配套全量扫描机制。

### 3.5 病根五：GitCommitGateway 用 --no-verify 绕过 pre-commit

**真源代码**：[`git_commit_gateway.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) commit 方法

GitCommitGateway 为实现"串行化 + stash 隔离"治本方案，在 `git commit` 时使用 `--no-verify` 跳过 pre-commit 钩子。这是幽灵提交治本的必要妥协（pre-commit stash 冲突是幽灵提交的根因之一），但副作用是 GATE-15 对通过 Gateway 提交的文件完全失效。

**病根定性**：**架构权衡的副作用**。Ghost-commit 治本与 GATE-15 增量校验存在执行路径冲突——Gateway 绕过 pre-commit 是有意的，但项目未在 Gateway 内部补回 GATE-15 等效校验。

### 3.6 病根六：配置文件虚假声明

**真源代码**：[`.pre-commit-config.yaml`](file:///d:/ZephyrAlpha/.pre-commit-config.yaml#L30-L32) L30-32

```yaml
#   GATE-15 (Frontmatter ttl)    → ✅ 已转硬阻断（commit 阶段增量校验）
#     依赖: ttl_vocabulary.yaml decision_tree 二元判定树
#     当前违规数: 0（5137 files 全量扫描通过）   ← 虚假声明
```

**实际**：违规数 4821，非 0。5137 是文件总数，"全量扫描通过"是错误声明。

**病根定性**：**认知盲区**。该声明可能源于某次"增量扫描通过"被误记为"全量扫描通过"，或某次手写计数未实际执行全量扫描。这导致 GATE-15 的真实健康状态被长期误判为"已达标"，无人发起存量治理。

### 3.7 病根七：ttl 与 KE 状态机的语义关系未文档化

**真源**：[`kb_repo.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/kb/kb_repo.py) L22-94 KE 10 状态机 vs [`ttl_vocabulary.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml) ttl 二元值

KE 状态机：`DRAFT→SUBMITTED→REVIEWED→ACCEPTED→INDEXED→VERIFIED→DEPRECATED/SUPERSEDED→ARCHIVED`

ttl 是文件级保留策略（permanent/task_bound），KE status 是知识级生命周期。两者**正交**但**未在文档中明确区分**，导致 AI 在创建 KB 文件时容易混淆"KE 状态"与"文件 ttl"——误以为有了 status 就不需要 ttl。

**病根定性**：**文档语义缺口**。非直接病根，但加剧了 AI 在 KB 场景下的 ttl 判定困惑。

---

## 四、业界实践对标（Industry Practices Benchmarking）

> 调研方法：Microsoft Purview / ISO 15489 / ARMA International 官方文档 + Superdocu 最佳实践 + Vibe coding 社区（Spec-driven / PEV / AGENTS.md）

### 4.1 专业机构实践（Records Management 流派）

| 实践 | Microsoft Purview | ISO 15489 | ARMA International | 本项目对标 |
|------|-------------------|-----------|---------------------|------------|
| **保留标签从创建时打** | retention labels 在创建/摄入时自动应用 | records management 从记录创建即纳入 | retention schedule 是基础蓝图 | ❌ bootstrap 创建时不注入 ttl |
| **元数据驱动分类** | metadata-driven auto-classification | 元数据是记录管理的核心 | metadata schema 是基础 | △ 有 frontmatter 但 ttl 缺失 |
| **事件触发保留** | event-based retention（创建后也可触发） | 保留期可由事件触发 | — | ❌ 无事件触发机制 |
| **全量+增量双轨** | full scan + incremental change tracking | 定期全量审计 | 定期 records audit | ❌ 仅增量，无全量扫描 |
| **门禁自动化** | policy enforcement at ingestion | records 入库即校验 | — | △ GATE-15 有门禁但被 --no-verify 绕过 |

**核心结论**：所有专业机构的共同铁律是 **"保留策略从创建时打标"（label-at-creation）**——Microsoft Purview 用 auto-apply policies，ISO 15489 要求 records 从创建即纳入管理，ARMA 把 retention schedule 作为基础蓝图。本项目的 bootstrap/ingest/index 生成器**全部违背**了这条铁律：在创建文件时不注入 ttl，事后靠门禁补——而门禁又是增量模式，等于不补。

### 4.2 量化社区实践（Vibe Coding 流派）

| 实践 | Spec-driven dev | PEV 循环 | AGENTS.md as context | Documentation as code | 本项目对标 |
|------|-----------------|----------|----------------------|----------------------|------------|
| **规格先行** | 先写 spec 再写码 | Plan→Execute→Verify | — | — | ✅ 有 ttl_vocabulary.yaml 规格真源 |
| **文档即代码** | — | — | — | frontmatter = metadata | ✅ frontmatter 体系完善 |
| **上下文引擎** | — | — | AGENTS.md 注入每个对话 | — | ✅ AGENTS.md 已声明 ttl 必填 |
| **可机器解析** | spec 可解析 | — | — | frontmatter 可解析 | ✅ check_frontmatter_metadata.py 可解析 |
| **创建时注入** | spec 定义后代码自动引用 | — | — | generator 注入 metadata | ❌ 生成器不注入 ttl |
| **全量验证** | spec 变更后全量回归 | Verify 阶段全量 | — | — | ❌ 无全量验证 |
| **防漂移** | spec 是 SSoT | — | — | generator 是 SSoT | △ ttl_vocabulary 是 SSoT 但生成器不消费它 |

**核心结论**：Vibe coding 社区的核心铁律是 **"generator 必须消费 spec"**——spec 是真源，generator 必须从 spec 读取字段并注入。本项目 `ttl_vocabulary.yaml` 是 ttl 真源，但 bootstrap/ingest/index 三个生成器**都不消费它**，硬编码了自己的字段清单——这是典型的"spec 与 generator 脱节"，正是 vibe coding 社区反复强调要避免的反模式。

### 4.3 业界共识量化

综合专业机构 + 量化社区，可提炼 **5 条业界共识**：

| # | 共识 | 专业机构依据 | 社区依据 | 本项目符合度 |
|---|------|-------------|----------|-------------|
| C1 | 保留策略从创建时打标 | ISO 15489 / Purview | Documentation as code | ❌ 不符合 |
| C2 | 生成器必须消费 spec | ARMA retention schedule | Spec-driven dev | ❌ 不符合 |
| C3 | 全量+增量双轨审计 | Purview full+incremental | PEV Verify 全量 | ❌ 仅增量 |
| C4 | 门禁不可被绕过 | ISO 15489 policy enforcement | AGENTS.md context | △ 被 --no-verify 绕过 |
| C5 | 元数据与生命周期正交但需文档化 | Purview retention vs lifecycle | — | ❌ 未文档化 |

**符合度：0/5（C4 半符合）**。这是一次彻底的系统性偏离，不是个别环节疏漏。

---

## 五、100% AI 开发场景的特殊考量

> 本项目 100% 由 AI 开发（见 AGENTS.md "三层 AI 工作分配"），这一语境对 ttl 治理有 3 个特殊约束：

### 5.1 AI 不能靠"自觉"——必须靠"代码强制"

人类开发者可以靠"code review 时记得检查 ttl"，但 100% AI 开发中：
- AI 会"忘记"加 ttl（尤其在长任务中注意力分散）
- AI 会"误判" ttl（KE status 与 ttl 语义混淆时）
- AI 会"绕过"门禁（--no-verify 是合法操作）

**结论**：治本方案必须从**代码注入端**强制，不能依赖 AI 自觉。业界 C1（label-at-creation）在 AI 场景下是硬约束，不是 best practice。

### 5.2 AI 生成量大——必须靠"生成器"而非"手工"

bootstrap 一次冷启动生成 4637 个 KE 文件——人类不可能手工逐个加 ttl。100% AI 开发中，文档生产高度依赖生成器（bootstrap / index generator / ingest pipeline），治本必须在生成器层修复。

### 5.3 AI 会复现错误——必须靠"spec 真源"阻断

如果生成器硬编码字段清单（而非从 spec 读取），AI 在维护生成器时会"复现"同样的遗漏（因为 AI 看不到 spec 与 generator 的脱节）。治本必须让生成器**动态消费 `ttl_vocabulary.yaml`**，而非硬编码。

---

## 六、分析过程（Analysis Process）

### 6.1 诊断反转验证（MTH-006）

按项目方法论 [`trae_024_methodology_diagnosis.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_024_methodology_diagnosis.yaml) MTH-006 要求，深挖后回溯初始诊断：

**初始诊断（表面）**：4821 个文件缺 ttl → "AI 不遵守 ttl 必填规则"

**回溯验证**：
- 若是"AI 不遵守"，则违规文件应分散在各目录、各生成路径——但实际 96.2% 集中在 08_knowledge/，由 bootstrap 统一生成。→ **推翻"AI 不遵守"**
- 若是"AI 不遵守"，则 frontmatter 应有 ttl 但被 AI 删除——但实际是从未注入（生成器模板无 ttl 字段）。→ **二次推翻**

**修正诊断（深层）**：病根是**生成器代码层注入缺口** + **门禁执行模式缺陷**，而非 AI 纪律问题。

### 6.2 5-Why 根因链

```
现象：4821 个 .md 文件缺 ttl 字段
  ↓ Why 1：为什么缺 ttl？→ 因为生成器不注入 ttl
    ↓ Why 2：为什么生成器不注入？→ bootstrap/ingest/index 三个生成器硬编码字段清单，不含 ttl
      ↓ Why 3：为什么硬编码不含 ttl？→ ttl_vocabulary.yaml 是真源，但生成器不消费它
        ↓ Why 4：为什么不消费真源？→ 缺少"生成器必须从 spec 动态读取字段"的架构约束
          ↓ Why 5：为什么存量违规未被发现？→ GATE-15 增量模式 + 配置虚假声明"违规数:0"
```

**根因终点**：架构层缺少"生成器必须消费 spec"约束 + 门禁层缺少"全量审计"机制 + 认知层有"虚假达标"盲区。

### 6.3 三层缺口模型

| 层次 | 缺口 | 业界对标 | 影响 |
|------|------|----------|------|
| **L1 创建层** | 3 个生成器不注入 ttl | ISO 15489 label-at-creation | 4821 文件从源头违规 |
| **L2 执行层** | GATE-15 增量 + Gateway --no-verify | Purview full+incremental | 存量违规永不暴露 |
| **L3 认知层** | 配置虚假声明"违规数:0" | — | 治理盲区，无人发起治理 |

---

## 七、裁定结果（Verdict）

> 作为客观专业架构师，基于上述数据、真源核实、业界对标、100% AI 场景分析，作出以下裁定：

### 裁定 1：病根定性——系统性代码缺陷，非纪律问题

4821 文件缺 ttl 的根因是**生成器代码层缺陷**（3 个生成器不注入 ttl）+ **门禁执行模式缺陷**（增量 + 绕过）+ **认知盲区**（虚假声明），**不是** AI 纪律问题。任何"要求 AI 以后记得加 ttl"的方案都治标不治本。

### 裁定 2：治本原则——代码注入端优先，门禁兜底

按业界 C1（label-at-creation）铁律，治本必须优先修复生成器注入端，而非靠门禁事后补。门禁是兜底机制，不是主机制。具体：
- **L1 创建层**：bootstrap / ingest / index 三个生成器必须注入 ttl（硬约束）
- **L2 执行层**：GATE-15 补全量扫描机制 + Gateway 内补 GATE-15 等效校验
- **L3 认知层**：修正配置虚假声明

### 裁定 3：生成器必须消费 spec，不得硬编码字段清单

按业界 C2（generator must consume spec）铁律，生成器的字段清单必须从 `ttl_vocabulary.yaml` 动态读取合法值，不得硬编码——否则 AI 在维护生成器时会复现同样的脱节。这是 100% AI 开发场景下的硬约束。

### 裁定 4：ttl 与 KE status 正交，须文档化

按业界 C5 共识，ttl（文件级保留策略）与 KE status（知识级生命周期）是正交概念，必须在 [`ttl_vocabulary.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml) 或 KB blueprint 中明确文档化，消除 AI 判定困惑。

### 裁定 5：存量回填可机械化批量执行

4821 个违规文件中 4813 个在永久区（按 decision_tree 应为 `permanent`），8 个在非永久区（应为 `task_bound`）。回填规则机械可判定，可批量脚本执行，无需逐文件人工审查。但回填前须先修生成器，否则修完又被新文件污染。

### 裁定 6：施工分 4 阶段，不可跳序

```
阶段 1：修生成器注入端（止血）  ← 不修则边修边漏
阶段 2：批量回填存量（治标）    ← 4821 文件机械化回填
阶段 3：修门禁执行模式（治本）  ← 全量扫描 + Gateway 等效校验
阶段 4：文档化语义关系（防漂移）← ttl vs KE status 正交文档化
```

---

## 八、治本施工方案（Root-cause Implementation Plan）

> 按"先止血→再治标→后治本→防漂移"顺序，每阶段含验证命令 + 回滚预案。

### 阶段 1：修生成器注入端（止血）

**目标**：3 个生成器创建文件时注入 ttl，阻断新增违规。

#### 1.1 修 bootstrap.py

**文件**：[`bootstrap.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/kb/bootstrap.py#L313-L323)

**改动**：`_build_frontmatter_text()` 注入 ttl 字段。KE 文件全部落在 `docs/08_knowledge/`（永久区），故 ttl 恒为 `permanent`。

```python
def _build_frontmatter_text(self, ke_id: str, chunk: BootstrapChunk) -> str:
    head = chunk.heading.strip() or ke_id
    return (
        f"---\n"
        f"module_id: {ke_id}\n"
        f"title: {head[:80]}\n"
        f"category: {chunk.category}\n"
        f"ttl: permanent\n"          # ← 新增：KE 落 08_knowledge/ 永久区
        f"---\n\n"
        f"# {head}\n\n"
        f"{chunk.content[:4000]}\n"
    )
```

**验证**：
```bash
python -m pytest tests/test_kb_bootstrap.py -k frontmatter -v
```

**回滚**：git revert。

#### 1.2 修 ingest.py

**文件**：[`ingest.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/kb/ingest.py#L63)

**改动**：`REQUIRED_FRONTMATTER_FIELDS` 加入 `ttl`。

```python
REQUIRED_FRONTMATTER_FIELDS = ["module_id", "title", "category", "ttl"]
```

**验证**：
```bash
python -m pytest tests/test_kb_ingest.py -v
```

**注意**：此改动会使存量无 ttl 的入库文件被门禁拒——故须在阶段 2 回填后启用，或先 warn-only。

#### 1.3 修 generate_missing_index_md.py

**文件**：[`generate_missing_index_md.py`](file:///d:/ZephyrAlpha/scripts/governance/d1_structure/generate_missing_index_md.py#L59-L69)

**改动**：`INDEX_TEMPLATE` 注入 ttl。index.md 落点取决于父目录区位——但为简化，可在模板留 `ttl: {ttl}` 占位，由调用方按 decision_tree 判定填入。鉴于 index.md 落点多样，更稳妥的做法是生成时按路径判定：

```python
def _infer_ttl(rel_path: str) -> str:
    """按 ttl_vocabulary.yaml decision_tree 判定 ttl。"""
    permanent_prefixes = (
        "docs/01_policies_and_standards/",
        "docs/02_enterprise_architecture/",
        "docs/03_modules/",
        "docs/08_knowledge/",
    )
    if any(rel_path.startswith(p) for p in permanent_prefixes):
        return "permanent"
    return "task_bound"
```

并在模板中注入 `f"ttl: {ttl}\n"`。

**验证**：
```bash
python scripts/governance/d1_structure/generate_missing_index_md.py --dry-run
```

---

### 阶段 2：批量回填存量（治标）

**目标**：4821 个存量违规文件机械化回填 ttl。

#### 2.1 编写批量回填脚本

**新增脚本**：`scripts/governance/d3_metadata/backfill_ttl_metadata.py`

**逻辑**：
1. 扫描 `docs/**/*.md`
2. 对每个有 frontmatter 但无 ttl 的文件：
   - 按路径判定 ttl（永久区 → `permanent`；否则 → `task_bound`）
   - 在 frontmatter 末尾（`---` 前）插入 `ttl: <value>\n`
3. 原子写入（RULE-ONE 并发安全：tmp + os.replace）
4. 输出统计报告

**核心代码骨架**：
```python
def backfill_file(fpath: Path, project_root: Path) -> bool:
    text = fpath.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return False  # 无 frontmatter，跳过
    fm = m.group(1)
    if re.search(r"^ttl\s*:", fm, re.MULTILINE):
        return False  # 已有 ttl，跳过
    rel = str(fpath.relative_to(project_root)).replace("\\", "/")
    ttl = "permanent" if _is_permanent_zone(rel) else "task_bound"
    # 在 --- 前插入 ttl 行
    new_fm = fm.rstrip() + f"\nttl: {ttl}\n"
    new_text = text[:m.start(1)] + new_fm + text[m.end(1):]
    # 原子写入
    _atomic_write(fpath, new_text)
    return True
```

**判定口径**：与 `ttl_vocabulary.yaml` decision_tree 完全一致——永久区 4 路径 → permanent；否则 → task_bound。

#### 2.2 分批执行

| 批次 | 范围 | 数量 | 预估 |
|------|------|------|------|
| Batch 1 | `docs/08_knowledge/01_raw_intake/` | 3,238 | 最大批 |
| Batch 2 | `docs/08_knowledge/04_archived/` | 1,399 | — |
| Batch 3 | `docs/03_modules/` 各子目录 | ~110 | — |
| Batch 4 | `docs/01_policies/` + `docs/02_enterprise_architecture/` + 其他 | ~74 | — |

每批执行后跑 GATE-15 全量校验确认该批 0 新违规。

**验证**：
```bash
python scripts/governance/d3_metadata/check_frontmatter_metadata.py --all-files
```

**回滚**：每批 commit 前先 `git stash`，出错 `git stash pop`。

---

### 阶段 3：修门禁执行模式（治本）

**目标**：GATE-15 补全量扫描 + Gateway 内补等效校验，消除执行缺口。

#### 3.1 GATE-15 新增全量扫描模式

**文件**：[`check_frontmatter_metadata.py`](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_frontmatter_metadata.py)

**改动**：新增 `--all-files` flag，全量扫描 `docs/**/*.md`，不依赖 pre-commit 传入的文件列表。

```python
parser.add_argument(
    "--all-files",
    action="store_true",
    help="全量扫描 docs/ 下所有 .md 文件（存量审计用）",
)
```

并在 main() 中：若 `--all-files`，则 `glob("docs/**/*.md")` 替代 `sys.argv` 文件列表。

#### 3.2 新增 CI/定时全量扫描任务

在 `trigger_router.yaml` 或 governance 定时任务中注册：
- 触发：每周一次 / spec 变更后
- 命令：`python scripts/governance/d3_metadata/check_frontmatter_metadata.py --all-files --ci`
- 失败：阻断 release / 告警 Owner

#### 3.3 GitCommitGateway 内补 GATE-15 等效校验

**文件**：[`git_commit_gateway.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py)

**改动**：在 `commit()` 方法中，对 `files` 中的 `.md` 文件，调用 `check_frontmatter_metadata._check_file()` 做等效校验。若违规，返回新的 `CommitStatus.METADATA_VIOLATION`（exit 4）。

这是对 `--no-verify` 副作用的治本——Gateway 绕过 pre-commit，但自身补回元数据校验。

#### 3.4 修正配置虚假声明

**文件**：[`.pre-commit-config.yaml`](file:///d:/ZephyrAlpha/.pre-commit-config.yaml#L30-L32) L30-32

```yaml
#   GATE-15 (Frontmatter ttl)    → ✅ 已转硬阻断（commit 阶段增量校验 + 全量审计）
#     依赖: ttl_vocabulary.yaml decision_tree 二元判定树
#     当前违规数: 4821（存量治理中，阶段 2 回填后归零）
#     全量审计: python scripts/governance/d3_metadata/check_frontmatter_metadata.py --all-files
```

---

### 阶段 4：文档化语义关系（防漂移）

**目标**：明确 ttl 与 KE status 正交关系，消除 AI 判定困惑。

#### 4.1 ttl_vocabulary.yaml 补语义说明

**文件**：[`ttl_vocabulary.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml)

在文件末尾新增：
```yaml
# ── ttl 与 KE status 的正交关系 ──
# ttl（本词表）：文件级保留策略——文件该留多久。
#   permanent = 永久保留（永久区文件）
#   task_bound = 任务绑定（过程性文件，完成即删）
#
# KE status（kb_repo.py 状态机）：知识级生命周期——知识条目处于哪个阶段。
#   DRAFT→SUBMITTED→REVIEWED→ACCEPTED→INDEXED→VERIFIED→DEPRECATED→SUPERSEDED→ARCHIVED
#
# 两者正交：
#   - 一个 KE 文件 ttl=permanent（文件永久留），但 KE status=ARCHIVED（知识已归档）
#   - 即：文件保留与知识生命周期是两个独立维度，不可互相替代
#   - 文件即使 KE status=ARCHIVED，文件本身 ttl=permanent 仍永久保留（供审计追溯）
```

#### 4.2 KB blueprint 补 ttl 必填说明

**文件**：[`blueprint.md`](file:///d:/ZephyrAlpha/docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md) §4.2

补充：KE 文件 frontmatter 必填 `ttl` 字段，由 bootstrap 注入，恒为 `permanent`（因 KE 落 08_knowledge/ 永久区）。

---

## 九、施工顺序与依赖

```
阶段 1（止血）─ 修生成器 ─┐
                         ├─→ 阶段 2（回填）─ 批量回填 4821 ─┐
                         │                                   ├─→ 阶段 3（治本）─ 修门禁 ─┐
                         │                                   │                           ├─→ 阶段 4（防漂移）─ 文档化
                         └───────────────────────────────────┘                           │
                                                                                         ↓
                                                                                     验证 + 2 轮零违规
```

**不可跳序原因**：
- 跳阶段 1 直接回填 → 新文件继续违规，边修边漏
- 跳阶段 2 直接修门禁 → 4821 存量违规触发全量阻断，无法 commit 回填
- 跳阶段 3 → 存量回填后无全量审计，无法发现新漂移
- 跳阶段 4 → AI 仍会混淆 ttl 与 KE status，复现错误

---

## 十、验证标准（Definition of Done）

按项目"两轮零违规"质控标准（user_profile.md）：

| 轮次 | 命令 | 期望 |
|------|------|------|
| 第 1 轮 | `python scripts/governance/d3_metadata/check_frontmatter_metadata.py --all-files` | 0 违规 |
| 第 2 轮 | 同上（重新跑确认） | 0 违规 |

**附加验证**：
- bootstrap 新生成 KE 文件含 ttl → `python -c "from zephyr.governance.kb.bootstrap import *"` + 抽样
- ingest 拒绝无 ttl 文件 → 单测
- index.md 新生成含 ttl → `generate_missing_index_md.py --dry-run` 抽样
- Gateway 等效校验生效 → 单测 `test_git_commit_gateway.py::test_metadata_violation`

---

## 十一、风险评估

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| 批量回填误改 frontmatter 结构 | 中 | 高 | 原子写入 + 每批后 GATE-15 全量校验 + git stash 回滚 |
| ingest 加 ttl 必填后阻断存量入库 | 高 | 中 | 阶段 2 回填后再启用，或先 warn-only |
| Gateway 等效校验增加 commit 耗时 | 低 | 低 | 仅对 .md 文件校验，非全量 |
| AI 在维护生成器时再次脱节 | 中 | 高 | 阶段 4 文档化 + 生成器动态消费 spec |

---

## 十二、结论

4821 文件缺 ttl 是一次**三层系统性故障**：

- **L1 创建层**：3 个生成器（bootstrap / ingest / index）违背业界"label-at-creation"铁律，创建时不注入 ttl
- **L2 执行层**：GATE-15 增量模式 + Gateway --no-verify，存量违规永不暴露
- **L3 认知层**：配置虚假声明"违规数:0"，治理盲区

治本须 4 阶段施工：**修生成器（止血）→ 批量回填（治标）→ 修门禁（治本）→ 文档化（防漂移）**，不可跳序。

核心教训：**100% AI 开发场景下，元数据注入必须在生成器代码层强制，不能靠 AI 自觉或事后门禁**——这是业界共识，也是本次故障的根本教训。

---

## 附录 A：调研真源文件清单

| 文件 | 作用 | 核实结论 |
|------|------|----------|
| [`bootstrap.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/kb/bootstrap.py#L313-L323) L313-323 | KB 冷启动生成 KE | ✅ 确认不注入 ttl |
| [`ingest.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/kb/ingest.py#L63) L63 | KB 入库门禁 | ✅ 确认 REQUIRED_FIELDS 不含 ttl |
| [`generate_missing_index_md.py`](file:///d:/ZephyrAlpha/scripts/governance/d1_structure/generate_missing_index_md.py#L59-L69) L59-69 | index.md 自动生成 | ✅ 确认模板无 ttl |
| [`check_frontmatter_metadata.py`](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_frontmatter_metadata.py#L82-L84) L82-84 | GATE-15 校验逻辑 | ✅ 确认增量模式 + 跳过无 frontmatter |
| [`.pre-commit-config.yaml`](file:///d:/ZephyrAlpha/.pre-commit-config.yaml#L30-L32) L30-32 | GATE-15 配置 | ✅ 确认 pass_filenames=true + 虚假声明 |
| [`ttl_vocabulary.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml) | ttl 受控词表真源 | ✅ 确认二元 decision_tree |
| [`kb_repo.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/kb/kb_repo.py) L22-94 | KE 10 状态机 | ✅ 确认与 ttl 正交但未文档化 |
| [`git_commit_gateway.py`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) | commit 网关 | ✅ 确认 --no-verify 绕过 pre-commit |

## 附录 B：业界实践参考来源

- Microsoft Purview: retention labels, auto-apply, event-based retention, metadata-driven classification
- ISO 15489: Information and documentation — Records management
- ARMA International: retention schedule as foundational blueprint
- Superdocu: 10 best practices for document retention (label-at-creation, automated management)
- Vibe coding 社区: Spec-driven development, PEV (Plan→Execute→Verify), AGENTS.md as context engine, documentation as code, semantic chunking
