---
task_id: "TASK-INF-0A18"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §3.0.19~§3.0.20 — C扩展/原生API绕过防护 + 进程级内存保护 (D-018-52~53)"

title: "实现取证级安全保障(下)——C扩展绕过防护 + 进程级内存保护（D-018-52~53）"
description: |
  实现§3.0.19~3.0.20两项深度防护：
  1. D-018-52 C扩展/原生API绕过防护——ctypes/cffi/Cython调用OS API绕过Python层安全检测
  2. D-018-53 进程级内存保护——key material/decision cache/agent token在内存中加密存储
     +Guardian进程独立保护+ASCII art绕过检测(Houdini prompt injection)
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\permission_guard.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\native_api_guard.py"
    description: "D-018-52 C扩展绕过防护——ctypes/cffi/Cython检测+OS API调用拦截+静态+动态双重检测"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\memory_guard.py"
    description: "D-018-53进程级内存保护——key/decision/token加密内存+Guardian进程+ASCII art绕过检测"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_forensic_c.py"
    description: "取证级安全C组测试(2项)"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\native_api_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\memory_guard.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_forensic_c.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§3.0.19~3.0.20深度防护完整规范+决策D-018-52~53+ASCII art绕过+C扩展拦截"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 60

acceptance_criteria:
  - "native_api_guard:ctypes导入→静态检测ctypes.CDLL/syscall→AUTO_GUARD+动态拦截OS API调用"
  - "memory_guard:secret/API key/decision cache→加密内存存储(fernet/AES-GCM)"
  - "memory_guard:Guardian进程独立进程保护密钥内存不可被Agent进程读取"
  - "memory_guard:ASCII art载入+隐藏命令检测(unicode box drawing+行内base64+Houdini)"
  - "memory_guard:中文双关语/多意行检测+语境冲突分析"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\native_api_guard.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\memory_guard.py
  3. 删除 D:\ZephyrAlpha\tests\agent_rbac\test_forensic_c.py
  4. 如启动了Guardian进程——kill该进程

depends_on:
  - "TASK-INF-0A13"
blocked_by: []

status: "created"

tags_fn:
  - "infra"
  - "security"
  - "forensic"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-018"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
