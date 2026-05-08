---
task_id: "DB-025-0016"
namespace: "OPS"
seq: 16
title: "task_repo CRUD 接口契约实现——§4 Python 代码块落地验证"
status: "PENDING"
priority: "P1"
phase: 0
execution_model: "deepseek-v4-pro"
model_rationale: "接口契约验证——15 个 TaskRepo 方法逐项对照 §4 Python 接口"
fallback_model: "glm-4.7"
safety_level: "medium"
directive: "verify_code_contract"
idempotent: true
classification: "confidential"
evolution_policy: "immutable"
estimate_hours: 0.5
actual_hours: 0
files_in_scope:
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
deliverables: []
acceptance: ""
depends_on: ["DB-025-0001"]
tags: ["fn:contract", "ly:cross_layer", "st:active", "mo:manual"]
session_id: null
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
acceptance_criteria:
  - "create(task)→TaskCard 方法签名与 §4 一致"
  - "get(task_id)→Optional[TaskCard] 方法签名与 §4 一致"
  - "update(task_id, updates)→TaskCard 方法签名与 §4 一致"
  - "upsert(task)→TaskCard 方法签名与 §4 一致——ON CONFLICT DO UPDATE 语义"
  - "delete(task_id)→bool 软删除方法签名与 §4 一致"
  - "hard_delete(task_id)→bool 物理删除方法签名与 §4 一致"
  - "transition(task_id, to_status)→TaskCard 方法签名与 §4 一致——G1 门禁在写事务内执行"
  - "list_by_status/phase/session/namespace→list[TaskCard] + is_deleted=0 过滤"
  - "list_active()→list[TaskCard]"
  - "list_by_dependency/tag/blocked_by→list[TaskCard] JSON1 查询"
rollback_instructions: "若接口签名不一致 → 登记到 §20 R*。不修改源文件"
context_assembly_manifest:
  - {file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\blueprint.md", reason: "§4 task_repo Python 代码块接口定义"}
  - {file_path: "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py", reason: "TaskRepo 类实现"}
upstream_files_content_hash: null
allowed_touch: []
forbidden_touch: []
applicable_rules: []
completed_gates: []
blocked_gates: {}
assigned_pipeline: "B"
pipeline_modules: ["M6", "M7"]
ai_autonomy_level: "supervised"
construction_status: "pending"
verification_status: "unverified"
parent_task_id: null
epic: "MOD-INF-012-database-v2.2-decomposition"
effective_priority: "P1"
diff_plan_required: false
estimated_context_tokens: 5000
context_window_limit: 128000
---

# DB-025-0016：task_repo CRUD 接口契约实现——§4 Python 代码块落地验证

验证 TaskRepo 类的 15 个方法签名与蓝图 §4 Python 代码块完全一致。

| 方法 | 蓝图签名 | 代码验证 |
|------|---------|---------|
| create | `(task: TaskCard) -> TaskCard` | grep task_repo.py |
| get | `(task_id: str) -> Optional[TaskCard]` | grep task_repo.py |
| update | `(task_id: str, updates: dict) -> TaskCard` | grep task_repo.py |
| upsert | `(task: TaskCard) -> TaskCard` | grep task_repo.py |
| delete | `(task_id: str) -> bool` | grep task_repo.py |
| hard_delete | `(task_id: str) -> bool` | grep task_repo.py |
| transition | `(task_id: str, to_status: Status) -> TaskCard` | grep task_repo.py |
| list_by_status | `(status: Status) -> list[TaskCard]` | grep task_repo.py |
| list_by_phase | `(phase: int) -> list[TaskCard]` | grep task_repo.py |
| list_by_session | `(session_id: str) -> list[TaskCard]` | grep task_repo.py |
| list_by_namespace | `(namespace) -> list[TaskCard]` | grep task_repo.py |
| list_active | `() -> list[TaskCard]` | grep task_repo.py |
| list_by_dependency | `(dependency_task_id: str) -> list[TaskCard]` | grep task_repo.py |
| list_by_tag | `(tag: str) -> list[TaskCard]` | grep task_repo.py |
| list_by_blocked_by | `(blocker_task_id: str) -> list[TaskCard]` | grep task_repo.py |

## 验收标准

- [ ] 15/15 方法签名与 §4 完全一致
- [ ] 差异 → §20 risk register
