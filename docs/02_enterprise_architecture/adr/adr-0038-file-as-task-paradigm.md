---
module_id: ADR-0038
refines: [ADR-0011]  # ADR-0011 runtime-planes-orthogonal-view \u7684\u7ec6\u5316\u51b3\u7b56
title: File-as-Task 范式（文件即任务最小单元）
doc_type: adr
status: active
version: 1.0.0
layer: L01
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-04-24
superseded_by: null
supersedes: null
related_rationale: R-PHASE2-FILE-AS-TASK, R-SSOT-FILE
related_open_questions: []
tags: [file-as-task, task-system, phase-2, mapping, triage, governance]
summary: Phase 2 采用 File-as-Task 范式——每一个受治理的可交付文件（ADR / 施工图 / KE / 脚本 / 契约 / Blueprint 等）对应 tasks 表中的一个 task_id。文件路径通过 file_task_mapper（T-2-02）从 triage-result.yaml + 路径规则派生 task_id；文件的物理存在、frontmatter、git 历史为该任务的主证据链；tasks 表（ADR-0030）是该映射的索引视图。此范式替代"中心化任务表 + 文件是产物"的旧模型，让 Phase 2 2559 个治理文件的进度可被双向审计。

date: '2026-04-24'
ttl: permanent
---

# ADR-0038：File-as-Task 范式（文件即任务最小单元）

## 1. 状态（Status）

- **当前状态**：`accepted`
- **提议日期**：2026-04-23
- **拍板日期**：2026-04-24
- **决策者**：Claude Opus 4.7（终局裁决）+ Project Owner
- **关联任务**：T-2-01（本 ADR）→ T-2-02（`scripts/infra/file_task_mapper.py`）
- **关联实现**：`scripts/infra/task_repo.py`（ADR-0030）、`docs/09_audit/reports/-triage-result.yaml`（T-1-22 产出）

## 2. 背景与问题（Context）

Phase 2 要把 Phase 1 建好的任务骨架（tasks / events / gates 四张表）与实际治理资产对接。实际情况：

1. **治理资产密度高**：Phase 2 初始盘点 ≈ **2559 个文件**（蓝图 + 施工图 + KE + ADR + 规则 + 脚本），新增速率 ≥ 20 文件/周。
2. **任务粒度问题**：若一个任务覆盖 N 个文件，任务状态无法精确反映某单文件是否已交付；若一个文件对应多个任务，审计时无法确权"谁负责它"。
3. **进度可观测性**：Owner 和下游 AI agent 需要用一句 `SELECT status FROM tasks WHERE task_id = ?` 回答"这份施工图到哪一步了"。
4. **双向审计需求**：
   - 正向：`task_id → file_path`（任务要交付哪个文件）
   - 反向：`file_path → task_id`（这个文件是哪个任务的产出，进度如何）
5. **triage 结果需落地**：T-1-22 产出的 `-triage-result.yaml` 把 ≈ 2559 文件按"保留/改造/归档/删除"四挡分类，Phase 2 必须把这个 YAML 变成可被任务系统调度的任务队列。
6. **CLI / 自动化依赖**：`scripts/cli/report.py`、Sentinel L1 扫描、Session Handoff 都需要一个稳定的 id-空间（task_id 稳定 ≠ 文件路径稳定，因路径可能被重构）。

**关键风险**：若此处的映射范式选错，整个 Phase 2（≈ 40 任务、9-10 人日）与 Phase 3 的 `file_task_mapper` / `knowledge_indexer` / `gate_engine` 调用方式会全部错位，回滚成本 ≥ 3 人日。

## 3. 考虑过的方案（Options Considered）

### 方案 A：中心化任务表 + 文件是产物（旧 Phase 1 模型的直接延伸）

- **思路**：tasks 表为 SSoT，每行任务描述里用自由字符串字段 `deliverable_path` 指向若干文件；文件本身无反向指针。
- **优点**
  - 结构简单，tasks 表自闭环
  - 任务可以不对应文件（例如"跑一次审计"）
- **缺点**
  - ❌ **反向查询困难**：`file_path → task_id` 需要全表扫描 `LIKE '%path%'`
  - ❌ **多文件任务状态模糊**：一个任务声称"产出 30 个施工图"，其中 20 个交付后 task 状态应为？不好定义
  - ❌ **triage YAML 无法直接落库**：必须额外写聚合逻辑把 2559 行压缩成 N 条任务，聚合规则本身成为争议点
  - ❌ **孤儿文件**：存在物理文件但查不到 task_id —— Sentinel L1 断链扫描失效
