---
module_id: STD-SESSION-CARRYOVER-001
title: Session Carryover Schema / 会话接续 Schema
doc_type: blueprint
status: Active
version: 1.0.0
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-04-24
superseded_by: null
supersedes: null
placement_note: "本文件是模块级接口契约（Context Engine 的 JSON Schema 定义），不是 TOGAF 架构视图。当前暂放 target_architecture/ 是因为它是跨层基础设施的核心接口定义；未来迁移至 03_modules/ 下对应位置时需同步更新此 frontmatter。"
truth_sources:
  - "[已归档-原模块候选池] vibe-coding-audit-merged.md §Opus 五 M-01 Session Carryover"
  - "[已归档-原模块候选池] vibe-coding-audit-merged.md §Kimi 9.7 Context Engine"
related_rationale: R71
related_open_questions: []
tags:
  - session-carryover
  - context_engine-integration
  - schema
  - vibe-coding-2.0
  - hallucination-event
summary: 定义 `session_carryover.json` 的完整 schema——前序 Session 未完成任务、失败原因、上下文状态、Token 预算、幻觉事件的结构化归档。Session 结束前由 Context Engine 写入，下一 Session 启动后由 Context Engine 读取以恢复工作状态。是跨 Session 连续性的核心锚点。
date: '2026-04-24'
ttl: permanent
design_maturity: design
---

# Session Carryover Schema
# 会话接续 Schema

---

## 0. 读者指南

| 章节 | 内容 | 主要读者 |
|------|------|----------|
| §1 | 设计动机：为什么需要 Session Carryover | 架构师、用户 |
| §2 | Schema 完整定义（JSON Schema + Pydantic）| 开发者 |
| §3 | 字段详细说明 | 开发者 |
| §4 | 写入时机（Session 结束前）| Context Engine 实现者 |
| §5 | 读取时机（Session 启动后）| Context Engine 实现者 |
| §6 | 与 Context Engine 的集成点 | CE 实现者 |
| §7 | 示例：一个完整的 `session_carryover.json` | 所有读者 |
| §8 | 演化策略（schema_version 管理）| 架构师 |

### 0.2 本文档不是

- ❌ Context Engine 的完整 API → 见 `docs/03_modules/_cross_layer/_b_track_interfaces/context_engine_interface.md`
- ❌ 单次 Session 内的任务追踪 → 见 `docs/03_modules/_cross_layer/_b_track_interfaces/agent_orchestrator_interface.md`
- ❌ Session 的定义（本文档假设读者已知）→ Session = 一次"打开 Cursor → 编码 → 关闭"的连续工作周期

---

## 1. 设计动机

### 1.1 当前问题

`vibe-coding-audit-merged.md §Opus §五 M-01` 识别：

1. **Session 断点丢失**：关闭 IDE 后，Agent 的工作状态（当前任务、已知失败、幻觉事件）全部丢失
2. **下次 Session 冷启动**：重新打开时，Agent 需要再次从零理解项目，大量重复上下文构建
3. **跨 Session 的风险盲区**：Session A 的幻觉事件在 Session B 不可见，相同错误可能重复发生
4. **用户心智负担**：用户需要自己记忆"上次做到哪了"，口头告诉 Agent

### 1.2 Session Carryover 的解决

```
Session A 结束前
  │
  ▼
Context Engine.save_session_carryover(session_id)
  │
  ▼
写入 .runtime/sessions/session_carryover.json
  │
  │ [IDE 关闭 / 用户下班 / 机器重启]
  │
  ▼
Session B 启动后
  │
  ▼
Context Engine.load_session_carryover()
  │
  ▼
Agent 接续工作：知道上次 TODO、已尝试过的失败、已知风险
```

### 1.3 核心设计原则

| 原则 | 说明 |
|------|------|
| **可机器读写 + 可人工审阅** | JSON 格式，frontmatter 友好；字段命名自解释 |
| **版本化**：`schema_version` 字段强制 | 未来 schema 演化时，老文件可被自动迁移 |
| **并行 session 命名空间隔离** | 多 session 并发时，`session_carryover.json` 按 `session_id` 命名空间隔离（`.runtime/sessions/<session_id>/session_carryover.json`）；合并时按 session 结束时间排序 merge，非"last-wins 覆盖"（P1-T1 并行模型，替代原串行幂等写入） |
| **单文件 SSoT（串行场景）** | 单 session 串行场景仍维持每项目根一份 `session_carryover.json`；并行场景退化为命名空间隔离 |
| **机密隔离** | 不写入敏感信息（API Key / Secret）|

