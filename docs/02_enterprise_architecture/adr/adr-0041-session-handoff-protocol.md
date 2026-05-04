---
module_id: ADR-0041
refines: [ADR-0011]  # ADR-0011 runtime-planes-orthogonal-view \u7684\u7ec6\u5316\u51b3\u7b56
title: Session Handoff Protocol（跨会话交接协议）技术选型
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
related_rationale: R-PHASE1-HANDOFF, R-SESSION-GOV
related_open_questions: []
tags: [handoff, session, carryover, governance, phase-1]
summary: 锁定 Session 交接协议基线：HandoffPackage 8 必填字段（YAML 人读 + Pydantic 机读）+ SessionCarryover 机读 schema + P0-P3 上下文优先级压缩 + 5 项反腐败校验。协议服务于跨 Session / 跨模型 / 跨平台切换场景，防止"任务丢失、决策覆盖、重复劳动"。依赖 ADR-0030（tasks.session_id 列）与 ADR-0040（HandoffPackage 模型）。

date: '2026-04-24'
ttl: permanent
---

# ADR-0041：Session Handoff Protocol（跨会话交接协议）

## 1. 状态

- **当前状态**：`accepted`
- **拍板日期**：2026-04-24
- **决策者**：Claude Opus 4.7（终局裁决）
- **关联规则**：`docs/01_policies_and_standards/governance/task/handoff-protocol.md`（T-1-17）
- **关联实现**：`HandoffPackage` 模型（T-1-13 `schemas.py`）

## 2. 背景（Context）

ZephyrAlpha 是单 Owner + 多 AI Agent 协作模式，典型会话切换包括：

1. **跨平台**：Cursor（Opus/Sonnet/GLM/Composer）↔ Trae CN（GLM-5.1、Qwen-3.6）
2. **跨模型**：Opus 配额耗尽 → 降级到 Sonnet → 降级到 GLM
3. **跨人机**：AI 会话 → Owner 介入决策 → 回到 AI
4. **跨时间**：昨日会话 → 今日继续

没有正式交接协议前的典型故障：

- 上一 Session 完成 T-1-08，下一 Session 不知道，重做一次
- 上一 Session 拍板"使用 SQLite"，下一 Session 提议"重新评估 DuckDB"
- 上一 Session 触发降级事件，下一 Session 不知道正在限流
- 上一 Session 给 T-1-17 新增了规则引用，下一 Session 没激活导致不遵守

本 ADR 锁定跨会话的数据契约与 5 项反腐败校验，保证每次切换都是"确定性状态转移"。

## 3. 考虑过的方案

### 方案 A：只写 Session Log（当前做法）
- 已存在 `docs/09_audit/state/SESSION_LOGS/`
- ❌ 仅文字描述，无机器可解析契约
- ❌ 无强制字段，信息缺失靠 AI 自觉
- ❌ 不支持自动校验

### 方案 B：Git commit 信息做交接
- 与开发流程天然耦合
- ❌ commit 粒度 ≠ Session 粒度
- ❌ 没有 completed_tasks / blocked_items 等字段
- ❌ 不便承载长文本（context_summary ≤ 500 字）

### 方案 C：独立数据库表 `sessions`（只用 DB 不用文档）
- 机器可读
- ❌ Owner 无法直接读写（不利于人工接棒）
- ❌ 与 Git 历史割裂
- ❌ Cursor / Trae 对 DB 操作能力弱

### 方案 D：LangChain / AutoGen 内置 Memory
- 生态工具
- ❌ 捆绑特定框架
- ❌ 语义太泛（Memory vs Handoff 语义混淆）
- ❌ 不适合跨工具场景

### 方案 E：**YAML 双份（handoff + carryover）+ Pydantic schema + 反腐败层（本 ADR 选定）**

