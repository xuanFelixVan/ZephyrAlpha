---
module_id: ADR-0030
refines: [ADR-0011]  # ADR-0011 runtime-planes-orthogonal-view \u7684\u7ec6\u5316\u51b3\u7b56
title: 采用 SQLite 作为本地元数据存储层
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
related_rationale: R-PHASE1-META, R-ZERO-DEP
related_open_questions: []
tags: [metadata, sqlite, phase-1, ssot, storage, task-system]
summary: Phase 1 元数据层（tasks / events / knowledge / gates）采用 SQLite 单文件数据库而非 YAML/JSON/TinyDB/PostgreSQL。单 Writer、零运维、SQL 原生支持事务与视图；业务数据仍走 DuckDB+Parquet（ADR-005），两层互补不冲突。本 ADR 是 Phase 1 任务系统（T-1-02~T-1-22）的架构基线。

date: '2026-04-24'
ttl: permanent
---

# ADR-0030：采用 SQLite 作为本地元数据存储层

## 1. 状态（Status）

- **当前状态**：`accepted`
- **提议日期**：2026-04-23
- **拍板日期**：2026-04-24
- **决策者**：Project Owner（Claude Opus 4.7 终局裁决）
- **被谁取代**：—
- **取代了谁**：ADR-005 `Under Review` 条目中的"元数据也走 DuckDB"隐含假设（见 §3 方案 D）

## 2. 背景与问题（Context）

Phase 1 需要为"Vibe Coding 工业流水线"搭建元数据骨架，承载四类核心对象：

| 对象 | 用途 | 典型读写模式 |
|------|------|-------------|
| **tasks** | 任务登记表（T-0-xx / T-1-xx / T-2-xx），10 状态流转（PENDING → IN_PROGRESS → COMPLETED → VERIFIED / FAILED / BLOCKED / WAITING / READY / RETRY / CANCELLED） | 频繁 UPDATE 少量行；按 phase / status / depends_on 查询 |
| **events** | DeferredQueue 的事件流（file_event / time_event / task_event / manual_event / metric_event） | 高频 INSERT，按 event_type / created_at 查询 |
| **knowledge** | KE 条目索引（KE-NNN：标题、分类、源文件、指纹） | 中频 INSERT + UPDATE；按 category / source_git_deleted 查询 |
| **gates** | 合规门禁运行记录（pre-commit / Sentinel L1 / phase-verification 等） | 中频 INSERT，按 gate_id / passed / created_at 查询 |

关键约束：

1. **单人项目 + AI 协作**：没有 DBA，工具链必须零运维、零进程、零网络。
2. **单 Writer**：任一时刻只有一个 AI session 在写元数据（通过 handoff-protocol 串行化）；读方可并发。
3. **事务与原子性**：任务状态机 10 转换需要 `BEGIN … COMMIT` 保证 tasks + events 原子写入。
4. **可审计**：所有变更需保留时间戳与操作来源（session_id / agent_id），便于 Phase 2 追溯。
5. **Python 原生**：标准库可用，不引入额外服务进程。
6. **与业务数据隔离**：OHLCV / 回测结果 / 因子矩阵走 DuckDB+Parquet（ADR-005），元数据层绝不与业务数据混库。
7. **规模上限**：Phase 1 预估 tasks 表 ≤ 10 000 行，events 表 ≤ 1 000 000 行，knowledge 表 ≤ 5 000 行，gates 表 ≤ 100 000 行。

**关键风险**：若此处选错，下游 `task_repo.py`、`deferred_queue.py`、`metrics_collector.py`、CLI 报表、Session Handoff 全部受影响；回滚成本与任务表行数线性正比。

## 3. 考虑过的方案（Options Considered）

### 方案 A：YAML 单文件（`tasks.yaml` / `events.yaml` / …）

- **优点**
  - 人类友好，`git diff` 可读
  - 零依赖，`PyYAML` 已在 requirements.txt
- **缺点**
  - ❌ 无事务：并发写 → 文件损坏
  - ❌ 无索引：10 000 行 + `depends_on` 查询需全表扫描
  - ❌ 写放大：每次 UPDATE 必须重写整个文件，git 历史爆炸
  - ❌ 无类型约束：AI 输出 typo 不会被检测（与 ADR-0040 Pydantic 层也只能在边界校验，存储层无二次保护）