- **机构案例**：JIRA / Asana 都采用这种模型，但它们服务于「人类团队 + 多样化工作项」，不适合"文件治理为主"的场景

### 方案 B：纯粹 File-as-Task（极端模式：不要 tasks 表）

- **思路**：废除 tasks 表，全部元数据写到文件的 frontmatter 里。
- **优点**
  - 文件自包含，`git` 即历史
- **缺点**
  - ❌ **查询性能崩溃**：`"所有 IN_PROGRESS 状态的 Phase 2 任务"` 需要扫 2559 个 markdown
  - ❌ **状态机破坏**：状态流转需要原子事务，frontmatter 写入不是事务安全
  - ❌ **与 ADR-0030 SQLite 冲突**：Phase 1 已花 5 人日建好任务系统，不能推倒

### 方案 C：双向映射，文件与 tasks 表 1:1 对齐（**本 ADR 选定**）

- **思路**：
  - **规则一（task_id 派生）**：`task_id` 由 `file_task_mapper` 从「文件路径 + triage 分类」派生；同一文件永远映射到同一 task_id
  - **规则二（1:1 约束）**：一个受治理的可交付文件**恰好**对应一个 task_id；一个 task_id 至多对应一个文件（非文件类任务走特殊命名空间 `T-RUN-*`）
  - **规则三（SSoT 分层）**：tasks 表是**索引视图**；文件本身（内容 + frontmatter + git 历史）是**证据链**
  - **规则四（进度语义）**：`file 不存在 ∧ task 存在` = `PENDING`；`file 存在 ∧ frontmatter.status = draft` = `IN_PROGRESS`；`file 存在 ∧ verified` = `VERIFIED`；…
- **优点**
  - ✅ **双向审计**：`task_id ↔ file_path` 常数时间互查
  - ✅ **triage YAML 零成本入库**：2559 行 → 2559 个 task（由 `register_from_triage` 批量注册）
  - ✅ **状态三元一致**：文件磁盘状态 + frontmatter + tasks 表三者可校验，出现不一致即可被 `sync_file_state` 触发告警
  - ✅ **与 ADR-0030 完美兼容**：tasks 表新增 `file_path` 列即可，无需重构
  - ✅ **与 ADR-0041 Handoff 天然对齐**：HandoffPackage 里"接下来要动的文件"直接等价于"接下来要推进的 task"
  - ✅ **Sentinel L1 零成本复用**：差集扫描（文件系统 vs 注册表）的逻辑直接改成（tasks 表 × file_path 列 vs glob）
- **权衡**
  - ⚠ 文件搬迁需要同步更新 tasks.file_path（已有 `moved: old -> new` commit 约定，`file_task_mapper.rollback` 可处理）
  - ⚠ 非文件任务（跑一次扫描、批处理一波 git log）需要走 `T-RUN-*` 命名空间，和 `T-1-*` / `T-2-*` 区分

### 方案 D：面向服务的任务图（Service-Oriented Task DAG）

- **思路**：把 task 建模成 DAG 节点，文件是边（artifact 指针）；用 Airflow / Prefect 编排。
- **优点**
  - 工业级可编排，符合大型团队直觉
- **缺点**
  - ❌ **过度工程**：单人 + AI 协作项目，无需 DAG executor
  - ❌ **引入 Airflow 违反"零运维"**（参照 ADR-0030 同款否决理由）
  - ❌ **与 ADR-0036 Deferred Queue 冲突**：Phase 1 已选择"轻量 SQLite 轮询 + Observer"

## 4. 决策（Decision）

**最终选择：方案 C —— 双向映射、文件与 tasks 表 1:1 对齐。**

### 4.1 命名空间约定

| 命名空间 | 含义 | 文件域 |
|---------|------|-------|
| `T-P-NNN` | Phase P 的第 NNN 个文件类任务（P ∈ {0,1,2,3,4,5}） | 恰好 1 个文件（映射到 `file_path`） |
| `T-RUN-YYYYMMDD-NNN` | 非文件型运行任务（跑审计 / 批处理 git log / 消除流水线一次 session） | 不绑定文件；产出写入 `.audit_cache/` |
| `T-KE-NNN` | 知识条目抽取任务（= Phase C Pipeline 产物） | `docs/08_knowledge/**/ke-NNN-*.md`（Stage G 后小写） |
| `T-BP-NNN` | 蓝图治理任务（= Phase B Pipeline） | `docs/03_blueprints/**/*.md`（Stage D 后小写，老树 `docs/01_FRAMEWORK/` 已并入 `docs/02_enterprise_architecture/`） |