- **优点**
  - ✅ **人机双读**：YAML 人可读可改；Pydantic 机器可校验
  - ✅ **结构化字段**：8 必填字段硬约束，缺任一即"半启动"模式
  - ✅ **双文件分工**：
    - `handoff-YYYYMMDD-NNN.yaml`（人类摘要 + 决策记录）
    - `session_carryover.json`（机器可消费的 schema）
  - ✅ **反腐败层**：5 项启动校验（签名/task_id/rule_id/directive/snapshot）
  - ✅ **与 SQLite tasks.session_id 直连**：持久化层即真源
  - ✅ **兼容 P0-P3 压缩策略**：上下文预算紧张时可逐级丢 P3 / P2
- **缺点 / 权衡**
  - ⚠ 双文件维护：但一份是报告（落档），一份是状态（给下一 Session），职责不同
  - ⚠ 首次手写成本：通过 D2-255 指令 + T-1-17 规则模板降低
- **机构案例**：
  - AutoGen Chat History JSON Schema
  - Letta（前 MemGPT）Context Persistence
  - OpenAI "Memory" feature 的 preference scaffolding
  - Google SRE Incident Handoff Doc 模板

## 4. 决策

**最终选择：方案 E —— YAML + Pydantic + 反腐败层。**

### 4.1 HandoffPackage 8 必填字段（v1.0 锚定，不得删减）

| 字段 | 类型 | 含义 | 可否为空 |
|------|------|------|---------|
| `session_id` | str（`session-YYYYMMDD-NNN`） | 本 Session 唯一 ID | 否 |
| `completed_tasks` | list[task_id] | 本 Session 完成的 T-x-xx 列表 | 否（可为空列表） |
| `in_progress_tasks` | list[task_id] | 未完成但推进过的任务 | 否（可为空列表） |
| `blocked_items` | list[{task_id, reason}] | 被阻塞任务 + 阻塞原因 | 否（可为空列表） |
| `decisions_made` | list[{topic, decision, rationale}] | 本 Session 做出的关键决策 | 否（可为空列表） |
| `next_actions` | list[{task_id, priority, est_hours}] | 建议下一 Session 首先处理的事项 | 否 |
| `context_summary` | str（≤ 500 字） | 核心进展的自然语言摘要 | 否 |
| `open_questions` | list[str] | 留给下一 Session 或 Owner 决策的开放问题 | 否（可为空列表） |

### 4.2 SessionCarryover（机器可读补充）

```yaml
session_carryover:
  from_session_id: session-YYYYMMDD-NNN
  to_session_id: null            # 下一 Session 启动填入
  generated_at: ISO8601
  pending_tasks:
    - task_id: T-X-YY
      status: IN_PROGRESS | BLOCKED | WAITING | READY
      last_checkpoint: str
      blocker: str | null
  failure_context:
    - failure_id: F-NNN
      pattern: str
      recommended_retry_strategy: str
  context_snapshot_path: docs/09_audit/SESSIONS/session-<id>/snapshot.md
  active_rules: [rule_id_1, rule_id_2]
  active_directive: "222+244+999"
  token_budget_remaining: int
  handoff_package_path: docs/09_audit/HANDOFF/session-<id>.yaml
```

### 4.3 P0-P3 上下文压缩策略

| 级别 | 内容 | 压缩动作 | 传递形式 |
|:---:|------|---------|---------|
| **P0** | 任务 ID + 状态、失败原因、关键决策、active_rules | 不压缩 | 完整字段（必传） |
| **P1** | 已完成任务产物路径、本 Session 教训 | 不压缩但用引用 | 链接 + 一句话摘要 |
| **P2** | 探索过程、备选方案对比 | 摘要 ≤ 200 字 | 摘要 |
| **P3** | 已消除 TODO、已废弃草案 | 丢弃 | 不传 |

### 4.4 跨会话锚点（100% 传递）

以下信息必须传递，丢失即视为"交接失败"：

1. `active_rules`：当前激活规则 ID 列表（防规则漂移）
2. 上一 Session 未闭环的 ADR 草案
3. SQLite `tasks.session_id` 列中与本 session 相关的所有行
4. `session_carryover.json` 路径（下一 Session 第一读）
5. 本 Session 触发过的降级事件（Opus 配额 / Cursor 连续失败）

### 4.5 5 项反腐败校验（Session 启动时强制）

