---
task_id: "TASK-INF-0208"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 2.3 + §6.2 B9/B40"

title: "回滚队列 + 并发序列化 + 优先级排序——rollback_lock 实现"
description: |
  实现 rollback_lock.py 全局锁（rollback.lock + SQLite advisory lock）：
  - 并发请求排队，超时 10s 返回 BUSY
  - 回滚队列按优先级排序：P0=hard_failure 插队 / P1=soft_failure / P2=manual
  - rollback_queue.insert_with_priority(priority, task)
  - 锁持有期间检测外部文件修改（B22）→ 返回 CONFLICT
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_lock.py"
    description: "全局锁——rollback.lock + SQLite advisory lock + 队列管理 + 优先级排序"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_lock.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§2.2 回滚锁流程 + §6.2 B9/B40 并发序列化盲点 + R3/R4 风险"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "rollback.lock 文件锁 + SQLite advisory lock 双保护"
  - "并发请求排队，超时 10s 返回 BUSY"
  - "优先级队列：P0(hard_failure) 跳队插最前"
  - "锁持有期间 watchdog/inotify 检测外部文件修改 → 终止 revert → CONFLICT"
  - "锁释放后重试或上报 Owner"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\rollback\rollback_lock.py

depends_on:
  - "TASK-INF-0203"
blocked_by: []
status: "done"

tags_fn: ["infra"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-021"]

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
