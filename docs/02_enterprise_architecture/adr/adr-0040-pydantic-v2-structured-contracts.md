---
module_id: ADR-0040
refines: [ADR-0011]  # ADR-0011 runtime-planes-orthogonal-view \u7684\u7ec6\u5316\u51b3\u7b56
title: AI 结构化输出契约采用 Pydantic v2
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
related_rationale: R-OUTPUT-CONTRACT, R-TYPE-SAFETY
related_open_questions: []
tags: [pydantic, schema, output-contract, validation, phase-1]
summary: 所有 AI Agent 的结构化输出（Task / AuditReport / KnowledgeEntry / FailurePattern / HandoffPackage 五类核心模型）必须经 Pydantic v2 校验。校验失败触发三级降级（重试 1 次 → 切备份模型 → 人工介入）。Pydantic v2 模型字段必须与 SQLite 列严格对齐（ADR-0030），并与 frontmatter-schema.json（R4 SSoT）互为补充：前者约束 AI 输出，后者约束文档 frontmatter。

date: '2026-04-24'
ttl: permanent
---

# ADR-0040：AI 结构化输出契约采用 Pydantic v2

## 1. 状态

- **当前状态**：`accepted`
- **拍板日期**：2026-04-24
- **决策者**：Claude Opus 4.7（终局裁决）
- **关联实现**：`scripts/infra/schemas.py`（T-1-13，待由 Sonnet B04 实现）

## 2. 背景（Context）

Vibe Coding 流水线里，AI 输出可以是自然语言（review 报告）、代码（sonnet 生成）、也可以是**结构化对象**（填表、交接、登记）。结构化输出如果没有硬契约，会出现：

- 字段名 typo（`task_id` vs `taskId`）
- 类型混乱（`"true"` 字符串 vs `True` 布尔）
- 必填缺失（`completed_tasks` 漏填）
- 枚举漂移（`status: "complete"` ≠ `"COMPLETED"`）

Phase 1 要把下列五类对象固化为单一真源 Pydantic v2 模型：

| # | 模型 | 用途 | 下游消费者 |
|---|------|------|-----------|
| 1 | `Task` | 任务登记（10 状态机 + directive + idempotent + classification + evolution_policy） | `task_repo.py`（T-1-04）、SQLite `tasks` 表、CLI 报表 |
| 2 | `AuditReport` | 审计/扫描产物 | Sentinel L1、Phase 验收 |
| 3 | `KnowledgeEntry` | KE 索引（KE-NNN） | `docs/08_knowledge/` 入库、ChromaDB 向量化 |
| 4 | `FailurePattern` | 失败模式登记（F-NNN） | Carryover `failure_context`、调度器重试策略 |
| 5 | `HandoffPackage` | Session 交接包（8 必填字段，见 ADR-0041） | `docs/09_audit/HANDOFF/*.yaml`、下一 Session 的 carryover |

约束：

1. **单一真源**：同一字段定义只能出现一次（不得在 ADR、代码、文档三处各写一份）
2. **与 SQLite 字段对齐**：ADR-0030 定义 tasks / events / knowledge / gates 四表；Pydantic 模型字段必须严格映射
3. **YAML / JSON 双读**：Handoff 产物是 YAML，内部调用是 JSON
4. **降级路径**：AI 校验失败不得静默吞掉，必须走人工兜底
5. **零 Any**：所有字段精确类型，禁止 `Any`（除 payload 等边界透传场景）

## 3. 考虑过的方案

### 方案 A：dataclasses + 自写 validator
- 标准库；轻量
- ❌ 无 `model_validate_json()`，从 YAML/JSON 恢复对象需手写
- ❌ 校验器散落各处，难以统一
- ❌ 无 JSON Schema 导出，对接 pre-commit 钩子成本高

### 方案 B：marshmallow
- 成熟；Flask 生态
- ❌ API 冗长：Schema 类与模型类分离（两处同步）
- ❌ 社区活力近年下滑；与 pydantic 相比维护更弱
- ❌ v3 迁移到 TypedDict 路径未定

### 方案 C：attrs + cattrs
- 快速、解耦
- ❌ validator 生态弱
- ❌ JSON Schema 导出需要额外插件

### 方案 D：Pydantic v1
- 老字号
- ❌ 2024 年起 v2 已稳定并性能大幅提升（Rust 核心）
- ❌ v1 已进入维护模式，新项目不应选择