下一 Session 启动时必须对 `SessionCarryover` 执行 5 项校验。任一失败即进入"半启动"模式（禁止执行任务，仅允许只读 + 向 Owner 报错）：

1. [ ] `from_session_id` 对应的 HandoffPackage 文件存在且 `model_validate_json()` 通过
2. [ ] `pending_tasks` 中每个 `task_id` 在 SQLite `tasks` 表中存在
3. [ ] `active_rules` 中每个 `rule_id` 在 `.cursor/rules/` 或 `docs/01_policies_and_standards/` 下仍有效（未 `superseded`/`deprecated`）
4. [ ] `active_directive` 在 `模块候选池/prompt库/DOS/directives/` 下仍可解析（编号存在）
5. [ ] `context_snapshot_path` 指向文件存在且 UTF-8 无 BOM

### 4.6 使用时序

```
Session N 结束：
  ① task_repo.list_by_session(N) → 抽取任务状态
  ② 按 §4.1 填写 HandoffPackage YAML
  ③ HandoffPackage.model_validate_json() 通过
  ④ 生成 SessionCarryover JSON（§4.2）
  ⑤ 两文件落盘 docs/09_audit/HANDOFF/ + docs/09_audit/state/

Session N+1 启动：
  ① 读 session_carryover.json
  ② 跑 §4.5 五项校验
  ③ 全通过 → 进入正式执行
     任一失败 → 半启动 + 向 Owner 报错
```

## 5. 后果

### 5.1 正面

- 跨会话零信息丢失（完成/进行/阻塞/决策全部锁定）
- 半启动机制阻止腐败上下文污染新会话
- 机器可校验 → 可自动化（未来 T-2-xx 可生成 handoff_writer CLI）
- SQLite `tasks.session_id` 列提供审计链（哪个 session 动了哪些任务）

### 5.2 负面 / 权衡

- Session 结束时有 5-10 分钟的"交接成本"：**缓解**——T-1-20 CLI 可一键生成初稿，只需人工复核
- YAML 文件数量增长：**缓解**——按月归档到 `docs/06_ARCHIVE/session-handoffs-YYYY-MM/`；只保留最近 30 份在活跃目录

### 5.3 重审触发条件

| # | 条件 | 动作 |
|---|------|------|
| 1 | Agent 并行化（多 Session 同时跑）出现 | 引入 session_parent_id / session_children 字段 |
| 2 | 单次 Handoff > 10 KB | 拆分 attachment 机制 |
| 3 | 8 必填字段不够用 | 走 ADR 增补流程，不得私自扩展 |

## 6. 落地动作

- [x] 本 ADR 落盘
- [x] T-1-17：`docs/01_policies_and_standards/governance/task/handoff-protocol.md`（规则文件已迁移到新树，含 frontmatter + 每字段 6 要素模板）
- [ ] T-1-13：`HandoffPackage` 模型并入 `scripts/infra/schemas.py`
- [ ] T-1-18：首份 Session 交接包范例（以本会话为实例）
- [ ] 在 `.cursor/rules/core-governance.mdc` 追加"会话结束前必须产出 HandoffPackage"条目

## 7. 参考

- 相关 ADR：
  - ADR-0030（SQLite 元数据层 —— `tasks.session_id` 列基础）
  - ADR-0040（Pydantic v2 输出契约 —— HandoffPackage 为五模型之一）
  - ADR-0036 / 011-012（Deferred / Observer —— Session 边界事件源）
- 相关 Prompt：
  - `模块候选池/prompt库/DOS/directives/D2-architecture/255-opus-session-protocol.md`
  - `模块候选池/prompt库/DOS/directives/D2-architecture/266-sonnet-rule-authoring.md`
- 外部参考：
  - AutoGen Conversation Memory Schema
  - Letta (MemGPT) Checkpointing
  - Google SRE *Handing Off Work* 模板

## 8. 修订记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-04-24 | 1.0.0 | 初版：锚定 8 必填字段 + SessionCarryover schema + P0-P3 压缩策略 + 5 项反腐败校验 + 与 SQLite/Pydantic 契约互引 |