### 4.2 file_path → task_id 映射规则（由 T-2-02 `file_task_mapper.py` 实现）

优先级从高到低：

1. **triage-result.yaml 显式登记**：若 `-triage-result.yaml` 已给出 `task_id`，直接采用
2. **frontmatter 自声明**：若目标文件 frontmatter 有 `task_id: T-x-xxx` 字段，采用之（幂等）
3. **路径模式推导**（fallback）：
   - `docs/02_enterprise_architecture/adr/adr-NNNN-*.md` → `T-ADR-NNNN`（Stage F 后采用 4 位编号 + 小写命名；task_id 只含数字段，与 `T-KE-NNN`/`T-CP-LXX` 同形）
   - `docs/04_construction_plans/construction-plan-lXX-*.md` → `T-CP-LXX`（Stage F 后小写；`derive_task_id` 以 `re.IGNORECASE` 同时兼容老树大写历史路径）
   - `docs/08_knowledge/**/ke-NNN-*.md` → `T-KE-NNN`（Stage G 后小写；`derive_task_id` 以 `re.IGNORECASE` 兼容老路径）
   - `docs/03_modules/l0x_*/*.md` → `T-BP-{hash8(path)}`（Stage D 后小写 kebab-case + 小写 lNN_* 子目录）
   - `scripts/**/*.py` → `T-SCRIPT-{hash8(path)}`
   - 兜底：`T-UNCLASSIFIED-{hash8(path)}`（并写入 `.audit_cache/uncaught-files.yaml` 由 Owner 补标）

### 4.3 tasks 表 schema 扩展（增量于 ADR-0030）

`scripts/infra/sqlite_schema.py`（T-1-02）需要追加一列：

```sql
ALTER TABLE tasks ADD COLUMN file_path TEXT;
CREATE UNIQUE INDEX idx_tasks_file_path ON tasks(file_path)
    WHERE file_path IS NOT NULL;
```

- 约束：`file_path` 为 `NULL` ⇔ `task_id LIKE 'T-RUN-%'`（非文件任务）
- 约束：`file_path` 非 NULL 时必须唯一（1:1 对齐）
- 约束：`file_path` 必须相对仓库根（如 `docs/02_enterprise_architecture/adr/adr-0038-file-as-task-paradigm.md`），不得包含 `..` 或绝对路径

### 4.4 三态一致性校验（由 T-2-02 `file_task_mapper.sync_file_state` 实施）

对任一 task_id：

| 磁盘状态 | frontmatter.status | tasks.status | 允许组合 | 不一致处置 |
|---------|--------------------|--------------|---------|-----------|
| 不存在 | — | `PENDING` / `READY` / `WAITING` | ✅ | — |
| 存在 | `draft` | `IN_PROGRESS` | ✅ | — |
| 存在 | `accepted` | `COMPLETED` / `VERIFIED` | ✅ | — |
| 存在 | `accepted` | `PENDING` | ❌ | 触发 `STALE_TASK_WARNING`，自动迁入 `VERIFIED` |
| 不存在 | — | `COMPLETED` / `VERIFIED` | ❌ | 触发 `MISSING_ARTIFACT_ERROR`，回滚至 `PENDING` 并 emit `manual_event` 给 Owner |
| 存在 | `draft` | `VERIFIED` | ❌ | `DOWNGRADE_WARNING`，置 `IN_PROGRESS` |

`sync_file_state` 由 `scripts/cli/report.py sync` 在每 session 开始时调用，且在 pre-commit `doc_guard` 中作为 Gate G2 之一（参照待拟 `gate-strategy.md`）。

### 4.5 API 契约（与 T-2-02 验收标准对齐）

```python
class FileTaskMapper:
    def register_from_triage(self, yaml_path: Path) -> RegisterReport: ...
        # 从 triage-result.yaml 批量写入 tasks 表；2559 行 < 2s
    def sync_file_state(self, task_id: str | None = None) -> SyncReport: ...
        # 全量或单任务三态校验；返回不一致列表
    def rollback(self, task_id: str) -> None: ...
        # 删除 tasks 表对应行 + 撤销 events；不碰磁盘文件
    def resolve(self, file_path: Path) -> str | None: ...
        # 反向查询 file_path → task_id（O(1)）
```

### 4.6 与其他 ADR 的边界

