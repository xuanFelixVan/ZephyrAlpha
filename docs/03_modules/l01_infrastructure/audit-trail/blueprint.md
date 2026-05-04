---
module_id: "MOD-INF-020"
title: "审计追踪链蓝图 — 不可变动作审计 + 分级 Provenance"
doc_type: blueprint
status: draft
version: "0.2.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-05"
valid_from: "2026-05-05"
ttl: permanent
construction_progress: not_started
summary: "ZephyrAlpha 审计追踪链蓝图——每个 AI 动作的不可变审计记录。两层审计粒度（任务级摘要+文件级明细）+ JSONL 为唯一真源 + SQLite 为派生查询索引 + Provenance 按权限级别分级（always_allow 轻量/auto_guard 完整/blocked 全量）。对标 Goldman SecDB immutable audit log + ISACA 2025。"
tags: [audit-trail, provenance, immutable-log, traceability, compliance, infrastructure]
priority: P0
depends_on:
  - {target: "MOD-INF-018", at: "§2.2", why: "Agent RBAC——审计记录的 subject 是 AgentIdentity + 权限级别决定 provenance 深度"}
  - {target: "MOD-INF-012", at: "§3", why: "Database——SQLite 派生查询索引的存储"}
  - {target: "MOD-INF-015", at: "§2", why: "System Telemetry——审计事件的遥测发射"}
---

# 审计追踪链蓝图 — 不可变动作审计

> **module_id**: MOD-INF-020 | **version**: 0.2.0 | **status**: draft | **layer**: cross_layer

> **对标**：Goldman SecDB immutable audit log（每个动作可追溯到毫秒）+ ISACA 2025 Agentic AI 审计三要素（agent身份+执行动作+使用工具）+ JPM Athena 审计链。

---

## 1. 概述与模块定位

### 1.1 模块身份

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-020 |
| 代码落位 | `src/zephyr/audit_trail/` |
| 运行时平面 | Hot memory（每个操作同步写入，延迟 < 5ms） |
| 核心职责 | 记录"谁在什么时候用什么工具做了什么"——不可变、不可篡改、唯一真源 |

### 1.2 核心职能（一句话）

**Audit Trail 是系统的黑匣子**——每个 AI 动作都有审计记录。出了问题可以回溯到任意时刻的任意操作，找到根因。JSONL 是唯一真源，SQLite 是派生查询索引。

### 1.3 运行场景约束

| 约束 | 影响 |
|------|------|
| 多 IDE 并发（TRAE/Cursor/RooCode） | 审计日志必须跨 IDE 统一——JSONL 是唯一所有 IDE 都能 append 的格式 |
| 10+ 并发对话 | 审计量可能很大——需要两层粒度，不能全是文件级 |
| 1 人 + AI，99% AI 维护 | 大部分操作没有"草稿"和"仲裁"——Provenance 不能强制三件套 |
| 先干后验模式 | 审计日志是后验的基础——没有审计就没有后验 |

### 1.4 当前痛点

| # | 痛点 | 后果 |
|---|------|------|
| 1 | 只有 blueprint_reads.jsonl（蓝图读取日志） | AI 改了代码但不知道它读了哪些蓝图、跳过了哪些门禁 |
| 2 | session-logs/ 是人工维护 | 不完整、不及时、格式不统一 |
| 3 | Provenance 三件套强制要求但无运行时执行 | 大部分操作没有草稿和仲裁——要求形同虚设 |
| 4 | 审计日志可修改 | SQLite 存储可被 AI 直接 UPDATE——违反不可变原则 |
| 5 | 没有唯一真源 | SQLite 和 JSONL 各写各的——数据可能不一致 |

---

## 2. 核心架构

### 2.1 两层审计粒度（决策 D-020-01）

> **决策 D-020-01**：审计粒度采用两层——任务级摘要（快速浏览）+ 文件级明细（问题定位）。任务级记录是主表，文件级记录是明细表，通过 task_id 关联。
>
> **决策依据**：1人+AI场景，审计日志主要是给 Owner"有空时翻翻"用的，任务级摘要就够了；但出了问题需要定位时，文件级明细不可少。对标 SecDB 的 trade-level + tick-level 两层审计。