---

## 2. Schema 完整定义

### 2.1 JSON Schema（权威）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "schemas/session-carryover-v1.schema.json",
  "title": "SessionCarryover",
  "type": "object",
  "required": ["schema_version", "session_id", "ended_at", "open_tasks"],
  "properties": {
    "schema_version": {
      "type": "string",
      "const": "1.0.0",
      "description": "Schema 版本，强制校验"
    },
    "session_id": {
      "type": "string",
      "pattern": "^sess-[0-9]{8}-[0-9]{6}-[a-f0-9]{6}$",
      "description": "Session 唯一 ID，格式：sess-YYYYMMDD-HHMMSS-<6-char hex>"
    },
    "started_at": {"type": "string", "format": "date-time"},
    "ended_at": {"type": "string", "format": "date-time"},
    "ended_reason": {
      "type": "string",
      "enum": ["normal_shutdown", "user_command", "crash", "idle_timeout", "ide_close"]
    },
    "ide_info": {
      "type": "object",
      "properties": {
        "ide_id": {"enum": ["cursor", "trae", "claude_desktop", "generic_mcp"]},
        "ide_version": {"type": "string"},
        "os": {"type": "string"}
      }
    },
    "open_tasks": {
      "type": "array",
      "items": {"$ref": "#/definitions/OpenTask"}
    },
    "blockers": {
      "type": "array",
      "items": {"$ref": "#/definitions/Blocker"}
    },
    "hallucination_events": {
      "type": "array",
      "items": {"$ref": "#/definitions/HallucinationEvent"}
    },
    "context_state": {"$ref": "#/definitions/ContextState"},
    "token_budget": {"$ref": "#/definitions/TokenBudget"},
    "artifacts_pending_review": {
      "type": "array",
      "items": {"type": "string", "description": "文件路径"}
    },
    "user_intentions": {
      "type": "array",
      "items": {"type": "string"},
      "description": "用户在 Session 中显式表达的下一步意图（从对话中抽取）"
    },
    "environment_snapshot": {"$ref": "#/definitions/EnvironmentSnapshot"}
  },

  "definitions": {
    "OpenTask": {
      "type": "object",
      "required": ["task_id", "status", "summary"],
      "properties": {
        "task_id": {"type": "string", "description": "来自 Orchestrator 的 task_id"},
        "status": {
          "type": "string",
          "enum": ["draft", "queued", "assigned", "running", "blocked", "reviewing"]
        },
        "summary": {"type": "string", "maxLength": 300},
        "files_in_scope": {"type": "array", "items": {"type": "string"}},
        "last_observation": {"type": "string", "maxLength": 500},
        "next_action_hint": {"type": "string", "maxLength": 300}
      }
    },
    "Blocker": {
      "type": "object",
      "required": ["task_id", "reason", "requires_user"],
      "properties": {
        "task_id": {"type": "string"},
        "reason": {"type": "string", "maxLength": 500},
        "requires_user": {"type": "boolean"},
        "suggested_prompt": {"type": "string", "description": "建议下次 Session 开场白"}
      }
    },
    "HallucinationEvent": {
      "type": "object",
      "required": ["event_id", "task_id", "rule_triggered", "evidence"],
      "properties": {
        "event_id": {"type": "string"},
        "task_id": {"type": "string"},
        "rule_triggered": {
          "type": "string",
          "enum": ["loop_same_observation", "no_progress_timeout",
                   "repeated_same_file_edit", "tool_repeat_without_result",
                   "fabricated_path", "fabricated_api", "other"]
        },
        "evidence": {"type": "string", "maxLength": 1000},
        "mitigation_applied": {"type": "string"},
        "timestamp": {"type": "string", "format": "date-time"}
      }
    },
    "ContextState": {
      "type": "object",
      "properties": {
        "active_collections": {
          "type": "array",
          "items": {
            "enum": ["decisions", "code_context", "lessons", "knowledge", "runtime_logs"]
          }
        },
        "recent_retrievals": {
          "type": "array",
          "maxItems": 20,
          "items": {
            "type": "object",
            "properties": {
              "query": {"type": "string"},
              "top_ids": {"type": "array", "items": {"type": "string"}},
              "timestamp": {"type": "string", "format": "date-time"}
            }
          }
        },
        "compression_strategy_used": {
          "enum": ["llm", "rule_based", "truncate", "none"]
        },
        "mcp_channels_active": {
          "type": "array",
          "items": {"enum": ["tools", "resources", "prompts", "sampling"]}
        }
      }
    },
    "TokenBudget": {
      "type": "object",
      "properties": {
        "session_total_used": {"type": "integer", "minimum": 0},
        "session_remaining": {"type": "integer"},
        "daily_quota_consumed": {"type": "integer"},
        "opus_calls_today": {"type": "integer", "maximum": 10,
          "description": "Opus 模型日配额 ≤ 10（源自 Opus M-03 建议）"}
      }
    },
    "EnvironmentSnapshot": {
      "type": "object",
      "properties": {
        "git_branch": {"type": "string"},
        "git_head_sha": {"type": "string"},
        "uncommitted_files": {"type": "array", "items": {"type": "string"}},
        "ruff_status": {"enum": ["clean", "warnings", "errors"]},
        "pytest_last_result": {"enum": ["pass", "fail", "not_run"]}
      }
    }
  }
}
```

### 2.2 Pydantic v2 等价定义（实现参考）

```python
# src/zephyr/context_engine/session_carryover.py
from datetime import datetime
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