- **机构案例**：Ansible / Kubernetes manifests（声明式、读多写少），与任务系统频繁 UPDATE 的特征相反

### 方案 B：JSON Lines（`tasks.jsonl` 追加）

- **优点**
  - append-only，无写冲突
  - 易被 LLM 产出
- **缺点**
  - ❌ UPDATE 需要压缩（compaction），复杂度高
  - ❌ 查询仍需全表扫
  - ❌ 状态机语义实现在应用层，难以用事务封装
- **机构案例**：Event Sourcing（Kafka / EventStore），但需要独立查询侧 CQRS，不适合单人项目

### 方案 C：TinyDB（JSON 文档数据库）

- **优点**
  - 纯 Python、零进程
  - Mongo-style 查询 API
- **缺点**
  - ❌ 无真正事务（写入期间进程崩溃可能丢数据）
  - ❌ 单文件性能瓶颈：10 000+ 文档后 `.search()` 变慢
  - ❌ 缺少视图 / 聚合 SQL
  - ❌ 无索引（需全量加载到内存）
- **机构案例**：仅见于小型脚本工具，量化机构未见采用

### 方案 D：DuckDB 复用（与业务数据同库）

- **优点**
  - 与 ADR-005 统一技术栈
  - OLAP 性能极佳
- **缺点**
  - ❌ DuckDB 偏 OLAP，频繁小事务写入性能弱于 SQLite
  - ❌ 元数据与业务数据混库 → **违反单一职责原则**，一次回测崩库会连带任务系统不可用
  - ❌ DuckDB 并发写入限制（单 Writer）与业务批量写入直接冲突
- **机构案例**：Snowflake / BigQuery（云原生），不适合本地元数据

### 方案 E：PostgreSQL（Docker 或本地服务）

- **优点**
  - 工业级、功能完备
  - 外键、CHECK、触发器、pgvector 全支持
- **缺点**
  - ❌ 引入 Docker / systemd 服务 → 违反"零运维"原则
  - ❌ 单人项目 5K 行/天的写入远远低于 Postgres 的合理规模
  - ❌ 备份/恢复/升级流程全部落在 Owner 一人身上
- **机构案例**：Airbnb / LinkedIn 任务系统，但团队 ≥ 5 人

### 方案 F：SQLite 单文件（**本 ADR 选定**）

- **优点**
  - ✅ **Python 标准库 `sqlite3`**，零外部依赖
  - ✅ **ACID 事务**：`BEGIN IMMEDIATE … COMMIT` 原生可用，status 流转 + events INSERT 可打包原子提交
  - ✅ **索引 + 视图**：CREATE INDEX 支持 depends_on / status / phase 的 O(log n) 查询；VIEW 封装常用报表
  - ✅ **单文件 = 可备份**：`cp zalpha_metadata.db bak/` 即完成快照；`git` 可追踪（虽然二进制 diff）
  - ✅ **PRAGMA journal_mode=WAL**：读写不互斥，单 Writer + 多 Reader 模式下性能充足
  - ✅ **与 DuckDB 协作良好**：DuckDB 可通过 `ATTACH … AS sqlite` 直连 SQLite 读取任务进度（监控场景）
  - ✅ **社区验证**：Airflow metadata DB 默认选项、Home Assistant、Obsidian sync、Firefox Places 均采用 SQLite 作为元数据层
  - ✅ **规模充分**：官方声明支持 281 TB 单库；我们预估 ≤ 100 MB，余量 ≥ 10⁶ 倍
- **缺点 / 权衡**
  - ⚠ 不支持单库多 Writer：Phase 2 若出现并行 AI agent 写任务表需切换为 `BEGIN IMMEDIATE` + 重试，或引入 `dogpile` 级锁
  - ⚠ 二进制格式 `git diff` 不可读：通过配套的 YAML 导出脚本（`cli report` 子命令）弥补
  - ⚠ 未来云同步不原生：需通过 Litestream / rsync 等外挂方案
- **机构案例**：Apache Airflow、Home Assistant、Mozilla Firefox、GitHub Desktop、WhatsApp（客户端）、Obsidian Sync metadata、dbt Cloud CLI

## 4. 决策（Decision）

**最终选择：方案 F —— SQLite 单文件作为 Phase 1 元数据层。**