```python
class TaskAuditSummary(BaseModel):
    event_id: str = Field(..., description="格式 AUD-T-{TIMESTAMP}-{SEQ}")
    timestamp: datetime = Field(..., description="UTC 毫秒精度")
    agent_id: str = Field(..., description="执行者——引用 AgentIdentity.agent_id")
    ide_source: str = Field(..., description="来源 IDE——trae/cursor/roocode")
    session_id: str = Field(..., description="会话 ID")
    task_id: str = Field(..., description="任务 ID")
    task_type: str = Field(..., description="任务类型——architect/implementer/governor")
    action_summary: str = Field(..., description="操作摘要——如'实现 MOD-INF-018 scaffold'")
    files_affected: int = Field(..., description="影响文件数")
    result: str = Field(..., description="success/fail/partial/rolled_back")
    permission_level: str = Field(..., description="always_allow/auto_guard/blocked")
    provenance_depth: ProvenanceDepth = Field(..., description="Provenance 深度——由权限级别决定")

class FileAuditDetail(BaseModel):
    event_id: str = Field(..., description="格式 AUD-F-{TIMESTAMP}-{SEQ}")
    task_audit_id: str = Field(..., description="关联的任务级审计 ID")
    timestamp: datetime
    file_path: str = Field(..., description="文件路径")
    action_type: FileActionType = Field(..., description="read/write/create/delete")
    sha256_before: Optional[str] = Field(default=None, description="操作前 SHA-256")
    sha256_after: Optional[str] = Field(default=None, description="操作后 SHA-256")

class FileActionType(str, Enum):
    READ = "read"
    WRITE = "write"
    CREATE = "create"
    DELETE = "delete"
```

### 2.2 JSONL 为唯一真源（决策 D-020-02）

> **决策 D-020-02**：JSONL 文件是审计日志的**唯一真源（SSoT）**，SQLite 是从 JSONL 派生的查询索引。写入流程：AI 操作 → 追加写入 JSONL → 异步重建 SQLite 索引。查询流程：读 SQLite → 如果 SQLite 不可用则回退读 JSONL。
>
> **决策依据**：
> 1. 多 IDE 并发场景——JSONL 是唯一所有 IDE 都能 append 的格式（SQLite 多进程写入有锁竞争）
> 2. 不可变性——JSONL 天然 append-only，不存在 UPDATE/DELETE 的可能
> 3. Git 友好——JSONL 可以放在 git 里，跨 IDE 共享，历史可追溯
> 4. 对标项目已有 blueprint_reads.jsonl 的成功实践
>
> 这与 GOV-AI-001 → rbac_roles.yaml 的派生模式一致：人类可读/可追加的格式是真源，机器可查询的格式是派生物。

```yaml
storage_ssoT:
  primary:
    format: "JSONL"
    path: "data/audit/audit-trail.jsonl"
    write_mode: "append-only——每个操作追加一行"
    rotation: "按日轮转——audit-trail-2026-05-05.jsonl"
    retention: "permanent——ttl=permanent，永不删除"
    git_tracked: true
    immutable_guarantee: "JSONL 天然 append-only，不存在 UPDATE/DELETE"

  derived:
    format: "SQLite"
    path: "data/audit/audit-index.db"
    write_mode: "异步重建——从 JSONL 派生"
    rebuild_trigger: "JSONL 追加后 5s / 手动触发 / CI 启动时"
    purpose: "查询加速——按 agent/target/时间/任务类型查询"
    fallback: "SQLite 不可用时，直接扫描 JSONL（较慢但保证可用）"

  consistency_check:
    ci_gate: "CI 门禁校验 SQLite 记录数 == JSONL 行数"
    rebuild_script: "scripts/governance/rebuild_audit_index.py"
```

### 2.3 分级 Provenance（决策 D-020-03）

> **决策 D-020-03**：Provenance 深度由权限级别决定——always_allow 只记录轻量 provenance，auto_guard 记录完整 provenance，blocked 记录全量 provenance（含阻断原因）。大部分操作没有"草稿"和"仲裁"，不应强制要求三件套。
>
> **决策依据**：1人+AI场景，99% 操作是 AI 自主执行，没有人类草稿和仲裁。强制要求三件套 = 大部分操作无法满足 = 要求形同虚设。分级 provenance 更务实。