class EndedReason(str, Enum):
    NORMAL_SHUTDOWN = "normal_shutdown"
    USER_COMMAND = "user_command"
    CRASH = "crash"
    IDLE_TIMEOUT = "idle_timeout"
    IDE_CLOSE = "ide_close"

class HallucinationRule(str, Enum):
    LOOP_SAME_OBSERVATION = "loop_same_observation"
    NO_PROGRESS_TIMEOUT = "no_progress_timeout"
    REPEATED_SAME_FILE_EDIT = "repeated_same_file_edit"
    TOOL_REPEAT_WITHOUT_RESULT = "tool_repeat_without_result"
    FABRICATED_PATH = "fabricated_path"
    FABRICATED_API = "fabricated_api"
    OTHER = "other"

class OpenTask(BaseModel):
    model_config = ConfigDict(extra='forbid')
    task_id: str
    status: Literal["draft", "queued", "assigned", "running", "blocked", "reviewing"]
    summary: str = Field(max_length=300)
    files_in_scope: list[str] = Field(default_factory=list)
    last_observation: str | None = Field(default=None, max_length=500)
    next_action_hint: str | None = Field(default=None, max_length=300)

class Blocker(BaseModel):
    model_config = ConfigDict(extra='forbid')
    task_id: str
    reason: str = Field(max_length=500)
    requires_user: bool
    suggested_prompt: str | None = None

class HallucinationEvent(BaseModel):
    model_config = ConfigDict(extra='forbid')
    event_id: str
    task_id: str
    rule_triggered: HallucinationRule
    evidence: str = Field(max_length=1000)
    mitigation_applied: str | None = None
    timestamp: datetime

class ContextState(BaseModel):
    model_config = ConfigDict(extra='forbid')
    active_collections: list[Literal["decisions", "code_context", "lessons",
                                      "knowledge", "runtime_logs"]] = Field(default_factory=list)
    recent_retrievals: list[dict] = Field(default_factory=list, max_length=20)
    compression_strategy_used: Literal["llm", "rule_based", "truncate", "none"] | None = None
    mcp_channels_active: list[Literal["tools", "resources", "prompts", "sampling"]] = \
        Field(default_factory=list)

class TokenBudget(BaseModel):
    model_config = ConfigDict(extra='forbid')
    session_total_used: int = Field(default=0, ge=0)
    session_remaining: int | None = None
    daily_quota_consumed: int | None = None
    opus_calls_today: int = Field(default=0, ge=0, le=10)   # Opus M-03 日配额

class EnvironmentSnapshot(BaseModel):
    model_config = ConfigDict(extra='forbid')
    git_branch: str | None = None
    git_head_sha: str | None = None
    uncommitted_files: list[str] = Field(default_factory=list)
    ruff_status: Literal["clean", "warnings", "errors"] | None = None
    pytest_last_result: Literal["pass", "fail", "not_run"] | None = None

class IDEInfo(BaseModel):
    model_config = ConfigDict(extra='forbid')
    ide_id: Literal["cursor", "trae", "claude_desktop", "generic_mcp"]
    ide_version: str | None = None
    os: str | None = None