### 4.1 物理路径

```
data/zalpha_metadata.db                     # 单一真源（受 .gitignore 管理，落盘但不进版本库）
src/zephyr/db/sqlite_schema.py              # DDL 定义 + 迁移脚本
src/zephyr/db/task_repo.py                  # CRUD + 状态机
```

**路径论证**：

- `data/` 而非 `docs/09_audit/state/`：`.db` 文件是系统运行心脏（任务状态机、事件流、KE 索引），不是审计文档。`data/` 语义匹配其运行时数据本质，与 `src/`（源码）、`docs/`（人类阅读文档）平行独立。
- 对齐 SQLite 官方"application file format"定位：数据库文件应独立于源码和文档目录。
- 对齐 Rails `db/` / Django `data/` 等行业惯例：生成/运行时数据不在文档树中。
- 扩展友好：将来 `data/backups/`、`data/warehouse/`（DuckDB）自然归入同一父目录。
- 数据库文件**不入 git**：避免二进制合并冲突；通过 `scripts/cli/report.py` 导出 YAML 快照归档。
- 初始化由 `python -m scripts.infra.sqlite_schema` 幂等执行。

### 4.2 核心表结构（ADR 级基线，细节由 T-1-02 `sqlite_schema.py` 承接）

| # | 表名 | 职责 | 关键列 |
|---|------|------|--------|
| 1 | `tasks` | 任务登记表 | task_id PK, phase, status, directive, idempotent, classification, evolution_policy, depends_on(JSON), execution_model, safety_level, created_at, updated_at, session_id |
| 2 | `events` | 事件流（Deferred Queue 消费） | event_id PK, event_type, payload(JSON), task_id FK, created_at, processed_at |
| 3 | `knowledge` | KE 索引 | ke_id PK, title, category, source_file, source_git_deleted, fingerprint_sha256, created_at |
| 4 | `gates` | 门禁运行记录 | gate_run_id PK, gate_id, passed, details(JSON), artifact_path, created_at |

附加：`metrics`（由 T-1-19 管理，复用同库）、`event_log` 视图（join tasks × events，给 CLI）、`phase_summary` 视图（按 phase 聚合进度）。

### 4.3 PRAGMA 基线

```sql
PRAGMA journal_mode = WAL;        -- 读写不互斥
PRAGMA synchronous = NORMAL;      -- 性能与安全平衡（电源故障至多丢失最近一次 commit）
PRAGMA foreign_keys = ON;         -- 强制外键
PRAGMA busy_timeout = 5000;       -- 并发读写时等待 5s
PRAGMA temp_store = MEMORY;
```

### 4.4 与其他层的边界

| 层 | 技术栈 | 与本 ADR 的关系 |
|----|-------|---------------|
| **业务数据（OHLCV / 回测）** | DuckDB + Parquet（ADR-005） | **不得写入本 SQLite**。反之本 SQLite 也不得承载 OHLCV/因子等业务数据 |
| **向量检索** | ChromaDB（ADR-0031，待拟） | 独立服务；本 SQLite 仅存元数据指针（ke_id → vector_id） |
| **事件流** | 本 SQLite `events` 表 | **唯一真源**；`scripts/infra/deferred_queue.py` 直连 |
| **输出契约** | Pydantic v2（ADR-0040） | Pydantic 模型字段必须与 SQLite 列**严格对齐**（由 T-1-13 `schemas.py` 联动校验） |
| **Handoff 协议** | SQLite `tasks.session_id` 列 | `handoff-protocol.md`（ADR-0041）依赖本表的 session_id / status 列实现 5 项反腐败校验 |

### 4.5 并发与锁策略（Phase 1 基线）

- **单 Writer 假设**：任一时刻仅一个 AI session 可执行写事务。
- 进入写事务前必须在 `gates` 表登记 `session_id + pid + started_at`（由 T-2-30 ATM 实施）。
- 读方任意并发（WAL 允许）。
- 破坏假设的处置：事务抛 `SqliteLockError` → 调用方退避 500 ms 重试 3 次 → 失败则走 FAILED 状态。

## 5. 后果（Consequences）

### 5.1 正面后果