```python
class ProvenanceDepth(str, Enum):
    LIGHT = "light"        # always_allow 操作
    STANDARD = "standard"  # auto_guard 操作
    FULL = "full"          # blocked 操作（阻断记录）

class ProvenanceLight(BaseModel):
    agent_id: str
    timestamp: datetime
    action_type: str
    ide_source: str

class ProvenanceStandard(BaseModel):
    agent_id: str
    timestamp: datetime
    action_type: str
    ide_source: str
    decision_basis: list[str] = Field(default_factory=list, description="决策依据——读了哪些蓝图/门禁结果")
    guard_checks: list[str] = Field(default_factory=list, description="后验检查项")
    guard_result: Optional[str] = Field(default=None, description="后验结果——pass/fail/rolled_back")

class ProvenanceFull(BaseModel):
    agent_id: str
    timestamp: datetime
    action_type: str
    ide_source: str
    blocked_reason: str = Field(..., description="阻断原因")
    attempted_action: str = Field(..., description="尝试的操作")
    rule_violated: str = Field(..., description="违反的规则")
```

### 2.4 审计查询接口

```python
class AuditQuery:
    def by_task(self, task_id: str) -> TaskAuditSummary:
        """查询任务级摘要——快速浏览"""

    def by_task_details(self, task_id: str) -> list[FileAuditDetail]:
        """查询任务关联的文件级明细——问题定位"""

    def by_agent(self, agent_id: str, time_range: tuple[datetime, datetime]) -> list[TaskAuditSummary]:
        """查询某个 Agent 在某时段的所有操作"""

    def by_target(self, file_path: str) -> list[FileAuditDetail]:
        """查询某个文件被谁操作过"""

    def by_permission_level(self, level: str, time_range: tuple[datetime, datetime]) -> list[TaskAuditSummary]:
        """查询某个权限级别的所有操作——如查看所有 auto_guard 后验失败的记录"""

    def rebuild_index(self) -> int:
        """从 JSONL 重建 SQLite 索引——返回重建记录数"""
```

---

## 3. 文件组成

| 文件 | 职责 |
|------|------|
| `audit_event.py` | 审计事件模型——TaskAuditSummary + FileAuditDetail + 分级 Provenance |
| `audit_writer.py` | 不可变写入器——JSONL append-only + 异步 SQLite 索引重建 |
| `audit_query.py` | 审计查询接口——SQLite 查询 + JSONL 回退 |
| `rebuild_audit_index.py` | 索引重建脚本——JSONL → SQLite |

---

## 4. 施工 Phase 规划

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| scaffold | AuditEvent 两层模型 + JSONL append-only 写入 + 基础查询 | 📋 Backlog |
| experimental | 分级 Provenance + SQLite 索引重建 + Gate Engine/RBAC 集成 | 📋 Backlog |
| beta | 审计仪表盘 + 异常审计模式检测 + CI 一致性校验 | 📋 Backlog |

---

## 5. 风险与缓解

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|:---:|:---:|------|
| R1 | 审计日志膨胀——大量操作导致 JSONL 文件过大 | 高 | 中 | 按日轮转 + gzip 压缩旧文件 |
| R2 | JSONL 写入冲突——多 IDE 同时追加同一文件 | 中 | 高 | 文件锁（fcntl/msvcrt）+ 重试机制 |
| R3 | SQLite 索引延迟——异步重建导致查询不到最新记录 | 中 | 低 | 查询时先检查 JSONL 最新 N 行 + 5s 重建间隔 |
| R4 | 审计日志被篡改——AI 修改 JSONL | 低 | 高 | git 跟踪 + pre-commit 校验 SHA-256 |

---

## 决策记录

| 决策 ID | 决策内容 | 日期 | 依据 |
|---------|---------|------|------|
| D-020-01 | 两层审计粒度（任务级摘要+文件级明细） | 2026-05-05 | 1人场景，任务级摘要够日常浏览，文件级明细够问题定位 |
| D-020-02 | JSONL 为唯一真源，SQLite 为派生查询索引 | 2026-05-05 | 多 IDE 并发，JSONL 天然 append-only 且 git 友好；对标 GOV-AI-001→rbac_roles.yaml 派生模式 |
| D-020-03 | Provenance 按权限级别分级（轻量/标准/全量） | 2026-05-05 | 1人+AI场景，99%操作无草稿和仲裁，强制三件套形同虚设 |

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-05 | 0.2.0 | 三项决策写入：D-020-01 两层粒度 + D-020-02 JSONL为SSoT + D-020-03 分级Provenance；重构存储模型为 JSONL→SQLite 派生；Provenance 从强制三件套改为分级 |
| 2026-05-05 | 0.1.0 | 初始创建——审计事件模型 + 不可变存储 + Provenance 执行器 |