class SessionCarryover(BaseModel):
    """Session 接续的权威 schema，由 Context Engine 写入 .runtime/sessions/session_carryover.json"""
    model_config = ConfigDict(extra='forbid')

    schema_version: Literal["1.0.0"] = "1.0.0"
    session_id: str = Field(pattern=r"^sess-[0-9]{8}-[0-9]{6}-[a-f0-9]{6}$")
    started_at: datetime | None = None
    ended_at: datetime
    ended_reason: EndedReason | None = None
    ide_info: IDEInfo | None = None

    open_tasks: list[OpenTask] = Field(default_factory=list)
    blockers: list[Blocker] = Field(default_factory=list)
    hallucination_events: list[HallucinationEvent] = Field(default_factory=list)

    context_state: ContextState | None = None
    token_budget: TokenBudget | None = None

    artifacts_pending_review: list[str] = Field(default_factory=list)
    user_intentions: list[str] = Field(default_factory=list)
    environment_snapshot: EnvironmentSnapshot | None = None
```

---

## 3. 字段详细说明

### 3.1 顶层字段

| 字段 | 必填 | 说明 |
|------|:----:|------|
| `schema_version` | ✅ | 版本号。`validate_ssot.py` 会强制校验 |
| `session_id` | ✅ | 唯一 ID，格式 `sess-YYYYMMDD-HHMMSS-<6-char hex>` |
| `started_at` | ⬜ | Session 开始时间（ISO 8601）|
| `ended_at` | ✅ | Session 结束时间 |
| `ended_reason` | ⬜ | 结束原因分类（5 种枚举值）|
| `ide_info` | ⬜ | 当前 IDE 环境信息 |
| `open_tasks` | ✅ | 未完成任务列表（可为空数组）|
| `blockers` | ⬜ | 阻塞事项 |
| `hallucination_events` | ⬜ | 本次 Session 记录到的幻觉事件 |
| `context_state` | ⬜ | Context Engine 运行时状态快照 |
| `token_budget` | ⬜ | Token 用量与余额 |
| `artifacts_pending_review` | ⬜ | 待人工审核的产物文件路径 |
| `user_intentions` | ⬜ | 从用户对话抽取的下一步意图（≤ 5 条）|
| `environment_snapshot` | ⬜ | Git / 测试 / Lint 状态 |

### 3.2 子结构重点字段

#### `OpenTask.next_action_hint`

> 下次 Session 启动时，Agent 应该执行的第一个动作。由本 Session 的 Agent 或用户显式填写。

示例：
- `"继续 T-1-03：将 ChromaDB 客户端替换为 InProcessVectorMemory 实现"`
- `"先跑 pytest tests/ 确认 M-01 没打断测试"`

#### `Blocker.suggested_prompt`

> 如果 Blocker 是"需要用户决策"，提供开场白模板，降低用户认知负担。

示例：`"上次 Session 卡在 ChromaDB 并发写入的选择题：A) 加 filelock；B) 等 beta 服务化。请选择。"`

#### `HallucinationEvent.mitigation_applied`

> 记录 Agent 或用户当时采取的缓解措施，防止下次 Session 重复踩坑。

示例：`"触发 repeated_same_file_edit 后，task_id=T-1-05 被 BLOCKED；用户手动确认应先查 KE-L02-20251015 再改"`

#### `TokenBudget.opus_calls_today`

> 源自 Opus M-03 建议：`opus` 模型日调用配额 ≤ 10 次。强制字段约束 `maximum: 10`，超限时 LSG 会拒绝。

---

## 4. 写入时机（Session 结束前）

### 4.1 触发点

| 触发场景 | 触发方式 | 必须字段 |
|---------|---------|---------|
| IDE 正常关闭 | 监听 IDE close 钩子 | `ended_reason: ide_close` |
| 用户显式命令 `/session save` | 用户手动触发 | `ended_reason: user_command` |
| IDE 崩溃后恢复 | 启动时检查上次是否异常退出 | `ended_reason: crash`（后补写）|
| IDE 空闲超时（> 30 min）| FLE 定时触发 | `ended_reason: idle_timeout` |
| Context Engine 正常关闭 | `CE.shutdown()` 前置 | `ended_reason: normal_shutdown` |

### 4.2 写入流程

```python
# 伪代码
async def save_session_carryover(self) -> None:
    # 1. 从 Orchestrator 查询 open tasks
    open_tasks = await self.orchestrator.get_open_tasks(session_id=self.session_id)

    # 2. 从 Orchestrator 查询 hallucination events
    events = await self.orchestrator.get_hallucination_events(session_id=self.session_id)

    # 3. 构造 SessionCarryover
    carryover = SessionCarryover(
        session_id=self.session_id,
        ended_at=datetime.now(),
        ended_reason=EndedReason.IDE_CLOSE,
        open_tasks=open_tasks,
        hallucination_events=events,
        context_state=self._snapshot_context_state(),
        token_budget=self._snapshot_token_budget(),
        environment_snapshot=self._snapshot_environment(),
    )

    # 4. 原子写入（先写 .tmp 再 rename）
    target = Path(".runtime/sessions/session_carryover.json")
    tmp = target.with_suffix(".json.tmp")
    tmp.write_text(carryover.model_dump_json(indent=2), encoding="utf-8")
    tmp.replace(target)   # atomic on POSIX; Windows 用 os.replace

    # 5. 写入前调 LSG 做 Secret 扫描（Pattern Inspector）
    # （省略）