- Phase 1 可在 5 人日内完成元数据层（已通过 T-1-02~T-1-22 任务卡估算）
- 零依赖、零运维、零网络；Cursor / Trae / CLI 任意环境均可读写
- SQL 原生事务 + 视图 + 索引，满足 `100 WAITING → READY < 1s` 性能断言
- 与 Pydantic v2 契约天然对齐：`sqlite3.Row` → `Task.model_validate(dict(row))` 零成本
- 支持 `cp` 级备份与 Git LFS 级归档；Phase 2 引入 Litestream 可无痛升级云同步
- 与 DuckDB 业务库解耦：任一侧故障不影响对方

### 5.2 负面后果 / 权衡

- Phase 3 多 AI agent 并发写入需要 `BEGIN IMMEDIATE` 重试器（已在 T-2-30 ATM 范畴内）
- 二进制格式不利于 `git diff` 审阅：**缓解**——CLI `report` 子命令导出 YAML 快照至 `docs/09_audit/state/SNAPSHOTS/latest.yaml`（覆盖写 LATEST，不入历史）
- 若 tasks 表膨胀 > 100 万行，查询延迟会显现：**缓解**——Phase 2 引入 Partitioned View（按 phase 分片）

### 5.3 未来需要重新审视的触发条件（Review Triggers）

| # | 触发条件（数值化） | 重审 ADR |
|---|-----------------|----------|
| 1 | 日并发 Writer ≥ 3 且 SqliteLockError 发生率 > 1% | 切换 PostgreSQL |
| 2 | tasks 行数 ≥ 1 × 10⁶ 或单表查询 P95 > 500 ms | 引入分表或 ClickHouse 镜像 |
| 3 | 需要多机房同步 | 引入 Litestream / rqlite |
| 4 | Phase 6 引入 Agent 集群 | 考虑 Postgres + PgBouncer |

## 6. 落地动作（Implementation）

- [x] 本 ADR 落盘 `docs/02_enterprise_architecture/adr/adr-0030-sqlite-task-metadata-store.md`（Stage F 后新树小写路径）
- [ ] T-1-02：`scripts/infra/sqlite_schema.py`（4 表 + event_log 视图 + 2 统计视图）
- [ ] T-1-03：Schema 初始化执行 → 生成 `docs/09_audit/state/zalpha_metadata.db`
- [ ] T-1-04：`scripts/infra/task_repo.py`（CRUD + 10 状态机）
- [ ] T-1-06：Phase 0 的 14 个任务批量补录为 `VERIFIED`
- [ ] `.gitignore` 追加 `docs/09_audit/state/zalpha_metadata.db` 与 `*.db-wal`/`*.db-shm`
- [x] `docs/02_enterprise_architecture/adr/index.md` 已登记本 ADR（Stage F 完成）

## 7. 参考

- 相关 ADR：
  - ADR-0040（Pydantic v2 数据验证 —— 契约层对齐）
  - ADR-0016（Vector Memory / ChromaDB —— GHG-001 向量体存储侧。注意：ADR-0016 增量取代 ADR-0005 KMS 实施路径，但本 ADR 引用的是 ChromaDB 选型本身）
  - ADR-0036（Deferred Queue —— 直接消费本库 events 表，即将拟定）
  - ADR-0037（Observer 模式 —— 事件源适配 events 表）
  - ADR-0040（Pydantic v2 输出契约 —— 字段对齐基础）
  - ADR-0041（Handoff Protocol —— 依赖 tasks.session_id 列）
- 相关文档：
  - `模块候选池/开发流程/vibe-coding-execution-order-v1.md` §三 Phase 1
  - `模块候选池/开发流程/脚本任务知识库架构/02-任务系统架构.md`
- 外部参考：
  - SQLite 官方 *When To Use SQLite*：<https://www.sqlite.org/whentouse.html>
  - Apache Airflow `airflow.cfg` 默认 metadata DB：SQLite
  - Home Assistant `core.db`：SQLite + WAL
  - D. Richard Hipp《SQLite as an Application File Format》(2021)
- 相关规则 / Schema：
  - `schemas/frontmatter-schema.json`（R4 SSoT，由 T-0-10 拟定）

## 8. 修订记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-04-24 | 1.0.0 | 初版：锁定 SQLite 为 Phase 1 元数据层；明确与 DuckDB 业务库边界；列出 6 个备选方案与选定理由；登记 4 条重审触发条件。 |