| ADR | 关系 |
|-----|------|
| ADR-0030（SQLite） | 本 ADR 依赖其 `tasks` 表；要求新增 `file_path` 列 |
| ADR-0036（Deferred Queue） | 非文件任务（`T-RUN-*`）的唤醒由 DQ 负责 |
| ADR-0040（Pydantic） | `Task.file_path: Path \| None` 字段必须与 SQLite 列对齐 |
| ADR-0041（Handoff） | HandoffPackage.open_files 列表可直接反查 `task_id`，实现"文件粒度交接" |
| ADR-0031（ChromaDB，下一条） | 向量入库时的 `ke_id` 通过 `T-KE-NNN` 与 tasks 表关联 |

## 5. 后果（Consequences）

### 5.1 正面后果

- triage 结果 2559 行直接批量入库为任务队列（估算 < 2s，满足 T-2-02 acceptance）
- Phase 2 进度可被一句 SQL 回答：
  `SELECT COUNT(*) FROM tasks WHERE phase=2 GROUP BY status`
- 孤儿文件 / 幽灵任务均被 `sync_file_state` 一次性定位
- Handoff 粒度下探到"单个文件"，Opus ↔ GLM ↔ Sonnet 切换零歧义
- Sentinel L1 的"注册表差集"扫描可复用：`tasks.file_path` 成为受控文件登记册之一

### 5.2 负面后果 / 权衡

- **file_path 列成为新的 SSoT 侧面**：搬迁文件时必须 `git mv` + `tasks.file_path 更新` 同 commit
  - **缓解**：pre-commit hook `file_path_consistency_check`（Phase 2 待补）扫描差集
- **1:1 约束限制了"多文件合并任务"**：例如"批量修 30 个 frontmatter"
  - **缓解**：这类批处理走 `T-RUN-*` 命名空间，产物登记在 session_log
- **frontmatter 成为关键数据源**：编码损坏会污染状态
  - **缓解**：AGENTS.md §八 编码安全规则已锁定；`doc_guard_pre_commit` 在 Gate G1 拦截

### 5.3 未来需要重新审视的触发条件（Review Triggers）

| # | 触发条件（数值化） | 重审 ADR |
|---|-----------------|---------|
| 1 | `T-RUN-*` 任务占比 > 30%（说明"文件即任务"覆盖不足） | 引入 task_group 或拆分模型 |
| 2 | tasks 表行数 > 10000 且反向查询 P95 > 50ms | 改为哈希索引 + 分区 |
| 3 | 出现合法的"一任务多文件"需求（例如多语言同步交付） | 引入 `task_artifacts` 关联表 |
| 4 | Phase 5 引入多 repo / monorepo 子模块 | 增加 `repo_id` 维度 |

## 6. 落地动作（Implementation）

- [x] 本 ADR 落盘 `docs/02_enterprise_architecture/adr/adr-0038-file-as-task-paradigm.md`（Stage F 后新树小写路径）
- [ ] T-2-02：`scripts/infra/file_task_mapper.py`（GLM C30 执行）
- [ ] T-1-02 追加：`ALTER TABLE tasks ADD COLUMN file_path TEXT`；重建 `idx_tasks_file_path`（Sonnet 补丁）
- [ ] T-1-13（schemas.py）追加：`Task.file_path: Path | None`
- [x] `docs/02_enterprise_architecture/adr/index.md` 已登记本 ADR（Stage F 完成）
- [ ] `docs/09_audit/reports/-triage-result.yaml`：确认每行含 `suggested_task_id` 字段（若无，由 T-2-02 `register_from_triage` 补全）

## 7. 参考

- 相关 ADR：
  - ADR-0030（SQLite —— tasks 表归属）
  - ADR-0036（Deferred Queue —— 非文件任务唤醒）
  - ADR-0040（Pydantic v2 —— Task 模型对齐）
  - ADR-0041（Handoff Protocol —— 文件粒度交接）
  - ADR-0031（ChromaDB —— 待拟，KE 任务关联）
  - ADR-0035（意图三阶段 —— 待拟，域分类用于 fallback 推导 task_id）
- 相关任务卡：
  - `模块候选池/开发流程/任务卡/phase-2-cards.md` §T-2-01 / §T-2-02
- 相关注册表：
  - `docs/09_audit/reports/-triage-result.yaml`（T-1-22）
  - `docs/01_policies_and_standards/governance-asset-inventory.yaml`（Stage J 待重建，当前老树注册表未迁移）
- 外部参考：
  - Apache Airflow DAG-as-file 范式（本方案的灵感来源，但我们更激进）
  - Unison / fossil-scm 的"file is the unit of versioning"哲学

## 8. 修订记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-04-24 | 1.0.0 | 初版：锁定 File-as-Task 范式；定义 4 个命名空间；固化 file_path → task_id 映射规则；列出三态一致性矩阵；登记 4 条重审触发条件。 |