```

### 4.3 写入频率

- **强制写入**：Session 结束时（任何 ended_reason）
- **可选频繁写入**：每 15 分钟一次（作为 crash 防护），`ended_reason` 暂填 `idle_timeout`，后续被最终写入覆盖

---

## 5. 读取时机（Session 启动后）

### 5.1 触发点

Context Engine 启动时调用 `load_session_carryover()`，位于 `CE.__aenter__` 或 `CE.initialize()`。

### 5.2 读取流程

```python
async def load_session_carryover(self) -> SessionCarryover | None:
    target = Path(".runtime/sessions/session_carryover.json")
    if not target.exists():
        return None

    try:
        raw = target.read_text(encoding="utf-8")
        carryover = SessionCarryover.model_validate_json(raw)
    except ValidationError as e:
        # schema 不匹配 → 触发迁移或拒绝
        return self._handle_schema_mismatch(raw, e)

    # 检查 schema_version
    if carryover.schema_version != "1.0.0":
        carryover = await self._migrate_schema(carryover)

    # 暴露给 Orchestrator：恢复 open_tasks
    await self.orchestrator.restore_open_tasks(carryover.open_tasks)

    # 暴露给用户：展示 blockers + user_intentions
    self._display_session_recap(carryover)

    return carryover
```

### 5.3 降级路径

| 场景 | 处理 |
|------|------|
| 文件不存在 | 正常（首次 Session 或已消费）|
| JSON 解析失败 | 写入 `.runtime/sessions/session_carryover.corrupted.<ts>.json`，从零启动 |
| schema_version 不匹配 | 尝试 `_migrate_schema()`；失败则降级到"部分恢复"（仅恢复 open_tasks）|
| 文件过期（`ended_at` > 7 天前）| 展示警告但仍加载；用户可选择清空 |

---

## 6. 与 Context Engine 的集成点

### 6.1 Context Engine 需要暴露的接口

```python
# 由 context_engine-interface.md §3.5 约束
class ContextEngineProtocol(Protocol):
    async def save_session_carryover(self,
                                      session_id: str,
                                      reason: EndedReason) -> None: ...

    async def load_session_carryover(self) -> SessionCarryover | None: ...

    async def clear_session_carryover(self) -> None: ...
```

### 6.2 Context Engine 对其他服务的调用

| 调用 | 目的 |
|------|------|
| `orchestrator.get_open_tasks()` | 查询未完成任务填充 `open_tasks` |
| `orchestrator.get_hallucination_events()` | 查询幻觉事件 |
| `orchestrator.restore_open_tasks()` | 下次启动时恢复任务队列 |
| `vms.get_recent_retrievals()` | 填充 `context_state.recent_retrievals` |
| `lsg.scan_for_secrets()` | 写入前扫描，防止敏感信息泄漏 |
| `fle.collect_metric()` | 上报 session 生命周期指标 |

### 6.3 文件系统契约

```
.runtime/sessions/
├── session_carryover.json              # 主文件（最新一次 Session 结束时）
├── session_carryover.json.tmp          # 原子写入的临时文件（正常情况不应存在）
├── session_carryover.corrupted.<ts>.json  # 损坏归档
└── history/                             # （beta+ 可选）历史 carryover 归档
    └── sess-20260424-153000-a1b2c3.json