### 方案 E：**Pydantic v2（本 ADR 选定）**

- **优点**
  - ✅ `BaseModel` 单类同时承载定义 + 校验 + 序列化
  - ✅ `model_validate_json()` / `model_dump_json()` 原生支持，AI 输出可直接 parse
  - ✅ Rust 核心：1 MB JSON 校验 < 1 ms（比 v1 快 5-50 倍）
  - ✅ `field_validator` / `model_validator` 干净的声明式约束
  - ✅ `ConfigDict(extra="forbid", str_strip_whitespace=True)` 一键强类型
  - ✅ `json_schema()` 可导出 Draft 2020-12 JSON Schema，直接挂 pre-commit
  - ✅ 生态活跃（FastAPI、LangChain、LlamaIndex 等均已迁 v2）
  - ✅ 支持 `Discriminator` / `Tagged Union`，建模 FailurePattern 的 subtype 很方便
- **缺点 / 权衡**
  - ⚠ 运行时需要 `pydantic>=2.5`：已在 T-1-14 requirements.txt 登记
  - ⚠ Rust 组件随 wheel 分发：Windows/macOS/Linux 主平台已 CI 覆盖
  - ⚠ 学习曲线：已被 ADR-003 采纳，团队（Owner）已熟悉
- **机构案例**：FastAPI、LangChain、Anthropic SDK、OpenAI SDK、Instructor、Outlines、Stripe Python SDK

## 4. 决策

**最终选择：方案 E —— Pydantic v2 作为所有 AI 结构化输出的单一契约真源。**

### 4.1 五类核心模型（T-1-13 `schemas.py` 承接）

```python
class Task(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=False)

    task_id: Annotated[str, Field(pattern=r"^T-\d+-\d+[A-Z]?$")]
    phase: int = Field(ge=0, le=9)
    name: str = Field(min_length=1, max_length=200)
    status: Literal["PENDING", "IN_PROGRESS", "COMPLETED", "VERIFIED",
                    "FAILED", "BLOCKED", "WAITING", "READY", "RETRY", "CANCELLED"]
    execution_model: str
    fallback_model: str | None = None
    safety_level: Literal["L", "M", "H"]
    depends_on: list[str] = Field(default_factory=list)
    directive: str                # v1.1 §14.4 新增
    idempotent: bool              # v1.1 §14.4 新增
    classification: Literal["public", "internal", "confidential"]  # v1.1 §14.4
    evolution_policy: Literal["frozen", "extendable", "rewritable"]  # v1.1 §14.4
    estimate_hours: float = Field(ge=0)
    deliverables: list[str] = Field(default_factory=list)
    acceptance: list[str] = Field(default_factory=list)
    session_id: str | None = None
    created_at: datetime
    updated_at: datetime
    waiting_for: str | None = None     # 与 ADR-0036 对齐
    ready_at: datetime | None = None

class AuditReport(BaseModel): ...
class KnowledgeEntry(BaseModel): ...
class FailurePattern(BaseModel): ...
class HandoffPackage(BaseModel):       # 详细字段见 ADR-0041 §5.1
    session_id: str
    completed_tasks: list[str]
    in_progress_tasks: list[str]
    blocked_items: list[BlockedItem]
    decisions_made: list[Decision]
    next_actions: list[NextAction]
    context_summary: str = Field(max_length=500)
    open_questions: list[str]
```

### 4.2 ConfigDict 统一基线

所有模型继承同一 `ConfigDict`：

| 配置 | 值 | 理由 |
|------|-----|------|
| `extra` | `"forbid"` | AI typo 的 extra 字段立即报错，防止 schema drift |
| `str_strip_whitespace` | `True` | 移除尾部空白防止 `"READY "` 不等于 `"READY"` |
| `frozen` | `False`（默认） | Task/Handoff 需要增量更新；Knowledge/AuditReport 可选 `frozen=True` |
| `populate_by_name` | `True` | 允许 alias（未来 camelCase/snake_case 兼容） |
| `validate_assignment` | `True` | 运行时字段重写也触发校验 |

### 4.3 三级降级链路（校验失败时）

