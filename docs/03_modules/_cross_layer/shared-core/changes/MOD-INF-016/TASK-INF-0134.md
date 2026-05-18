---
task_id: "TASK-INF-0134"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §2.10 ProcessPool 增强"

title: "增强 ProcessPool 空闲超时回收 + DaemonRegistry 集成"
description: "修改现有 process_pool.py：新增 idle_timeout_s 参数(默认600s)实现空闲超时自动回收，新增 DaemonRegistry 注册/注销逻辑。新增 launch_daemon() 方法。不改变现有 get_or_create/terminate_all 接口签名。"
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\infra\\process_pool.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\daemon_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\resource_optimization_models.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\infra\\process_pool.py"
    description: "增强后的 MCPProcessPool——新增 idle_timeout_s 空闲超时 + DaemonRegistry 集成 + launch_daemon()"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\infra\\process_pool.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\daemon_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\resource_optimization_models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\runtime\\auto_runtime_core.py"

applicable_rules:
  - module_id: "RULE-ZERO"
    section: "全篇"
    reason: "修改前锁文件"
  - module_id: "防幻觉#8"
    section: "编辑优先"
    reason: "SearchReplace 精确替换，禁止删+建"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\infra\\process_pool.py"
    reason: "理解现有 _zombie_scan_loop 和 _remove_entry 逻辑"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\daemon_registry.py"
    reason: "理解 register / unregister 签名"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\lifecycle\\resource_optimization_models.py"
    reason: "理解 ProcessPoolStats 是否需要扩展"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1", "M3"]
estimated_tokens: 8000
timeout_minutes: 20

acceptance_criteria:
  - "ProcessPool.__init__ 新增 idle_timeout_s 参数，默认 600"
  - "_zombie_scan_loop 中增加空闲超时检测：last_used_at 超过 idle_timeout_s 的进程被 _remove_entry"
  - "get_or_create 成功后自动调用 DaemonRegistry.register(name, start_fn, stop_fn, priority=3)"
  - "_remove_entry 时自动调用 DaemonRegistry.unregister(name)"
  - "新增 launch_daemon(name, target_fn) 方法，内部调用 ProcessPool + DaemonRegistry"
  - "现有接口签名不变（向后兼容）"
  - "ProcessPoolStats 新增 idle_count 字段"

rollback_instructions: "git checkout src/zephyr/shared/infra/process_pool.py"
depends_on: ["TASK-INF-0133"]
blocked_by: []
status: "created"

tags_fn: ["infra"]
tags_ly: "_cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-016"]

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist:
  - "Edit-only: SearchReplace 精确替换，不删+建"
  - "向后兼容: 现有调用方不加 idle_timeout_s 参数时行为不变"
  - "线程安全: idle 检测和 DaemonRegistry 调用在 _lock 内执行"
---