```

---

## 7. 完整示例

```json
{
  "schema_version": "1.0.0",
  "session_id": "sess-20260424-153000-a1b2c3",
  "started_at": "2026-04-24T09:15:00+08:00",
  "ended_at": "2026-04-24T15:30:00+08:00",
  "ended_reason": "user_command",
  "ide_info": {
    "ide_id": "cursor",
    "ide_version": "0.47.0",
    "os": "Windows 10.0.26200"
  },
  "open_tasks": [
    {
      "task_id": "T-1-05",
      "status": "blocked",
      "summary": "替换 ChromaDB 客户端为 InProcessVectorMemory 实现",
      "files_in_scope": [
        "src/zephyr/vector_memory/in_process.py",
        "tests/vector_memory/test_in_process.py"
      ],
      "last_observation": "pytest tests/ 3 passed, 2 failed: test_multi_search_rrf / test_bootstrap_resume",
      "next_action_hint": "先修 test_multi_search_rrf：RRF 权重分子应该是 60 而不是 1"
    }
  ],
  "blockers": [
    {
      "task_id": "T-1-05",
      "reason": "RRF 实现细节歧义：60 常数是来自 BM25 论文还是实践经验？",
      "requires_user": true,
      "suggested_prompt": "T-1-05 的 RRF 权重常数选择：A) 60（BM25 论文）；B) 10（经验值）；C) 自适应。请决策。"
    }
  ],
  "hallucination_events": [
    {
      "event_id": "hall-20260424-142015-xyz789",
      "task_id": "T-1-05",
      "rule_triggered": "fabricated_api",
      "evidence": "Agent 试图调 ChromaDB.collection.search_with_weights() 不存在的 API",
      "mitigation_applied": "任务 BLOCKED，用户介入确认实际 API 为 query(n_results=..., where=...)",
      "timestamp": "2026-04-24T14:20:15+08:00"
    }
  ],
  "context_state": {
    "active_collections": ["decisions", "code_context"],
    "recent_retrievals": [
      {
        "query": "ChromaDB multi-collection search with RRF",
        "top_ids": ["KE-L12-VMS-0003", "KBG-0016", "KE-L12-VMS-0007"],
        "timestamp": "2026-04-24T14:10:00+08:00"
      }
    ],
    "compression_strategy_used": "llm",
    "mcp_channels_active": ["tools", "resources", "prompts"]
  },
  "token_budget": {
    "session_total_used": 87500,
    "session_remaining": null,
    "daily_quota_consumed": 142300,
    "opus_calls_today": 3
  },
  "artifacts_pending_review": [
    "src/zephyr/vector_memory/in_process.py"
  ],
  "user_intentions": [
    "修掉 RRF 测试后进入 T-1-06（bootstrap 断点续传）",
    "周五前完成 experimental 骨架 6 大核心服务的 InProcess 实现"
  ],
  "environment_snapshot": {
    "git_branch": "main",
    "git_head_sha": "a3f9b2c1",
    "uncommitted_files": [
      "src/zephyr/vector_memory/in_process.py",
      "tests/vector_memory/test_in_process.py"
    ],
    "ruff_status": "clean",
    "pytest_last_result": "fail"
  }
}
```

---

## 8. 演化策略

### 8.1 schema_version 约定

| 版本 | 变更类型 | 迁移策略 |
|------|---------|---------|
| `1.0.0` → `1.X.0` | 向后兼容（加字段）| 老文件加载时填默认值 |
| `1.X.0` → `2.0.0` | 破坏性变更 | 强制调用 `_migrate_schema_1_to_2()` |

### 8.2 新增字段规则

- 新字段必须带默认值或声明为 Optional
- 新增枚举值时，老文件中未出现该值也应能加载
- 禁止删除已有字段（改为 `deprecated: true` 标记后保留 2 个次版本）

### 8.3 破坏性变更规则

- 必须新建 KB 决策记录说明
- 必须提供 `_migrate_schema()` 自动迁移
- 必须在发布前用历史真实 carryover 文件做迁移验证

---

## 9. 开放问题

| OQ | 议题 | 何时闭合 |
|----|------|---------|
| OQ-SC-01 | 是否需要加密 `session_carryover.json`（含 user_intentions 等）| beta |
| OQ-SC-02 | `history/` 的保留策略（时间 / 数量 / 尺寸）| beta |
| OQ-SC-03 | 跨机器同步 Session（笔记本 ↔ 台式机）是否需要 | beta+ |

---

## 10. 修订记录

| 日期 | 版本 | 作者 | 说明 |
|------|------|------|------|
| 2026-04-24 | 1.0.0 | opus47_architect | 初版。基于 Opus §五 M-01 + Kimi §9.7 Context Engine 合并产出。完整 JSON Schema + Pydantic v2 双声明 + 7 个子 definition + 示例 + 演化策略。|