```
AI 输出 → Pydantic.model_validate_json()
   │
   ├─ ValidationError（字段缺失/类型错）
   │     │
   │     ├─ 第 1 级：同模型重试 1 次（带回错误详情的 prompt）
   │     │
   │     ├─ 第 2 级：切换 fallback_model（Opus → Sonnet，或 Sonnet → GLM）
   │     │
   │     └─ 第 3 级：写入 gates 表（passed=False）+ emit METRIC_EVENT
   │                  + 在 SESSION_LOG 标红 + 等待 Owner 介入
   │
   └─ 通过 → 提交下游（SQLite / YAML / ChromaDB）
```

三级失败后**禁止静默继续**，必须由 Owner 或降级模型明确接管。

### 4.4 与其他 Schema 的分工

| Schema | 管辖范围 | 真源位置 |
|--------|---------|---------|
| **frontmatter-schema.json**（R4） | Markdown 文档 YAML frontmatter | `schemas/frontmatter-schema.json` |
| **Pydantic v2 模型**（本 ADR） | AI 运行时结构化输出 + SQLite 对象 | `scripts/infra/schemas.py` |
| **SQLite DDL**（ADR-0030） | 元数据持久化层 | `scripts/infra/sqlite_schema.py` |

三者**必须互相锁死**：新增字段必须同时更新本 ADR / SQLite DDL / Pydantic Model 三处。建议 T-2-xx 引入 `schema-consistency-check` 脚本对齐。

### 4.5 反模式（禁止）

- ❌ 使用裸 `dict` 或 `TypedDict` 做对外输出契约
- ❌ 用 `Any` 类型字段（除 `payload: dict[str, Any]` 等透传场景，且必须写注释说明）
- ❌ 跳过 `ValidationError` 静默重试（必须按 §4.3 三级降级）
- ❌ 在 Pydantic 模型里定义 DB 会话 / ORM 方法（契约层保持纯粹）
- ❌ 在多处复制粘贴模型字段（必须从 `schemas.py` 统一 import）

## 5. 后果

### 5.1 正面

- 所有 AI 输出类型安全，mypy --strict 可捕获 90% 字段错误
- `model_validate_json` + `model_dump_json` 直接支撑 Handoff YAML 序列化
- JSON Schema 导出自动为 pre-commit 钩子提供校验规则
- 与 SQLite / frontmatter schema 协同，形成三位一体的契约铁三角

### 5.2 负面 / 权衡

- 新增字段成本：需要同步改三处（ADR + DDL + Model），但 **这正是我们想要的门禁成本**
- Rust wheel 冷启动略慢：实际 30 ms 级别，忽略不计

### 5.3 重审触发条件

| # | 条件 | 动作 |
|---|------|------|
| 1 | Pydantic 主版本升级（v3） | 重写本 ADR |
| 2 | 需要流式校验（大 Handoff > 10 MB） | 引入 `msgspec` 或切 Pydantic streaming |
| 3 | 跨语言消费（Rust/Go agent） | 转 JSON Schema 为唯一真源、Pydantic 降为 Python 绑定 |

## 6. 落地动作

- [x] 本 ADR 落盘
- [ ] T-1-13：`scripts/infra/schemas.py`（5 模型 + ConfigDict 基线）
- [ ] T-1-14：`requirements.txt` 增加 `pydantic>=2.5, pydantic-settings>=2.1`
- [ ] T-1-15：`tests/infra/test_schemas.py`（每模型 3 有效 + 3 无效 = 30 用例）
- [ ] 追加"schema 一致性"pre-commit hook（对齐 SQLite DDL）

## 7. 参考

- 相关 ADR：
  - ADR-0030（SQLite 元数据层 —— Pydantic 模型字段必须与 SQLite 列严格对齐）
  - ADR-0036 / ADR-0037（Deferred / Observer —— Task 与 Event 模型承载对象）
  - ADR-0041（Handoff Protocol —— HandoffPackage 即本 ADR 五模型之一）
- 相关 Schema：
  - `schemas/frontmatter-schema.json`（R4 SSoT，与本 ADR 互补）
- 外部参考：
  - Pydantic v2 官方文档 <https://docs.pydantic.dev/2.0/>
  - FastAPI 契约模式 <https://fastapi.tiangolo.com/tutorial/body/>
  - Instructor（pydantic + LLM）<https://github.com/jxnl/instructor>
  - Outlines 结构化生成 <https://github.com/outlines-dev/outlines>

## 8. 修订记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-04-24 | 1.0.0 | 初版：选定 Pydantic v2；锁定 5 类核心模型；ConfigDict 基线；三级降级链路；与 SQLite/frontmatter 契约分工 |
