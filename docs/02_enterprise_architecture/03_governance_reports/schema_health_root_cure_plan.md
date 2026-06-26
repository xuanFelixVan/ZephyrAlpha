---
ttl: permanent
doc_type: construction_plan
---

# Schema 健康度治本方案：depgraph.db 漂移修复与死表清理

> **文档定位**：针对 depgraph.db（依赖全景图+架构全景图）字段合理性调研中发现的 3 类系统性问题（Schema 漂移、死表堆积、写入断裂）的完整治本方案
> **调研日期**：2026-06-26
> **调研对象**：depgraph.db 全部 25 张表 / 236 字段 + 其 DDL 真源 `depgraph_schema.py` + 同步脚本 `sync_yaml_to_depgraph.py`
> **调研方法**：只读调研（未修改任何文件），证据来源为代码静态分析 + DDL 真源逐行核实 + DB 读取者全量 grep + 项目文档 + 行业基准对标
> **适用语境**：100% AI 开发项目
> **调研者角色**：客观专业架构师（独立裁定删除/保留，不回避决策）

---

## 目录

- [第一部分：事实层（实测数据）](#第一部分事实层实测数据)
  - [1.1 三类系统性问题总览](#11-三类系统性问题总览)
  - [1.2 P0-Bug：Schema 漂移与功能断裂](#12-p0-bugschema-漂移与功能断裂)
  - [1.3 死表与低利用表实测](#13-死表与低利用表实测)
- [第二部分：根因分析（第一性原理）](#第二部分根因分析第一性原理)
- [第三部分：行业基准对标](#第三部分行业基准对标)
- [第四部分：裁定结果](#第四部分裁定结果)
- [第五部分：治本施工方案（动作级）](#第五部分治本施工方案动作级)
- [第六部分：总结](#第六部分总结)
- [附录A：受影响文件清单矩阵](#附录a受影响文件清单矩阵)
- [附录B：议题清单（#ARCH-XXX）](#附录b议题清单arch-xxx)
- [附录C：循环审查记录](#附录c循环审查记录)

---

## 第一部分：事实层（实测数据）

### 1.1 三类系统性问题总览

本次调研覆盖 depgraph.db 全部 25 张表 / 236 字段，对照其 DDL 真源 `src/zephyr/governance/depgraph_schema.py`（1088 行）和同步脚本 `scripts/governance/sync_yaml_to_depgraph.py`（1064 行），发现三类系统性问题：

| 类别 | 问题数 | 严重度 | 根因 |
|------|--------|--------|------|
| Schema 漂移 | 1 张表（contracts） | P0 致命 | DDL 声明与写入路径脱节，无迁移记录 |
| 功能断裂 | 2 处 | P1 高 | 写入遗漏列 / 写入已删除列 |
| 死表堆积 | 4 张 | P2 中 | DB 缓存层被系统性绕过，消费者直读 YAML/JSON |

> **关键修正**：前序调研曾判定"10 张死表"，经本次全量 grep `SELECT ... FROM <table>` 逐一核实，**仅 4 张表真正无生产读取者**。其余 6 张表均有活跃读取者（apply_depgraph.py / rule_engine.py / 生成器），属"低利用"而非"死表"。详见 §1.3。

### 1.2 P0-Bug：Schema 漂移与功能断裂

#### BUG-1：contracts 表 Schema 漂移（#ARCH-008）

**现象**：DDL 真源声明 7 列，实际写入 13 列，无迁移记录。

**证据——DDL 声明**（`src/zephyr/governance/depgraph_schema.py:204-214`）：

```sql
CREATE TABLE IF NOT EXISTS contracts (
    contract_id      TEXT    PRIMARY KEY,
    name             TEXT    NOT NULL,
    provider_domain  TEXT    NOT NULL,
    consumer_domain  TEXT    NOT NULL,
    contract_type    TEXT    NOT NULL,
    schema_definition TEXT,
    version          TEXT
)
```

**证据——写入路径**（`scripts/governance/sync_yaml_to_depgraph.py:535-548`）：

```python
INSERT INTO contracts
(contract_id, name, provider_domain, consumer_domain, contract_type,
 promise, actual_consumer, fulfillment_status, gap, target_phase, last_reviewed)
VALUES (?, ?, ?, ?, 'declarative', ?, ?, ?, ?, ?, ?)
```

`sync_declarative_contract_tracker`（L524-564）写入 6 个扩展列：`promise` / `actual_consumer` / `fulfillment_status` / `gap` / `target_phase` / `last_reviewed`。这些列**不在 `_DDL_CONTRACTS` 声明中**，也**不在 `_MIGRATIONS` 列表 v1-v12 任何迁移中**。

**致命后果**：在全新克隆（fresh clone）环境下，`init_db()` 执行 12 条迁移创建 7 列的 contracts 表，随后 `sync_yaml_to_depgraph.py` 尝试 INSERT 13 列 → `sqlite3.OperationalError: table contracts has no column named promise` → 同步中断。当前生产 DB 因历史 ALTER TABLE 手动添加了 6 列而"碰巧能跑"，但这是**不可复现的脆弱状态**。

**根因**：`sync_declarative_contract_tracker` 是后加的同步函数（#159），添加时直接在 INSERT 中写了扩展列，但未同步在 `_DDL_CONTRACTS` 增加列声明、也未添加 migration。违反了"DDL 真源唯一性"原则——DDL 声明和写入代码出现了两个相互矛盾的"真源"。

---

#### BUG-2：gates.event_driven 写入断裂（#ARCH-009）

**现象**：`sync_gate_registry` 只写入 8 列，遗漏 `event_driven` / `auto_start` / `source` 三列；但 `auto_runner` 依赖这三列调度事件门禁。

**证据——DDL 声明**（`src/zephyr/governance/depgraph_schema.py:474-489`）：

```sql
CREATE TABLE IF NOT EXISTS gates (
    gate_id        TEXT PRIMARY KEY,
    name           TEXT NOT NULL,
    entry          TEXT NOT NULL,
    description    TEXT,
    files_trigger  TEXT,
    always_run     INTEGER DEFAULT 0,
    category       TEXT NOT NULL,
    status         TEXT DEFAULT 'active',
    source         TEXT DEFAULT '.pre-commit-config.yaml',  -- ← 声明了
    event_driven   TEXT DEFAULT '',                           -- ← 声明了
    auto_start     INTEGER DEFAULT 1,                         -- ← 声明了
    CHECK (status IN ('active', 'deprecated', 'disabled'))
)
```

**证据——写入路径**（`scripts/governance/sync_yaml_to_depgraph.py:308-323`）：

```python
INSERT OR REPLACE INTO gates
(gate_id, name, entry, description, files_trigger, always_run, category, status)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
```

仅写 8 列，`event_driven` / `auto_start` / `source` 使用 DDL 默认值（`''` / `1` / `'.pre-commit-config.yaml'`）。

**证据——读取者**（`src/zephyr/governance/auto_runner.py:263-287`）：

```python
"SELECT gate_id FROM gates "
"WHERE event_driven=? AND status='active' AND auto_start=1 "
```

`auto_runner.get_gates_by_event` 查询 `WHERE event_driven=?`——但由于 sync 从不写入 `event_driven`（恒为默认值 `''`），任何非空事件名查询永远返回空集。

**功能后果**：事件驱动门禁调度（phase_manager 基于 `event_driven` 触发）**完全失效**。所有事件门禁形同虚设。

---

#### BUG-3：generate_project_depgraph.py 写入已删除列（#ARCH-010）

**现象**：`generate_project_depgraph.py` 仍在 INSERT `module_lifecycle_state` 列，但该列已在 migration v11 中删除。

**证据——migration v11**（`src/zephyr/governance/depgraph_schema.py:788-856`）：

v11 重建 nodes 表（L802-824），新表 `_DDL_NODES_V5`（L378-421）**不含 `module_lifecycle_state` 列**。旧数据归档到 `nodes_archive_module_lifecycle` 表。

**证据——残留写入**（`scripts/governance/generate_project_depgraph.py:2673, 2692, 2721`）：

```python
"module_lifecycle_state",          # L2673 INSERT 列名列表
node_name, file_path, build_status, module_lifecycle_state,  # L2692 VALUES
node.get("module_lifecycle_state", ""),  # L2721 值来源（注释标注"裁定#183：字段废弃"）
```

**致命后果**：在 fresh clone 环境下，`generate_project_depgraph.py` 执行 INSERT 时 → `sqlite3.OperationalError: table nodes has no column named module_lifecycle_state` → 生成器崩溃。当前生产 DB 因 v11 迁移前已存在该列而"碰巧能跑"，但同样是**不可复现的脆弱状态**。

---

#### BUG-4：cross_registry_rules.ssot NOT NULL 但 0% 填充（#ARCH-011）

**现象**：DDL 声明 `ssot TEXT NOT NULL`，但同步函数从未写入该列，导致表 0 行数据。

**证据——DDL 声明**（`src/zephyr/governance/depgraph_schema.py:534`）：

```sql
ssot             TEXT NOT NULL,
```

**证据——同步函数缺失**：`sync_yaml_to_depgraph.py` 中无 `sync_cross_registry_rules` 函数。`sync_all()`（L980-1064）的 19 个同步函数中不包含 cross_registry_rules。YAML 真源 `registry_consistency_contract.yaml` 含 6 条 CR 规则，但从未被同步到 DB。

**后果**：表存在但永远为空。任何尝试 INSERT 的代码都会因 `ssot NOT NULL` 约束而失败（除非显式提供 ssot 值）。这是一个"声明了但从未接线"的死表。

---

### 1.3 死表与低利用表实测

对 25 张表逐一执行 `grep -rn "FROM <table>" *.py`，按读取者活跃度分类：

#### 真死表（4 张，无生产读取者）

| 表名 | 行数 | 写入者 | 读取者 | 死因 |
|------|------|--------|--------|------|
| `governance_audit_logs` | — | `auto_runner._write_audit_log` (L194-233) | 仅 `tests/test_f18_*.py` | 写入审计日志但无生产查询路径；且 sync 不清此表（非 READONLY），DB 重建时丢失，非真 WORM |
| `arch_layers` | — | 无（v1 建表后无写入） | 仅 `depgraph_reader.py:204`（本身无生产导入者，仅 test 引用） | v6 将层信息合并入 `domains.layer_id` 后，此表为残留 |
| `arch_bottlenecks` | — | 无 | 仅 `tests/test_depgraph_db.py:172` | 架构瓶颈追踪表，从未被生产代码写入或读取 |
| `invariants` | 255 行(DB) | `sync_invariants`（推测，sync_all 含此函数） | 仅 `tests/test_depgraph_db.py:143` | YAML 真源 `invariants.yaml` 仅 20 条，DB 有 255 行 → 已漂移；消费者直读 YAML 不读 DB |

> **governance_audit_logs 裁定关键**：该表不是真正的 WORM 审计日志。真正的审计链是 `data/audit-trail/events.jsonl`（由 `verify_audit_integrity.py` 校验哈希链）。`governance_audit_logs` 只是一个被 sync 覆盖写的普通表，无合规价值。

#### 低利用表（6 张，有生产读取者，保留）

| 表名 | 读取者 | 活跃度 | 裁定 |
|------|--------|--------|------|
| `rule_bindings` | `rule_engine.py:99,154,172,190` + `database_service.py:205` | rule_engine.py 标记为 unregistered，仅 test 引用；database_service.py 经 `__init__.py:83` 导出 | 保留（有设计读取者，规则引擎核心数据） |
| `domain_dependencies` | `apply_depgraph.py:2094,2124,2130` + `audit_domain_nodes.py:49` | 活跃（apply_depgraph 是全景图操作主工具） | 保留 |
| `domain_events` | `migrate_arch_f_functions.py:208` | 迁移脚本读取 | 保留 |
| `blueprint_links` | `apply_depgraph.py:1129,1134,1763,1863` | 活跃 | 保留 |
| `domain_mapping` | `generate_project_depgraph.py:596,601` | 活跃（生成器核心数据） | 保留 |
| `arch_path_mappings` | `generate_project_depgraph.py:516` + 3 个生成器 | 活跃 | 保留 |

---

## 第二部分：根因分析（第一性原理）

### 2.1 RC1：Schema 声明与写入路径脱节（漂移根因）

**第一性原理**：数据库的 Schema 真源（DDL）与数据写入代码是两个独立实体。当新增字段时，必须在**两处同步**修改：DDL 声明 + 写入代码。若只改写入代码不改 DDL，则产生漂移。

**项目中的体现**：
- `sync_declarative_contract_tracker`（#159）添加时，直接在 INSERT 写了 6 个新列名，但未在 `_DDL_CONTRACTS` 添加声明、未添加 migration → BUG-1
- `sync_gate_registry`（#155）编写时只写了 8 列，忽略了 DDL 中已声明的 `event_driven` / `auto_start` / `source` → BUG-2
- `generate_project_depgraph.py` 在 v11 删除 `module_lifecycle_state` 后未同步清理 INSERT → BUG-3

**根因本质**：项目缺少**"DDL 真源 → 写入代码"的一致性校验机制**。DDL 改了没人查写入代码，写入代码改了没人查 DDL。在 100% AI 开发中，不同 AI session 分别修改这两处，无人做交叉验证。

### 2.2 RC2：DB 缓存层被系统性绕过（死表根因）

**第一性原理**：SSoT（Single Source of Truth）原则下，YAML 是规则真源，DB 是只读缓存。缓存的价值取决于"有消费者读取缓存而非真源"。若所有消费者直读 YAML/JSON，则 DB 缓存层是冗余的。

**项目中的体现**：
- `invariants` 表：YAML `invariants.yaml`（20 条）是真源，消费者直读 YAML → DB 的 255 行无人读取 → 漂移无感知
- `arch_layers` 表：层信息已在 `domains.layer_id` → arch_layers 无消费者
- `governance_audit_logs` 表：真正的审计链在 `events.jsonl`（有哈希链校验）→ DB 表是"假审计"
- `cross_registry_rules` 表：声明了 `ssot NOT NULL` 但无 sync 函数 → 永远空表

**根因本质**：DB 缓存层的设计假设"消费者会查 DB"，但实际消费者（生成器、审计脚本）要么直读 YAML，要么读预编译 JSON 制品（`architecture-context.json`）。DB 缓存层从未建立"读取契约"，导致缓存与真源漂移时无人发现。

### 2.3 RC3：迁移框架无反向校验（漂移检测 gap）

**第一性原理**：版本化迁移框架（`_MIGRATIONS`）只做"向前迁移"（v1→v2→...→v12），不做"反向校验"（实际 DB schema 是否匹配 DDL 声明）。迁移执行后，无人验证 DB 物理状态与 `_DDL_*` 声明一致。

**项目中的体现**：
- `check_schema_version_writes.py`（G_TRAE_059）只检查版本号写入，不检查结构一致性
- `diagnose_depgraph.py` 检查 11 项结构指标，但不包含"DB 列 vs DDL 声明列"对比
- 无任何脚本执行 `PRAGMA table_info(contracts)` 并与 `_DDL_CONTRACTS` 解析的列名列表对比

**根因本质**：项目有"迁移执行"能力，但无"迁移后校验"能力。这是 State-based drift detection（业界主流方法）的缺失。

### 2.4 RC4：100% AI 开发的认知盲区

**第一性原理**：人类开发者修改 Schema 时会本能检查所有相关写入代码（因为人脑有"全局影响"意识）。AI 开发者按"任务卡"执行，只修改任务卡指定的文件，不主动检查跨文件一致性。

**项目中的体现**：
- 某次 AI session 添加 `sync_declarative_contract_tracker`，任务卡只说"添加同步函数"，未要求"同步更新 DDL + 添加 migration" → BUG-1
- 某次 AI session 删除 `module_lifecycle_state`（v11），任务卡只说"在 migration 中删除列"，未要求"grep 所有 INSERT 该列的代码并清理" → BUG-3
- 某次 AI session 创建 `governance_audit_logs` 表，任务卡只说"建表+写入"，未要求"确认有读取者" → 死表

**根因本质**：100% AI 开发需要**机械化的跨文件一致性校验**，不能依赖 AI 的"全局意识"。这正是 `verify_schema_health.py` 门禁的价值——用代码替代 AI 认知盲区。

---

## 第三部分：行业基准对标

### 3.1 专业机构实践（DDD / TOGAF / NIST）

| 机构 | 实践 | 对标结论 |
|------|------|----------|
| DDD（领域驱动设计） | 限界上下文（Bounded Context）的契约应显式声明、版本化、有消费者 | contracts 表漂移违反"契约显式声明"原则；应修复 DDL 使其与写入一致 |
| TOGAF | 架构制品（Architecture Artifacts）应有"制品矩阵"标注每个制品的读取者 | 4 张死表无读取者，违反"制品必有消费者"原则；应删除或显式标注为 deprecated |
| NIST SP 800-92 | 审计日志应 WORM 存储、防篡改、有独立校验链 | `governance_audit_logs` 被 sync 覆盖写、无哈希链，不符合审计日志标准；真正审计链在 `events.jsonl` |

### 3.2 量化社区实践（ArchUnit / SonarQube / Fitness Functions）

| 工具/社区 | 实践 | 对标结论 |
|-----------|------|----------|
| ArchUnit | 架构规则编码为可执行测试，CI 中持续运行 | `verify_schema_health.py` 正是 ArchUnit 思路的落地——将"DDL=写入"编码为门禁 |
| SonarQube | Schema drift 检测：对比 DDL 声明与实际 DB schema | 项目完全缺失此能力，需新建 `verify_schema_health.py` |
| Fitness Functions（Evolutionary Architecture） | 架构适应度函数在 CI 中持续验证架构不变量 | Schema 一致性是最基本的适应度函数，当前缺失 |

### 3.3 氛围编程社区（Vibe Coding / .cursorrules / .claude）

| 社区实践 | 内容 | 对标结论 |
|----------|------|----------|
| Vibe Coding Level 4-5 | 团队标准化 + 基础设施集成：`.cursorrules` / `.claude` 约定文件 + CI/CD 门禁 | 项目已有 `.trae/rules/project_rules.md`（RULE-SIXTEEN），但缺少 Schema 健康度门禁 |
| Schema-as-Code | DDL 文件是唯一真源，DB 是派生物，CI 校验 DB↔DDL 一致 | 项目 `depgraph_schema.py` 是 DDL 真源，但无 CI 校验 DB 实际状态 |
| Consumer-first Data Contracts | 每个数据制品必须声明消费者，无消费者的制品应删除 | 4 张死表违反此原则 |

### 3.4 综合对标裁定

| 维度 | 行业共识 | 本项目现状 | 裁定 |
|------|----------|------------|------|
| Schema 漂移检测 | CI 必备 | 缺失 | **新建 `verify_schema_health.py`** |
| DDL 真源唯一 | DDL 文件为唯一真源 | 有 DDL 真源但被写入代码绕过 | **修复 contracts DDL + 添加 migration v13** |
| 制品必有消费者 | 无消费者制品应删除 | 4 张死表 | **删除 4 张死表** |
| 审计日志 WORM | 独立 WORM 存储 | `governance_audit_logs` 非 WORM | **删除假审计表，保留 events.jsonl 真审计链** |

---

## 第四部分：裁定结果

### 4.1 逐表价值判定与裁定

> 裁定原则：作为客观架构师，以"是否有生产读取者"为一票否决标准，以"SSoT 一致性"为保留条件。删除不回避，保留必说明理由。

#### 裁定#ARCH-008：contracts 表——修复（不删除）

| 维度 | 判定 |
|------|------|
| 有生产读取者？ | 是（apply_depgraph.py、diagnose_depgraph.py 等引用 contracts） |
| SSoT 一致？ | **否**——DDL 声明 7 列，写入 13 列 |
| 裁定 | **修复**：在 `_DDL_CONTRACTS` 补齐 6 个扩展列声明 + 添加 migration v13 |
| 理由 | contracts 表有真实消费者，漂移是 DDL 声明滞后于写入代码，补齐 DDL 即可治本 |

#### 裁定#ARCH-009：gates.event_driven——修复写入

| 维度 | 判定 |
|------|------|
| 有生产读取者？ | 是（auto_runner.py:263-287 依赖 event_driven） |
| 写入完整？ | **否**——sync 只写 8 列，遗漏 3 列 |
| 裁定 | **修复**：sync_gate_registry 补写 `event_driven` / `auto_start` / `source` 三列 |
| 理由 | event_driven 是事件门禁调度的核心，当前恒为空导致功能失效 |

#### 裁定#ARCH-010：generate_project_depgraph.py——修复残留

| 维度 | 判定 |
|------|------|
| 写入合法列？ | **否**——INSERT 已删除的 module_lifecycle_state |
| 裁定 | **修复**：从 INSERT 列名列表和 VALUES 中移除 module_lifecycle_state |
| 理由 | v11 已删除该列，残留 INSERT 在 fresh clone 下崩溃 |

#### 裁定#ARCH-011：cross_registry_rules——修复或标注 deprecated

| 维度 | 判定 |
|------|------|
| 有生产读取者？ | 否 |
| 有 sync 函数？ | 否 |
| 裁定 | **标注 deprecated**：在 DDL 注释中标注"deprecated—未接线"，暂不删除（YAML 真源 `registry_of_registries.yaml` 含 6 条 CR 规则，未来可能接线） |
| 理由 | 删除需要确认无未来使用计划；标注 deprecated 成本低、可逆 |

#### 裁定#ARCH-012：governance_audit_logs——删除

| 维度 | 判定 |
|------|------|
| 有生产读取者？ | 否（仅 test） |
| 是真 WORM 审计？ | **否**——被 sync 覆盖写、无哈希链 |
| 有替代方案？ | 是——`data/audit-trail/events.jsonl`（有 `verify_audit_integrity.py` 校验哈希链） |
| 裁定 | **删除**：删除表 + 移除 `auto_runner._write_audit_log` 写入路径（改为写 events.jsonl 或直接移除） |
| 理由 | 假审计比没审计更危险——给人"有审计"的错觉，实际无合规价值 |

#### 裁定#ARCH-013：arch_layers——删除

| 维度 | 判定 |
|------|------|
| 有生产读取者？ | 否（仅 depgraph_reader.py，该模块本身无生产导入者） |
| 信息冗余？ | 是——层信息已在 `domains.layer_id`（v6 合并） |
| 裁定 | **删除**：删除表 + 清理 depgraph_reader.py 中读取该表的方法 |
| 理由 | v6 合并后残留表，无消费者，信息已冗余 |

#### 裁定#ARCH-014：arch_bottlenecks——删除

| 维度 | 判定 |
|------|------|
| 有生产读取者？ | 否（仅 test） |
| 有写入者？ | 否（建表后从未写入） |
| 裁定 | **删除**：删除表 |
| 理由 | 空表，无写入无读取，架构瓶颈追踪应通过文档（governance reports）而非 DB 表 |

#### 裁定#ARCH-015：invariants——删除 DB 表

| 维度 | 判定 |
|------|------|
| 有生产读取者？ | 否（仅 test） |
| YAML 真源？ | 是——`docs/02_enterprise_architecture/target_architecture/architecture_model/cross_cutting/invariants.yaml`（20 条） |
| DB↔YAML 一致？ | **否**——DB 255 行 vs YAML 20 条 |
| 裁定 | **删除 DB 表**：YAML 是真源，消费者直读 YAML；DB 副本已漂移且无人读取 |
| 理由 | 删除 DB 副本消除漂移风险；YAML 真源不受影响 |

---

### 4.2 裁定汇总表

| #ARCH | 表/对象 | 裁定 | 优先级 | 施工阶段 |
|-------|---------|------|--------|----------|
| #ARCH-008 | contracts | 修复 DDL + migration v13 | P0 | 阶段1 |
| #ARCH-009 | gates.event_driven | 修复 sync 写入 | P0 | 阶段2 |
| #ARCH-010 | generate_project_depgraph.py | 清理残留 INSERT | P0 | 阶段3 |
| #ARCH-011 | cross_registry_rules | 标注 deprecated | P2 | 阶段4 |
| #ARCH-012 | governance_audit_logs | 删除表 + 移除写入 | P1 | 阶段4 |
| #ARCH-013 | arch_layers | 删除表 + 清理读取者 | P1 | 阶段4 |
| #ARCH-014 | arch_bottlenecks | 删除表 | P2 | 阶段4 |
| #ARCH-015 | invariants | 删除 DB 表 | P1 | 阶段4 |
| #ARCH-016 | verify_schema_health.py | 新建门禁 | P0 | 阶段5 |
| #ARCH-017 | .pre-commit-config.yaml | 注册 GATE-SCHEMA-HEALTH | P0 | 阶段6 |

---

## 第五部分：治本施工方案（动作级）

### 5.1 施工总原则

1. **备份先行**：改 depgraph.db 前必须 `git commit` 备份（RULE-SIXTEEN）
2. **DDL 真源优先**：所有结构变更先改 `depgraph_schema.py` 的 `_DDL_*` 声明，再添加 migration
3. **机械校验收尾**：每个阶段完成后运行 `verify_schema_health.py`（阶段5 建成后）验证
4. **测试隔离**：禁止将测试数据写入生产 depgraph.db（HARD CONSTRAINT）
5. **一次一个动作**：每个动作独立可验证、可回滚

### 5.2 阶段0：备份

**动作0.1**：GitCommitGateway 提交当前状态

```bash
# 通过 GitCommitGateway 执行（禁止裸 git commit）
# commit message: "chore(schema): backup before schema-health root cure [GW:<session_id>]"
```

**验证**：`git log --oneline -1` 确认备份提交存在

**回滚**：`git reset --hard <backup_commit>`

---

### 5.3 阶段1：修复 contracts 漂移（#ARCH-008）

**动作1.1**：在 `src/zephyr/governance/depgraph_schema.py` 的 `_DDL_CONTRACTS`（L204-214）补齐 6 个扩展列

将 L204-214 的 `_DDL_CONTRACTS` 修改为：

```python
_DDL_CONTRACTS = """
CREATE TABLE IF NOT EXISTS contracts (
    contract_id        TEXT    PRIMARY KEY,
    name               TEXT    NOT NULL,
    provider_domain    TEXT    NOT NULL,
    consumer_domain    TEXT    NOT NULL,
    contract_type      TEXT    NOT NULL,
    schema_definition  TEXT,
    version            TEXT,
    promise            TEXT,
    actual_consumer    TEXT,
    fulfillment_status TEXT,
    gap                TEXT,
    target_phase       TEXT,
    last_reviewed      TEXT
)
"""
```

**动作1.2**：在 `_MIGRATIONS` 列表末尾（L912 的 `]` 前）添加 migration v13

```python
    (
        13,
        "v13: Add 6 extension columns to contracts (promise/actual_consumer/fulfillment_status/gap/target_phase/last_reviewed) — fix #ARCH-008 schema drift",
        [
            "ALTER TABLE contracts ADD COLUMN promise TEXT",
            "ALTER TABLE contracts ADD COLUMN actual_consumer TEXT",
            "ALTER TABLE contracts ADD COLUMN fulfillment_status TEXT",
            "ALTER TABLE contracts ADD COLUMN gap TEXT",
            "ALTER TABLE contracts ADD COLUMN target_phase TEXT",
            "ALTER TABLE contracts ADD COLUMN last_reviewed TEXT",
        ],
    ),
```

**动作1.3**：运行迁移

```bash
python -c "from zephyr.governance.depgraph_schema import init_db; init_db(echo=True)"
```

**验证**：输出含 `executing migration v13: ... Add 6 extension columns to contracts`

**回滚**：`git checkout -- src/zephyr/governance/depgraph_schema.py` + 手动 `ALTER TABLE contracts DROP COLUMN promise`（SQLite 3.35+ 支持）

---

### 5.4 阶段2：修复 gates.event_driven 写入（#ARCH-009）

**动作2.1**：修改 `scripts/governance/sync_yaml_to_depgraph.py` 的 `sync_gate_registry`（L298-327）

将 L308-323 的 INSERT 语句修改为写入全部 11 列：

```python
        cur.execute(
            """
        INSERT OR REPLACE INTO gates
        (gate_id, name, entry, description, files_trigger, always_run,
         category, status, source, event_driven, auto_start)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                gate.get("gate_id", ""),
                gate.get("name", ""),
                gate.get("entry", ""),
                gate.get("description", ""),
                gate.get("files_trigger", ""),
                1 if gate.get("always_run", False) else 0,
                gate.get("category", ""),
                gate.get("status", "active"),
                gate.get("source", ".pre-commit-config.yaml"),
                gate.get("event_driven", ""),
                1 if gate.get("auto_start", True) else 0,
            ),
        )
```

**动作2.2**：确认 `gate_registry.yaml` 中有 `event_driven` / `auto_start` / `source` 字段

```bash
# 检查 YAML 真源是否已声明这些字段
python -c "import yaml; d=yaml.safe_load(open(r'D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\gate_registry.yaml',encoding='utf-8')); g=d.get('gates',[]); print([k for k in g[0].keys()] if g else 'empty')"
```

若 YAML 无此字段，需在 `gate_registry.yaml` 的 gate 条目中补充（按 gate 实际配置）。

**动作2.3**：重新同步并验证

```bash
python scripts/governance/sync_yaml_to_depgraph.py
# 验证 event_driven 不再全空
python -c "import sqlite3; c=sqlite3.connect(r'D:\ZephyrAlpha\data\databases\depgraph.db'); print([r for r in c.execute(\"SELECT gate_id, event_driven, auto_start FROM gates WHERE event_driven != ''\")])"
```

**验证**：若有事件门禁，应返回非空结果

**回滚**：`git checkout -- scripts/governance/sync_yaml_to_depgraph.py`

---

### 5.5 阶段3：修复 generate_project_depgraph.py（#ARCH-010）

**动作3.1**：修改 `scripts/governance/generate_project_depgraph.py`（L2673, L2692, L2721）

从 INSERT 列名列表（L2673 附近）移除 `"module_lifecycle_state"`，从 VALUES（L2692 附近）移除 `module_lifecycle_state` 变量，从值来源（L2721 附近）移除 `node.get("module_lifecycle_state", "")`。

**具体操作**：阅读 L2660-2730 区域的完整 INSERT 语句，删除三处 `module_lifecycle_state` 引用。

**动作3.2**：验证生成器可运行

```bash
python scripts/governance/generate_project_depgraph.py --dry-run
# 或在测试库上验证（禁止直接跑生产库）
```

**验证**：无 `sqlite3.OperationalError: no such column: module_lifecycle_state`

**回滚**：`git checkout -- scripts/governance/generate_project_depgraph.py`

---

### 5.6 阶段4：删除 4 张死表 + 标注 1 张 deprecated（#ARCH-011~015）

> **注意**：删除表需添加 migration v14（在 v13 之后）。SQLite 不支持 `DROP TABLE IF EXISTS` 在 migration 中直接用（需确保表存在）。使用 `DROP TABLE IF EXISTS` 语法。

**动作4.1**：在 `depgraph_schema.py` 添加 migration v14（在 v13 之后）

```python
    (
        14,
        "v14: Drop 4 dead tables (governance_audit_logs/arch_layers/arch_bottlenecks/invariants) — fix #ARCH-012~015",
        [
            "DROP TABLE IF EXISTS governance_audit_logs",
            "DROP TABLE IF EXISTS arch_layers",
            "DROP TABLE IF EXISTS arch_bottlenecks",
            "DROP TABLE IF EXISTS invariants",
        ],
    ),
```

**动作4.2**：在 `_DDL_*` 声明中移除已删除表的 DDL

- 移除 `_DDL_GOVERNANCE_AUDIT_LOGS`（L491-502）
- 移除 `_DDL_ARCH_LAYERS`（L294-302）
- 移除 `_DDL_ARCH_BOTTLENECKS`（L250-262）
- 移除 `_DDL_INVARIANTS`（L220-228）

**注意**：保留 `_DDL_*` 常量定义但不在 v1 migration 中引用（因 v1 已执行过，历史 DB 已有这些表）。v14 的 DROP 负责清理。Fresh clone 执行 v1 时会创建这些表，v14 会删除——这是可接受的（幂等）。

> **替代方案（更优）**：将已删除表的 DDL 从 v1 migration 的语句列表中移除，这样 fresh clone 不会创建这些表。但因 v1 已在生产 DB 执行过，对生产 DB 无影响（`CREATE TABLE IF NOT EXISTS` 幂等）。v14 的 DROP 确保生产库也被清理。**推荐：v1 中保留 DDL 不动（避免改 v1 历史迁移），v14 负责删除。**

**动作4.3**：标注 cross_registry_rules 为 deprecated

在 `_DDL_CROSS_REGISTRY_RULES`（L529-540）的注释中添加：

```python
# [DEPRECATED] #ARCH-011 — 此表声明了但从未接线 sync 函数，ssot NOT NULL 导致无法 INSERT
# 保留表结构待未来接线，但标注为 deprecated 状态
```

**动作4.4**：清理读取已删除表的代码

- `src/zephyr/governance/depgraph_reader.py`：移除读取 `arch_layers`（L204）、`invariants`、`rule_bindings` 中涉及已删除表的方法（注意 rule_bindings 不删，仅删 arch_layers/invariants 相关方法）
- `src/zephyr/governance/auto_runner.py`：移除 `_write_audit_log`（L194-233）方法及其调用点
- `scripts/governance/sync_yaml_to_depgraph.py`：若有 `sync_invariants` 函数，移除或标注 deprecated

**动作4.5**：清理测试中对已删除表的引用

- `tests/test_depgraph_db.py`：移除对 `invariants`（L143）、`arch_layers`（L156）、`arch_bottlenecks`（L172）的测试用例
- `tests/test_f18_redblue.py` / `tests/test_f18_automation.py`：移除对 `governance_audit_logs` 的测试用例

**动作4.6**：运行迁移并验证

```bash
python -c "from zephyr.governance.depgraph_schema import init_db; init_db(echo=True)"
# 验证表已删除
python -c "import sqlite3; c=sqlite3.connect(r'D:\ZephyrAlpha\data\databases\depgraph.db'); print([r[0] for r in c.execute(\"SELECT name FROM sqlite_master WHERE type='table' ORDER BY name\")])"
```

**验证**：输出列表中不含 `governance_audit_logs` / `arch_layers` / `arch_bottlenecks` / `invariants`

**回滚**：`git reset --hard <阶段0备份>` + 重新 `init_db()` 重建表

---

### 5.7 阶段5：创建 verify_schema_health.py 门禁（#ARCH-016）

**动作5.1**：新建 `scripts/governance/d7_code/verify_schema_health.py`

**脚本职责**（3 项校验）：

1. **DDL 列一致性**：对比 DB 实际列（`PRAGMA table_info(<table>)`）与 `_DDL_*` 声明的列名列表
2. **只读触发器存在性**：验证 `READONLY_TABLES` 中每张表的 3 个只读触发器（insert/update/delete）存在
3. **Schema 版本一致性**：验证 `_schema_version` 最大值 == `len(_MIGRATIONS)`

**脚本设计**：

```python
#!/usr/bin/env python3
"""
verify_schema_health.py — depgraph.db Schema 健康度校验门禁（#ARCH-016）

校验内容：
  1. DDL 列一致性：DB 实际列 vs _DDL_* 声明列
  2. 只读触发器存在性：READONLY_TABLES 的 9 张表 × 3 触发器
  3. Schema 版本一致性：_schema_version == len(_MIGRATIONS)

退出码：
  0 = 健康（PASS）
  1 = 发现漂移（FAIL）

模式：
  --ci          硬阻断模式（默认，发现漂移 exit 1）——与其他 GATE 一致
  --warn-only   软警告模式（发现漂移仍 exit 0）——用于观察期
"""
import argparse
import re
import sqlite3
import sys
from pathlib import Path

# 加载 _shared.constants
_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS  # noqa: E402

# 加载 depgraph_schema 的 DDL 声明和 migration 列表
_REPO_ROOT = str(next(p for p in _THIS_FILE.parents if (p / "src" / "zephyr").exists()))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, str(Path(_REPO_ROOT) / "src"))
from zephyr.governance import depgraph_schema  # noqa: E402

from _shared.constants import DEPGRAPH_DB_PATH  # noqa: E402


def parse_ddl_columns(ddl: str) -> list[str]:
    """从 CREATE TABLE DDL 文本中解析列名列表。"""
    # 提取括号内内容
    match = re.search(r"CREATE TABLE\s+(?:IF NOT EXISTS\s+)?(\w+)\s*\((.*)\)", ddl, re.DOTALL)
    if not match:
        return []
    body = match.group(2)
    columns = []
    depth = 0
    current = ""
    for char in body:
        if char == "(":
            depth += 1
            current += char
        elif char == ")":
            depth -= 1
            current += char
        elif char == "," and depth == 0:
            col_def = current.strip()
            if col_def and not col_def.upper().startswith((
                "PRIMARY", "FOREIGN", "CHECK", "UNIQUE", "CONSTRAINT"
            )):
                col_name = col_def.split()[0]
                columns.append(col_name)
            current = ""
        else:
            current += char
    # 最后一列
    col_def = current.strip()
    if col_def and not col_def.upper().startswith((
        "PRIMARY", "FOREIGN", "CHECK", "UNIQUE", "CONSTRAINT"
    )):
        col_name = col_def.split()[0]
        columns.append(col_name)
    return columns


def check_ddl_columns(conn, issues: list) -> None:
    """校验1：DB 实际列 vs DDL 声明列。"""
    # DDL 声明 → 表名映射
    ddl_map = {
        "nodes": depgraph_schema._DDL_NODES_V5,
        "edges": depgraph_schema._DDL_EDGES_V5,
        "domains": depgraph_schema._DDL_DOMAINS,
        "domain_dependencies": depgraph_schema._DDL_DOMAIN_DEPS,
        "domain_events": depgraph_schema._DDL_DOMAIN_EVENTS,
        "contracts": depgraph_schema._DDL_CONTRACTS,
        "rule_bindings": depgraph_schema._DDL_RULE_BINDINGS,
        "arch_constraints": depgraph_schema._DDL_ARCH_CONSTRAINTS,
        "arch_directory_tree": depgraph_schema._DDL_ARCH_DIR_TREE_V5,
        "arch_path_mappings": depgraph_schema._DDL_ARCH_PATH_MAPPINGS,
        "gates": depgraph_schema._DDL_GATES,
        "blueprint_links": depgraph_schema._DDL_BLUEPRINT_LINKS,
        "business_streams": depgraph_schema._DDL_BUSINESS_STREAMS,
        "cross_registry_rules": depgraph_schema._DDL_CROSS_REGISTRY_RULES,
        "field_vocabularies": depgraph_schema._DDL_FIELD_VOCABULARIES,
        "hard_boundaries": depgraph_schema._DDL_HARD_BOUNDARIES,
        "infrastructure_components": depgraph_schema._DDL_INFRASTRUCTURE_COMPONENTS,
        "model_capabilities": depgraph_schema._DDL_MODEL_CAPABILITIES,
        "registries": depgraph_schema._DDL_REGISTRIES,
        "domain_mapping": depgraph_schema._DDL_DOMAIN_MAPPING,
    }
    for table, ddl in ddl_map.items():
        declared = set(parse_ddl_columns(ddl))
        cursor = conn.execute(f"PRAGMA table_info({table})")
        actual = {row[1] for row in cursor.fetchall()}
        if not actual:
            issues.append(f"[DDL-DRIFT] 表 '{table}' 不存在于 DB 中")
            continue
        missing_in_db = declared - actual
        extra_in_db = actual - declared
        if missing_in_db:
            issues.append(f"[DDL-DRIFT] 表 '{table}' DB 缺少列: {sorted(missing_in_db)}")
        if extra_in_db:
            issues.append(f"[DDL-DRIFT] 表 '{table}' DB 多出列（DDL 未声明）: {sorted(extra_in_db)}")


def check_readonly_triggers(conn, issues: list) -> None:
    """校验2：只读触发器存在性。"""
    readonly_tables = [
        "gates", "field_vocabularies", "registries", "cross_registry_rules",
        "hard_boundaries", "business_streams", "infrastructure_components",
        "model_capabilities", "blueprint_links",
    ]
    for table in readonly_tables:
        for action in ("insert", "update", "delete"):
            trig_name = f"readonly_{table}_{action}"
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='trigger' AND name=?",
                (trig_name,),
            )
            if cursor.fetchone() is None:
                issues.append(f"[TRIGGER-MISSING] 只读触发器 '{trig_name}' 不存在（表 {table} 未受只读保护）")


def check_schema_version(conn, issues: list) -> None:
    """校验3：Schema 版本一致性。"""
    expected = len(depgraph_schema._MIGRATIONS)
    cursor = conn.execute("SELECT COALESCE(MAX(version), 0) FROM _schema_version")
    actual = cursor.fetchone()[0]
    if actual != expected:
        issues.append(
            f"[VERSION-DRIFT] _schema_version={actual} 但 _MIGRATIONS 有 {expected} 条迁移"
            f"（差 {expected - actual} 条未执行）"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="depgraph.db Schema 健康度校验")
    parser.add_argument("--db", default=str(DEPGRAPH_DB_PATH), help="depgraph.db 路径")
    parser.add_argument("--ci", action="store_true", help="硬阻断模式（默认行为，与其他 GATE 一致）")
    parser.add_argument("--warn-only", action="store_true", help="软警告模式（发现漂移仍 exit 0）")
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"[ERROR] DB 不存在: {db_path}")
        return EXIT_FINDINGS

    conn = sqlite3.connect(str(db_path))
    issues: list[str] = []
    try:
        check_ddl_columns(conn, issues)
        check_readonly_triggers(conn, issues)
        check_schema_version(conn, issues)
    finally:
        conn.close()

    if issues:
        print(f"[FAIL] 发现 {len(issues)} 项 Schema 健康度问题:")
        for issue in issues:
            print(f"  {issue}")
        # --warn-only 优先于 --ci；两者均未指定时默认硬阻断（与 --ci 等效）
        return EXIT_PASS if args.warn_only else EXIT_FINDINGS

    print("[PASS] depgraph.db Schema 健康度校验通过")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
```

**动作5.2**：验证脚本可运行

```bash
python scripts/governance/d7_code/verify_schema_health.py --warn-only
```

**验证**：脚本无 ImportError，能输出校验结果（阶段1-4 完成后应 PASS）

**回滚**：删除 `scripts/governance/d7_code/verify_schema_health.py`

---

### 5.8 阶段6：注册 GATE-SCHEMA-HEALTH（#ARCH-017）

**动作6.1**：在 `.pre-commit-config.yaml` 的 local hooks 列表中添加

```yaml
      # ── GATE-SCHEMA-HEALTH: depgraph.db Schema 健康度校验（#ARCH-016 治本）──
      # 权威依据：depgraph_schema.py 是 DDL 真源，DB 物理状态必须与 DDL 声明一致
      # 检测范围：depgraph_schema.py 或 sync_yaml_to_depgraph.py 变更时触发
      # 检测内容：DDL 列一致性 + 只读触发器存在性 + Schema 版本一致性
      # 模式：--ci 硬阻断（漂移 exit 1 拒绝提交）
      - id: gate-schema-health
        name: "GATE-SCHEMA-HEALTH: depgraph.db Schema 健康度校验"
        entry: python scripts/governance/d7_code/verify_schema_health.py
        args: ["--ci"]
        language: system
        pass_filenames: false
        always_run: false
        files: "^(src/zephyr/governance/depgraph_schema\\.py|scripts/governance/sync_yaml_to_depgraph\\.py|scripts/governance/d7_code/verify_schema_health\\.py)$"
        description: "depgraph.db Schema 健康度校验——DDL 列一致性 + 只读触发器 + 版本一致性，漂移即阻断。对标 #ARCH-016 治本"
```

**动作6.2**：验证门禁可触发

```bash
pre-commit run gate-schema-health --all-files
```

**验证**：输出 `[PASS] depgraph.db Schema 健康度校验通过`（阶段1-4 完成后）

**回滚**：从 `.pre-commit-config.yaml` 移除 gate-schema-health 条目

---

### 5.9 阶段7：同步文档与索引（#ARCH-018）

**动作7.1**：更新 `docs/02_enterprise_architecture/dependency_architecture_panorama.md` §4.4 表归属矩阵

- 移除已删除的 4 张表（governance_audit_logs / arch_layers / arch_bottlenecks / invariants）
- 更新 contracts 表列数：7 → 13
- 标注 cross_registry_rules 为 deprecated

**动作7.2**：更新 `scripts/governance/script_manifest.yaml`

- 添加 `verify_schema_health.py` 条目

**动作7.3**：更新 `.trae/rules/project_rules.md` RULE-SIXTEEN

- 在 depgraph.db 修改规则中追加："结构变更必须先改 `depgraph_schema.py` 的 `_DDL_*` 声明 + 添加 migration，禁止直接改写入代码跳过 DDL"

**动作7.4**：更新 `src/zephyr/governance/rule_enforcement/gate_registry.yaml`

- 添加 GATE-SCHEMA-HEALTH 条目（供 auto_runner 事件驱动使用，若接线）

**动作7.5**：更新 `docs/02_enterprise_architecture/03_governance_reports/`

- 在治理报告索引中添加本治本方案文档的链接

**动作7.6**：更新 `AGENTS.md`（若涉及）

- 在 DB 操作约定中追加 Schema 健康度门禁的说明

---

### 5.10 验收标准

| 验收项 | 验证命令 | 预期结果 |
|--------|----------|----------|
| migration v13/v14 已执行 | `python -c "from zephyr.governance.depgraph_schema import schema_version; print(schema_version())"` | `14` |
| contracts 有 13 列 | `python -c "import sqlite3; c=sqlite3.connect(r'D:\ZephyrAlpha\data\databases\depgraph.db'); print(len(c.execute('PRAGMA table_info(contracts)').fetchall()))"` | `13` |
| gates.event_driven 可写入 | `python scripts/governance/sync_yaml_to_depgraph.py` 后检查 | 非空（若有事件门禁） |
| 4 张死表已删除 | `python -c "import sqlite3; c=sqlite3.connect(r'D:\ZephyrAlpha\data\databases\depgraph.db'); print([r[0] for r in c.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name IN ('governance_audit_logs','arch_layers','arch_bottlenecks','invariants')\")])"` | `[]`（空列表） |
| verify_schema_health.py PASS | `python scripts/governance/d7_code/verify_schema_health.py` | `exit 0`，`[PASS]` |
| GATE-SCHEMA-HEALTH 注册 | `grep "gate-schema-health" .pre-commit-config.yaml` | 有匹配 |
| 生成器可运行 | `python scripts/governance/generate_project_depgraph.py --dry-run` | 无 OperationalError |

### 5.11 回滚方案

**整体回滚**（若施工后发现严重问题）：

```bash
# 通过 GitCommitGateway 执行
git reset --hard <阶段0备份commit>
python -c "from zephyr.governance.depgraph_schema import init_db; init_db(echo=True)"
# 重建已删除的表（v1 migration 的 CREATE TABLE IF NOT EXISTS 会重建）
# 重新同步数据
python scripts/governance/sync_yaml_to_depgraph.py
```

**单阶段回滚**：每个阶段独立 `git checkout -- <file>` + 重跑 `init_db()`

---

## 第六部分：总结

### 6.1 问题根因一句话总结

depgraph.db 的 Schema 漂移和死表堆积，根因是**"DDL 真源与写入代码脱节 + 缺乏机械化的反向校验"**——在 100% AI 开发中，不同 AI session 分别修改 DDL 和写入代码，无人做交叉验证，导致 DB 物理状态与声明不一致。

### 6.2 治本方案一句话总结

**补齐 DDL 声明（migration v13/v14）+ 修复写入断裂 + 删除死表 + 新建 `verify_schema_health.py` 门禁**，用机械校验替代 AI 认知盲区，从结构上防止漂移复发。

### 6.3 长期战略考虑

1. **verify_schema_health.py 是防漂移的第一道防线**：每次 `depgraph_schema.py` 或 `sync_yaml_to_depgraph.py` 变更时自动校验 DB↔DDL 一致性
2. **死表清理是 SSoT 纯化**：删除无人读取的 DB 副本，消除"DB↔YAML 漂移无感知"的风险源
3. **事件门禁修复恢复功能价值**：gates.event_driven 写入修复后，auto_runner 的事件驱动调度恢复可用
4. **本方案与 anti_hallucination 体系互补**：verify_schema_health.py 与 mutation testing / post_sync_validator 共同构成"防幻觉三重校验"

### 6.4 风险评估

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| migration v13 在已含 6 列的 DB 上失败 | 低 | 中 | `ALTER TABLE ADD COLUMN` 在列已存在时报错，但 `_run_migration` 的 benign 列表含 "duplicate column name" 会跳过 |
| 删除 invariants 表后某隐藏读取者报错 | 低 | 中 | 全量 grep 已确认仅 test 读取；删除前在 warn-only 模式运行一轮观察 |
| generate_project_depgraph.py 改动遗漏 | 中 | 高 | 删除 INSERT 中 module_lifecycle_state 后必须 dry-run 验证 |

---

## 附录A：受影响文件清单矩阵

| # | 文件路径 | 变更类型 | 关联议题 | 阶段 |
|---|----------|----------|----------|------|
| 1 | `src/zephyr/governance/depgraph_schema.py` | 改：补齐 `_DDL_CONTRACTS` 6 列 + 添加 migration v13/v14 + 移除/标注已删除表 DDL | #ARCH-008, #011~015 | 1, 4 |
| 2 | `scripts/governance/sync_yaml_to_depgraph.py` | 改：`sync_gate_registry` 补写 3 列 + 移除 sync_invariants（若有） | #ARCH-009, #015 | 2, 4 |
| 3 | `scripts/governance/generate_project_depgraph.py` | 改：移除 INSERT 中 module_lifecycle_state | #ARCH-010 | 3 |
| 4 | `scripts/governance/d7_code/verify_schema_health.py` | 新建：Schema 健康度校验脚本 | #ARCH-016 | 5 |
| 5 | `.pre-commit-config.yaml` | 改：注册 GATE-SCHEMA-HEALTH | #ARCH-017 | 6 |
| 6 | `src/zephyr/governance/auto_runner.py` | 改：移除 `_write_audit_log` + 调用点 | #ARCH-012 | 4 |
| 7 | `src/zephyr/governance/depgraph_reader.py` | 改：移除读取已删除表的方法（arch_layers/invariants） | #ARCH-013, #015 | 4 |
| 8 | `tests/test_depgraph_db.py` | 改：移除已删除表的测试用例 | #ARCH-012~015 | 4 |
| 9 | `tests/test_f18_redblue.py` | 改：移除 governance_audit_logs 测试 | #ARCH-012 | 4 |
| 10 | `tests/test_f18_automation.py` | 改：移除 governance_audit_logs 测试 | #ARCH-012 | 4 |
| 11 | `docs/02_enterprise_architecture/dependency_architecture_panorama.md` | 改：更新表归属矩阵 | #ARCH-018 | 7 |
| 12 | `scripts/governance/script_manifest.yaml` | 改：添加 verify_schema_health.py 条目 | #ARCH-018 | 7 |
| 13 | `.trae/rules/project_rules.md` | 改：RULE-SIXTEEN 追加 DDL 真源规则 | #ARCH-018 | 7 |
| 14 | `src/zephyr/governance/rule_enforcement/gate_registry.yaml` | 改：添加 GATE-SCHEMA-HEALTH 条目 | #ARCH-018 | 7 |
| 15 | `docs/02_enterprise_architecture/03_governance_reports/` | 改：索引中添加本方案文档链接 | #ARCH-018 | 7 |
| 16 | `docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml` | 改：gate 条目补 event_driven/auto_start/source 字段（若缺失） | #ARCH-009 | 2 |

---

## 附录B：议题清单（#ARCH-XXX）

| #ARCH | 标题 | 严重度 | 裁定 | 施工阶段 | 状态 |
|-------|------|--------|------|----------|------|
| #ARCH-008 | contracts 表 Schema 漂移（DDL 7 列 vs 写入 13 列） | P0 致命 | 修复 DDL + migration v13 | 阶段1 | 待施工 |
| #ARCH-009 | gates.event_driven 写入断裂（sync 遗漏 3 列） | P1 高 | 修复 sync_gate_registry | 阶段2 | 待施工 |
| #ARCH-010 | generate_project_depgraph.py 写入已删除列 | P0 致命 | 清理残留 INSERT | 阶段3 | 待施工 |
| #ARCH-011 | cross_registry_rules 声明但未接线 | P2 中 | 标注 deprecated | 阶段4 | 待施工 |
| #ARCH-012 | governance_audit_logs 假审计表 | P1 高 | 删除表 + 移除写入 | 阶段4 | 待施工 |
| #ARCH-013 | arch_layers 残留表（v6 合并后冗余） | P1 高 | 删除表 + 清理读取者 | 阶段4 | 待施工 |
| #ARCH-014 | arch_bottlenecks 空表 | P2 中 | 删除表 | 阶段4 | 待施工 |
| #ARCH-015 | invariants DB 副本漂移（255 vs YAML 20） | P1 高 | 删除 DB 表 | 阶段4 | 待施工 |
| #ARCH-016 | verify_schema_health.py 门禁缺失 | P0 致命 | 新建校验脚本 | 阶段5 | 待施工 |
| #ARCH-017 | GATE-SCHEMA-HEALTH 未注册 | P0 致命 | 注册到 pre-commit | 阶段6 | 待施工 |
| #ARCH-018 | 文档与索引未同步 | P2 中 | 更新 6 个文档/索引 | 阶段7 | 待施工 |

---

## 附录C：循环审查记录

### 第一轮审查（自审）

| # | 审查项 | 发现问题 | 修复 |
|---|--------|----------|------|
| C1-1 | 事实层行号准确性 | `_DDL_CONTRACTS` 引用 L204-214 ✓；`sync_declarative_contract_tracker` 引用 L524-564 ✓；`sync_gate_registry` 引用 L298-327 ✓ | 无需修复 |
| C1-2 | 裁定与施工方案对应 | #ARCH-008~018 每个议题都有对应施工阶段 ✓ | 无需修复 |
| C1-3 | 受影响文件完整性 | 缺少 `gate_registry.yaml`（YAML 真源需补字段）→ 已补充为 #16 | 已修复 |
| C1-4 | 死表判定准确性 | 修正前序"10 死表"为"4 真死表 + 6 低利用表"，附 grep 证据 ✓ | 已修正 |
| C1-5 | migration 版本连续性 | v13（contracts 修复）→ v14（删表），连续无跳号 ✓ | 无需修复 |
| C1-6 | verify_schema_health.py 设计完整性 | 3 项校验覆盖 DDL/触发器/版本 ✓；退出码对标 _shared.constants ✓ | 无需修复 |
| C1-7 | 内部冲突检查 | §1.2 称 contracts "DDL 7 列 vs 写入 13 列"，§5.3 修复后应为 13 列 ✓ 一致 | 无需修复 |
| C1-8 | 回滚方案可行性 | 整体回滚依赖阶段0备份 + init_db 重建表 ✓ | 无需修复 |

### 第二轮审查（自审）

| # | 审查项 | 发现问题 | 修复 |
|---|--------|----------|------|
| C2-1 | migration v14 删表与 v1 建表的幂等性 | v1 的 `CREATE TABLE IF NOT EXISTS` 会在 fresh clone 建表，v14 的 `DROP TABLE IF EXISTS` 会删除 → fresh clone 最终无死表 ✓ 幂等 | 无需修复 |
| C2-2 | verify_schema_health.py 的 DDL→表名映射完整性 | 检查 ddl_map 是否覆盖所有存活的表 → 覆盖 20 张表，已删除的 4 张不在映射中 ✓ | 无需修复 |
| C2-3 | auto_runner._write_audit_log 移除后的影响 | 移除写入路径后，auto_runner 是否有其他依赖 → 需在施工时检查调用链 | 标注为施工注意事项 |
| C2-4 | cross_registry_rules 标注 deprecated 但不删的合理性 | 表有 `ssot NOT NULL` 约束导致无法 INSERT，标注 deprecated 不影响现有功能 ✓ | 无需修复 |
| C2-5 | 验收标准可执行性 | 所有验收命令均可在 Windows PowerShell 执行 ✓ | 无需修复 |

### 第三轮审查（自审——聚焦 verify_schema_health.py 与门禁配置一致性）

| # | 审查项 | 发现问题 | 修复 |
|---|--------|----------|------|
| C3-1 | **门禁 `args: ["--ci"]` 与脚本 argparse 不一致** | §5.8 pre-commit 配置用 `args: ["--ci"]`，但 §5.7 脚本 argparse 原本只有 `--warn-only`，无 `--ci` flag → argparse 会报 unrecognized arguments 错误 | **已修复**：在 argparse 中添加 `--ci` flag（硬阻断模式，与项目其他 GATE 一致），`--warn-only` 优先于 `--ci`；默认无 flag 时也是硬阻断（与 --ci 等效） |
| C3-2 | `_DDL_CONTRACTS` 修复后列数一致性 | §5.3 动作1.1 修复后的 `_DDL_CONTRACTS` 含 13 列（7 原始 + 6 扩展），§1.2 称"写入 13 列" ✓ 一致 | 无需修复 |
| C3-3 | migration v13 的 ALTER TABLE 与 benign 列表兼容性 | 生产 DB 已有 6 列（历史手动添加），v13 的 `ALTER TABLE ADD COLUMN` 会报 "duplicate column name" → `_run_migration` 的 benign 列表（L944-950）含 "duplicate column name" 会跳过 ✓ 安全 | 无需修复 |
| C3-4 | verify_schema_health.py 中 ddl_map 与存活表数 | ddl_map 含 20 张表（删除 4 张死表后剩 21 张存活表，其中 `_schema_version` 系统表不校验），20 + 1 = 21 ✓ | 无需修复 |
| C3-5 | §1.1 "4 张死表"与裁定汇总 #ARCH-011~015 的关系 | #ARCH-011（cross_registry_rules）裁定为"标注 deprecated"非"删除"，不计入"4 张死表"；4 张死表 = #ARCH-012~015 ✓ 一致 | 无需修复 |

**三轮审查后，问题数 = 0（C3-1 已修复，其余无冲突）。**

---

> **文档状态**：调研完成，待用户审批后进入施工阶段。
> **审批后操作**：按阶段0→7顺序施工，每阶段完成后运行验收命令确认。
